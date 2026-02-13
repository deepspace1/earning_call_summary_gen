# CallMosaic AI - Earnings Transcript Intelligence Engine

CallMosaic AI is a structured research tool designed to analyze earnings call transcripts. It extracts text from PDF transcripts (including scanned ones), cleans it, and uses Groq's LLM to generate a comprehensive, structured one-page summary for analysts.

## Features

- **Full PDF Ingestion**: Extracts text from every page of uploaded PDF transcripts.
- **OCR Support**: Automatically detects scanned PDFs and uses `Tesseract` OCR to extract text.
- **AI-Powered Analysis**: Uses Groq (Llama-3) to generate structured insights.
- **Smart Chunking**: Automatically handles large transcripts by splitting them into logical blocks and respects rate limits.
- **Structured Output**: Displays logical sections including Management Tone, Financial Performance, Risks, and Guidance.
- **PDF Export**: Download the summary as a clean, professional PDF report.

## How It Works

| Step 1: Upload | Step 2: Analyze |
| :---: | :---: |
| ![Upload](images/step_1_upload_template.png) | ![Analyze](images/step_2_analyzing_template.png) |
| **Upload your PDF transcript (digital or scanned)** | **The AI processes the text and extracts insights** |

| Step 3: Review | Step 4: Export |
| :---: | :---: |
| ![Review](images/step_3_dashboard_template.png) | ![Export](images/step_4_report_template.png) |
| **View the structured summary dashboard** | **Download the professional PDF report** |

*(Note: Place your own images in the `images/` folder with these names to customize this guide)*

## Setup

1.  **System Dependencies**:
    Ensure `tesseract-ocr` and `poppler-utils` are installed on your system.
    ```bash
    sudo apt-get install tesseract-ocr poppler-utils
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory and add your Groq API key:
    ```
    GROQ_API_KEY=your_groq_api_key_here
    ```

## Usage

Run the app using the helper script (handles environment activation):

```bash
./run.sh
```

1.  Upload a PDF earnings call transcript.
2.  Wait for extraction (OCR usually takes a bit longer for scanned files).
3.  Click **Generate Intelligence Report**.
4.  View the structured summary and download the PDF.
