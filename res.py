import streamlit as st
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import spacy
import re
import tempfile
import os
from pytesseract import image_to_string
import json
from collections import defaultdict
from difflib import SequenceMatcher

nlp = spacy.load("en_core_web_sm")

# Utility functions
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_text_from_image_pdf(file_path):
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text.strip()


def clean_text(text):
    return re.sub(r'\s+', ' ', text)

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{4,6}", text)
    return match.group() if match else None

def extract_linkedin(text):
    match = re.search(r"(https?:\/\/)?(www\.)?linkedin\.com\/[A-Za-z0-9\/\-_%]+", text)
    return match.group() if match else None

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_education(text):
    education_keywords = ["Bachelor", "Master", "B.Tech", "B.E", "M.Tech", "MBA", "PhD", "Diploma"]
    educations = []
    lines = text.split("\n")
    for line in lines:
        for keyword in education_keywords:
            if keyword.lower() in line.lower():
                year_match = re.search(r"(19|20)\d{2}", line)
                educations.append({
                    "degree": keyword,
                    "institution": line,
                    "year": year_match.group() if year_match else None
                })
                break
    return educations

def extract_experience(text):
    experience_section = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.search(r"(Company|Experience|Work)", line, re.IGNORECASE):
            for j in range(i+1, min(i+10, len(lines))):
                if re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})", lines[j]):
                    match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}[\s\-to–]+(Present|\w+ \d{4})", lines[j])
                    experience_section.append({
                        "company": lines[i+1].strip(),
                        "title": lines[i+2].strip(),
                        "duration": match.group() if match else None,
                        "description": lines[i+3].strip() if i+3 < len(lines) else None
                    })
                    break
    return experience_section

def extract_skills(text):
    common_skills = ["Python", "SQL", "Excel", "Tableau", "Java", "C++", "TensorFlow", "Keras", "Pandas", "NumPy", "Machine Learning"]
    skills_found = []
    for skill in common_skills:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            skills_found.append(skill)
    return skills_found

def extract_certifications(text):
    lines = text.split("\n")
    certifications = []
    for line in lines:
        if "certificate" in line.lower() or "certified" in line.lower():
            certifications.append(line.strip())
    return certifications

def extract_projects(text):
    lines = text.split("\n")
    projects = []
    for line in lines:
        if "project" in line.lower():
            projects.append(line.strip())
    return projects

def get_confidence(field_value):
    if not field_value:
        return 0.0
    if isinstance(field_value, list) and not field_value:
        return 0.0
    return 1.0  # Simplified. You can improve this using model certainty, etc.

def parse_resume(text):
    # try:
    #     text = extract_text_from_pdf(text)
    #     if len(text.strip()) < 100:
    #         text = extract_text_from_image_pdf(text)
    # except Exception as e:
    #     print(f"OCR fallback triggered: {e}")
    #     text = extract_text_from_image_pdf(text)

    text = clean_text(text)

    result = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "certifications": extract_certifications(text),
        "projects": extract_projects(text)
    }

    # Add confidence scores
    output = {}
    for key, value in result.items():
        output[key] = {
            "value": value if value else None,
            "confidence": get_confidence(value)
        }

    return output


# ---------- Streamlit UI ----------

st.title("📄 Intelligent Resume Parser using SpaCy")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    try:
        text = extract_text_from_pdf(tmp_path)
        if len(text.strip()) < 100:
            st.warning("Low text content detected, using OCR fallback.")
            text = extract_text_from_image_pdf(tmp_path)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        text = extract_text_from_image_pdf(tmp_path)

    resume_data = parse_resume(text)

    st.subheader("📋 Extracted Resume Information")
    for field, info in resume_data.items():
        st.markdown(f"### {field.capitalize()}")
        st.json(info)

    os.unlink(tmp_path)

