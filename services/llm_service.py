class LLMService:

    def get_hypotheses(self, data):
        return [
            {
                "name": "Cláusula abusiva",
                "score": 0.92,
                "severity": "high",
                "detail": "Renuncia anticipada a derechos de prórroga e indemnización por mejoras (cláusula 7.ª).",
            },
            {
                "name": "Condiciones ambiguas",
                "score": 0.68,
                "severity": "medium",
                "detail": "Modificación unilateral de penalizaciones sin notificación previa (anexo I).",
            },
            {
                "name": "Riesgo legal oculto",
                "score": 0.78,
                "severity": "high",
                "detail": "Indemnización desproporcionada incompatible con art. 82.4 TRLGDCU (STS 564/2023).",
            },
            {
                "name": "Incumplimiento de forma",
                "score": 0.34,
                "severity": "low",
                "detail": "Comunicaciones de modificación realizadas por correo electrónico no fehaciente.",
            },
        ]

    def get_diagnosis(self, model):
        return {
            "diagnosis": "Contrato con riesgo legal ALTO",
            "severity": "high",
            "summary": (
                "Se han detectado tres cláusulas potencialmente abusivas y una ambigüedad "
                "en la modificación unilateral de condiciones económicas. La línea "
                "jurisprudencial reciente (STS 564/2023) refuerza la nulidad de los pactos identificados."
            ),
            "justification": [
                {
                    "heading": "Hechos relevantes",
                    "body": (
                        "Contrato de arrendamiento modificado mediante anexo unilateral en 2024, "
                        "con incremento del 12% sobre la mensualidad y endurecimiento de penalizaciones."
                    ),
                },
                {
                    "heading": "Cláusulas analizadas",
                    "body": (
                        "La cláusula séptima contiene una renuncia anticipada a derechos del "
                        "arrendatario que la jurisprudencia consolidada considera nula de pleno derecho."
                    ),
                    "cite": {"label": "Contrato_arrendamiento_2020.pdf", "page": 7},
                },
                {
                    "heading": "Marco normativo",
                    "body": (
                        "Art. 82.4 TRLGDCU (RDL 1/2007) sobre cláusulas abusivas. "
                        "Art. 1256 CC sobre validez de los contratos."
                    ),
                    "cite": {"label": "Sentencia_TS_2023_564.pdf", "page": 14},
                },
                {
                    "heading": "Conclusión",
                    "body": (
                        "Se recomienda impugnar las cláusulas 7.ª y 12.3 mediante demanda "
                        "declarativa de nulidad parcial, manteniendo la vigencia del resto del contrato."
                    ),
                },
            ],
            "citations": [
                {"id": "pdf-1", "label": "Contrato_arrendamiento_2020.pdf", "page": 7},
                {"id": "pdf-2", "label": "Anexo_clausulas_modificadas.pdf", "page": 2},
                {"id": "pdf-3", "label": "Sentencia_TS_2023_564.pdf", "page": 14},
            ],
        }
