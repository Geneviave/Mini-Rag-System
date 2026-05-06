import fitz
import re
import unicodedata
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from langdetect import detect, LangDetectException


def normalize_arabic(text):
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u0640", "")
    for variant in ["\u0622", "\u0623", "\u0625"]:
        text = text.replace(variant, "\u0627")
    text = text.replace("\u0629", "\u0647")
    text = re.sub(r"[\u064B-\u065F]", "", text)
    return text.strip()


def fix_arabic_display(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def contains_arabic(text):
    return bool(re.search(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]", text))


def detect_language(text):
    try:
        clean = text.strip()
        if len(clean) < 10:
            return "unknown"
        lang = detect(clean)
        return lang if lang in ("ar", "en") else "unknown"
    except LangDetectException:
        return "unknown"


class PDFParser:

    def __init__(self, preserve_emails=True, preserve_urls=False):
        self.preserve_emails = preserve_emails
        self.preserve_urls = preserve_urls

    def parse(self, pdf_path):
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        pages = []
        doc = fitz.open(str(pdf_path))

        for idx in range(len(doc)):
            pages.append(self._process_page(doc[idx], idx + 1))

        doc.close()
        return pages

    def _process_page(self, page, page_number):
        raw_blocks = page.get_text("blocks")
        processed_blocks = []
        all_text_parts = []

        for i, block in enumerate(raw_blocks):
            if block[6] != 0:
                continue

            raw_text = block[4]
            bbox = block[:4]

            cleaned = self._clean_text(raw_text)
            if not cleaned:
                continue

            lang = self._detect_block_language(cleaned)
            if lang == "ar" or contains_arabic(cleaned):
                cleaned = normalize_arabic(cleaned)

            processed_blocks.append({
                "block_id": i,
                "text": cleaned,
                "language": lang,
                "bbox": bbox,
            })
            all_text_parts.append(cleaned)

        full_text = re.sub(r"\n{3,}", "\n\n", "\n".join(all_text_parts))
        page_lang = self._dominant_language(processed_blocks)

        return {
            "page_number": page_number,
            "raw_text": full_text,
            "language": page_lang,
            "blocks": processed_blocks,
        }

    def _clean_text(self, text):
        text = re.sub(r"[ \t]+", " ", text)
        if not self.preserve_urls:
            text = re.sub(r"https?://\S+|www\.\S+", "[URL]", text)
        if not self.preserve_emails:
            text = re.sub(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", "[EMAIL]", text)
        text = re.sub(
            r"[^\w\s\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF.,;:!?@()\[\]\"'\-–—/\\%$&#*]",
            " ", text
        )
        return text.strip()

    def _detect_block_language(self, text):
        if contains_arabic(text):
            latin = len(re.findall(r"[a-zA-Z]", text))
            arabic = len(re.findall(r"[\u0600-\u06FF]", text))
            if latin > 10 and arabic > 10:
                return "mixed"
            return "ar"
        return detect_language(text)

    def _dominant_language(self, blocks):
        if not blocks:
            return "unknown"
        counts = {}
        for b in blocks:
            counts[b["language"]] = counts.get(b["language"], 0) + 1
        if counts.get("ar", 0) > 0 and counts.get("en", 0) > 0:
            return "mixed"
        return max(counts, key=counts.get)