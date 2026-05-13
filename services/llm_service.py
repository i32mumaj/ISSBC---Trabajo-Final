import json
import re

import ollama

from services.settings_service import load_settings

MODEL = "qwen2.5:7b"


def _current_model() -> str:
    return load_settings().get("ollama_model", MODEL)


def _extra_prompt() -> str:
    return load_settings().get("extra_prompt", "").strip()

_HYPO_SYSTEM = """\
You are a Spanish legal assistant. ALWAYS respond in Spanish. Never use Chinese or any other language.
Analyze the case summary and return ONLY a valid JSON array, no extra text, no markdown code blocks.

Exact format (nothing else):
[{"name":"nombre breve","score":0.9,"severity":"high","detail":"explicación concisa en español"}]

Rules:
- All text fields MUST be in Spanish
- score: decimal number between 0.0 and 1.0
- severity: exactly "high", "medium" or "low"
- Between 2 and 5 hypotheses, ordered by score descending
- Reply ONLY with the JSON array"""

_HYPO_DETAIL = [
    # Rápido
    "\nDetail level: CONCISE. Return exactly 2 hypotheses. Keep each 'detail' field under 20 words.",
    # Estándar (default — no extra instruction)
    "",
    # Exhaustivo
    "\nDetail level: EXHAUSTIVE. Return 4 to 5 hypotheses. Each 'detail' field must be 2-3 sentences with specific legal grounds.",
]

_DIAG_SYSTEM = """\
You are a Spanish legal assistant. ALWAYS respond in Spanish. Never use Chinese or any other language.
Analyze the case and return ONLY a valid JSON object, no extra text, no markdown code blocks.

Exact format (nothing else):
{"diagnosis":"título breve en español","severity":"high","summary":"resumen en 2-3 frases en español","justification":[{"heading":"Hechos relevantes","body":"..."},{"heading":"Marco normativo","body":"..."},{"heading":"Conclusión","body":"..."}],"citations":[{"doc":"nombre del archivo","page":1,"note":"referencia breve sin comillas"}],"legal_refs":[{"ref":"Art. 50 ET","law":"Estatuto de los Trabajadores"}]}

Rules:
- ALL text fields MUST be in Spanish
- severity: exactly "high", "medium" or "low"
- justification: 3 to 5 sections with heading and body
- citations: for EACH document referenced, include its filename, the page number, and a short note (max 80 chars, NO quotes inside). Empty array only if no documents were provided.
- legal_refs: 2 to 4 specific legal references (articles, laws, royal decrees) directly applicable to the case. Each "ref" is short (e.g. "Art. 50.1 ET"), "law" is the full law name in Spanish. Never invent references.
- Reply ONLY with the JSON object"""

_DIAG_DETAIL = [
    # Rápido
    "\nDetail level: CONCISE. Keep summary to 1-2 sentences. Provide exactly 3 justification sections with brief bodies (1-2 sentences each).",
    # Estándar (default — no extra instruction)
    "",
    # Exhaustivo
    "\nDetail level: EXHAUSTIVE. Provide 4-5 justification sections. Each body must be detailed (3-5 sentences) with specific article references, case law, or statutory grounds where applicable. Summary should be 3-4 sentences.",
]

_CHAT_SYSTEM = """\
You are a Spanish legal assistant. ALWAYS respond in Spanish. Never use Chinese or any other language.
Help the user understand and analyze their legal case.
Be clear, concise and helpful. Use the case summary and any attached documents as context."""

_TITLE_SYSTEM = """\
Generate a short title (3-5 words, in Spanish) for a legal case based on the user's first message.
Reply ONLY with the title, no punctuation, no quotes."""


