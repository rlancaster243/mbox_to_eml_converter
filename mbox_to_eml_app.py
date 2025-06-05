import streamlit as st
import tempfile
import os
import io
import pandas as pd
from PIL import Image
import markdown as md
import nbformat
import mailbox
import zipfile

# --- Try/except for optional/large libraries ---
try:
    from pdf2docx import Converter
    import pdfplumber
    import pdf2image
    import pytesseract
    import weasyprint
    import mammoth
    import openpyxl
except ImportError:
    pass

# ---- Conversion Matrix ----
CONVERSION_MATRIX = {
    "txt": ["pdf", "docx", "md", "html"],
    "md": ["html", "pdf", "txt"],
    "html": ["pdf", "txt", "md"],
    "csv": ["xlsx", "ods", "pdf", "txt"],
    "tsv": ["xlsx", "csv", "pdf", "txt"],
    "xlsx": ["csv", "tsv", "ods", "pdf"],
    "ods": ["xlsx", "csv", "pdf"],
    "docx": ["pdf", "txt"],
    "odt": ["pdf", "docx"],
    "pdf": ["txt", "docx", "xlsx", "jpg", "png"],
    "jpg": ["png", "bmp", "gif", "tiff", "webp", "pdf"],
    "png": ["jpg", "bmp", "gif", "tiff", "webp", "pdf"],
    "bmp": ["jpg", "png", "gif", "tiff", "webp"],
    "gif": ["jpg", "png", "bmp", "tiff", "webp"],
    "tiff": ["jpg", "png", "bmp", "gif", "webp"],
    "webp": ["jpg", "png", "bmp", "gif", "tiff"],
    "mp3": ["wav", "ogg", "flac", "aac"],
    "wav": ["mp3", "ogg", "flac", "aac"],
    "ogg": ["mp3", "wav", "flac", "aac"],
    "flac": ["mp3", "wav", "ogg", "aac"],
    "aac": ["mp3", "wav", "ogg", "flac"],
    "mp4": ["avi", "mov", "mkv", "webm"],
    "avi": ["mp4", "mov", "mkv", "webm"],
    "mov": ["mp4", "avi", "mkv", "webm"],
    "mkv": ["mp4", "avi", "mov", "webm"],
    "webm": ["mp4", "avi", "mov", "mkv"],
    "zip": ["extract"],
    "tar": ["extract"],
    "gz": ["extract"],
    "7z": ["extract"],
    "mbox": ["eml"],
    "eml": ["mbox"],
    "py": ["ipynb"],
    "ipynb": ["py"],
}

EXTENSION_LABELS = {
    "txt": "Plain Text",
    "md": "Markdown",
    "html": "HTML",
    "csv": "CSV",
    "tsv": "TSV",
    "xlsx": "Excel (XLSX)",
    "ods": "OpenDocument Spreadsheet (ODS)",
    "docx": "Word (DOCX)",
    "odt": "OpenDocument Text (ODT)",
    "pdf": "PDF",
    "jpg": "JPEG Image",
    "png": "PNG Image",
    "bmp": "Bitmap Image",
    "gif": "GIF Image",
    "tiff": "TIFF Image",
    "webp": "WEBP Image",
    "mp3": "MP3 Audio",
    "wav": "WAV Audio",
    "ogg": "OGG Audio",
    "flac": "FLAC Audio",
    "aac": "AAC Audio",
    "mp4": "MP4 Video",
    "avi": "AVI Video",
    "mov": "MOV Video",
    "mkv": "MKV Video",
    "webm": "WEBM Video",
    "zip": "ZIP Archive",
    "tar": "TAR Archive",
    "gz": "GZip Archive",
    "7z": "7-Zip Archive",
    "mbox": "MBOX Email Mailbox",
    "eml": "EML Email Message",
    "py": "Python Script",
    "ipynb": "Jupyter Notebook",
    "extract": "Extract Files",
}

# -------- Conversion Functions --------

