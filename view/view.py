from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QTextEdit, QFileDialog, QDialog, QFrame, QSizePolicy,
    QListWidgetItem, QStackedWidget, QSplitter, QScrollArea, QProgressBar,
    QScrollBar, QLineEdit, QAbstractScrollArea
)
from datetime import date as _date
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import (
    QFont, QImage, QPixmap, QGuiApplication, QIcon, QPainter, QColor,
    QKeySequence, QPen, QPainterPath, QShortcut
)

try:
    import fitz
    PDF_PREVIEW_AVAILABLE = True
except Exception:
    fitz = None
    PDF_PREVIEW_AVAILABLE = False


# ── Color tokens (cool neutral SaaS) ─────────────────────────────────────────

LIGHT_THEME = {
    "bg": "#f6f7f9",
    "canvas": "#ffffff",
    "surface2": "#fafbfc",
    "border": "#e4e7eb",
    "border_strong": "#cbd0d6",
    "text": "#0f1419",
    "text_muted": "#5b6573",
    "text_subtle": "#8a93a1",
    "accent": "#3b7dd8",
    "accent_soft": "#eef4fd",
    "accent_text": "#2a5db8",
    "success": "#1a9452",
    "warn": "#c47a0d",
    "danger": "#d43535",
    "scrollbar_bg": "#f0f1f3",
    "scrollbar_handle": "#c5cad2",
}

DARK_THEME = {
    "bg": "#0c1014",
    "canvas": "#11161c",
    "surface2": "#161c24",
    "border": "#222a35",
    "border_strong": "#2e3744",
    "text": "#e6ebf2",
    "text_muted": "#9aa4b2",
    "text_subtle": "#6b7585",
    "accent": "#6b9eff",
    "accent_soft": "#1a2c4a",
    "accent_text": "#93baf7",
    "success": "#4ade82",
    "warn": "#f59e0b",
    "danger": "#f47474",
    "scrollbar_bg": "#0c1014",
    "scrollbar_handle": "#2e3744",
}

TIMELINE_STEPS = [
    ("s1", "Resumen recibido"),
    ("s2", "Indexando documentos"),
    ("s3", "Extrayendo cláusulas"),
    ("s4", "Cotejo jurisprudencial"),
    ("s5", "Generando hipótesis"),
]
TIMELINE_STEP_MS = [350, 800, 700, 900, 600]


def severity_color(theme, severity):
    return {"high": theme["danger"], "medium": theme["warn"], "low": theme["success"]}.get(
        severity, theme["text_muted"]
    )


def severity_label(severity):
    return {"high": "ALTO", "medium": "MEDIO", "low": "BAJO"}.get(severity, "—")


def get_stylesheet(theme):
    return f"""
        QWidget {{
            background-color: {theme['bg']};
            color: {theme['text']};
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', sans-serif;
            font-size: 13px;
        }}
        QMainWindow, QDialog {{
            background-color: {theme['bg']};
        }}
        QTextEdit {{
            background-color: {theme['canvas']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 12px;
            selection-background-color: {theme['accent']};
        }}
        QTextEdit:focus {{
            border: 1px solid {theme['accent']};
        }}
        QListWidget {{
            background-color: {theme['canvas']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 4px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            border-radius: 4px;
        }}
        QListWidget::item:selected {{
            background-color: {theme['accent_soft']};
            color: {theme['accent_text']};
        }}
        QListWidget::item:hover:!selected {{
            background-color: {theme['surface2']};
        }}
        QLineEdit {{
            background-color: {theme['surface2']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 4px 10px;
        }}
        QLineEdit:focus {{
            border: 1px solid {theme['accent']};
            background-color: {theme['canvas']};
        }}
        QPushButton {{
            background-color: {theme['canvas']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 7px;
            padding: 5px 10px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            border-color: {theme['border_strong']};
            background-color: {theme['surface2']};
        }}
        QPushButton:pressed {{ background-color: {theme['surface2']}; }}
        QPushButton:disabled {{ color: {theme['text_subtle']}; }}
        QPushButton#primary {{
            background-color: {theme['accent']};
            color: #ffffff;
            border-color: {theme['accent']};
        }}
        QPushButton#primary:hover {{ background-color: {theme['accent_text']}; }}
        QPushButton#primary:disabled {{
            background-color: {theme['accent']};
            color: #ffffff;
            opacity: 0.5;
        }}
        QPushButton#ghost {{
            background-color: transparent;
            border: 1px solid transparent;
            color: {theme['text_muted']};
        }}
        QPushButton#ghost:hover {{
            background-color: {theme['surface2']};
            color: {theme['text']};
        }}
        QPushButton#soft {{
            background-color: {theme['surface2']};
            border: 1px solid {theme['border']};
            color: {theme['text']};
        }}
        QPushButton#soft:hover {{ border-color: {theme['border_strong']}; }}
        QPushButton#icon_btn {{
            background-color: transparent;
            border: 1px solid transparent;
            color: {theme['text_muted']};
            border-radius: 6px;
            padding: 3px;
            font-size: 14px;
        }}
        QPushButton#icon_btn:hover {{
            background-color: {theme['surface2']};
            color: {theme['text']};
        }}
        QLabel {{ background-color: transparent; color: {theme['text']}; }}
        QLabel#section {{ font-weight: 600; font-size: 14px; }}
        QLabel#hint {{ color: {theme['text_muted']}; font-size: 12px; }}
        QLabel#mono {{
            font-family: 'JetBrains Mono', 'Cascadia Mono', 'Consolas', monospace;
            font-size: 11px;
            color: {theme['text_subtle']};
        }}
        QFrame#command_bar {{
            background-color: {theme['canvas']};
            border-bottom: 1px solid {theme['border']};
        }}
        QFrame#pdf_tray {{
            background-color: {theme['canvas']};
            border: none;
        }}
        QFrame#results_pane {{
            background-color: {theme['canvas']};
            border: none;
        }}
        QFrame#timeline_box {{
            background-color: {theme['canvas']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
        }}
        QFrame#card {{
            background-color: {theme['canvas']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
        }}
        QFrame#chat_user_bg {{
            background-color: {theme['accent_soft']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
        }}
        QFrame#chat_assistant_bg {{
            background-color: {theme['surface2']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
        }}
        QFrame#drawer_panel {{
            background-color: {theme['canvas']};
            border-left: 1px solid {theme['border']};
        }}
        QSplitter::handle {{
            background-color: {theme['border']};
        }}
        QSplitter::handle:horizontal {{ width: 1px; }}
        QProgressBar {{
            background-color: {theme['surface2']};
            border: none;
            border-radius: 2px;
        }}
        QProgressBar::chunk {{
            background-color: {theme['accent']};
            border-radius: 2px;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {theme['scrollbar_bg']};
            width: 7px;
            border-radius: 3px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {theme['scrollbar_handle']};
            min-height: 20px;
            border-radius: 3px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none; background: none; height: 0;
        }}
        QScrollBar:horizontal {{
            border: none;
            background: {theme['scrollbar_bg']};
            height: 7px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal {{
            background: {theme['scrollbar_handle']};
            min-width: 20px;
            border-radius: 3px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none; background: none; width: 0;
        }}
        QTabWidget::pane {{
            border: none;
        }}
        QTabBar::tab {{
            background: {theme['surface2']};
            color: {theme['text_muted']};
            border: none;
            padding: 6px 14px;
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background: {theme['canvas']};
            color: {theme['text']};
            font-weight: 600;
            border-bottom: 2px solid {theme['accent']};
        }}
        QTabBar::tab:hover:!selected {{
            background: {theme['border']};
        }}
        QStatusBar {{
            background-color: {theme['canvas']};
            border-top: 1px solid {theme['border']};
            color: {theme['text_subtle']};
            font-family: 'JetBrains Mono', 'Cascadia Mono', 'Consolas', monospace;
            font-size: 11px;
        }}
        QToolTip {{
            background-color: {theme['canvas']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 12px;
        }}
    """


def build_app_icon():
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(2, 2, 60, 60, 14, 14)
    p.fillPath(path, QColor("#3b7dd8"))
    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "§")
    p.end()
    return QIcon(pix)


def build_pdf_icon():
    pix = QPixmap(20, 26)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.fillRect(1, 1, 18, 24, QColor("#d43535"))
    p.setPen(Qt.GlobalColor.white)
    p.setFont(QFont("Arial", 6, QFont.Weight.Bold))
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "PDF")
    p.end()
    return QIcon(pix)


