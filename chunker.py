import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SECTION_PATTERNS = [
    (r'^\s*abstract\s*$', 'abstract'),
    (r'^\s*introduction\s*$', 'introduction'),
    (r'^\s*(related\s+work|background|literature\s+review)\s*$', 'related_work'),
    (r'^\s*(method(ology)?s?|approach|proposed\s+method)\s*$', 'methods'),
    (r'^\s*(experiment(s|al\s+results?)?|evaluation|results?(\s+and\s+discussion)?)\s*$', 'results'),
    (r'^\s*discussion\s*$', 'discussion'),
    (r'^\s*(conclusion(s)?|summary)\s*$', 'conclusion'),
    (r'^\s*(references?|bibliography)\s*$', 'references'),
]


class StructureAwareChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def detect_section(self, text: str) -> str:
        for line in text.split('\n')[:6]:
            candidate = line.strip().lower()
            if not candidate:
                continue
            for pattern, label in _SECTION_PATTERNS:
                if re.match(pattern, candidate, re.IGNORECASE):
                    return label
        return 'body'

    def split(self, documents: list) -> list:
        all_chunks = []
        for doc in documents:
            section = self.detect_section(doc.page_content)
            chunks = self._splitter.split_documents([doc])
            for chunk in chunks:
                chunk.metadata['section'] = section
            all_chunks.extend(chunks)
        return all_chunks
