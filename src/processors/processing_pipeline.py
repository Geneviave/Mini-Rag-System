import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)

    def __len__(self):
        return len(self.text.split())


EN_SECTION_RE = re.compile(
    r"^(summary|objective|profile|about me"
    r"|work experience|professional experience|experience|employment|employment history"
    r"|education|academic background|qualifications"
    r"|skills|technical skills|core competencies|competencies|expertise"
    r"|projects|key projects|personal projects"
    r"|certifications?|certificates?|licenses?"
    r"|languages?|language proficiency"
    r"|awards?|honors?|achievements?|accomplishments?"
    r"|publications?|research"
    r"|volunteer|community|activities?|interests?|hobbies?"
    r"|references?|referees?"
    r"|contact|personal information|personal details)$",
    re.IGNORECASE | re.MULTILINE,
)

AR_SECTION_RE = re.compile(
    r"^(summary_ar)$",
    re.MULTILINE,
)


def is_section_header(line):
    s = line.strip()
    return bool(EN_SECTION_RE.match(s) or AR_SECTION_RE.match(s))


def word_count(text):
    return len(text.split())


def approx_tokens(text):
    return int(word_count(text) * 1.3)


class CVChunker:

    MAX_SAFE_TOKENS = 300

    def __init__(self, chunk_size_tokens=300, overlap_tokens=50, min_chunk_tokens=30):
        self.chunk_size_tokens = min(chunk_size_tokens, self.MAX_SAFE_TOKENS)
        self.overlap_tokens = overlap_tokens
        self.min_chunk_tokens = min_chunk_tokens

        self.chunk_words = int(self.chunk_size_tokens / 1.3)
        self.overlap_words = int(overlap_tokens / 1.3)
        self.min_words = int(min_chunk_tokens / 1.3)

    def chunk_pages(self, pages, source_file=""):
        all_chunks = []

        for page in pages:
            page_text = page["raw_text"]
            page_num = page["page_number"]
            page_lang = page["language"]

            if not page_text.strip():
                continue

            sections = self._split_into_sections(page_text)

            for section_name, section_text in sections:
                if not section_text.strip():
                    continue

                for i, chunk_text in enumerate(self._sliding_window_chunk(section_text)):
                    if not chunk_text.strip():
                        continue
                    all_chunks.append(Chunk(
                        text=chunk_text,
                        metadata={
                            "source_file": source_file,
                            "page_number": page_num,
                            "section": section_name,
                            "chunk_index": i,
                            "language": page_lang,
                            "approx_tokens": approx_tokens(chunk_text),
                            "word_count": word_count(chunk_text),
                        }
                    ))

        for g_idx, chunk in enumerate(all_chunks):
            chunk.metadata["global_chunk_index"] = g_idx

        return all_chunks

    def _split_into_sections(self, text):
        lines = text.split("\n")
        sections = []
        current_section = "body"
        current_lines = []

        for line in lines:
            if is_section_header(line):
                if current_lines:
                    body = "\n".join(current_lines).strip()
                    if body:
                        sections.append((current_section, body))
                current_section = line.strip().lower() or "body"
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            body = "\n".join(current_lines).strip()
            if body:
                sections.append((current_section, body))

        return sections or [("body", text)]

    def _sliding_window_chunk(self, text):
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        chunks = []
        words_buffer = []

        for sentence in sentences:
            s_words = sentence.split()
            if len(words_buffer) + len(s_words) > self.chunk_words and words_buffer:
                chunks.append(" ".join(words_buffer))
                overlap_start = max(0, len(words_buffer) - self.overlap_words)
                words_buffer = words_buffer[overlap_start:]
            words_buffer.extend(s_words)

        if words_buffer:
            chunks.append(" ".join(words_buffer))

        return self._merge_short_chunks(chunks)

    def _split_sentences(self, text):
        parts = re.split(r"(?<=[.!?])\s+|(?<=\n)\s*", text)
        return [s.strip() for s in parts if s.strip()]

    def _merge_short_chunks(self, chunks):
        if not chunks:
            return chunks

        merged = []
        pending = ""

        for chunk in chunks:
            if pending:
                chunk = pending + " " + chunk
                pending = ""
            if word_count(chunk) < self.min_words:
                pending = chunk
            else:
                merged.append(chunk)

        if pending:
            if merged:
                merged[-1] += " " + pending
            else:
                merged.append(pending)

        return merged