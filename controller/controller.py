from datetime import datetime

from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QFileDialog

from services.export_service import ExportService
from services.llm_service import LLMService
from services.pdf_service import PDFService
from services.conversation_service import (
    save_conv, load_convs, load_conv, new_conv_id, delete_conv
)


class _LLMWorker(QThread):
    finished = pyqtSignal(str, object)
    failed = pyqtSignal(str, str)
    progress = pyqtSignal(str, str)   # kind, partial text

    def __init__(self, fn, kind: str):
        super().__init__()
        self._fn = fn
        self._kind = kind

    def run(self):
        try:
            result = self._fn(self._emit_progress)
            self.finished.emit(self._kind, result)
        except Exception as exc:
            self.failed.emit(self._kind, str(exc))

    def _emit_progress(self, kind: str, text: str):
        self.progress.emit(kind, text)


class Controller(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self.llm = LLMService()
        self.pdf_service = PDFService()
        self.export_service = ExportService()
        self._worker: _LLMWorker | None = None
        self._typing_bubble = None
        self._pending_name: str | None = None
        self._stream_text: str = ""
        self._connect()
        self._restore_session()

    def _connect(self):
        self.view.on_diagnose_clicked(self.analyze)
        self.view.on_justify_clicked(self.show_justification)
        self.view.on_chat_send(self.send_chat)
        self.view.on_pdf_clicked(self.open_pdf_manager)
        self.view.on_pdf_add_clicked(self.manage_pdfs)
        self.view.on_export_clicked(self.export_diagnosis)
        self.view.on_new_chat(self.new_chat)
        self.view.on_conv_selected(self.load_conversation)

    # ── Session / conversations ───────────────────────────────

    def _restore_session(self):
        convs = load_convs()
        self.view.show_conversations(convs)
        if convs:
            # Load the most recent conversation silently
            self._load_conv_data(convs[0]["id"], update_list=False)

    def _auto_save(self):
        if not self.model.current_conv_id:
            self.model.current_conv_id = new_conv_id()
        symptoms = self.model.symptoms or []
        name = self._pending_name or \
               (symptoms[0][:40] if symptoms else None) or \
               (self.model.diagnosis.get("diagnosis", "")[:40] if self.model.diagnosis else None) or \
               "Sin título"
        data = {
            "id": self.model.current_conv_id,
            "name": name,
            "symptoms": symptoms,
            "chat_history": self.model.chat_history[-60:],
            "hypotheses": self.model.hypotheses,
            "diagnosis": self.model.diagnosis,
            "justification": self.model.justification,
            "pdf_paths": [p["path"] for p in self.model.pdfs],
        }
        save_conv(self.model.current_conv_id, data)

    def new_chat(self, name: str = "Sin título"):
        self._auto_save()
        self.model.current_conv_id = new_conv_id()
        self.model.symptoms = []
        self.model.chat_history = []
        self.model.hypotheses = []
        self.model.diagnosis = {}
        self.model.justification = []
        self.model.pdfs = []
        self._pending_name = name.strip() or "Sin título"
        self._auto_save()  # persist the new empty conversation so it appears in list
        self.view.clear_chat()
        self.view.clear_results()
        self.view.set_editor_text("")
        self.view.show_pdf_window([])
        self.view.add_chat_message(
            "assistant",
            "Nuevo caso iniciado. Describe los hechos en el editor o escríbeme directamente."
        )
        self.view.show_conversations(load_convs())

    def load_conversation(self, conv_id: str):
        self._auto_save()
        self._load_conv_data(conv_id, update_list=True)

    def _load_conv_data(self, conv_id: str, update_list: bool):
        data = load_conv(conv_id)
        if not data:
            return
        self.model.current_conv_id = conv_id
        self.model.symptoms = data.get("symptoms", [])
        self.model.chat_history = data.get("chat_history", [])
        self.model.hypotheses = data.get("hypotheses", [])
        self.model.diagnosis = data.get("diagnosis", {})
        self.model.justification = data.get("justification", [])

        # Reload PDFs that still exist
        import pathlib
        pdf_paths = [p for p in data.get("pdf_paths", []) if pathlib.Path(p).exists()]
        self.model.pdfs = self.pdf_service.add_pdfs(pdf_paths) if pdf_paths else []
        self.view.show_pdf_window(self.model.pdfs)

        self.view.clear_chat()
        for msg in self.model.chat_history:
            self.view.add_chat_message(msg["role"], msg["content"])
        if self.model.symptoms:
            self.view.set_editor_text("\n".join(self.model.symptoms))
        self.view.clear_results()
        if self.model.hypotheses:
            self.view.show_hypotheses(self.model.hypotheses)
        if self.model.diagnosis:
            self.view.show_diagnosis(self.model.diagnosis)
        if update_list:
            self.view.show_conversations(load_convs())

    # ── Analysis ──────────────────────────────────────────────

    def analyze(self):
        self.model.symptoms = self.view.get_symptoms()
        if not self.model.symptoms:
            self.view.add_chat_message(
                "assistant",
                "Escribe el resumen del caso en el editor antes de analizar."
            )
            self.view.set_running(False)
            return
        symptoms = list(self.model.symptoms)
        mode = self.model.mode
        pdfs = list(self.model.pdfs)

        def _run(emit):
            import types
            hyps = self.llm.get_hypotheses({"symptoms": symptoms, "mode": mode, "pdfs": pdfs})
            ctx = types.SimpleNamespace(symptoms=symptoms, hypotheses=hyps, pdfs=pdfs)
            diag = self.llm.get_diagnosis(ctx)
            return hyps, diag

        self._run_worker("analyze", _run)

    def _run_worker(self, kind: str, fn):
        if self._worker and self._worker.isRunning():
            return
        self._worker = _LLMWorker(fn, kind)
        self._worker.finished.connect(self._on_done, Qt.ConnectionType.QueuedConnection)
        self._worker.failed.connect(self._on_error, Qt.ConnectionType.QueuedConnection)
        self._worker.progress.connect(self._on_progress, Qt.ConnectionType.QueuedConnection)
        self._worker.start()

    def _on_progress(self, kind: str, text: str):
        if kind == "chat" and self._typing_bubble:
            self._typing_bubble.set_content(text)
            self._typing_bubble.repaint()

    def _on_done(self, kind: str, result):
        if kind == "analyze":
            hyps, diag = result
            self.model.hypotheses = hyps
            self.model.diagnosis = diag
            self.model.justification = diag.get("justification", diag.get("summary", ""))
            now = datetime.now()
            months = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
            self.model.history.insert(0, {
                "label": diag.get("diagnosis", "Análisis"),
                "severity": diag.get("severity", "medium"),
                "when": f"{now.day} {months[now.month - 1]} · {now.strftime('%H:%M')}",
            })
            self.view.show_hypotheses(hyps)
            self.view.show_diagnosis(diag)
            self._auto_save()

            sev_icons = {"high": "● ALTO", "medium": "◐ MEDIO", "low": "○ BAJO"}
            sev = sev_icons.get(diag.get("severity", "medium"), "")
            lines = [
                f"**Análisis: {sev}**",
                "",
                f"**{diag.get('diagnosis', '')}**",
                "",
                diag.get("summary", ""),
                "",
                "─────────────────────",
                "**Hipótesis:**",
                "",
            ]
            for h in sorted(hyps, key=lambda x: x.get("score", 0), reverse=True):
                icon = {"high": "●", "medium": "◐", "low": "○"}.get(h.get("severity", "medium"), "•")
                lines.append(f"- {icon} **{h['name']}** — {int(h.get('score', 0) * 100)}%")
                if h.get("detail"):
                    lines.append(f"  {h['detail']}")
            self.view.add_chat_message("assistant", "\n".join(lines))
            self.view.add_regenerate_button(self.analyze)
            self.view.show_conversations(load_convs())

        elif kind == "chat":
            self._stream_text = ""
            if self._typing_bubble:
                self._typing_bubble.set_content(result)
                self._typing_bubble = None
            else:
                self.view.add_chat_message("assistant", result)
            self.model.chat_history.append({"role": "assistant", "content": result})
            self._auto_save()

        self.view.set_running(False)

    def _on_error(self, kind: str, error_msg: str):
        self._stream_text = ""
        if self._typing_bubble:
            self.view.remove_bubble(self._typing_bubble)
            self._typing_bubble = None
        self.view.set_running(False)
        self.view.show_status_error(f"Error ({kind}): {error_msg}")
        self.view.add_chat_message("assistant", f"Error al procesar la solicitud:\n{error_msg}")

    # ── Other actions ─────────────────────────────────────────

    def send_chat(self, text: str):
        self.view.add_chat_message("user", text)
        self.model.chat_history.append({"role": "user", "content": text})
        case_text = "\n".join(self.view.get_symptoms())
        pdfs = list(self.model.pdfs)
        history = list(self.model.chat_history)
        self.view.set_running(True)
        self._typing_bubble = self.view.show_typing_indicator()

        def _run(emit):
            return self.llm.chat(
                history, case_text, pdfs,
                on_token=lambda t: emit("chat", t)
            )

        self._run_worker("chat", _run)

    def show_justification(self):
        self.view.show_justification(self.model.justification)

    def manage_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self.view, "Seleccionar PDFs", "", "PDF Files (*.pdf)"
        )
        if files:
            self.model.pdfs.extend(self.pdf_service.add_pdfs(files))
            self.view.show_pdf_window(self.model.pdfs)
            self._auto_save()

    def export_diagnosis(self):
        if not self.model.diagnosis:
            self.view.add_chat_message("assistant", "No hay diagnóstico para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Exportar diagnóstico", "diagnostico.pdf", "PDF Files (*.pdf)"
        )
        if not path:
            return
        try:
            self.export_service.export_pdf(path, self.model.diagnosis, self.model.hypotheses)
            self.view.add_chat_message("assistant", f"Exportado en:\n{path}")
        except Exception as e:
            self.view.show_status_error(f"Error al exportar: {e}")

    def open_pdf_manager(self):
        self.view.show_pdf_window(self.model.pdfs)
