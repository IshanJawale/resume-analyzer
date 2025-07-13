"""
Resume Text Extraction Module

Handles extraction of text from PDF files including both text-based and image-based PDFs.
"""

import logging
import os
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning(
        "OCR libraries not available. Only text-based PDFs will be supported."
    )


class ResumeTextExtractor:
    """
    Handles extraction of text from resume PDFs
    """

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from resume PDF - handles both text and image-based PDFs

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        extracted_text = ""

        try:
            logger.debug(f"Extracting text from: {pdf_path}")

            # Method 1: Try extracting text directly from PDF
            logger.debug("Attempting direct text extraction...")
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n"

            # Check if we got meaningful text (more than just spaces/newlines)
            if len(extracted_text.strip()) > 50:  # Arbitrary threshold
                logger.info("Direct text extraction successful!")
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                logger.debug(f"Extracted {word_count} words, {char_count} characters")
                return extracted_text.strip()
            else:
                logger.debug(
                    "Direct text extraction failed or insufficient. Trying OCR..."
                )
                extracted_text = ""  # Reset

                if not OCR_AVAILABLE:
                    logger.warning(
                        "OCR libraries not available. Cannot process image-based PDFs."
                    )
                    return ""

                # Method 2: Use OCR for image-based or flattened PDFs
                logger.debug("Converting PDF to images for OCR...")

                # Convert PDF to images
                pages = convert_from_path(pdf_path, dpi=300)  # High DPI for better OCR

                logger.debug(f"Processing {len(pages)} pages with OCR...")
                for page_num, page_image in enumerate(pages):
                    logger.debug(f"  Processing page {page_num + 1}/{len(pages)}...")

                    # Use OCR to extract text from the image
                    page_text = pytesseract.image_to_string(page_image, lang="eng")

                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n"

                if len(extracted_text.strip()) > 50:
                    logger.info("OCR text extraction successful!")
                    word_count = len(extracted_text.split())
                    char_count = len(extracted_text)
                    logger.debug(
                        f"Extracted {word_count} words, {char_count} characters"
                    )
                    return extracted_text.strip()
                else:
                    logger.warning("OCR extraction failed or insufficient text found")
                    return ""

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
