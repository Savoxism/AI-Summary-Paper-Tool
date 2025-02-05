import requests
import pdfplumber

def download_pdf(url, title):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = f"{title}.pdf"
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded PDF to '{file_path}'")
        return file_path
    else:
        print(f"Failed to download PDF: {response.status_code}")
        return None

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None