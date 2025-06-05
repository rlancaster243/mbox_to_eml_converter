import streamlit as st
import mailbox
import email
import re
import os
import tempfile
import zipfile
from io import BytesIO
import email.header

def sanitize_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', '_', text)
    return text.strip()

def mbox_to_eml_bytesio(mbox_file, mbox_name):
    """Convert mbox file-like object to a dict of {filename: BytesIO}."""
    mbox_path = tempfile.mktemp(suffix='.mbox')
    with open(mbox_path, 'wb') as f:
        f.write(mbox_file.getbuffer())
    mbox = mailbox.mbox(mbox_path)
    files = {}
    for i, msg in enumerate(mbox, 1):
        subject = msg.get('subject', 'No_Subject')
        subject = email.header.decode_header(subject)
        subject = ''.join([
            (t[0].decode(t[1] or 'utf8') if isinstance(t[0], bytes) else t[0])
            for t in subject
        ])
        subject = sanitize_filename(subject)[:50]
        filename = f"{mbox_name}_{i:04d}_{subject}.eml"
        eml_bytes = bytes(msg)
        files[filename] = eml_bytes
    os.remove(mbox_path)
    return files

st.title("Bulk MBOX to EML Converter (with Zip Download)")

uploaded_files = st.file_uploader(
    "Upload one or more .mbox files",
    type=["mbox"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Convert & Download as Zip"):
        with BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for mbox_file in uploaded_files:
                    mbox_name = os.path.splitext(mbox_file.name)[0]
                    st.write(f"Processing: {mbox_file.name}")
                    eml_files = mbox_to_eml_bytesio(mbox_file, mbox_name)
                    for fname, fbytes in eml_files.items():
                        zipf.writestr(fname, fbytes)
            zip_buffer.seek(0)
            st.success(f"Done! {len(uploaded_files)} mbox file(s) processed.")
            st.download_button(
                label="Download All EMLs as Zip",
                data=zip_buffer,
                file_name="mbox_eml_exports.zip",
                mime="application/zip"
            )
