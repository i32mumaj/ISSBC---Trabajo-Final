class LLMService:

    def get_hypotheses(self, data):
        return [
            {"name": "Cláusula abusiva", "score": 0.9},
            {"name": "Condiciones ambiguas", "score": 0.6},
            {"name": "Riesgo legal oculto", "score": 0.75}
        ]

    def get_diagnosis(self, model):
        return {
            "diagnosis": "Contrato con ALTO riesgo legal",
            "justification": (
                "Se han detectado múltiples cláusulas potencialmente abusivas. "
                "El contrato presenta ambigüedades que pueden perjudicar al firmante."
            )
        }