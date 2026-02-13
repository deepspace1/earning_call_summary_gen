import os
import fitz  # PyMuPDF
from groq import Groq
from dotenv import load_dotenv
from utils import clean_text
try:
    from pdf2image import convert_from_bytes
    import pytesseract
except ImportError as e:
    print(f"Warning: OCR dependencies not found: {e}")
    convert_from_bytes = None
    pytesseract = None

load_dotenv()

class CallMosaicBackend:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=self.api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct" # Using the requested model

    def extract_text_from_pdf(self, pdf_file) -> dict:
        """
        Extracts text from a PDF file stream.
        If no text is found, attempts OCR using pytesseract.
        Returns a dict with 'text', 'page_count', 'word_count', 'is_scanned'.
        """
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        page_count = doc.page_count
        
        text_content_found = False
        
        # unique_set needed to avoid re-reading if we seek(0) but we have bytes 
        # Actually pdf_file is a Streamlit UploadedFile, so .read() moves cursor. 
        # We stored bytes in pdf_bytes so we can reuse if needed for OCR.
        
        for page in doc:
            page_text = page.get_text()
            full_text += page_text + "\n"
            if len(page_text.strip()) > 50: 
                text_content_found = True
            
        is_scanned = not text_content_found and page_count > 0
        
        if is_scanned:
            # Fallback to OCR
            if convert_from_bytes is None or pytesseract is None:
                print("Error: OCR dependencies (pdf2image, pytesseract) are not available.")
                # We can't do anything, so it will return empty text and is_scanned=True
            else:
                # This might be slow for large PDFs, but necessary for scans
                # Convert PDF to list of images
                try:
                    images = convert_from_bytes(pdf_bytes)
                    full_text = ""
                    for img in images:
                        text = pytesseract.image_to_string(img)
                        full_text += text + "\n"
                    
                    # Re-evaluate text content
                    if len(full_text.strip()) > 50:
                         text_content_found = True
                         is_scanned = False # Treated as text now
                except Exception as e:
                    # If OCR fails (e.g. missing poppler), return original empty result but keep is_scanned=True
                    print(f"OCR Failed: {e}")
                    pass

        cleaned_text = clean_text(full_text)
        word_count = len(cleaned_text.split())
        
        return {
            "text": cleaned_text,
            "page_count": page_count,
            "word_count": word_count,
            "is_scanned": is_scanned # If OCR worked, this is now False. If OCR failed/not installed, remains True.
        }


    def generate_summary(self, transcript_text: str) -> str:
        """
        Sends the transcript to Groq for summarization.
        Handles chunking if necessary (basic implementation for now).
        """
        system_prompt = """You are a professional equity research analyst.
Your task is to analyze an earnings call transcript.

STRICT RULES:
* Use ONLY information present in transcript.
* Do NOT fabricate numbers.
* If something is not mentioned, state “Not mentioned in transcript.”
* Produce structured output in JSON format.
* Cover ALL major sections discussed.
"""

        user_prompt = f"""Analyze the following full earnings call transcript:

{transcript_text}

Generate a structured JSON response with the following keys:
1. "Management Tone" (Optimistic / Neutral / Cautious / Pessimistic)
2. "Business Performance Overview"
3. "Revenue and Margin Discussion"
4. "Cost & Operational Commentary"
5. "Key Positives" (List of strings)
6. "Key Risks / Challenges" (List of strings)
7. "Forward Guidance & Outlook"
8. "Strategic / Growth Initiatives" (List of strings)
9. "Capital Allocation / Capex Commentary"
10. "Q&A Insights"
11. "Executive One-Page Summary Paragraph"

Ensure the JSON is valid and values are concise but comprehensive.
"""
        
        # Chunking Strategy
        # User reported 6000 TPM limit on Groq 'on_demand'. 
        # We must stay well below this.
        
        estimated_tokens = len(transcript_text.split()) / 0.75
        
        # Lower threshold to trigger chunking earlier to avoid Rate Limit Exceeded
        if estimated_tokens > 3500: 
             return self._chunked_summary(transcript_text, system_prompt)
        
        try:
            return self._call_llm(system_prompt, user_prompt, json_mode=True)
        except Exception as e:
            if "rate_limit_exceeded" in str(e) or "413" in str(e):
                 # Fallback to chunking if we hit a limit even with a smaller doc
                 return self._chunked_summary(transcript_text, system_prompt)
            return f"Error generating summary: {str(e)}"

    def _chunked_summary(self, text, system_prompt):
        """
        Splits text into chunks, summarizes each, then consolidates.
        Respects strict rate limits.
        """
        import time
        words = text.split()
        chunk_size = 2000 # Reduced chunk size (~2600 tokens)
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            # STAGE 1: Summarize Chunks
            chunk_prompt = f"Summarize this section of the earnings call (Part {i+1}/{len(chunks)}). Extract key financial figures, tone, and strategic points:\n\n{chunk}"
            try:
                summary = self._call_llm(system_prompt, chunk_prompt, json_mode=False)
                chunk_summaries.append(summary)
            except Exception as e:
                chunk_summaries.append(f"[Error summarizing chunk {i+1}: {e}]")
            
            # Rate Limit Safety: Wait between chunks to reset TPM window (approx 1 min window)
            # 2600 tokens + response ~ 3000 tokens. Limit is 6000. 
            # Two requests might hit it. Safe to wait 20s.
            if i < len(chunks) - 1:
                time.sleep(20) 
            
        combined_summary = "\n\n".join(chunk_summaries)
        
        # Rate Limit Safety: Wait before final consolidation
        time.sleep(20)

        final_prompt = f"""Analyze the following summarized sections of an earnings call transcript:

{combined_summary}

Generate a final structured JSON response merging all insights with the following keys:
1. "Management Tone" (Optimistic / Neutral / Cautious / Pessimistic)
2. "Business Performance Overview"
3. "Revenue and Margin Discussion"
4. "Cost & Operational Commentary"
5. "Key Positives" (List of strings)
6. "Key Risks / Challenges" (List of strings)
7. "Forward Guidance & Outlook"
8. "Strategic / Growth Initiatives" (List of strings)
9. "Capital Allocation / Capex Commentary"
10. "Q&A Insights"
11. "Executive One-Page Summary Paragraph"
"""
        return self._call_llm(system_prompt, final_prompt, json_mode=True)

    def _call_llm(self, system_prompt, user_prompt, json_mode=True):
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "top_p": 0.9,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        completion = self.client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content