# ── Custom widgets ────────────────────────────────────────────────────────────

class ElidedLabel(QLabel):
    """QLabel that elides text with '…' without triggering resize loops."""

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = painter.fontMetrics()
        elided = metrics.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width())
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(self.rect(), int(self.alignment()), elided)


class SeverityPill(QFrame):
    """Colored dot + label pill for severity levels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(22)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 2, 9, 2)
        lay.setSpacing(5)
        self._dot = QLabel()
        self._dot.setFixedSize(7, 7)
        self._lbl = QLabel("—")
        lay.addWidget(self._dot)
        lay.addWidget(self._lbl)
        self._theme = LIGHT_THEME
        self._severity = ""

    def set_severity(self, severity, theme):
        self._severity = severity
        self._theme = theme
        c = severity_color(theme, severity)
        label = severity_label(severity)
        self._dot.setStyleSheet(f"background-color: {c}; border-radius: 3px;")
        self._lbl.setText(label)
        self._lbl.setStyleSheet(
            f"color: {c}; font-size: 11px; font-weight: 600;"
            f" font-family: 'JetBrains Mono', 'Consolas', monospace;"
        )
        bg = QColor(c)
        bg.setAlpha(30)
        border = QColor(c)
        border.setAlpha(55)
        self.setStyleSheet(
            f"QFrame {{ background-color: rgba({bg.red()},{bg.green()},{bg.blue()},30);"
            f" border: 1px solid rgba({border.red()},{border.green()},{border.blue()},55);"
            f" border-radius: 11px; }}"
        )


class SeverityMeter(QWidget):
    """3-segment bar showing low/medium/high severity."""

    SEG_COLORS = {"low": "success", "medium": "warn", "high": "danger"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self._severity = ""
        self._theme = LIGHT_THEME

    def set_severity(self, severity, theme):
        self._severity = severity
        self._theme = theme
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        seg_w = (w - 8) // 3
        segs = ["low", "medium", "high"]
        active_map = {
            "high": {"low", "medium", "high"},
            "medium": {"low", "medium"},
            "low": {"low"},
        }
        active = active_map.get(self._severity, set())
        for i, s in enumerate(segs):
            x = i * (seg_w + 4)
            c = QColor(self._theme[self.SEG_COLORS[s]]) if s in active else QColor(self._theme["border"])
            path = QPainterPath()
            path.addRoundedRect(x, 0, seg_w, h, 4, 4)
            p.fillPath(path, c)
        p.end()


class HypothesisRow(QFrame):
    """Compact single-line hypothesis row."""

    def __init__(self, hyp, theme, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        c = severity_color(theme, hyp.get("severity", "medium"))
        pct = int(hyp.get("score", 0) * 100)

        dot = QLabel("●")
        dot.setFixedWidth(10)
        dot.setStyleSheet(f"color: {c}; font-size: 7px; background: transparent;")
        lay.addWidget(dot)

        name_lbl = QLabel(hyp.get("name", ""))
        name_lbl.setStyleSheet(f"font-size: 11.5px; font-weight: 500; background: transparent;")
        name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        name_lbl.setMinimumWidth(0)
        lay.addWidget(name_lbl, 1)

        # Mini progress bar
        bar_bg = QFrame()
        bar_bg.setFixedSize(44, 4)
        bar_bg.setStyleSheet(f"background-color: {theme['border']}; border-radius: 2px;")
        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(4)
        bar_fill.setStyleSheet(f"background-color: {c}; border-radius: 2px;")
        bar_fill.setFixedWidth(max(0, int(44 * pct / 100)))
        lay.addWidget(bar_bg)

        score_lbl = QLabel(f"{pct}%")
        score_lbl.setFixedWidth(30)
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        score_lbl.setStyleSheet(
            f"color: {c}; font-size: 10.5px; font-weight: 600; background: transparent;"
            f" font-family: 'JetBrains Mono', 'Consolas', monospace;"
        )
        lay.addWidget(score_lbl)


class HypothesisBar(QFrame):
    """Full-width horizontal bar chart row for a hypothesis."""

    def __init__(self, hyp, theme, parent=None):
        super().__init__(parent)
        c = severity_color(theme, hyp.get("severity", "medium"))
        pct = int(hyp.get("score", 0) * 100)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(6)
        name_lbl = QLabel(hyp.get("name", ""))
        name_lbl.setStyleSheet("font-size: 12px; font-weight: 500; background: transparent;")
        name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top.addWidget(name_lbl, 1)

        pct_lbl = QLabel(f"{pct}%")
        pct_lbl.setStyleSheet(
            f"color: {c}; font-size: 11px; font-weight: 600; background: transparent;"
            f" font-family: 'JetBrains Mono', 'Consolas', monospace;"
        )
        top.addWidget(pct_lbl)
        lay.addLayout(top)

        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet(f"background-color: {theme['border']}; border-radius: 3px;")
        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(6)
        bar_fill.setStyleSheet(f"background-color: {c}; border-radius: 3px;")
        bar_fill.setFixedWidth(0)
        self._bar_fill = bar_fill
        self._pct = pct
        lay.addWidget(bar_bg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        total = self.width()
        if total > 0 and hasattr(self, "_bar_fill"):
            self._bar_fill.setFixedWidth(max(0, int(total * self._pct / 100)))


class CitationRow(QFrame):
    """Compact single-line citation row."""

    def __init__(self, citation, theme, parent=None):
        super().__init__(parent)
        self.setFixedHeight(26)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        doc_name = citation.get("doc", citation.get("label", citation.get("name", "")))
        self._name_lbl = ElidedLabel(doc_name)
        self._name_lbl.setStyleSheet(
            f"font-size: 11px; color: {theme['accent_text']}; background: transparent;"
        )
        self._name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._name_lbl.setMinimumWidth(0)
        lay.addWidget(self._name_lbl, 1)

        page = citation.get("page")
        if page is not None:
            page_lbl = QLabel(f"p.{page}")
            page_lbl.setObjectName("mono")
            page_lbl.setFixedWidth(28)
            lay.addWidget(page_lbl)

class TimelineStep(QFrame):
    """Single step in the analysis timeline."""

    def __init__(self, label, state="pending", theme=None, ms=None, parent=None):
        super().__init__(parent)
        if theme is None:
            theme = LIGHT_THEME
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(10)

        c = {
            "done": theme["success"],
            "running": theme["accent"],
            "pending": theme["text_subtle"],
        }.get(state, theme["text_subtle"])

        self._dot = QLabel()
        self._dot.setFixedSize(14, 14)
        if state == "done":
            self._dot.setStyleSheet(
                f"background-color: {c}; border-radius: 7px;"
                f" border: 1.5px solid {c}; color: white;"
                f" font-size: 8px; font-weight: 700;"
            )
            self._dot.setText("✓")
            self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif state == "running":
            self._dot.setStyleSheet(
                f"border: 1.5px solid {c}; border-radius: 7px; background: transparent;"
            )
            self._inner = QLabel()
            self._inner.setParent(self._dot)
            self._inner.setFixedSize(6, 6)
            self._inner.move(3, 3)
            self._inner.setStyleSheet(f"background-color: {c}; border-radius: 3px;")
        else:
            self._dot.setStyleSheet(
                f"border: 1.5px solid {c}; border-radius: 7px; background: transparent;"
            )
        lay.addWidget(self._dot)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {theme['text'] if state != 'pending' else theme['text_muted']};"
            f" font-size: 12.5px;"
        )
        lay.addWidget(lbl, 1)

        if state == "running":
            status_lbl = QLabel("en curso…")
            status_lbl.setObjectName("mono")
            lay.addWidget(status_lbl)
        elif state == "done" and ms:
            ms_lbl = QLabel(f"{ms}ms")
            ms_lbl.setObjectName("mono")
            lay.addWidget(ms_lbl)


class BackdropWidget(QWidget):
    """Semi-transparent backdrop for drawers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.hide()

    def paintEvent(self, event):
        pass

    def mousePressEvent(self, event):
        if hasattr(self, '_close_cb') and self._close_cb:
            self._close_cb()

    def set_close_callback(self, cb):
        self._close_cb = cb


