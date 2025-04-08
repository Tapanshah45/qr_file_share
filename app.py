from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

# Limit file size to 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Disallow only mp4 files
def is_allowed(filename):
    return not filename.lower().endswith('.mp4')

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return "QR File Share Backend Running!"

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)

    if not is_allowed(filename):
        return jsonify({'error': 'MP4 files are not allowed.'}), 400

    try:
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        file_url = request.url_root + 'download/' + filename
        return jsonify({'file_url': file_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Open file in memory
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Prepare response first
        response = send_file(
            BytesIO(file_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename
        )

        # Delete the file after sending
        os.remove(file_path)
        print(f"Deleted after download: {filename}")
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/generate_qr/<filename>")
def generate_qr(filename):
    file_url = request.url_root + 'download/' + filename
    qr_img = qrcode.make(file_url)

    # Save QR code to in-memory stream
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
