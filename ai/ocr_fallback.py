import sys
import base64
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import subprocess

def improve_image(img):
    """Enhance image for better OCR results"""
    return img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')

def extract_text(pdf_bytes):
    try:
        images = convert_from_bytes(pdf_bytes)
        full_text = ""
        for img in images:
            img = improve_image(img)
            text = pytesseract.image_to_string(img)
            full_text += text + "\n"
        return full_text.strip()
    except Exception as e:
        return f"OCR_ERROR: {str(e)}"

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("ERROR: Missing PDF data or job title", file=sys.stderr)
            sys.exit(1)

        # Decode base64 inputs
        pdf_bytes = base64.b64decode(sys.argv[1])
        job_title = base64.b64decode(sys.argv[2]).decode('utf-8')

        # OCR extract
        result = extract_text(pdf_bytes)

        if result.startswith("OCR_ERROR"):
            print(result, file=sys.stderr)
            sys.exit(1)

        # Encode extracted text and job title to pass to resume_analyser.py
        encoded_text = base64.b64encode(result.encode('utf-8')).decode('utf-8')
        encoded_title = base64.b64encode(job_title.encode('utf-8')).decode('utf-8')

        # Call resume_analyser.py
        analyser_result = subprocess.run(
            ['python3', 'resume_analyser.py', encoded_text, encoded_title],
            capture_output=True, text=True
        )

        if analyser_result.returncode != 0:
            print(f"ANALYSER_ERROR: {analyser_result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)

        print(analyser_result.stdout.strip())

    except Exception as e:
        print(f"FATAL_ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
