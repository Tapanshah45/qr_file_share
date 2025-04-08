import tkinter as tk
from tkinter import filedialog
import requests
import qrcode
from PIL import Image, ImageTk

BACKEND_URL = "https://qr-file-share-2.onrender.com/upload"

def upload_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    try:
        with open(file_path, 'rb') as f:
            response = requests.post(BACKEND_URL, files={'file': f})
        
        print("Status Code:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            data = response.json()
            file_url = data['file_url']
            generate_qr(file_url)
        else:
            result_label.config(text=f"Upload failed: {response.status_code}")
    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

def generate_qr(link):
    qr_img = qrcode.make(link)
    qr_img = qr_img.resize((200, 200))
    img = ImageTk.PhotoImage(qr_img)
    qr_label.config(image=img)
    qr_label.image = img
    result_label.config(text="Scan QR to download!")

# GUI Setup
root = tk.Tk()
root.title("QR File Sharer")

upload_btn = tk.Button(root, text="Upload File", command=upload_file)
upload_btn.pack(pady=10)

qr_label = tk.Label(root)
qr_label.pack(pady=10)

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
