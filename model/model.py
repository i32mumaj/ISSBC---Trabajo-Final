class Model:
    def __init__(self):
        self.symptoms = []
        self.observables = {}

        self.hypotheses = []
        self.diagnosis = ""
        self.justification = ""

        self.pdfs = []
        self.web_sources = []

        self.mode = "LOCAL"