from services.llm_service import LLMService
from services.pdf_service import PDFService
from PyQt6.QtWidgets import QFileDialog


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.llm = LLMService()
        self.pdf_service = PDFService()

        self.connect()

    def connect(self):
        self.view.on_evaluate_clicked(self.evaluate)
        self.view.on_diagnose_clicked(self.diagnose)
        self.view.on_justify_clicked(self.show_justification)
        self.view.on_pdf_clicked(self.open_pdf_manager)
        self.view.on_pdf_add_clicked(self.manage_pdfs)

    def evaluate(self):
        self.model.symptoms = self.view.get_symptoms()

        data = {
            "symptoms": self.model.symptoms,
            "mode": self.model.mode
        }

        self.model.hypotheses = self.llm.get_hypotheses(data)
        self.view.show_hypotheses(self.model.hypotheses)

    def diagnose(self):
        result = self.llm.get_diagnosis(self.model)

        self.model.diagnosis = result["diagnosis"]
        self.model.justification = result["justification"]

        self.view.show_diagnosis(self.model.diagnosis)

    def show_justification(self):
        self.view.show_justification(self.model.justification)

    def manage_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self.view,
            "Seleccionar PDFs",
            "",
            "PDF Files (*.pdf)"
        )

        if files:
            self.model.pdfs.extend(self.pdf_service.add_pdfs(files))
            self.view.show_pdf_window(self.model.pdfs)

    def open_pdf_manager(self):
        self.view.show_pdf_window(self.model.pdfs)