class DrawerPanel(QFrame):
    """Animated side drawer that slides in from the right."""

    WIDTH = 460

    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setObjectName("drawer_panel")
        self.hide()
        self._open = False

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("card")
        header.setStyleSheet("QFrame#card { border-radius: 0; border-left: none; border-top: none; border-right: none; }")
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(18, 14, 14, 14)
        header_lay.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self._title_lbl = QLabel(title)
        self._title_lbl.setStyleSheet("font-size: 13px; font-weight: 600;")
        title_col.addWidget(self._title_lbl)
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("hint")
            title_col.addWidget(sub_lbl)
        header_lay.addLayout(title_col, 1)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("icon_btn")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Cerrar (Esc)")
        close_btn.clicked.connect(self.close_drawer)
        header_lay.addWidget(close_btn)
        lay.addWidget(header)

        # Content scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._content_widget = QWidget()
        self._content_lay = QVBoxLayout(self._content_widget)
        self._content_lay.setContentsMargins(18, 16, 18, 16)
        self._content_lay.setSpacing(16)
        self._content_lay.addStretch()
        self._scroll.setWidget(self._content_widget)
        lay.addWidget(self._scroll, 1)

        # Footer
        self._footer = QFrame()
        self._footer.setObjectName("card")
        self._footer.setStyleSheet("QFrame#card { border-radius: 0; border-left: none; border-bottom: none; border-right: none; }")
        footer_lay = QHBoxLayout(self._footer)
        footer_lay.setContentsMargins(18, 12, 18, 12)
        footer_lay.addStretch()
        lay.addWidget(self._footer)

        self._anim = None
        self._backdrop = None
        self._close_esc = None

    def set_backdrop(self, backdrop):
        self._backdrop = backdrop
        backdrop.set_close_callback(self.close_drawer)

    def open_drawer(self):
        if self._open:
            return
        self._open = True
        p = self.parent()
        if not p:
            return
        h = p.height()
        w = self.WIDTH
        self.setGeometry(p.width(), 0, w, h)
        self.show()
        self.raise_()
        if self._backdrop:
            self._backdrop.setGeometry(p.rect())
            self._backdrop.show()
            self._backdrop.raise_()
        self._start_anim(
            QRect(p.width(), 0, w, h),
            QRect(p.width() - w, 0, w, h),
        )

    def close_drawer(self):
        if not self._open:
            return
        self._open = False
        p = self.parent()
        if not p:
            self.hide()
            return
        h = p.height()
        w = self.WIDTH
        self._start_anim(
            QRect(p.width() - w, 0, w, h),
            QRect(p.width(), 0, w, h),
            on_finish=self._on_close_done,
        )

    def _on_close_done(self):
        self.hide()
        if self._backdrop:
            self._backdrop.hide()

    def _start_anim(self, start, end, on_finish=None):
        if self._anim:
            self._anim.stop()
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        if on_finish:
            self._anim.finished.connect(on_finish)
        self._anim.start()

    def set_content(self, widget):
        lay = self._content_lay
        while lay.count() > 1:
            item = lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        lay.insertWidget(0, widget)

    def set_footer_widget(self, widget):
        lay = self._footer.layout()
        while lay.count() > 1:
            item = lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        lay.insertWidget(0, widget)

    def is_open(self):
        return self._open


class ResultsPane(QWidget):
    """Right pane: severity header, hypotheses, citations."""

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self._theme = theme
        self._severity = ""
        self._on_justify = None
        self._on_export = None
        self._diagnosis_data = {}
        self._hypotheses_data = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._container = QWidget()
        self._container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._lay = QVBoxLayout(self._container)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)
        self._scroll.setWidget(self._container)
        outer.addWidget(self._scroll)

        self._build_empty()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        vw = self._scroll.viewport().width()
        if vw > 0:
            self._container.setMaximumWidth(vw)

    def _build_empty(self):
        t = self._theme
        lay = self._lay

        # Severity header (placeholder)
        self._severity_header = QFrame()
        self._severity_header.setObjectName("card")
        self._severity_header.setStyleSheet(
            "QFrame#card { border-radius: 0; border-left: none; border-right: none; border-top: none; }"
        )
        sh_lay = QVBoxLayout(self._severity_header)
        sh_lay.setContentsMargins(16, 14, 16, 14)
        sh_lay.setSpacing(8)

        top_row = QHBoxLayout()
        self._pill = SeverityPill()
        top_row.addWidget(self._pill)
        self._date_lbl = QLabel()
        self._date_lbl.setObjectName("mono")
        top_row.addWidget(self._date_lbl)
        top_row.addStretch()
        sh_lay.addLayout(top_row)

        self._diag_title = QLabel("Sin análisis aún")
        self._diag_title.setStyleSheet("font-size: 13px; font-weight: 600;")
        self._diag_title.setWordWrap(True)
        self._diag_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sh_lay.addWidget(self._diag_title)

        self._severity_meter = SeverityMeter()
        sh_lay.addWidget(self._severity_meter)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        self._confidence_lbl = QLabel()
        self._confidence_lbl.setObjectName("mono")
        self._confidence_lbl.setStyleSheet("font-size: 10px;")
        self._confidence_lbl.hide()
        meta_row.addWidget(self._confidence_lbl)
        self._pdf_badge = QLabel()
        self._pdf_badge.setObjectName("mono")
        self._pdf_badge.setStyleSheet("font-size: 10px;")
        self._pdf_badge.hide()
        meta_row.addWidget(self._pdf_badge)
        meta_row.addStretch()
        sh_lay.addLayout(meta_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self._just_btn = QPushButton("Justificación")
        self._just_btn.setObjectName("soft")
        self._just_btn.setFixedHeight(26)
        self._just_btn.clicked.connect(lambda: self._on_justify() if self._on_justify else None)
        self._copy_diag_btn = QPushButton("Copiar")
        self._copy_diag_btn.setObjectName("ghost")
        self._copy_diag_btn.setFixedHeight(26)
        self._copy_diag_btn.clicked.connect(self._copy_summary)
        self._export_btn = QPushButton("Exportar")
        self._export_btn.setObjectName("ghost")
        self._export_btn.setFixedHeight(26)
        btn_row.addWidget(self._just_btn)
        btn_row.addWidget(self._copy_diag_btn)
        btn_row.addWidget(self._export_btn)
        btn_row.addStretch()
        sh_lay.addLayout(btn_row)
        lay.addWidget(self._severity_header)

        # Hypotheses section
        self._hyp_section = QFrame()
        hyp_lay = QVBoxLayout(self._hyp_section)
        hyp_lay.setContentsMargins(16, 12, 16, 4)
        hyp_lay.setSpacing(8)

        hyp_header = QLabel("HIPÓTESIS")
        hyp_header.setObjectName("mono")
        hyp_lay.addWidget(hyp_header)

        self._hyp_placeholder = QLabel("—")
        self._hyp_placeholder.setStyleSheet(f"color: {t['text_subtle']}; font-size: 12px;")
        hyp_lay.addWidget(self._hyp_placeholder)

        self._hyp_rows_lay = QVBoxLayout()
        self._hyp_rows_lay.setSpacing(6)
        hyp_lay.addLayout(self._hyp_rows_lay)
        lay.addWidget(self._hyp_section)

        # Citations section
        self._cit_section = QFrame()
        cit_lay = QVBoxLayout(self._cit_section)
        cit_lay.setContentsMargins(16, 4, 16, 14)
        cit_lay.setSpacing(6)

        self._cit_header = QLabel("CITAS")
        self._cit_header.setObjectName("mono")
        cit_lay.addWidget(self._cit_header)

        self._cit_placeholder = QLabel("—")
        self._cit_placeholder.setStyleSheet(f"color: {t['text_subtle']}; font-size: 12px;")
        cit_lay.addWidget(self._cit_placeholder)

        self._cit_rows_lay = QVBoxLayout()
        self._cit_rows_lay.setSpacing(5)
        cit_lay.addLayout(self._cit_rows_lay)
        lay.addWidget(self._cit_section)
        lay.addStretch()

    def set_pdf_count(self, n: int):
        if n > 0:
            self._pdf_badge.setText(f"📄 {n} doc{'s' if n != 1 else ''}")
            self._pdf_badge.show()
        else:
            self._pdf_badge.hide()

    def set_on_justify(self, cb):
        self._on_justify = cb

    def set_on_export(self, cb):
        self._export_btn.clicked.connect(cb)

    def _copy_summary(self):
        d = self._diagnosis_data
        if not d:
            return
        sev_map = {"high": "ALTO", "medium": "MEDIO", "low": "BAJO"}
        lines = [
            f"DIAGNÓSTICO: {d.get('diagnosis', '')}",
            f"Severidad: {sev_map.get(d.get('severity', ''), '—')}",
        ]
        if d.get("summary"):
            lines += ["", d["summary"]]
        if self._hypotheses_data:
            lines += ["", "Hipótesis:"]
            for h in sorted(self._hypotheses_data, key=lambda x: x.get("score", 0), reverse=True):
                pct = int(h.get("score", 0) * 100)
                lines.append(f"  • {h.get('name', '')} — {pct}%")
        QGuiApplication.clipboard().setText("\n".join(lines))
        self._copy_diag_btn.setText("Copiado")
        QTimer.singleShot(1500, lambda: self._copy_diag_btn.setText("Copiar"))

    def _update_confidence(self):
        if not self._hypotheses_data:
            self._confidence_lbl.hide()
            return
        avg = sum(h.get("score", 0) for h in self._hypotheses_data) / len(self._hypotheses_data)
        pct = int(avg * 100)
        t = self._theme
        color = t["success"] if pct >= 70 else t["warn"] if pct >= 40 else t["danger"]
        self._confidence_lbl.setText(f"{pct}% conf.")
        self._confidence_lbl.setStyleSheet(
            f"font-size: 10px; color: {color}; background: transparent;"
        )
        self._confidence_lbl.show()

    def update_theme(self, theme):
        self._theme = theme
        if self._severity:
            self._pill.set_severity(self._severity, theme)
            self._severity_meter.set_severity(self._severity, theme)
        self._update_confidence()

    def update_hypotheses(self, hypotheses):
        t = self._theme
        self._hypotheses_data = hypotheses or []
        while self._hyp_rows_lay.count():
            item = self._hyp_rows_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if hypotheses:
            self._hyp_placeholder.hide()
            sorted_hyps = sorted(hypotheses, key=lambda h: h.get("score", 0), reverse=True)
            header_lbl = self._hyp_section.layout().itemAt(0).widget()
            if header_lbl:
                header_lbl.setText(f"HIPÓTESIS · {len(hypotheses)}")
            for h in sorted_hyps:
                row = HypothesisBar(h, t)
                self._hyp_rows_lay.addWidget(row)
        else:
            self._hyp_placeholder.show()
            self._hyp_placeholder.setText("—")
        self._update_confidence()

    def update_diagnosis(self, diagnosis_data):
        t = self._theme
        self._diagnosis_data = diagnosis_data
        severity = diagnosis_data.get("severity", "medium")
        self._severity = severity
        self._pill.set_severity(severity, t)
        today = _date.today()
        months = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
        self._date_lbl.setText(f"{today.day} {months[today.month-1]}")
        self._diag_title.setText(diagnosis_data.get("diagnosis", diagnosis_data.get("title", "")))
        self._severity_meter.set_severity(severity, t)

        citations = diagnosis_data.get("citations", [])
        while self._cit_rows_lay.count():
            item = self._cit_rows_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if citations:
            self._cit_placeholder.hide()
            self._cit_header.setText(f"CITAS · {len(citations)}")
            for ci in citations:
                row = CitationRow(ci, t)
                self._cit_rows_lay.addWidget(row)
        else:
            self._cit_placeholder.show()


class ProcessingWidget(QFrame):
    """Status bar shown below the chat during analysis."""

    _DOTS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setObjectName("timeline_box")
        self._theme = theme
        self._on_done = None
        self._dot_idx = 0
        self._dot_timer = QTimer()
        self._dot_timer.timeout.connect(self._tick)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(14, 8, 14, 8)
        outer.setSpacing(10)

        self._spinner = QLabel(self._DOTS[0])
        self._spinner.setFixedWidth(16)
        self._spinner.setStyleSheet("font-size: 13px;")
        outer.addWidget(self._spinner)

        self._lbl = QLabel("Listo")
        self._lbl.setObjectName("mono")
        outer.addWidget(self._lbl, 1)

        self._bar = QProgressBar()
        self._bar.setFixedWidth(120)
        self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 0)
        self._bar.hide()
        outer.addWidget(self._bar)

    def start_animation(self, on_done=None):
        self._on_done = on_done
        self._lbl.setText("Iniciando análisis…")
        self._bar.show()
        self._dot_timer.start(80)
        QTimer.singleShot(200, self._fire)

    def _fire(self):
        self._lbl.setText("Procesando con IA…  (puede tardar)")
        if self._on_done:
            self._on_done()

    def _tick(self):
        self._dot_idx = (self._dot_idx + 1) % len(self._DOTS)
        self._spinner.setText(self._DOTS[self._dot_idx])

    def set_done(self):
        self._dot_timer.stop()
        self._spinner.setText("✓")
        self._lbl.setText("Análisis completado")
        self._bar.hide()

    def set_idle(self):
        self._dot_timer.stop()
        self._spinner.setText("○")
        self._lbl.setText("Listo")
        self._bar.hide()

    def update_theme(self, theme):
        self._theme = theme


