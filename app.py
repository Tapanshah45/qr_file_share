from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import qrcode
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Replace with your actual local IP address
LOCAL_IP = "192.168.202.67"  # ← Replace this with your machine's local IP

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if file:
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Use local IP to generate downloadable link
        download_link = f"http://{LOCAL_IP}:5000/download/{filename}"

        # Generate QR code
        qr = qrcode.make(download_link)
        qr_path = os.path.join('static', f"{filename}.png")
        qr.save(qr_path)

        return render_template('download.html', qr_image=qr_path, link=download_link)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
