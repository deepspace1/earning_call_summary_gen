import streamlit as st
import json
from backend import CallMosaicBackend
from utils import create_pdf_report

st.set_page_config(page_title="CallMosaic AI", page_icon="📊", layout="wide")

# Custom CSS for "wow" factor
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #0e1117;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0;
    }
    .sub-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        color: #fff;
        background-color: #0068c9;
        border-color: #0068c9;
    }
    .metric-box {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">CallMosaic AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Earnings Transcript Intelligence Engine</div>', unsafe_allow_html=True)

backend = CallMosaicBackend()

uploaded_file = st.file_uploader("Upload Earnings Call Transcript (PDF)", type="pdf")

if uploaded_file is not None:
    with st.spinner("Processing PDF..."):
        try:
            # Step 1: Extract
            extraction_result = backend.extract_text_from_pdf(uploaded_file)
            
            # Validation
            # Validation
            if extraction_result.get("is_scanned", False):
                st.error("🚨 Error: This appears to be a scanned PDF and OCR failed to extract text. Please ensure the file is legible or upload a text-based PDF.")
                st.stop()
            elif extraction_result["word_count"] < 800:
                st.warning(f"⚠️ Warning: Extracted text is very short ({extraction_result['word_count']} words). This might not be a full transcript.")
                
            cols = st.columns(3)
            with cols[0]:
                st.metric("Pages Processed", extraction_result["page_count"])
            with cols[1]:
                st.metric("Total Words", extraction_result["word_count"])
                
            with st.expander("View Extracted Text"):
                st.text(extraction_result["text"][:2000] + "...")
                
            # Step 2: Analyze
            if st.button("Generate Intelligence Report"):
                with st.spinner("Analyzing transcript using Groq (Llama-3)..."):
                    summary_json_str = backend.generate_summary(extraction_result["text"])
                    
                    try:
                        summary_data = json.loads(summary_json_str)
                        
                        # Display
                        st.subheader("📊 Executive Summary")
                        
                        # Tone
                        tone_color = "gray"
                        tone = summary_data.get("Management Tone", "Neutral")
                        if "Positive" in tone or "Optimistic" in tone:
                            tone_color = "green"
                        elif "Caution" in tone or "Negative" in tone:
                            tone_color = "red"
                            
                        st.markdown(f"**Management Tone:** <span style='color:{tone_color};font-weight:bold'>{tone}</span>", unsafe_allow_html=True)

                        st.markdown("---")
                        
                        # Layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 📈 Performance & Financials")
                            st.write("**Business Performance:**", summary_data.get("Business Performance Overview", "N/A"))
                            st.write("**Revenue & Margin:**", summary_data.get("Revenue and Margin Discussion", "N/A"))
                            st.write("**Forward Guidance:**", summary_data.get("Forward Guidance & Outlook", "N/A"))
                            
                            st.markdown("### ✅ Key Positives")
                            for item in summary_data.get("Key Positives", []):
                                st.write(f"• {item}")
                                
                        with col2:
                            st.markdown("### ⚙️ Operations & Strategy")
                            st.write("**Operational Commentary:**", summary_data.get("Cost & Operational Commentary", "N/A"))
                            st.write("**Capital Allocation:**", summary_data.get("Capital Allocation / Capex Commentary", "N/A"))
                            
                            st.markdown("### ⚠️ Key Risks")
                            for item in summary_data.get("Key Risks / Challenges", []):
                                st.write(f"• {item}")
                                
                        st.markdown("---")
                        st.markdown("### 🚀 Strategic Initiatives")
                        for item in summary_data.get("Strategic / Growth Initiatives", []):
                            st.write(f"• {item}")
                            
                        st.markdown("### 💬 Q&A Insights")
                        st.write(summary_data.get("Q&A Insights", "N/A"))
                        
                        st.markdown("---")
                        st.markdown("### 📝 One-Page Summary")
                        st.info(summary_data.get("Executive One-Page Summary Paragraph", "N/A"))
                        
                        # PDF Export
                        pdf_file = create_pdf_report(summary_data)
                        st.download_button(
                            label="Download Report as PDF",
                            data=pdf_file,
                            file_name="earnings_summary.pdf",
                            mime="application/pdf"
                        )
                        
                    except json.JSONDecodeError:
                        st.error("Error parsing LLM response. The model might not have returned valid JSON.")
                        st.code(summary_json_str)
                        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

else:
    st.info("Please upload a PDF transcript to begin.")