# PDF to DOCX
def pdf_to_docx(pdf_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
        tf.write(pdf_bytes)
        tf.flush()
        docx_path = tf.name.replace('.pdf', '.docx')
        cv = Converter(tf.name)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
    with open(docx_path, 'rb') as f:
        output_bytes = f.read()
    os.remove(docx_path)
    return output_bytes

# DOCX to PDF
def docx_to_pdf(docx_bytes):
    import mammoth
    import weasyprint
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tf:
        tf.write(docx_bytes)
        tf.flush()
        with open(tf.name, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
        html = result.value
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    os.remove(tf.name)
    return pdf_bytes

# PDF to XLSX
def pdf_to_xlsx(pdf_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tf:
        tf.write(pdf_bytes)
        tf.flush()
        with pdfplumber.open(tf.name) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    all_tables.append(table)
        if not all_tables:
            return None
        writer = pd.ExcelWriter(tf.name.replace('.pdf', '.xlsx'))
        for i, table in enumerate(all_tables):
            df = pd.DataFrame(table[1:], columns=table[0])
            df.to_excel(writer, index=False, sheet_name=f"Table_{i+1}")
        writer.close()
        with open(tf.name.replace('.pdf', '.xlsx'), 'rb') as f:
            xlsx_bytes = f.read()
        os.remove(tf.name.replace('.pdf', '.xlsx'))
    return xlsx_bytes

# PDF to OCR text
def pdf_to_text_ocr(pdf_bytes):
    from pdf2image import convert_from_bytes
    import pytesseract
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for i, img in enumerate(images):
        text += f"\n--- PAGE {i+1} ---\n"
        text += pytesseract.image_to_string(img)
    return text

# PY to IPYNB
def py_to_ipynb(py_bytes):
    code = py_bytes.decode('utf-8')
    notebook = nbformat.v4.new_notebook()
    notebook.cells.append(nbformat.v4.new_code_cell(code))
    return nbformat.writes(notebook).encode('utf-8')

# IPYNB to PY
def ipynb_to_py(ipynb_bytes):
    notebook = nbformat.reads(ipynb_bytes.decode('utf-8'), as_version=4)
    code = ""
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            code += cell.source + '\n\n'
    return code.encode('utf-8')

# mbox to eml
def mbox_to_eml_files(mbox_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mbox') as tf:
        tf.write(mbox_bytes)
        tf.flush()
        mbox = mailbox.mbox(tf.name)
        eml_files = []
        for i, msg in enumerate(mbox, 1):
            eml_bytes = bytes(msg)
            eml_files.append((f"{i:04d}.eml", eml_bytes))
    os.remove(tf.name)
    return eml_files

# eml to mbox
def eml_files_to_mbox(eml_file_list):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mbox') as tf:
        mbox = mailbox.mbox(tf.name)
        for name, eml_bytes in eml_file_list:
            msg = mailbox.mboxMessage(eml_bytes)
            mbox.add(msg)
        mbox.flush()
        with open(tf.name, 'rb') as mbox_file:
            mbox_bytes = mbox_file.read()
    os.remove(tf.name)
    return mbox_bytes

# Simple text conversions
def txt_to_pdf(txt_bytes):
    from fpdf import FPDF
    text = txt_bytes.decode('utf-8')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    output = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(output.name)
    with open(output.name, "rb") as f:
        result = f.read()
    os.remove(output.name)
    return result

def txt_to_docx(txt_bytes):
    from docx import Document
    text = txt_bytes.decode('utf-8')
    doc = Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    output = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(output.name)
    with open(output.name, "rb") as f:
        result = f.read()
    os.remove(output.name)
    return result

def md_to_html(md_bytes):
    text = md_bytes.decode('utf-8')
    html = md.markdown(text)
    return html.encode('utf-8')

def html_to_pdf(html_bytes):
    import weasyprint
    html = html_bytes.decode('utf-8')
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    return pdf_bytes

# Add more as needed: CSV/TSV/XLSX, Image, Audio, Archive, etc.

# ---- Streamlit UI ----

st.title("Universal File Converter (Python-powered, OCR, .py⇄.ipynb, PDF-DOCX-Excel, Email, Images, Archives, & More)")

from_ext = st.selectbox(
    "Convert FROM",
    options=list(CONVERSION_MATRIX.keys()),
    format_func=lambda x: EXTENSION_LABELS.get(x, x)
)
to_ext_options = CONVERSION_MATRIX[from_ext]
to_ext = st.selectbox(
    "Convert TO",
    options=to_ext_options,
    format_func=lambda x: EXTENSION_LABELS.get(x, x) if x in EXTENSION_LABELS else x
)

accept_multiple = from_ext in [
    "zip", "tar", "gz", "7z", "mbox", "eml", "jpg", "png", "bmp", "gif", "tiff", "webp",
    "mp3", "wav", "ogg", "flac", "aac", "mp4", "avi", "mov", "mkv", "webm"
]
uploaded_files = st.file_uploader(
    f"Upload .{from_ext} file(s)",
    type=[from_ext],
    accept_multiple_files=accept_multiple
)

st.info(f"Selected: {EXTENSION_LABELS.get(from_ext, from_ext)} → {EXTENSION_LABELS.get(to_ext, to_ext)}")

if uploaded_files and st.button("Convert & Download"):
    try:
        # PDF -> DOCX
        if from_ext == "pdf" and to_ext == "docx":
            output_bytes = pdf_to_docx(uploaded_files[0].read())
            st.download_button("Download DOCX", data=output_bytes, file_name="converted.docx")

        # PDF -> XLSX
        elif from_ext == "pdf" and to_ext == "xlsx":
            output_bytes = pdf_to_xlsx(uploaded_files[0].read())
            st.download_button("Download XLSX", data=output_bytes, file_name="converted.xlsx")

        # PDF OCR
        elif from_ext == "pdf" and to_ext == "txt":
            output_text = pdf_to_text_ocr(uploaded_files[0].read())
            st.download_button("Download OCR Text", data=output_text.encode(), file_name="ocr_output.txt")

        # PY -> IPYNB
        elif from_ext == "py" and to_ext == "ipynb":
            output_bytes = py_to_ipynb(uploaded_files[0].read())
            st.download_button("Download Notebook", data=output_bytes, file_name="converted.ipynb")

        # IPYNB -> PY
        elif from_ext == "ipynb" and to_ext == "py":
            output_bytes = ipynb_to_py(uploaded_files[0].read())
            st.download_button("Download Script", data=output_bytes, file_name="converted.py")

        # mbox -> eml
        elif from_ext == "mbox" and to_ext == "eml":
            eml_files = mbox_to_eml_files(uploaded_files[0].read())
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for fname, eml_bytes in eml_files:
                    zipf.writestr(fname, eml_bytes)
            zip_buffer.seek(0)
            st.download_button("Download EML Zip", data=zip_buffer, file_name="emls.zip")

        # eml -> mbox
        elif from_ext == "eml" and to_ext == "mbox":
            eml_file_list = [(f.name, f.read()) for f in uploaded_files]
            mbox_bytes = eml_files_to_mbox(eml_file_list)
            st.download_button("Download MBOX", data=mbox_bytes, file_name="converted.mbox")

        # txt -> pdf
        elif from_ext == "txt" and to_ext == "pdf":
            output_bytes = txt_to_pdf(uploaded_files[0].read())
            st.download_button("Download PDF", data=output_bytes, file_name="converted.pdf")

        # txt -> docx
        elif from_ext == "txt" and to_ext == "docx":
            output_bytes = txt_to_docx(uploaded_files[0].read())
            st.download_button("Download DOCX", data=output_bytes, file_name="converted.docx")

        # md -> html
        elif from_ext == "md" and to_ext == "html":
            output_bytes = md_to_html(uploaded_files[0].read())
            st.download_button("Download HTML", data=output_bytes, file_name="converted.html")

        # html -> pdf
        elif from_ext == "html" and to_ext == "pdf":
            output_bytes = html_to_pdf(uploaded_files[0].read())
            st.download_button("Download PDF", data=output_bytes, file_name="converted.pdf")

        else:
            st.warning("This conversion is not yet implemented.")
    except Exception as e:
        st.error(f"Error during conversion: {e}")

with st.expander("Supported File Types and Conversion Matrix"):
    st.write(CONVERSION_MATRIX)
