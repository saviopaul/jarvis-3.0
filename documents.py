"""
documents.py - Universal Document Parser for Jarvis 3.0

Parses and extracts text/data from:
- PDF (.pdf)
- Word Documents (.docx)
- Excel Spreadsheets (.xlsx, .xls)
- CSV / TSV (.csv, .tsv)
- Text, Code, JSON, Markdown (.txt, .md, .py, .js, .json, .html, .log, .yaml)
"""

import os
import io
import csv
import json
import logging
import requests

logger = logging.getLogger(__name__)

def parse_document(file_bytes: bytes, file_name: str) -> str:
    """Extracts text content from various document formats."""
    ext = os.path.splitext(file_name.lower())[1]
    
    try:
        # 1. Plain Text / Code / Markdown / JSON / Configs
        if ext in [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml", ".log", ".sql", ".sh", ".env", ".xml"]:
            return file_bytes.decode("utf-8", errors="ignore")

        # 2. CSV / TSV Files
        elif ext in [".csv", ".tsv"]:
            delimiter = "\t" if ext == ".tsv" else ","
            content = file_bytes.decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(content), delimiter=delimiter)
            rows = [", ".join(row) for row in list(reader)[:150]]  # Top 150 rows
            return f"CSV/TSV Data Preview ({file_name}):\n" + "\n".join(rows)

        # 3. PDF Files
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                text = ""
                for idx, page in enumerate(reader.pages[:30]):  # Up to 30 pages
                    extracted = page.extract_text()
                    if extracted:
                        text += f"\n--- Page {idx+1} ---\n" + extracted
                return text if text.strip() else "PDF contains scanned images with no selectable text."
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                return f"Error reading PDF: {str(e)}"

        # 4. Word Documents (.docx)
        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                return f"Word Document ({file_name}):\n\n" + "\n".join(paragraphs)
            except Exception as e:
                logger.error(f"DOCX extraction error: {e}")
                return f"Error reading Word document: {str(e)}"

        # 5. Excel Spreadsheets (.xlsx, .xls)
        elif ext in [".xlsx", ".xls"]:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
                output = f"Excel Spreadsheet ({file_name}):\n"
                for sheet_name in wb.sheetnames[:5]:  # Up to 5 sheets
                    sheet = wb[sheet_name]
                    output += f"\n📊 Sheet: {sheet_name}\n"
                    for row in sheet.iter_rows(values_only=True, max_row=100):
                        non_empty = [str(cell) for cell in row if cell is not None]
                        if non_empty:
                            output += " | ".join(non_empty) + "\n"
                return output
            except Exception as e:
                logger.error(f"Excel extraction error: {e}")
                return f"Error reading Excel file: {str(e)}"

        # 6. Fallback: Try decoding as raw text
        else:
            return file_bytes.decode("utf-8", errors="ignore")

    except Exception as e:
        return f"Could not extract text from {file_name}: {str(e)}"


def analyze_document_content(doc_text: str, file_name: str, caption_prompt: str = "") -> str:
    """Sends extracted document text to Gemini 2.5 Flash for deep analysis and insights."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return "Error: GEMINI_API_KEY not configured for document processing."

    default_prompt = (
        f"You are Jarvis 3.0, the user's trusted AI partner and analyst.\n"
        f"Carefully analyze this uploaded document ({file_name}).\n"
        f"Provide a structured summary, key metrics/findings, anomalies or patterns, "
        f"and 3 actionable next steps or recommendations."
    )
    prompt = caption_prompt if caption_prompt.strip() else default_prompt

    system_instruction = (
        "You are Jarvis 3.0, an expert document analyst, accountant, engineer, and advisor. "
        "Analyze documents accurately and concisely. Always provide 3 strategic options with a clear recommendation."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    payload = {
        "system_instruction": {"parts": {"text": system_instruction}},
        "contents": [
            {
                "parts": [
                    {"text": f"{prompt}\n\nDOCUMENT CONTENT:\n{doc_text[:50000]}"}
                ]
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=40)
        data = resp.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            return f"📄 *DOCUMENT ANALYSIS ({file_name})*\n\n" + data["candidates"][0]["content"]["parts"][0]["text"]
        return f"Document text extracted ({len(doc_text)} chars), but analysis failed."
    except Exception as e:
        return f"Document analysis error: {str(e)}"
