from pathlib import Path

import fitz


def _format_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    elif n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


class PDFService:

    def add_pdfs(self, paths: list, on_progress=None) -> list:
        pdfs = []
        total = len(paths)
        for i, p in enumerate(paths):
            if on_progress:
                on_progress(i, total)
            path = Path(p)
            text_by_page: list[str] = []
            page_count = 0

            try:
                doc = fitz.open(str(p))
                page_count = doc.page_count
                for page in doc:
                    text_by_page.append(page.get_text())
                doc.close()
            except Exception:
                pass

            full_text = "\n".join(text_by_page)
            excerpt = " ".join(full_text.split())[:400] if full_text.strip() else ""

            pdfs.append({
                "name": path.name,
                "path": str(p),
                "pages": page_count,
                "size": _format_size(path.stat().st_size) if path.exists() else "",
                "full_text": full_text,
                "text_by_page": text_by_page,
                "excerpt": excerpt,
            })
        if on_progress:
            on_progress(total, total)
        return pdfs
