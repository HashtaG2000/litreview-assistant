import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import CHUNK_SIZE, CHUNK_OVERLAP

# Maps regex patterns (matched against the first few lines of a page) to section labels.
_SECTION_PATTERNS = [
    (r'^\s*abstract\s*$',                                          'abstract'),
    (r'^\s*introduction\s*$',                                      'introduction'),
    (r'^\s*(related\s+work|background|literature\s+review)\s*$',   'related_work'),
    (r'^\s*(method(ology)?s?|approach|proposed\s+method)\s*$',     'methods'),
    (r'^\s*(experiment(s|al\s+results?)?|evaluation|results?(\s+and\s+discussion)?)\s*$', 'results'),
    (r'^\s*discussion\s*$',                                        'discussion'),
    (r'^\s*(conclusion(s)?|summary)\s*$',                          'conclusion'),
    (r'^\s*(references?|bibliography)\s*$',                        'references'),
]


class StructureAwareChunker:
    """
    Splits PDF pages into chunks while tagging each chunk with the detected
    academic section (abstract, methods, results, …).  Falls back to 'body'
    when no header is matched.
    """

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def detect_section(self, text: str) -> str:
        """Return a section label for the given page text."""
        for line in text.split('\n')[:6]:
            candidate = line.strip().lower()
            if not candidate:
                continue
            for pattern, label in _SECTION_PATTERNS:
                if re.match(pattern, candidate, re.IGNORECASE):
                    return label
        return 'body'

    def split(self, documents: list) -> list:
        """Split a list of LangChain Documents and attach 'section' metadata."""
        all_chunks = []
        for doc in documents:
            section = self.detect_section(doc.page_content)
            chunks = self._splitter.split_documents([doc])
            for chunk in chunks:
                chunk.metadata['section'] = section
            all_chunks.extend(chunks)
        return all_chunks
