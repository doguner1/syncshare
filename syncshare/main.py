import sys
import subprocess
import threading
import requests
import time
import qrcode
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit, QLabel,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import os

FLASK_CMD = ["python", "app.py"]
NGROK_CMD = [r"C:\\Users\\qwerty\\Downloads\\ngrok-v3-stable-windows-amd64\\ngrok.exe", "http", "8000"]

class SyncShareApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SyncShare Desktop")
        self.setFixedSize(600, 600)
        self.setStyleSheet("background-color: #0f1e2e; color: #d6eaff; font-family: Segoe UI;")

        self.flask_process = None
        self.ngrok_process = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # QR Code Area
        self.qr_label = QLabel("QR Kodu")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.qr_label)

        # Gelen Metin Alanı
        self.received_label = QLabel("Gelen Mesaj:")
        layout.addWidget(self.received_label)

        self.received_text = QTextEdit()
        self.received_text.setReadOnly(True)
        self.received_text.setFixedHeight(80)
        self.received_text.setStyleSheet("background-color: #1a2e42; color: #d6eaff;")
        layout.addWidget(self.received_text)

        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.clicked.connect(self.update_received_text)
        layout.addWidget(self.refresh_btn)
        refresh_copy_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("Kopyala")
        self.copy_btn.clicked.connect(self.copy_received_text)
        refresh_copy_layout.addWidget(self.copy_btn)
        layout.addLayout(refresh_copy_layout)

        # Text Input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Buraya metin yaz veya yapıştır...")
        self.text_input.setEnabled(False)
        layout.addWidget(self.text_input)

        # Send Button
        self.send_btn = QPushButton("Gönder")
        self.send_btn.setEnabled(False)
        self.send_btn.clicked.connect(self.send_text)
        layout.addWidget(self.send_btn)

        # File Upload
        self.upload_btn = QPushButton("Dosya Seç ve Yükle")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_btn)

        # Control Buttons
        ctrl_layout = QHBoxLayout()

        self.start_btn = QPushButton("Sistemi Başlat")
        self.start_btn.clicked.connect(self.start_services)
        ctrl_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.clicked.connect(self.stop_services)
        ctrl_layout.addWidget(self.stop_btn)

        self.goto_btn = QPushButton("Siteyi Aç")
        self.goto_btn.clicked.connect(self.open_site)
        ctrl_layout.addWidget(self.goto_btn)

        layout.addLayout(ctrl_layout)
        self.setLayout(layout)
        
    def copy_received_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.received_text.toPlainText())

    def start_services(self):
        self.flask_process = subprocess.Popen(FLASK_CMD)
        time.sleep(2)
        self.ngrok_process = subprocess.Popen(NGROK_CMD)

        time.sleep(3)
        try:
            tunnel_info = requests.get("http://localhost:4040/api/tunnels").json()
            public_url = tunnel_info['tunnels'][0]['public_url']
            self.generate_qr(public_url)
            self.public_url = public_url

            self.text_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.upload_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Ngrok bağlantısı alınamadı: {e}")

    def stop_services(self):
        if self.flask_process:
            self.flask_process.terminate()
        if self.ngrok_process:
            self.ngrok_process.terminate()
        self.text_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.qr_label.setPixmap(QPixmap())

    def open_site(self):
        import webbrowser
        if hasattr(self, 'public_url'):
            webbrowser.open(self.public_url)
        else:
            QMessageBox.information(self, "Bilgi", "Site henüz başlatılmadı.")

    def generate_qr(self, url):
        img = qrcode.make(url)
        img_path = "qr_temp.png"
        img.save(img_path)
        image = QImage(img_path)
        self.qr_label.setPixmap(QPixmap.fromImage(image).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        os.remove(img_path)

    def send_text(self):
        text = self.text_input.toPlainText()
        try:
            requests.post(f"{self.public_url}/", data={"text": text})
        except:
            QMessageBox.warning(self, "Bağlantı Hatası", "Metin gönderilemedi.")

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç")
        if file_path:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                try:
                    requests.post(f"{self.public_url}/", files=files)
                except:
                    QMessageBox.warning(self, "Bağlantı Hatası", "Dosya gönderilemedi.")

    def update_received_text(self):
        if hasattr(self, 'public_url'):
            try:
                res = requests.get(f"{self.public_url}/get_text")
                if res.status_code == 200:
                    data = res.json()
                    self.received_text.setText(data.get("text", ""))
            except:
                pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SyncShareApp()
    window.show()
    sys.exit(app.exec())
