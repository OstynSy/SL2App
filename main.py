import sys
import os
import platform
import subprocess
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QFormLayout
)
from PyQt6.QtCore import Qt

# ======= IMPORT YOUR EXISTING HELPERS =======
# These functions can be copied directly from your Tkinter version
from helpers import (
    create_overlay,
    write_on_pdf,
    load_config,
    save_config,
    get_downloads_folder,
    sanitize_filename,
)

CONFIG_FILE = "sl2_config.json"


class SL2Form(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SL‑2 Diligent Search Form")
        self.setFixedWidth(520)

        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
                color: #1f2937;
                background-color: #f9fafb;
            }
            QLabel {
                font-weight: 500;
                color: #4b5563;
                border: none;
            }
            QLineEdit, QComboBox {
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3b82f6;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                color: #374151;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)

        # ===== Header =====
        title = QLabel("SL‑2 Diligent Search Form")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        """)
        main_layout.addWidget(title)

        # ===== Form Layout =====
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(form)

        # ===== Template PDF =====
        self.template_input = QLineEdit(
            self.config.get("template_pdf", "")
        )
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_template)

        form.addRow("Template PDF", self.template_input)
        form.addRow("", browse_btn)

        # ===== Fields =====
        self.insured_input = QLineEdit()
        self.risk_input = QLineEdit()

        self.coverage_input = QComboBox()
        self.coverage_input.setEditable(True)
        self.coverage_input.addItems([
            "General Liability",
            "Excess Liability",
            "Pollution",
            "Commercial Property",
            "Package",
        ])

        today = datetime.today()
        if platform.system() == "Windows":
            month_year = today.strftime("%#m/%Y")
            current_date = today.strftime("%#m/%#d/%Y")
        else:
            month_year = today.strftime("%-m/%Y")
            current_date = today.strftime("%-m/%-d/%Y")

        self.month_year_input = QLineEdit(month_year)
        self.date_input = QLineEdit(current_date)

        form.addRow("Name of Insured", self.insured_input)
        form.addRow("Description of Risk", self.risk_input)
        form.addRow("Coverage Type", self.coverage_input)
        form.addRow("Policy Month & Year", self.month_year_input)
        form.addRow("Submission Date", self.date_input)

        # ===== Submit Button =====
        submit_btn = QPushButton("Create SL‑2 PDF")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 14px;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e3a8a;
            }
        """)

        submit_btn.clicked.connect(self.submit)
        main_layout.addWidget(submit_btn)

    # ===== Actions =====
    def browse_template(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Template PDF",
            "",
            "PDF Files (*.pdf)"
        )
        if path:
            self.template_input.setText(path)
            self.config["template_pdf"] = path
            save_config(self.config)

    def submit(self):
        template_pdf = self.template_input.text().strip()
        insured = self.insured_input.text().strip()
        risk = self.risk_input.text().strip()

        if not template_pdf or not os.path.exists(template_pdf):
            QMessageBox.critical(
                self,
                "Error",
                "Please select a valid SL‑2 template PDF."
            )
            return

        if not insured or not risk:
            QMessageBox.critical(
                self,
                "Error",
                "Insured name and risk description are required."
            )
            return

        downloads = get_downloads_folder()
        filename = (
            f"{sanitize_filename(insured)} - "
            f"{sanitize_filename(risk)} - SL2.pdf"
        )
        output_pdf = os.path.join(downloads, filename)

        data = {
            "insured": insured,
            "risk": risk,
            "coverage": self.coverage_input.currentText(),
            "month_year": self.month_year_input.text(),
            "date": self.date_input.text(),
        }

        try:
            overlay = create_overlay(data)
            write_on_pdf(template_pdf, output_pdf, overlay)

            QMessageBox.information(
                self,
                "Success",
                f"Saved to Downloads:\n{filename}"
            )

            if platform.system() == "Windows":
                os.startfile(output_pdf)
            elif platform.system() == "Darwin":
                subprocess.run(["open", output_pdf])
            else:
                subprocess.run(["xdg-open", output_pdf])

            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ===== App Entry Point =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SL2Form()
    window.show()
    sys.exit(app.exec())