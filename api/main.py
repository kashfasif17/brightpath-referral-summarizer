import re
import json
import os
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from json_repair import repair_json

app = FastAPI(title="BrightPath Referral Letter Summarizer")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class LetterRequest(BaseModel):
    letter_text: str

def build_prompt(letter_text):
    return f"""You are an expert clinical data extraction assistant working for a hospital referral system. Your job is to carefully read a referral letter (which may come from ANY medical specialty — cardiology, orthopedics, dermatology, neurology, psychiatry, pediatrics, ENT, urology, gastroenterology, endocrinology, vascular surgery, or any other) and extract structured information.

You must output ONLY a single valid JSON object. No comments, no explanations, no markdown formatting, no text before or after the JSON.

EXTRACTION GUIDELINES (read carefully before extracting):

1. AGE: Look for any number followed by "year(s)", "yo", "y/o", "y.o.", "aged", "day(s)-old", "month(s)-old", or similar. Include the unit if it is NOT years (e.g. "24 days", "3 months"). If the unit is years, just return the number (e.g. "58").

2. GENDER: Look for "male", "female", "M", "F", "man", "woman", "he", "she", "his", "her" pronouns to infer gender if not explicitly stated.

3. CHIEF_COMPLAINT: The main symptom or reason the patient is having problems — usually described early in the letter. Include duration if mentioned.

4. MEDICAL_HISTORY: Any pre-existing conditions, chronic diseases, past surgeries, current medications, allergies, family history, or lifestyle factors mentioned anywhere in the letter.

5. SUSPECTED_DIAGNOSIS: The doctor's clinical suspicion or working diagnosis, even if described indirectly through clinical findings (e.g. a described mass, aneurysm, lesion, or abnormality that has not been explicitly labeled as a "diagnosis"). Read the FULL letter including any narrative/case description to infer this, not just the opening lines.

6. REFERRAL_REASON: What the referring doctor is specifically asking the specialist to do. This may be stated explicitly ("please assess", "requesting evaluation") OR implied through context (e.g. "the patient was referred for a vascular opinion" appearing anywhere in the text, even mid-paragraph). Search the ENTIRE letter, not just the beginning or end.

GENERAL RULES:
- Read the ENTIRE letter carefully, including narrative/case-report style letters, before answering.
- Extract information even if phrased indirectly, abbreviated, or embedded in a longer sentence.
- Do not invent information not present in the letter.
- If a field truly cannot be determined after careful full-text reading, use an empty string "" — never use null, never omit the field.
- Keep values concise but complete.

EXAMPLE 1 (cardiology, formal style):
Letter: "Dear colleague, I refer this 58-year-old female with 3 months of exertional chest discomfort. History of hypertension and smoking. Suspect stable angina. Please assess for further cardiac workup."
Output: {{"age": "58", "gender": "female", "chief_complaint": "3 months of exertional chest discomfort", "medical_history": "Hypertension, smoker", "suspected_diagnosis": "Stable angina", "referral_reason": "Further cardiac workup requested"}}

EXAMPLE 2 (narrative/case-report style with implicit referral reason):
Letter: "A 78 year old male presented with swelling of the right leg. On vascular review, the patient had a pulsatile mass comparable with a popliteal artery aneurysm of 12 cms. The patient was referred for a vascular opinion regarding management."
Output: {{"age": "78", "gender": "male", "chief_complaint": "Swelling of the right leg", "medical_history": "", "suspected_diagnosis": "Popliteal artery aneurysm", "referral_reason": "Vascular opinion requested regarding management"}}

Required JSON structure (exactly these 6 fields, nothing else):
{{
  "age": "",
  "gender": "",
  "chief_complaint": "",
  "medical_history": "",
  "suspected_diagnosis": "",
  "referral_reason": ""
}}

Now extract from this letter:
{letter_text}

Return ONLY the JSON object, nothing before or after it.
"""

def extract_age_fallback(text):
    match = re.search(r'(\d{1,3})[\s-]*(year|yo\b|y/o|y\.o\.)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'(\d{1,3})[\s-]*(day|days)[\s-]*old', text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} days"
    match = re.search(r'(\d{1,3})[\s-]*(month|months)[\s-]*old', text, re.IGNORECASE)
    if match:
        return f"{match.group(1)} months"
    return ""

def extract_gender_fallback(text):
    text_lower = text.lower()
    if re.search(r'\bmale\b', text_lower) and not re.search(r'\bfemale\b', text_lower):
        return "Male"
    if re.search(r'\bfemale\b', text_lower):
        return "Female"
    return ""

@app.get("/")
def home():
    return {"message": "BrightPath Referral Letter Summarizer API is running (Groq-powered)"}

@app.post("/summarize")
def summarize(request: LetterRequest):
    prompt = build_prompt(request.letter_text)

    response = client.chat.completions.create(
       model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    result_text = response.choices[0].message.content
    fixed_json_string = repair_json(result_text)

    try:
        data = json.loads(fixed_json_string)

        if not str(data.get("age", "")).strip():
            data["age"] = extract_age_fallback(request.letter_text)

        if not str(data.get("gender", "")).strip():
            data["gender"] = extract_gender_fallback(request.letter_text)

        fixed_json_string = json.dumps(data)
    except Exception:
        pass

    return {"summary": fixed_json_string}