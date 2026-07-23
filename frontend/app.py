import streamlit as st
import requests
import json
import textwrap
import PyPDF2
from fpdf import FPDF
from datetime import datetime

st.set_page_config(
    page_title="BrightPath Referral Summarizer",
    layout="wide"
)

# ---------- Sample Letter (for demo mode) ----------
SAMPLE_LETTER_TEXT = """Referral Letter - Huisartsenpraktijk De Linde
Bezoekerslaan 14, 3521 VK Utrecht, Netherlands | Tel: +31 30 245 6781
Date: 14/03/2026

To: Dr. R. van Dijk, Cardiologist, St. Antonius Ziekenhuis, Nieuwegein
Re: Mrs. Anneke Bosman, 67 years old, Female, DOB 02/05/1958

Dear Dr. van Dijk,

I am referring the above patient for cardiology evaluation. She has been experiencing
intermittent chest tightness and shortness of breath on exertion for the past six weeks,
worsening over the last week with two episodes of chest pain radiating to the left arm at rest.
Her past medical history includes type 2 diabetes mellitus (diagnosed 2014, on metformin),
hypertension (on amlodipine 5mg), and a 20 pack-year smoking history (quit 2019).
Family history is significant for father with myocardial infarction at age 58.
Resting ECG in clinic showed nonspecific ST-T wave changes in the lateral leads.
Blood pressure at review was 148/92 mmHg, heart rate 88 bpm regular.

Given her risk profile and new-onset exertional symptoms, I would be grateful for an urgent
assessment to rule out unstable angina, including consideration of stress testing or coronary
angiography as clinically indicated. She is not currently on any antiplatelet or statin therapy.

Kind regards,
Dr. M. Hendriks, General Practitioner
"""

