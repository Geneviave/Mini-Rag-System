import logging
from pathlib import Path

from processors.pdf_parser import PDFParser
from processors.chunker import CVChunker, Chunk

logger = logging.getLogger(__name__)


class ProcessingPipeline:

    def __init__(self, chunk_size_tokens=300, overlap_tokens=50, preserve_emails=True):
        self.parser = PDFParser(preserve_emails=preserve_emails)
        self.chunker = CVChunker(
            chunk_size_tokens=chunk_size_tokens,
            overlap_tokens=overlap_tokens,
        )

    def process(self, pdf_path):
        pdf_path = Path(pdf_path)
        logger.info(f"Processing: {pdf_path.name}")

        pages = self.parser.parse(pdf_path)
        chunks = self.chunker.chunk_pages(pages, source_file=pdf_path.name)

        avg_tokens = sum(c.metadata["approx_tokens"] for c in chunks) // max(len(chunks), 1)
        logger.info(f"{pdf_path.name} -> {len(chunks)} chunks (avg {avg_tokens} tokens)")

        return chunks

    def process_batch(self, pdf_paths):
        all_chunks = []
        for path in pdf_paths:
            try:
                all_chunks.extend(self.process(path))
            except Exception as exc:
                logger.warning(f"Skipping {path}: {exc}")
        return all_chunks

    def process_and_format(self, pdf_path):
        return [
            {"text": c.text, "metadata": c.metadata}
            for c in self.process(pdf_path)
        ]