import os
import io
from utils import clean_text, create_pdf_report
from backend import CallMosaicBackend
from reportlab.pdfgen import canvas
import unittest
from unittest.mock import MagicMock, patch

class TestCallMosaic(unittest.TestCase):
    def setUp(self):
        # Create a dummy PDF in memory
        self.pdf_buffer = io.BytesIO()
        c = canvas.Canvas(self.pdf_buffer)
        c.drawString(100, 750, "Earnings Call Transcript Page 1")
        c.drawString(100, 700, "This is a test transcript for the earnings call.")
        c.showPage()
        c.save()
        self.pdf_buffer.seek(0)

    def test_utils_clean_text(self):
        raw = "Page 1 of 10\nThis is text.\n\n\nMore text."
        cleaned = clean_text(raw)
        self.assertNotIn("Page 1 of 10", cleaned)
        self.assertIn("This is text.", cleaned)
        self.assertNotIn("\n\n\n", cleaned)

    def test_utils_pdf_generation(self):
        data = {
            "Management Tone": "Optimistic",
            "Key Positives": ["Growth", "Margins"],
            "Business Performance Overview": "Great quarter."
        }
        pdf = create_pdf_report(data)
        self.assertTrue(len(pdf.getvalue()) > 0)
        # Check basic header bytes for PDF
        self.assertTrue(pdf.getvalue().startswith(b'%PDF'))

    @patch("backend.Groq")
    @patch("os.getenv")
    @patch("backend.fitz.open")
    def test_backend_extraction(self, mock_fitz_open, mock_getenv, mock_groq):
        mock_getenv.return_value = "fake_key"
        backend = CallMosaicBackend()
        
        # Test 1: Normal PDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Earnings Call Transcript Page 1"
        mock_doc.page_count = 1
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        result = backend.extract_text_from_pdf(self.pdf_buffer)
        self.assertIn("text", result)
        self.assertFalse(result.get("is_scanned", False))
        self.assertIn("Earnings Call Transcript", result["text"])

    @patch("backend.Groq")
    @patch("os.getenv")
    @patch("backend.convert_from_bytes")
    @patch("backend.pytesseract")
    @patch("backend.fitz.open")
    def test_backend_ocr_fallback(self, mock_fitz, mock_pytesseract, mock_pdf2image, mock_getenv, mock_groq):
        # Test 2: Scanned PDF
        mock_getenv.return_value = "fake_key"
        backend = CallMosaicBackend()

        # Mock Empty Text from PyMuPDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "" # Empty text
        mock_doc.page_count = 1
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.return_value = mock_doc
        
        # Mock OCR result
        mock_pdf2image.return_value = ["dummy_image"]
        mock_pytesseract.image_to_string.return_value = "Scanned Text Content Recovered Which Is Now Long Enough To Pass The Threshold Of Fifty Characters."
        
        result = backend.extract_text_from_pdf(self.pdf_buffer)
        self.assertIn("Scanned Text Content Recovered", result["text"])
        self.assertFalse(result.get("is_scanned", True)) # Should be False if OCR worked


    @patch("backend.Groq")
    @patch("os.getenv")
    def test_backend_llm_call(self, mock_getenv, mock_groq):
        mock_getenv.return_value = "fake_key"
        backend = CallMosaicBackend()
        
        # Mock LLM response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '{"Management Tone": "Positive"}'
        backend.client.chat.completions.create.return_value = mock_completion
        
        summary = backend.generate_summary("Some transcript text")
        self.assertIn("Positive", summary)

if __name__ == '__main__':
    unittest.main()