class ConversationOverlay(QFrame):
    """Floating overlay with conversation list, shown over the PDF tray."""

    WIDTH = 280

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setObjectName("drawer_panel")
        self.hide()
        self._open = False
        self._new_cb = None
        self._select_cb = None
        self._splitter = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        hdr = QHBoxLayout()
        title_lbl = QLabel("Conversaciones")
        title_lbl.setStyleSheet("font-size: 12px; font-weight: 600;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setObjectName("icon_btn")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide_overlay)
        hdr.addWidget(close_btn)
        lay.addLayout(hdr)

        self._new_btn = QPushButton("＋  Nuevo chat")
        self._new_btn.setObjectName("primary")
        self._new_btn.setFixedHeight(30)
        self._new_btn.clicked.connect(self._on_new)
        lay.addWidget(self._new_btn)

        self._list = QListWidget()
        self._list.setFrameShape(QFrame.Shape.NoFrame)
        self._list.setSpacing(1)
        self._list.itemClicked.connect(self._on_select)
        lay.addWidget(self._list, 1)

    def set_splitter(self, splitter):
        self._splitter = splitter

    def _panel_width(self):
        if self._splitter:
            sizes = self._splitter.sizes()
            if sizes and sizes[0] > 0:
                return sizes[0]
        return self.WIDTH

    def show_overlay(self):
        p = self.parent()
        if not p:
            return
        w = self._panel_width()
        self.setGeometry(0, 0, w, p.height())
        self.show()
        self.raise_()
        self._open = True

    def hide_overlay(self):
        self.hide()
        self._open = False

    def toggle(self):
        if self._open:
            self.hide_overlay()
        else:
            self.show_overlay()

    def is_open(self):
        return self._open

    def set_new_callback(self, cb):
        self._new_cb = cb

    def set_select_callback(self, cb):
        self._select_cb = cb

    def _on_new(self):
        if self._new_cb:
            self._new_cb()

    def _on_select(self, item):
        if self._select_cb:
            self._select_cb(item.data(Qt.ItemDataRole.UserRole))
        self.hide_overlay()

    def update_conversations(self, convs: list):
        self._list.clear()
        for c in convs:
            name = c.get("name", "Sin título")
            updated = c.get("updated_at", "")[:16].replace("T", " ")
            item = QListWidgetItem(f"{name}\n{updated}")
            item.setData(Qt.ItemDataRole.UserRole, c["id"])
            self._list.addItem(item)

    def update_theme(self, theme):
        pass


class PdfTray(QFrame):
    """Left pane: compact PDF list with mini preview."""

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setObjectName("pdf_tray")
        self._theme = theme
        self._pdfs = []
        self._add_cb = None
        self._remove_cb = None
        self._pdf_dblclick_cb = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Section header
        header_row = QHBoxLayout()
        self._menu_btn = QPushButton("☰")
        self._menu_btn.setObjectName("icon_btn")
        self._menu_btn.setFixedSize(26, 26)
        self._menu_btn.setToolTip("Chats")
        self._menu_btn.setStyleSheet("font-size: 14px; font-weight: 700;")
        header_row.addWidget(self._menu_btn)
        header_row.addSpacing(4)
        lbl = QLabel("DOCUMENTOS")
        lbl.setObjectName("mono")
        header_row.addWidget(lbl)
        header_row.addStretch()
        self._add_btn = QPushButton("+ Añadir")
        self._add_btn.setObjectName("ghost")
        self._add_btn.setFixedHeight(22)
        self._add_btn.setStyleSheet(
            f"QPushButton {{ font-size: 11px; padding: 2px 7px; border-radius: 5px; }}"
        )
        self._add_btn.clicked.connect(self._on_add)
        header_row.addWidget(self._add_btn)

        self._del_btn = QPushButton("✕")
        self._del_btn.setObjectName("icon_btn")
        self._del_btn.setFixedSize(22, 22)
        self._del_btn.setToolTip("Eliminar PDF seleccionado")
        self._del_btn.setEnabled(False)
        self._del_btn.clicked.connect(self._on_delete)
        header_row.addWidget(self._del_btn)
        lay.addLayout(header_row)

        # PDF list
        self._list = QListWidget()
        self._list.setIconSize(QPixmap(20, 26).size())
        self._list.itemDoubleClicked.connect(self._on_double_click)
        lay.addWidget(self._list, 1)

        # Mini preview box
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {theme['border']};")
        lay.addWidget(sep)

        self._preview_title = QLabel("Vista previa")
        self._preview_title.setObjectName("mono")
        lay.addWidget(self._preview_title)

        self._preview_card = QFrame()
        self._preview_card.setObjectName("card")
        self._preview_card.setMinimumHeight(220)
        self._preview_card.hide()
        pc_lay = QVBoxLayout(self._preview_card)
        pc_lay.setContentsMargins(6, 6, 6, 6)
        pc_lay.setSpacing(5)

        self._prev_img = QLabel()
        self._prev_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._prev_img.setMinimumHeight(160)
        self._prev_img.setStyleSheet("border-radius: 4px; background: transparent;")
        pc_lay.addWidget(self._prev_img, 1)

        self._prev_name = QLabel()
        self._prev_name.setStyleSheet("font-size: 11px; font-weight: 600;")
        self._prev_name.setWordWrap(True)
        pc_lay.addWidget(self._prev_name)
        self._prev_meta = QLabel()
        self._prev_meta.setObjectName("mono")
        pc_lay.addWidget(self._prev_meta)
        lay.addWidget(self._preview_card, 1)

        self._list.currentItemChanged.connect(self._on_selection_changed)
        self._list.currentItemChanged.connect(
            lambda cur, _: self._del_btn.setEnabled(cur is not None)
        )

    def set_add_callback(self, cb):
        self._add_cb = cb

    def set_remove_callback(self, cb):
        self._remove_cb = cb

    def set_menu_callback(self, cb):
        self._menu_btn.clicked.connect(cb)

    def set_dblclick_callback(self, cb):
        self._pdf_dblclick_cb = cb

    def _on_add(self):
        if self._add_cb:
            self._add_cb()

    def _on_delete(self):
        idx = self._list.currentRow()
        if idx < 0 or idx >= len(self._pdfs):
            return
        path = self._pdfs[idx].get("path", "")
        if hasattr(self, "_remove_cb") and self._remove_cb:
            self._remove_cb(path)

    def _on_double_click(self, item):
        if self._pdf_dblclick_cb:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                self._pdf_dblclick_cb(path)

    def _on_selection_changed(self, current, previous):
        if not current:
            self._preview_card.hide()
            return
        idx = self._list.row(current)
        if 0 <= idx < len(self._pdfs):
            pdf = self._pdfs[idx]
            self._prev_name.setText(pdf.get("name", ""))
            pages = pdf.get("pages")
            size = pdf.get("size", "")
            meta_parts = []
            if pages:
                meta_parts.append(f"{pages} pág")
            if size:
                meta_parts.append(size)
            self._prev_meta.setText(" · ".join(meta_parts) if meta_parts else "")
            # Render first page thumbnail
            self._prev_img.clear()
            path = pdf.get("path", "")
            if path and PDF_PREVIEW_AVAILABLE:
                try:
                    doc = fitz.open(path)
                    page = doc.load_page(0)
                    avail_w = max(180, self.width() - 20)
                    scale = avail_w / page.rect.width
                    mat = fitz.Matrix(scale, scale)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    img = QImage(pix.samples, pix.width, pix.height,
                                 pix.stride, QImage.Format.Format_RGB888).copy()
                    doc.close()
                    pm = QPixmap.fromImage(img)
                    self._prev_img.setPixmap(pm)
                    self._prev_img.setFixedHeight(min(pm.height(), 300))
                except Exception:
                    self._prev_img.setText("Vista previa no disponible")
            self._preview_card.show()

    def update_pdfs(self, pdfs):
        self._pdfs = pdfs
        self._list.clear()
        icon = build_pdf_icon()
        for pdf in pdfs:
            item = QListWidgetItem(icon, pdf.get("name", ""))
            item.setData(Qt.ItemDataRole.UserRole, pdf.get("path", ""))
            self._list.addItem(item)
        if pdfs:
            self._list.setCurrentRow(0)

    def update_theme(self, theme):
        self._theme = theme


# ── PDF viewer dialog (unchanged from original, restyled) ─────────────────────

class PDFWindow(QDialog):
    def __init__(self, is_dark_mode=False):
        super().__init__()
        self.setWindowTitle("Documentos anexos")
        self.setMinimumSize(700, 500)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.is_dark_mode = is_dark_mode
        self.setStyleSheet(get_stylesheet(DARK_THEME if is_dark_mode else LIGHT_THEME))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(15)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(220)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

        self.preview_stack = QStackedWidget()
        self.preview_placeholder = QLabel("Selecciona un PDF para vista previa.")
        self.preview_placeholder.setObjectName("hint")
        self.preview_placeholder.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.preview_stack.addWidget(self.preview_placeholder)

        self.preview_container = QFrame()
        self.preview_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        pcc = QVBoxLayout(self.preview_container)
        pcc.setContentsMargins(0, 0, 0, 0)
        pcc.setSpacing(0)

        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.preview_image.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.preview_scroll.setWidget(self.preview_image)

        overlay = QHBoxLayout()
        overlay.setContentsMargins(12, 12, 12, 0)
        self.overlay_label = QLabel("")
        self.overlay_label.setStyleSheet(
            "background: rgba(0,0,0,0.38); padding: 5px 10px; border-radius: 7px; color: white; font-size: 12px;"
        )
        overlay.addStretch()
        overlay.addWidget(self.overlay_label)

        pcc.addLayout(overlay)
        pcc.addWidget(self.preview_scroll)

        if PDF_PREVIEW_AVAILABLE:
            self.preview_stack.addWidget(self.preview_container)

        self.splitter.addWidget(self.list_widget)
        self.splitter.addWidget(self.preview_stack)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([240, 900])
        lay.addWidget(self.splitter)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton("◀")
        self.next_btn = QPushButton("▶")
        self.page_lbl = QLabel("— / —")
        self.page_lbl.setObjectName("mono")
        self.zoom_out_btn = QPushButton("–")
        self.zoom_in_btn = QPushButton("+")
        self.zoom_lbl = QLabel("100%")
        self.zoom_lbl.setObjectName("mono")
        for b in (self.prev_btn, self.next_btn, self.zoom_out_btn, self.zoom_in_btn):
            b.setFixedWidth(40)
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.page_lbl)
        nav.addWidget(self.next_btn)
        nav.addSpacing(12)
        nav.addWidget(self.zoom_out_btn)
        nav.addWidget(self.zoom_lbl)
        nav.addWidget(self.zoom_in_btn)
        nav.addStretch()
        lay.addLayout(nav)

        btns = QHBoxLayout()
        self.add_btn = QPushButton("Añadir PDFs")
        self.add_btn.setObjectName("primary")
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(self.add_btn)
        btns.addWidget(self.close_btn)
        lay.addLayout(btns)

        self.current_pdf_path = None
        self.current_page = 0
        self.current_page_count = 0
        self.zoom_factor = 1.0
        self.current_file_name = None

        self.prev_btn.clicked.connect(lambda: self.change_page(-1))
        self.next_btn.clicked.connect(lambda: self.change_page(1))
        self.zoom_out_btn.clicked.connect(lambda: self.change_zoom(-0.1))
        self.zoom_in_btn.clicked.connect(lambda: self.change_zoom(0.1))

    def update_theme(self, is_dark):
        self.is_dark_mode = is_dark
        self.setStyleSheet(get_stylesheet(DARK_THEME if is_dark else LIGHT_THEME))

    def update_data(self, pdfs):
        self.list_widget.clear()
        if not pdfs:
            item = QListWidgetItem("No hay PDFs aún.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            self.preview_placeholder.setText("Añade PDFs para comenzar.")
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            return
        icon = build_pdf_icon()
        for pdf in pdfs:
            item = QListWidgetItem(icon, pdf.get("name", ""))
            item.setData(Qt.ItemDataRole.UserRole, pdf.get("path", ""))
            self.list_widget.addItem(item)
        self.list_widget.setCurrentRow(0)
        self.on_selection_changed()

    def on_selection_changed(self):
        sel = self.list_widget.selectedItems()
        if not sel:
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            return
        path = sel[0].data(Qt.ItemDataRole.UserRole)
        if not path or not PDF_PREVIEW_AVAILABLE:
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            return
        try:
            doc = fitz.open(path)
            count = doc.page_count
            doc.close()
            if count == 0:
                raise ValueError
        except Exception:
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            return
        self.current_pdf_path = path
        self.current_page_count = count
        self.current_page = 0
        self.current_file_name = path.replace("\\", "/").split("/")[-1]
        self.zoom_factor = 1.0
        self.render_page(0)

    def render_page(self, idx):
        if not self.current_pdf_path:
            return
        try:
            doc = fitz.open(self.current_pdf_path)
            page = doc.load_page(idx)
            target_w = 1100
            scale = min(2.5, max(1.0, target_w / page.rect.width)) * self.zoom_factor
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888).copy()
            doc.close()
        except Exception:
            self.preview_stack.setCurrentWidget(self.preview_placeholder)
            return
        self.preview_image.setPixmap(QPixmap.fromImage(img))
        self.preview_image.adjustSize()
        self.preview_scroll.verticalScrollBar().setValue(0)
        self.page_lbl.setText(f"  {idx + 1} / {self.current_page_count}  ")
        self.zoom_lbl.setText(f"{int(self.zoom_factor * 100)}%")
        self.overlay_label.setText(f"{self.current_file_name}  ·  {idx + 1}/{self.current_page_count}")
        self.preview_stack.setCurrentWidget(self.preview_container)

    def change_page(self, delta):
        if self.current_pdf_path is None:
            return
        new = self.current_page + delta
        if 0 <= new < self.current_page_count:
            self.current_page = new
            self.render_page(new)

    def change_zoom(self, delta):
        if self.current_pdf_path is None:
            return
        self.zoom_factor = round(min(3.0, max(0.5, self.zoom_factor + delta)), 1)
        self.render_page(self.current_page)


