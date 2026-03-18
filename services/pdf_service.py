from pathlib import Path


class PDFService:

    def add_pdfs(self, paths):
        pdfs = []
        for p in paths:
            pdfs.append({"name": Path(p).name, "path": p})
        return pdfs
