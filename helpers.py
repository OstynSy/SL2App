import os
import platform
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

CONFIG_FILE = "sl2_config.json"


# ================= HELPERS =================
def get_downloads_folder():
    if platform.system() == "Windows":
        user_profile = os.environ.get("USERPROFILE")
        candidates = [
            os.path.join(user_profile, "Downloads"),
            os.path.join(user_profile, "OneDrive", "Downloads"),
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return user_profile

    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.exists(downloads):
        os.makedirs(downloads, exist_ok=True)
    return downloads


def sanitize_filename(text):
    return "".join(c for c in text if c not in r'\/:*?"<>|').strip()


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ================= PDF =================
def create_overlay(text):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(142, 607, text["insured"])
    c.drawString(153, 591, text["risk"])
    c.drawString(238, 560, text["coverage"])
    c.drawString(132, 424, text["month_year"])
    c.drawString(330, 424, text["month_year"])
    c.drawString(520, 424, text["month_year"])
    c.drawString(453, 57, text["date"])

    c.save()
    packet.seek(0)
    return packet


def write_on_pdf(input_pdf, output_pdf, overlay_stream):
    reader = PdfReader(input_pdf)
    overlay = PdfReader(overlay_stream)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == 0:
            page.merge_page(overlay.pages[0])
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)