# ---------- Design tokens ----------
# Blue gradient hero (trust, clinical) + orange CTA accent (energy, action) —
# same family as modern patient-management SaaS products.
BLUE_DARK = "#12395E"
BLUE_MID = "#1E5C94"
BLUE_LIGHT = "#3B82C4"
ORANGE = "#F2994A"
ORANGE_DARK = "#D97F2E"
TEAL_OK = "#0F6E56"
TEXT_MUTED = "#5B6470"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    /* ---------- Hero banner ---------- */
    .hero {{
        background: linear-gradient(120deg, {BLUE_DARK} 0%, {BLUE_MID} 55%, {BLUE_LIGHT} 100%);
        border-radius: 16px;
        padding: 3rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }}
    .hero::after {{
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 260px; height: 260px;
        border-radius: 50%;
        background: rgba(255,255,255,0.06);
    }}
    .hero-eyebrow {{
        font-family: 'Poppins', sans-serif;
        color: {ORANGE};
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }}
    .hero-title {{
        font-family: 'Poppins', sans-serif;
        color: #FFFFFF;
        font-size: 2.6rem;
        font-weight: 700;
        line-height: 1.15;
        margin-bottom: 0.9rem;
        max-width: 640px;
    }}
    .hero-subtitle {{
        color: #D6E6F2;
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.6;
        max-width: 560px;
        margin-bottom: 0;
    }}

    /* ---------- Feature strip ---------- */
    .feature-strip {{
        display: flex;
        gap: 1rem;
        margin-bottom: 2.2rem;
        flex-wrap: wrap;
    }}
    .feature-pill {{
        flex: 1;
        min-width: 200px;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
    }}
    .feature-pill-num {{
        font-family: 'Poppins', sans-serif;
        color: {ORANGE};
        font-weight: 800;
        font-size: 0.78rem;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }}
    .feature-pill-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--text-color);
        margin-bottom: 0.2rem;
    }}
    .feature-pill-desc {{
        font-size: 0.82rem;
        color: {TEXT_MUTED};
        line-height: 1.4;
    }}

    /* ---------- Section labels ---------- */
    .section-label {{
        font-family: 'Poppins', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {BLUE_MID};
        margin-bottom: 0.7rem;
    }}

    /* ---------- Field cards ---------- */
    .field-card {{
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.18);
        border-left: 3px solid {BLUE_MID};
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.65rem;
    }}
    .field-label {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: {BLUE_MID};
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    .field-value {{
        color: var(--text-color);
        font-size: 0.98rem;
        margin-top: 0.35rem;
        line-height: 1.5;
    }}

    /* ---------- Badges ---------- */
    .completeness-badge {{
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        border: 1px solid currentColor;
    }}
    .saved-toast {{
        color: {TEAL_OK};
        font-size: 0.85rem;
        font-weight: 600;
    }}

    /* ---------- Buttons ---------- */
    div[data-testid="stFormSubmitButton"] button,
    button[kind="primary"] {{
        background-color: {ORANGE} !important;
        color: #1A1A1A !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stFormSubmitButton"] button:hover,
    button[kind="primary"]:hover {{
        background-color: {ORANGE_DARK} !important;
    }}
    button[kind="secondary"] {{
        border-radius: 8px !important;
        border: 1.5px solid {BLUE_MID} !important;
        color: {BLUE_MID} !important;
        font-weight: 600 !important;
    }}

    /* ---------- Footer ---------- */
    .app-footer {{
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(128,128,128,0.18);
        color: {TEXT_MUTED};
        font-size: 0.78rem;
    }}
</style>
""", unsafe_allow_html=True)

# ---------- Session State Setup ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "current_summary" not in st.session_state:
    st.session_state.current_summary = None
if "current_filename" not in st.session_state:
    st.session_state.current_filename = None
if "current_text" not in st.session_state:
    st.session_state.current_text = None
if "edits_saved" not in st.session_state:
    st.session_state.edits_saved = False

FIELD_LABELS = {
    "age": "Age",
    "gender": "Gender",
    "chief_complaint": "Chief Complaint",
    "medical_history": "Medical History",
    "suspected_diagnosis": "Suspected Diagnosis",
    "referral_reason": "Referral Reason",
}

# ---------- Helper Functions ----------
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def create_summary_pdf(summary_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "BrightPath Clinical Summary", ln=True)
    pdf.ln(5)

    effective_width = pdf.w - 2 * pdf.l_margin
    chars_per_line = max(int(effective_width / 2.2), 20)

    for key, value in summary_dict.items():
        label = FIELD_LABELS.get(key, key.replace("_", " ").title())
        display_value = str(value).strip()
        if display_value == "":
            display_value = "Not specified"

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"{label}:", ln=True)

        pdf.set_font("Helvetica", "", 12)
        wrapped_lines = textwrap.wrap(display_value, width=chars_per_line)
        if not wrapped_lines:
            wrapped_lines = ["Not specified"]
        for line in wrapped_lines:
            pdf.cell(0, 8, line, ln=True)
        pdf.ln(2)

    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, (bytes, bytearray)):
        return bytes(pdf_output)
    return pdf_output.encode("latin-1", errors="ignore")

def completeness_score(summary_dict):
    total = len(FIELD_LABELS)
    filled = sum(1 for k in FIELD_LABELS if str(summary_dict.get(k, "")).strip())
    return filled, total

def run_summarization(letter_text, filename):
    with st.spinner("Reading letter and extracting clinical fields..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/summarize",
                json={"letter_text": letter_text},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            summary_text = result.get("summary", "")
            parsed = json.loads(summary_text)

            st.session_state.current_summary = parsed
            st.session_state.current_filename = filename
            st.session_state.current_text = letter_text
            st.session_state.edits_saved = False

            st.session_state.history.append({
                "filename": filename,
                "time": datetime.now().strftime("%H:%M:%S"),
                "summary": parsed,
                "original_text": letter_text,
            })
            return True

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Make sure it's running: `uvicorn api.main:app --reload`")
        except json.JSONDecodeError:
            st.error("The AI model returned an unexpected format. Please try again.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
    return False

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### BrightPath Clinics")
    st.markdown("**Referral Letter Summarizer**")
    st.markdown("---")
    st.markdown("""
    **How to use**
    1. Upload a referral letter (PDF), or try the sample
    2. Click Summarize
    3. Review and correct the extracted fields if needed
    4. Download the summary as a PDF
    """)
    st.markdown("---")
    st.markdown(f"**Letters processed this session:** {len(st.session_state.history)}")

    if st.session_state.history:
        st.markdown("### Session History")
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{item['filename']} — {item['time']}"):
                filled, total = completeness_score(item['summary'])
                st.caption(f"Completeness: {filled}/{total} fields")
                st.json(item['summary'])

    if st.button("Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.current_summary = None
        st.session_state.current_filename = None
        st.session_state.current_text = None
        st.rerun()

# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">BrightPath Clinics · Document Intelligence</div>
    <div class="hero-title">Referral letters, understood in seconds.</div>
    <div class="hero-subtitle">
        Upload any referral letter and get a clean, structured clinical summary —
        chief complaint, history, suspected diagnosis, and urgency — before your
        doctors even open the file.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Feature strip ----------
st.markdown("""
<div class="feature-strip">
    <div class="feature-pill">
        <div class="feature-pill-num">01</div>
        <div class="feature-pill-title">Upload</div>
        <div class="feature-pill-desc">Drop in any referral letter PDF, structured or free-text.</div>
    </div>
    <div class="feature-pill">
        <div class="feature-pill-num">02</div>
        <div class="feature-pill-title">Extract</div>
        <div class="feature-pill-desc">AI pulls out the fields doctors actually need to prep.</div>
    </div>
    <div class="feature-pill">
        <div class="feature-pill-num">03</div>
        <div class="feature-pill-title">Review</div>
        <div class="feature-pill-desc">Correct any field in place before it's saved or shared.</div>
    </div>
    <div class="feature-pill">
        <div class="feature-pill-num">04</div>
        <div class="feature-pill-title">Export</div>
        <div class="feature-pill-desc">Download a clean one-page PDF summary in one click.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Upload area ----------
st.markdown('<div class="section-label">Step 1 — Provide a letter</div>', unsafe_allow_html=True)

upload_col, sample_col = st.columns([3, 1])
with upload_col:
    uploaded_file = st.file_uploader("Upload referral letter (PDF)", type=["pdf"], label_visibility="collapsed")
with sample_col:
    try_sample = st.button("Try a sample letter", use_container_width=True, type="secondary")

summarize_clicked = st.button("Summarize", type="primary", disabled=(uploaded_file is None))

# ---------- Trigger summarization ----------
if try_sample:
    run_summarization(SAMPLE_LETTER_TEXT, "sample_referral_letter.txt")

if uploaded_file is not None and summarize_clicked:
    letter_text = extract_text_from_pdf(uploaded_file)
    if letter_text.strip() == "":
        st.warning("Could not extract any text from this PDF. It may be a scanned image.")
    else:
        run_summarization(letter_text, uploaded_file.name)

# ---------- Display results ----------
if st.session_state.current_summary is not None:
    parsed = st.session_state.current_summary
    letter_text = st.session_state.current_text

    st.markdown('<div class="section-label" style="margin-top: 2rem;">Step 2 — Review the summary</div>', unsafe_allow_html=True)

    filled, total = completeness_score(parsed)
    pct = int((filled / total) * 100)
    badge_color = "#0F6E56" if pct >= 80 else "#8A6416" if pct >= 50 else "#B54A1C"
    badge_bg = "#EEF7F3" if pct >= 80 else "#FBF6EA" if pct >= 50 else "#FDF1EC"

    st.markdown(f"""
    <span class="completeness-badge" style="background-color:{badge_bg}; color:{badge_color};">
        {filled}/{total} fields extracted ({pct}%)
    </span>
    """, unsafe_allow_html=True)
    st.write("")

    tab_summary, tab_original = st.tabs(["Structured Summary", "Original Letter"])

    with tab_summary:
        st.caption("Click into any field to correct it before saving.")

        edited_values = {}
        with st.form("edit_summary_form"):
            for key, label in FIELD_LABELS.items():
                current_value = str(parsed.get(key, "")).strip()
                edited_values[key] = st.text_area(
                    label,
                    value=current_value,
                    height=70 if key in ("medical_history", "referral_reason") else 50,
                    key=f"field_{key}",
                )
            save_clicked = st.form_submit_button("Confirm & Save Corrections", type="primary")

        if save_clicked:
            parsed.update(edited_values)
            st.session_state.current_summary = parsed
            if st.session_state.history:
                st.session_state.history[-1]["summary"] = parsed
            st.session_state.edits_saved = True
            st.rerun()

        if st.session_state.edits_saved:
            st.markdown('<div class="saved-toast">Corrections saved.</div>', unsafe_allow_html=True)

        st.write("")
        pdf_bytes = create_summary_pdf(parsed)
        st.download_button(
            label="Download Summary as PDF",
            data=pdf_bytes,
            file_name=f"summary_{st.session_state.current_filename.replace('.pdf', '').replace('.txt', '')}.pdf",
            mime="application/pdf",
        )

    with tab_original:
        st.text_area("Extracted text", letter_text, height=450, label_visibility="collapsed")

elif uploaded_file is None:
    st.info("Upload a referral letter PDF, or click 'Try a sample letter' to see a demo.")

# ---------- Footer ----------
st.markdown("""
<div class="app-footer">
    BrightPath Clinics — Document Intelligence Prototype. Built for internal appointment-prep workflows.
</div>
""", unsafe_allow_html=True)