def _build_pdf_context(pdfs: list) -> str:
    if not pdfs:
        return ""
    parts = []
    for pdf in pdfs[:4]:
        name = pdf["name"]
        pages = pdf.get("text_by_page", [])
        if not pages:
            full = pdf.get("full_text", "")
            if full.strip():
                parts.append(f"[{name}]\nPágina 1: {' '.join(full.split())[:800]}")
            continue
        page_snippets = []
        chars = 0
        for i, page_text in enumerate(pages, 1):
            clean = " ".join(page_text.split())
            if not clean:
                continue
            chunk = clean[:300]
            page_snippets.append(f"  Página {i}: {chunk}")
            chars += len(chunk)
            if chars >= 1200:
                break
        if page_snippets:
            parts.append(f"[{name}]\n" + "\n".join(page_snippets))
    if not parts:
        return ""
    return "\n\n---\nDocumentos adjuntos:\n\n" + "\n\n".join(parts)


def _chat(system: str, user: str, on_token=None) -> str:
    extra = _extra_prompt()
    if extra:
        system = system + f"\n\nInstrucciones adicionales:\n{extra}"
    model = _current_model()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    if on_token is not None:
        full = ""
        for chunk in ollama.chat(model=model, messages=messages, stream=True):
            token = chunk["message"]["content"]
            full += token
            on_token(full)
        return full
    response = ollama.chat(model=model, messages=messages)
    return response["message"]["content"]


def _repair_json(text: str) -> str:
    text = text.rstrip()
    if text.endswith(","):
        text = text[:-1]
    # close any open string
    in_string = False
    escaped = False
    for ch in text:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
    if in_string:
        text += '"'
    # close open braces/brackets
    text += "}" * max(0, text.count("{") - text.count("}"))
    text += "]" * max(0, text.count("[") - text.count("]"))
    return text


def _parse_json(text: str):
    text = text.strip()
    for candidate in [text]:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    m = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text, re.DOTALL)
    if m:
        candidate = m.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            try:
                return json.loads(_repair_json(candidate))
            except json.JSONDecodeError:
                pass
    raise ValueError(f"No se pudo extraer JSON de: {text[:300]}")


class LLMService:

    def get_hypotheses(self, data: dict, on_token=None, detail_level: int = 1) -> list:
        case_text = "\n".join(data.get("symptoms", []))
        if not case_text.strip():
            return []
        pdf_ctx = _build_pdf_context(data.get("pdfs", []))
        level = max(0, min(2, detail_level))
        system = _HYPO_SYSTEM + _HYPO_DETAIL[level]
        raw = _chat(system, f"Caso:\n{case_text}{pdf_ctx}", on_token=on_token)
        return _parse_json(raw)

    def get_diagnosis(self, model, on_token=None, detail_level: int = 1) -> dict:
        case_text = "\n".join(model.symptoms) if model.symptoms else ""
        hyp_block = ""
        if model.hypotheses:
            lines = [
                f"- {h['name']} ({int(h['score'] * 100)}%): {h.get('detail', '')}"
                for h in model.hypotheses
            ]
            hyp_block = "\n\nHipótesis previas:\n" + "\n".join(lines)
        pdf_ctx = _build_pdf_context(getattr(model, "pdfs", []))
        level = max(0, min(2, detail_level))
        system = _DIAG_SYSTEM + _DIAG_DETAIL[level]
        raw = _chat(system, f"Caso:\n{case_text}{hyp_block}{pdf_ctx}", on_token=on_token)
        return _parse_json(raw)

    def generate_title(self, first_message: str) -> str:
        try:
            title = _chat(_TITLE_SYSTEM, first_message[:300]).strip().strip('"\'').strip()
            return title[:60] if title else "Sin título"
        except Exception:
            return "Sin título"

    def chat(self, messages: list, case_text: str = "", pdfs: list = None,
             on_token=None) -> str:
        extra = _extra_prompt()
        system = _CHAT_SYSTEM
        if case_text.strip():
            system += f"\n\nResumen del caso:\n{case_text}"
        if pdfs:
            system += _build_pdf_context(pdfs)
        if extra:
            system += f"\n\nInstrucciones adicionales:\n{extra}"
        model = _current_model()
        ollama_msgs = [{"role": "system", "content": system}] + [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]
        if on_token is not None:
            full = ""
            for chunk in ollama.chat(model=model, messages=ollama_msgs, stream=True):
                token = chunk["message"]["content"]
                full += token
                on_token(full)
            return full
        response = ollama.chat(model=model, messages=ollama_msgs)
        return response["message"]["content"]
