# Universal File Converter

This project provides a robust, easy-to-use file converter web app built with Streamlit and 100% pure Python libraries—**no system dependencies required**. It supports a wide variety of file formats and enables batch, drag-and-drop conversions directly in your browser. **Perfect for quick document, email, spreadsheet, notebook, and image conversions on any device.**

---

## 🚀 Features

- **Works on Streamlit Cloud—no special setup or OS permissions required**
- **Intuitive UI:** Choose input and output file types with dropdowns; only valid conversions are shown
- **Supports:**  
    - Text, Markdown, HTML conversions  
    - CSV, TSV, Excel conversions  
    - PDF to DOCX, XLSX, OCR text  
    - Word DOCX to TXT  
    - Image conversions (jpg, png, gif, etc.)  
    - Email (mbox <-> eml)  
    - Jupyter Notebooks <-> Python scripts  
- **Batch conversion** for images and emails (output is zipped)
- **Shows friendly errors for unsupported conversions**

---

## ⚡️ Live Demo

> _You can deploy this on [Streamlit Cloud]([https://share.streamlit.io/](https://mboxtoemlconverter-rkepxujhzktdhgwejw7wsq.streamlit.app/) instantly—no code changes required!_

---

## 🛠️ How to Run (Locally or in Streamlit Cloud)

1. **Clone this repository:**

    ```sh
    git clone https://github.com/your-username/universal-file-converter.git
    cd universal-file-converter
    ```

2. **Install dependencies (locally):**

    ```sh
    pip install -r requirements.txt
    ```

3. **Run the app (locally):**

    ```sh
    streamlit run app.py
    ```

4. **Or deploy on [Streamlit Cloud](https://share.streamlit.io/)**
    - Push to GitHub  
    - In Streamlit Cloud, click "New app" and select your repo

---

## 📝 Supported Conversions

| From    | To Supported               |
|---------|----------------------------|
| txt     | docx, md, html             |
| md      | html, txt                  |
| html    | txt, md                    |
| csv     | xlsx, txt                  |
| tsv     | xlsx, txt                  |
| xlsx    | csv, tsv, txt              |
| docx    | txt                        |
| pdf     | docx, xlsx, txt (OCR)      |
| jpg, png, bmp, gif, tiff, webp | (any other in this set) |
| mbox    | eml                        |
| eml     | mbox                       |
| py      | ipynb                      |
| ipynb   | py                         |

_Note: All conversions are handled by pure Python libraries, so no system-level dependencies are needed. Conversions such as DOCX→PDF or HTML→PDF are **not available** on Streamlit Cloud and will display a friendly error if attempted._

---

## 🧩 Requirements

- Python 3.8+
- See `requirements.txt` for all needed Python packages

---

## ⚠️ Limitations

- **DOCX→PDF, HTML→PDF, and similar conversions are NOT supported** on Streamlit Cloud or in this app, as they require system-level packages (LibreOffice, WeasyPrint, etc.).
- Some conversions (like PDF→DOCX or PDF→XLSX) depend on the complexity of the source file—results may vary, especially for scanned or poorly-formatted documents.
- **OCR requires Tesseract:** On Streamlit Cloud, Tesseract is available; for local use, you may need to [install Tesseract](https://github.com/tesseract-ocr/tesseract) separately if running PDF OCR.

---

## 🤝 Contributing

PRs welcome! Please file issues for bugs, feature requests, or new file types that are possible with pure Python.

---

## 📄 License

MIT License

---

## 🙏 Credits

Built with [Streamlit](https://streamlit.io/), [Pandas](https://pandas.pydata.org/), [pdf2docx](https://github.com/dothinking/pdf2docx), [pdfplumber](https://github.com/jsvine/pdfplumber), [pytesseract](https://github.com/madmaze/pytesseract), [Pillow](https://python-pillow.org/), and more.

---

### _Happy converting!_
