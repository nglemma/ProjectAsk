import os
import json
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import re

    # Folder where your files are stored
data_dir = '/Users/mac/Documents/NewCAFormat/dataa'  
ouput_dir = os.path.join(data_dir, 'llm.txt') # Output directory

def clean_text(content):
    # Remove citation-like patterns such as [1], [2], etc.
    content = re.sub(r'\[\d+\]', '', content)
    content = re.sub(r'\s+', ' ', content)  # normalize whitespace
    return content.strip()

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == '.csv':
            df = pd.read_csv(filepath)
            return df.to_string(index=False)

        elif ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)

        elif ext == '.docx':
            doc = Document(filepath)
            return '\n'.join([para.text for para in doc.paragraphs])

        elif ext == '.pdf':
            reader = PdfReader(filepath)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text

        else:
            print(f"Unsupported file type: {ext}")
            return ""

    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return ""
    


with open(ouput_dir, 'w', encoding='utf-8') as outfile:
    for root, _, files in os.walk(data_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            print(f"Processing: {filename}")
            raw_text = extract_text_from_file(filepath)
            clean = clean_text(raw_text)
            outfile.write(clean + '\n')

print("All content written to llm.txt")

with open(ouput_dir, 'r', encoding='utf-8') as file:
    lines = file.readlines()
    # Print the first 20 lines
    for line in lines[:1000]:
        print(line.strip())