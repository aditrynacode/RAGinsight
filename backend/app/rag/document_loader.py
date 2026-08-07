from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

class DocumentLoader:

    def __init__(self, document_directory: Path):

        self.document_directory = document_directory

    def list_documents(self) -> List[Path]:

        pdf_files = sorted(self.document_directory.glob("*.pdf"))
        return pdf_files

    def load_single_document(self, pdf_path: Path) -> List[Document]:

        loader = PyPDFLoader(str(pdf_path))
        return loader.load()

    def load_all_documents(self) -> List[Document]:

        all_pages = []
        pdf_files = self.list_documents()
        print(f"\nFound {len(pdf_files)} PDF(s).\n")

        for pdf in pdf_files:

            print(f"Loading: {pdf.name}")
            pages = self.load_single_document(pdf)
            print(f"Loaded {len(pages)} page(s)\n")
            all_pages.extend(pages)

        return all_pages
