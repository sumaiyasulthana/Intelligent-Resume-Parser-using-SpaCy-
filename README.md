# Intelligent-Resume-Parser-using-SpaCy-

This project is a Streamlit-based application that parses resumes in PDF format and extracts structured information such as contact details, skills, education, experience, certifications, and projects. It uses a combination of NLP (SpaCy) and OCR (Tesseract) to handle both text-based and image-based PDFs.

1.** Approach**
File Upload (PDF): The app allows users to upload resumes in .pdf format.

**Text Extraction:**

# If the PDF is text-based, it's parsed using pdfplumber.

# If little to no text is detected, OCR is applied using pytesseract + pdf2image.

**Information Extraction:**

# The extracted text is processed using SpaCy’s en_core_web_sm model and custom regex patterns.

# Fields like name, email, phone, LinkedIn URL, education, work experience, skills, certifications, and projects are identified.

**Confidence Scores:** Each extracted field is tagged with a confidence score (1.0 if detected, 0.0 if missing).

**Display:** The structured data is displayed using Streamlit’s interactive UI in JSON format.

2.**Libraries / Tools Used**

SpaCy – NLP for entity recognition (e.g., name).

pdfplumber – To extract text from PDF pages.

pdf2image – To convert image-based PDFs to images.

pytesseract – OCR engine for extracting text from images.

Streamlit – For building the interactive web app.

Poppler – Backend used by pdf2image to render PDFs (required separately).

3.**Assumptions & Limitations**

# Predefined Structure: The parser is tailored for resumes with certain keywords and format (e.g., degrees like B.E., experience durations like Jan 2020 – Dec 2021).

# No Deep Learning: This is rule-based with basic NLP—no ML model is trained.

# Limited Name Recognition: The name is extracted using entity recognition and may not always be 100% accurate if formatting is unusual.

# No PDF Form Support: Only resumes as standard PDFs (not interactive forms or scanned as images without OCR) are supported.

# LinkedIn Detection: Will return null if LinkedIn URL is not present in the resume.

