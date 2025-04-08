import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import qrcode
from PIL import Image, ImageTk
import io

# Replace this with your deployed Flask URL on Render
BACKEND_URL = "https://qr-file-share-2.onrender.com/upload"  # Add /upload route

def upload_file():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(BACKEND_URL, files=files)
            response.raise_for_status()
            file_url = response.json().get('file_url')
            if file_url:
                generate_qr(file_url)
            else:
                messagebox.showerror("Error", "No file URL returned.")
    except Exception as e:
        messagebox.showerror("Upload Failed", str(e))

def generate_qr(data):
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    qr_img = Image.open(buffer)
    qr_img = qr_img.resize((250, 250))
    tk_img = ImageTk.PhotoImage(qr_img)

    qr_label.config(image=tk_img)
    qr_label.image = tk_img

    messagebox.showinfo("Success", "QR Code generated for file download!")

# GUI Setup
root = tk.Tk()
root.title("QR File Share")
root.geometry("400x400")

upload_btn = tk.Button(root, text="Upload File", command=upload_file, bg="black", fg="white", font=("Arial", 12))
upload_btn.pack(pady=20)

qr_label = tk.Label(root)
qr_label.pack()

root.mainloop()
