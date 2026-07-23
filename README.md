1. BrightPath Referral Letter Summarizer
AI-powered tool that extracts and summarizes key clinical details from patient referral letters (PDF), helping doctors reduce prep time and spend more time with patients.

2.Problem
BrightPath Clinics doctors spend too much time reading long, unstructured referral letters before appointments. This tool extracts structured clinical info from a referral letter PDF and returns a clean summary — downloadable as a PDF.

3.Features
 Upload a referral letter as a PDF, get a structured summary PDF back
 Extracts: age, gender, chief complaint, medical history, suspected diagnosis, referral reason
 Automatic PII removal (names/locations redacted) before processing
 LLM-based extraction via Groq API
 FastAPI backend + Streamlit frontend
 Custom evaluation metrics (JSON validity + field completeness)
 Dockerized for easy deployment

4.Tech Stack
 FastAPI · Groq API (Llama 3.3 70B) · HuggingFace Transformers (NER) · PyPDF2 · fpdf2 · Streamlit · Docker

 5.Project Structure
brightpath-referral-summarizer/
├── data/                       # sample referral letters + processed data
├── api/
│   └── main.py                 # FastAPI backend
├── frontend/
│   └── app.py                  # Streamlit demo
├── clean\_data.py                # data cleaning script
├── remove\_pii.py                 # PII removal script
├── extraction.py                 # batch extraction script
├── evaluation.py                  # evaluation metric script
├── evaluation\_report.json         # evaluation results
├── Dockerfile
├── requirements.txt
└── README.md

6.How to Run
Option A: Run with Docker (Recommended)

1\. Build the image:

&#x20;  ```bash

&#x20;  docker build -t brightpath-summarizer .

&#x20;  ```

2\. Run the container (replace with your own Groq API key):

&#x20;  ```bash

&#x20;  docker run -p 8000:8000 -p 8501:8501 -e GROQ\_API\_KEY=your\_groq\_api\_key brightpath-summarizer

&#x20;  ```

3\. Open in browser:

&#x20;  ```

&#x20;  http://localhost:8501

&#x20;  ```



\### Option B: Run Locally (Without Docker)
1\. Install dependencies:

&#x20;  ```bash

&#x20;  pip install -r requirements.txt

&#x20;  ```

2\. Set your Groq API key:

&#x20;  ```bash

&#x20;  set GROQ\_API\_KEY=your\_groq\_api\_key

&#x20;  ```

3\. Start the backend API:

&#x20;  ```bash

&#x20;  uvicorn api.main:app --reload

&#x20;  ```

4\. Start the frontend (in a new terminal):

&#x20;  ```bash

&#x20;  streamlit run frontend/app.py

&#x20;  ```

5\. Open in browser:

&#x20;  ```

&#x20;  http://localhost:8501

&#x20;  ```

 7.Dataset
\- 10 synthetic referral letters (self-generated, covering multiple specialties)

\- 20 clinical notes sampled from HuggingFace's `AGBonnet/augmented-clinical-notes`

8. Limitations

\- Occasional malformed JSON output from the model on longer or unusually formatted letters

\- No OCR support (text-based PDFs only, not scanned images)

\- Not tested on real-world clinical data due to privacy and access constraints

\- Requires a valid Groq API key to run

9. Future Improvements

\- Add OCR support for scanned/image-based referral letters

\- Fine-tune a model specifically on referral letter data

\- Deploy to a cloud platform for a publicly accessible live demo

 10.Author
  
  Portfolio project demonstrating document intelligence and clinical NLP for a real-world healthcare workflow (BrightPath Clinics, Netherlands).