# ── Content area with drawer overlay ─────────────────────────────────────────

class ContentArea(QWidget):
    """Body area that hosts the 3-pane splitter + overlay drawers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._splitter = None
        self._backdrop = None
        self._drawers = []
        self._conv_overlay = None

    def setup(self, splitter, backdrop, drawers, conv_overlay=None):
        self._splitter = splitter
        self._backdrop = backdrop
        self._drawers = drawers
        self._conv_overlay = conv_overlay
        splitter.setParent(self)
        backdrop.setParent(self)
        for d in drawers:
            d.setParent(self)
            d.set_backdrop(backdrop)
        if conv_overlay:
            conv_overlay.setParent(self)
            conv_overlay.hide()
        splitter.show()
        backdrop.hide()
        for d in drawers:
            d.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._splitter:
            self._splitter.setGeometry(self.rect())
        if self._backdrop:
            self._backdrop.setGeometry(self.rect())
        for d in self._drawers:
            if d.is_open():
                w = d.WIDTH
                d.setGeometry(self.width() - w, 0, w, self.height())
        if self._conv_overlay and self._conv_overlay.is_open():
            w = self._conv_overlay._panel_width()
            self._conv_overlay.setGeometry(0, 0, w, self.height())


# ── Chat bubble ──────────────────────────────────────────────────────────────

def _md_to_html(text: str) -> str:
    """Convert basic markdown to HTML for display in QLabel."""
    import re
    # Escape HTML special chars first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Bullet lists: lines starting with "- " or "• "
    lines = text.split("\n")
    result, in_list = [], False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("- ") or stripped.startswith("• "):
            if not in_list:
                result.append("<ul style='margin:4px 0; padding-left:18px;'>")
                in_list = True
            result.append(f"<li>{stripped[2:]}</li>")
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(line)
    if in_list:
        result.append("</ul>")
    text = "\n".join(result)
    # Paragraphs: double newline → paragraph break
    text = re.sub(r"\n{2,}", "<br><br>", text)
    # Single newline → line break
    text = text.replace("\n", "<br>")
    return text


class ChatBubble(QFrame):
    def __init__(self, role: str, content: str, theme: dict = None, timestamp: str = None, parent=None):
        super().__init__(parent)
        self._role = role
        self._raw_content = content
        self.setObjectName("chat_bubble_outer")
        self.setStyleSheet(
            "QFrame#chat_bubble_outer { background: transparent; border: none; }"
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 4)
        outer.setSpacing(4)

        # Header row: role label + timestamp + copy button
        header = QHBoxLayout()
        header.setSpacing(6)
        role_lbl = QLabel("Tú" if role == "user" else "Asistente")
        role_lbl.setObjectName("mono")
        role_lbl.setStyleSheet(
            "font-size: 10.5px; font-weight: 600; background: transparent; border: none;"
        )
        header.addWidget(role_lbl)

        from datetime import datetime as _dt
        ts_text = timestamp if timestamp is not None else _dt.now().strftime("%H:%M")
        ts = QLabel(ts_text)
        ts.setObjectName("mono")
        ts.setStyleSheet("font-size: 9.5px; background: transparent; border: none;")
        header.addWidget(ts)
        header.addStretch()

        self._copy_btn = QPushButton("Copiar")
        self._copy_btn.setObjectName("ghost")
        self._copy_btn.setFixedHeight(18)
        self._copy_btn.setStyleSheet("font-size: 10px; padding: 0 6px; border-radius: 4px;")
        self._copy_btn.clicked.connect(self._copy_text)
        header.addWidget(self._copy_btn)
        outer.addLayout(header)

        inner = QFrame()
        inner.setObjectName("chat_user_bg" if role == "user" else "chat_assistant_bg")
        il = QVBoxLayout(inner)
        il.setContentsMargins(12, 10, 12, 10)

        self._content_lbl = QLabel()
        self._content_lbl.setWordWrap(True)
        self._content_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._content_lbl.setStyleSheet(
            "font-size: 13px; line-height: 1.6; background: transparent; border: none;"
        )
        self._content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._content_lbl.setOpenExternalLinks(False)
        self.set_content(content)
        il.addWidget(self._content_lbl)
        outer.addWidget(inner)

    def set_content(self, text: str):
        self._raw_content = text
        self._content_lbl.setText(_md_to_html(text))

    def _copy_text(self):
        QGuiApplication.clipboard().setText(self._raw_content)


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagnóstico legal · ISSBC")
        self.setMinimumSize(1000, 640)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.is_dark_mode = False
        self._pdf_add_callback = None
        self._pw = None
        self._running = False
        self._chat_send_cb = None
        self.setWindowIcon(build_app_icon())

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # ── Command bar ──────────────────────────────────────────
        self._cmd_bar = QFrame()
        self._cmd_bar.setObjectName("command_bar")
        self._cmd_bar.setFixedHeight(56)
        cmd_lay = QHBoxLayout(self._cmd_bar)
        cmd_lay.setContentsMargins(16, 0, 16, 0)
        cmd_lay.setSpacing(10)

        # Title + date stacked vertically on the left
        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_col.setContentsMargins(0, 0, 0, 0)
        title_lbl = QLabel("Diagnóstico legal")
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 700;")
        title_col.addWidget(title_lbl)
        today = _date.today()
        months = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
        date_str = f"{today.day} {months[today.month - 1]} {today.year}"
        self._case_id_lbl = QLabel(date_str)
        self._case_id_lbl.setObjectName("mono")
        title_col.addWidget(self._case_id_lbl)
        cmd_lay.addLayout(title_col)

        cmd_lay.addSpacing(12)

        # Search bar
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Buscar en el chat…  Ctrl+K")
        self._search_bar.setFixedHeight(32)
        self._search_bar.setMaximumWidth(360)
        cmd_lay.addWidget(self._search_bar, 1)
        cmd_lay.addSpacing(8)

        self._theme_btn = QPushButton("◑")
        self._theme_btn.setObjectName("ghost")
        self._theme_btn.setFixedSize(32, 32)
        self._theme_btn.setStyleSheet(
            "QPushButton { font-size: 16px; border: none; background: transparent; }"
            "QPushButton:hover { background: rgba(128,128,128,0.12); border-radius: 6px; }"
        )
        self._theme_btn.setToolTip("Alternar tema claro / oscuro")
        self._theme_btn.clicked.connect(self.toggle_theme)
        cmd_lay.addWidget(self._theme_btn)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFixedHeight(22)
        divider.setStyleSheet("color: #e4e7eb;")
        cmd_lay.addWidget(divider)

        self._diag_btn = QPushButton("▶  Analizar")
        self._diag_btn.setObjectName("primary")
        self._diag_btn.setFixedSize(110, 34)
        self._diag_btn.setToolTip("Analizar caso  (Ctrl+Enter)")
        cmd_lay.addWidget(self._diag_btn)

        root_lay.addWidget(self._cmd_bar)

        # ── Body (content area with 3-pane splitter + drawers) ──
        self._content_area = ContentArea()
        root_lay.addWidget(self._content_area, 1)

        # 3-pane splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)

        # Left pane: PDF tray
        self._pdf_tray = PdfTray(LIGHT_THEME)
        self._pdf_tray.setObjectName("pdf_tray")
        self._pdf_tray.setMinimumWidth(180)
        self._pdf_tray.setMaximumWidth(320)
        self._pdf_tray.set_dblclick_callback(self._open_pdf_detail)
        splitter.addWidget(self._pdf_tray)

        # Center pane: compact editor + chat + input
        center_widget = QWidget()
        center_lay = QVBoxLayout(center_widget)
        center_lay.setContentsMargins(0, 0, 0, 0)
        center_lay.setSpacing(0)

        # Compact editor section
        editor_section = QWidget()
        es_lay = QVBoxLayout(editor_section)
        es_lay.setContentsMargins(14, 10, 14, 8)
        es_lay.setSpacing(6)

        editor_header = QHBoxLayout()
        editor_header.setSpacing(8)
        editor_title = QLabel("Resumen del caso")
        editor_title.setObjectName("section")
        editor_header.addWidget(editor_title)
        kbd_hint = QLabel("  Ctrl+Enter para analizar")
        kbd_hint.setObjectName("mono")
        editor_header.addWidget(kbd_hint)
        editor_header.addStretch()
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        self._clear_btn = QPushButton("Limpiar")
        self._clear_btn.setObjectName("ghost")
        self._clear_btn.setFixedHeight(28)
        self._paste_btn = QPushButton("Pegar")
        self._paste_btn.setObjectName("ghost")
        self._paste_btn.setFixedHeight(28)
        toolbar.addWidget(self._clear_btn)
        toolbar.addWidget(self._paste_btn)
        editor_header.addLayout(toolbar)
        es_lay.addLayout(editor_header)

        self._editor = QTextEdit()
        self._editor.setFixedHeight(82)
        self._editor.setPlaceholderText(
            "Ej. El cliente firmó un contrato de arrendamiento en 2020 y…"
        )
        self._editor.textChanged.connect(self._update_status)
        es_lay.addWidget(self._editor)

        self._counter_lbl = QLabel("0 palabras · 0 caracteres")
        self._counter_lbl.setObjectName("mono")
        self._counter_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        es_lay.addWidget(self._counter_lbl)
        center_lay.addWidget(editor_section)

        self._editor_sep = QWidget()
        self._editor_sep.setFixedHeight(1)
        self._editor_sep.setStyleSheet(f"background-color: {LIGHT_THEME['border']};")
        center_lay.addWidget(self._editor_sep)

        # Chat messages area
        self._chat_scroll = QScrollArea()
        self._chat_scroll.setWidgetResizable(True)
        self._chat_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._chat_container = QWidget()
        self._chat_lay = QVBoxLayout(self._chat_container)
        self._chat_lay.setContentsMargins(12, 12, 12, 8)
        self._chat_lay.setSpacing(10)
        self._chat_lay.addStretch()
        self._chat_scroll.setWidget(self._chat_container)
        center_lay.addWidget(self._chat_scroll, 1)

        # Processing status bar
        self._timeline = ProcessingWidget(LIGHT_THEME)
        center_lay.addWidget(self._timeline)

        # Chat input row
        input_frame = QFrame()
        input_frame.setObjectName("card")
        input_frame.setStyleSheet(
            "QFrame#card { border-radius: 0; border-left: none;"
            " border-right: none; border-bottom: none; }"
        )
        ifl = QHBoxLayout(input_frame)
        ifl.setContentsMargins(12, 8, 12, 12)
        ifl.setSpacing(8)
        self._chat_input = QLineEdit()
        self._chat_input.setPlaceholderText(
            "Escribe un mensaje o pregunta sobre el caso…"
        )
        self._chat_input.setFixedHeight(34)
        self._chat_input.returnPressed.connect(self._on_chat_send_internal)
        self._send_btn = QPushButton("Enviar")
        self._send_btn.setObjectName("soft")
        self._send_btn.setFixedHeight(34)
        self._send_btn.setFixedWidth(70)
        self._send_btn.clicked.connect(self._on_chat_send_internal)
        ifl.addWidget(self._chat_input)
        ifl.addWidget(self._send_btn)
        center_lay.addWidget(input_frame)

        splitter.addWidget(center_widget)

        # Right pane: results
        self._results = ResultsPane(LIGHT_THEME)
        self._results.setObjectName("results_pane")
        self._results.setMinimumWidth(300)
        self._results.setMaximumWidth(560)
        splitter.addWidget(self._results)
        self._results.hide()   # hidden until first analysis

        self._splitter = splitter
        splitter.setSizes([220, 9999, 0])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        # Drawers
        self._just_drawer = DrawerPanel("Justificación del diagnóstico", "Razonamiento, citas y normativa")

        # Conversation overlay
        self._conv_overlay = ConversationOverlay(LIGHT_THEME)

        backdrop = BackdropWidget()
        backdrop.set_close_callback(self._close_all_overlays)

        self._content_area.setup(splitter, backdrop, [self._just_drawer], self._conv_overlay)
        self._pdf_tray.set_menu_callback(self._toggle_conv_overlay)
        self._conv_overlay.set_splitter(splitter)
        self._results.set_on_justify(self._open_just_drawer)
        self._search_bar.textChanged.connect(self._on_search_changed)

        # Status bar
        self._status = self.statusBar()
        self._status.showMessage("● Listo · Modo Local · 0 palabras · 0 documentos")

        # Micro-UX
        self._clear_btn.clicked.connect(self._editor.clear)
        self._paste_btn.clicked.connect(self._paste_text)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self._diag_btn.click)
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self._search_bar.setFocus)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._close_open_drawer)

        self.apply_theme()

        # Welcome chat message
        self.add_chat_message(
            "assistant",
            "Hola, soy tu asistente de análisis legal. Describe el caso en el "
            "editor o escríbeme directamente aquí. Cuando estés listo, pulsa "
            "▶ Analizar o hazme una pregunta."
        )

    # ── Theme ─────────────────────────────────────────────────

    def apply_theme(self):
        theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        self.setStyleSheet(get_stylesheet(theme))
        self._theme_btn.setText("○" if self.is_dark_mode else "◑")
        if self.is_dark_mode:
            self._cmd_bar.setStyleSheet(
                f"QFrame#command_bar {{ background-color: {DARK_THEME['canvas']};"
                f" border-bottom: 1px solid {DARK_THEME['border']}; }}"
            )
        else:
            self._cmd_bar.setStyleSheet("")
        self._editor_sep.setStyleSheet(f"background-color: {theme['border']};")
        self._results.update_theme(theme)
        self._timeline.update_theme(theme)
        self._pdf_tray.update_theme(theme)
        if self._pw:
            self._pw.update_theme(self.is_dark_mode)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    # ── Drawer helpers ─────────────────────────────────────────

    def _open_just_drawer(self):
        self._just_drawer.open_drawer()

    def _toggle_conv_overlay(self):
        self._conv_overlay.toggle()

    def _close_all_overlays(self):
        if self._just_drawer.is_open():
            self._just_drawer.close_drawer()
        if self._conv_overlay.is_open():
            self._conv_overlay.hide_overlay()

    def _close_open_drawer(self):
        if self._just_drawer.is_open():
            self._just_drawer.close_drawer()
        elif self._conv_overlay.is_open():
            self._conv_overlay.hide_overlay()

    # ── Editor helpers ─────────────────────────────────────────

    def _paste_text(self):
        clip = QGuiApplication.clipboard()
        if clip:
            self._editor.insertPlainText(clip.text())

    def _update_status(self):
        text = self._editor.toPlainText()
        words = len([w for w in text.split() if w.strip()])
        chars = len(text)
        self._counter_lbl.setText(f"{words} palabras · {chars} caracteres")
        n_pdfs = len(self._pdf_tray._pdfs)
        if self._running:
            status = f"● Ejecutando…  ·  Modo Local  ·  {words} palabras  ·  {n_pdfs} documentos"
        else:
            status = f"● Listo  ·  Modo Local  ·  {words} palabras  ·  {n_pdfs} documentos"
        self._status.showMessage(status)

    def _update_status_running(self, is_running):
        self._running = is_running
        self._diag_btn.setEnabled(not is_running)
        self._send_btn.setEnabled(not is_running)
        self._chat_input.setEnabled(not is_running)
        self._diag_btn.setEnabled(not is_running)
        self._update_status()

    # ── PDF detail viewer ──────────────────────────────────────

    def _open_pdf_detail(self, path):
        if not self._pw:
            self._pw = PDFWindow(self.is_dark_mode)
            if self._pdf_add_callback:
                self._pw.add_btn.clicked.connect(self._pdf_add_callback)
        self._pw.update_data(self._pdf_tray._pdfs)
        self._pw.show()
        self._pw.raise_()
        self._pw.activateWindow()

    # ── Controller interface (public API) ──────────────────────

    def on_diagnose_clicked(self, callback):
        def _wrapped():
            self._update_status_running(True)
            self.add_chat_message("assistant", "Analizando el caso… (puede tardar unos segundos)")
            self._timeline.start_animation(on_done=callback)
        self._diag_btn.clicked.connect(_wrapped)

    def set_running(self, is_running: bool):
        self._update_status_running(is_running)
        if not is_running:
            self._timeline.set_done()

    def show_status_error(self, message: str):
        self._status.showMessage(f"⚠ {message}")

    def on_chat_send(self, callback):
        self._chat_send_cb = callback

    def add_chat_message(self, role: str, content: str, timestamp: str = None) -> "ChatBubble":
        theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        bubble = ChatBubble(role, content, theme, timestamp=timestamp)
        count = self._chat_lay.count()
        self._chat_lay.insertWidget(count - 1, bubble)
        self._scroll_chat_bottom()
        return bubble

    def _scroll_chat_bottom(self):
        QTimer.singleShot(40, lambda: self._chat_scroll.verticalScrollBar().setValue(
            self._chat_scroll.verticalScrollBar().maximum()
        ))

    def show_typing_indicator(self) -> "ChatBubble":
        return self.add_chat_message("assistant", "…")

    def remove_bubble(self, bubble: "ChatBubble"):
        self._chat_lay.removeWidget(bubble)
        bubble.deleteLater()

    def add_regenerate_button(self, callback):
        btn = QPushButton("↺  Regenerar análisis")
        btn.setObjectName("ghost")
        btn.setFixedHeight(26)
        btn.setStyleSheet("font-size: 11px; margin-left: 4px;")
        count = self._chat_lay.count()
        self._chat_lay.insertWidget(count - 1, btn)
        btn.clicked.connect(lambda: (callback(), btn.deleteLater()))
        self._scroll_chat_bottom()

    def _on_chat_send_internal(self):
        text = self._chat_input.text().strip()
        if not text or not self._chat_send_cb:
            return
        self._chat_input.clear()
        self._chat_send_cb(text)

    def on_justify_clicked(self, callback):
        self._on_justify_cb = callback

    def on_pdf_clicked(self, callback):
        # Gestionar PDFs: in V3 the tray is always visible; wire to opening the detail viewer
        pass  # no dedicated button; double-click in tray opens the viewer

    def on_new_chat(self, callback):
        from PyQt6.QtWidgets import QInputDialog
        def _ask_name():
            name, ok = QInputDialog.getText(
                self, "Nuevo chat", "Nombre del caso:",
                text="Caso sin título"
            )
            if ok:
                callback(name.strip() or "Caso sin título")
                self._conv_overlay.hide_overlay()
        self._conv_overlay.set_new_callback(_ask_name)

    def on_conv_selected(self, callback):
        self._conv_overlay.set_select_callback(callback)

    def show_conversations(self, convs: list):
        self._conv_overlay.update_conversations(convs)

    def reveal_results_pane(self):
        if not self._results.isVisible():
            self._results.show()
            self._splitter.setSizes([220, 9999, 440])

    def clear_chat(self):
        lay = self._chat_lay
        for i in reversed(range(lay.count())):
            item = lay.itemAt(i)
            if not item:
                continue
            w = item.widget()
            if w:
                lay.removeWidget(w)
                w.hide()
                w.deleteLater()
            else:
                lay.removeItem(item)  # remove spacer/stretch items too
        lay.addStretch()
        self._chat_scroll.verticalScrollBar().setValue(0)

    def clear_results(self):
        self._results.update_hypotheses([])
        self._results.update_diagnosis({"diagnosis": "Sin análisis aún", "severity": "medium"})

    def on_export_clicked(self, callback):
        self._results.set_on_export(callback)

    def _on_search_changed(self, query: str):
        query = query.strip().lower()
        lay = self._chat_lay
        for i in range(lay.count()):
            item = lay.itemAt(i)
            if not item:
                continue
            w = item.widget()
            if not isinstance(w, ChatBubble):
                continue
            if not query:
                w.setVisible(True)
                w.setGraphicsEffect(None)
                continue
            labels = w.findChildren(QLabel)
            text = " ".join(lbl.text().lower() for lbl in labels)
            match = query in text
            w.setVisible(True)
            opacity = 1.0 if match else 0.25
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            effect = QGraphicsOpacityEffect(w)
            effect.setOpacity(opacity)
            w.setGraphicsEffect(effect)

    def on_pdf_add_clicked(self, callback):
        self._pdf_add_callback = callback
        self._pdf_tray.set_add_callback(callback)
        if self._pw:
            try:
                self._pw.add_btn.clicked.disconnect()
            except Exception:
                pass
            self._pw.add_btn.clicked.connect(callback)

    def on_pdf_remove_clicked(self, callback):
        self._pdf_tray.set_remove_callback(callback)

    def get_symptoms(self):
        return [line for line in self._editor.toPlainText().split("\n") if line.strip()]

    def set_editor_text(self, text: str):
        self._editor.setPlainText(text)

    def show_hypotheses(self, hypotheses):
        self._results.update_hypotheses(hypotheses)

    def show_diagnosis(self, diagnosis):
        if isinstance(diagnosis, str):
            data = {"diagnosis": diagnosis, "severity": "high"}
        else:
            data = diagnosis
        self._results.update_diagnosis(data)
        self.reveal_results_pane()

    def set_pdf_count(self, n: int):
        self._results.set_pdf_count(n)

    def show_justification(self, justification):
        theme = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        if isinstance(justification, list):
            for item in justification:
                self._add_just_block(lay, item, theme)
        else:
            lbl = QLabel(str(justification))
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"font-size: 13px; color: {theme['text']}; line-height: 1.6;")
            lay.addWidget(lbl)
        lay.addStretch()
        self._just_drawer.set_content(content)
        close_btn = QPushButton("Cerrar")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self._just_drawer.close_drawer)
        self._just_drawer.set_footer_widget(close_btn)
        self._just_drawer.open_drawer()

    def _add_just_block(self, lay, item, theme):
        block = QFrame()
        block_lay = QVBoxLayout(block)
        block_lay.setContentsMargins(0, 0, 0, 0)
        block_lay.setSpacing(6)
        block.setStyleSheet(
            f"QFrame {{ border-left: 2px solid {theme['border']}; padding-left: 14px; }}"
        )
        heading = QLabel(item.get("heading", ""))
        heading.setStyleSheet(
            f"font-size: 11px; font-weight: 600; letter-spacing: 0.4px;"
            f" text-transform: uppercase; color: {theme['text_subtle']};"
            f" font-family: 'JetBrains Mono', 'Consolas', monospace;"
        )
        block_lay.addWidget(heading)
        body = QLabel(item.get("body", ""))
        body.setWordWrap(True)
        body.setStyleSheet(f"font-size: 13px; color: {theme['text']}; line-height: 1.6;")
        block_lay.addWidget(body)
        if item.get("cite"):
            ci = item["cite"]
            cite_lbl = QLabel(f"⬜ {ci.get('label', '')}  ·  p. {ci.get('page', '')}")
            cite_lbl.setStyleSheet(
                f"font-size: 11px; color: {theme['accent_text']};"
                f" background-color: {theme['accent_soft']};"
                f" border-radius: 5px; padding: 3px 7px;"
                f" font-family: 'JetBrains Mono', 'Consolas', monospace;"
            )
            block_lay.addWidget(cite_lbl)
        lay.addWidget(block)

    def show_pdf_window(self, pdfs):
        self._pdf_tray.update_pdfs(pdfs)
        self._update_status()
