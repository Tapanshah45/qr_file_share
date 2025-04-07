import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
import os

# Change this to your actual deployed Flask server URL on Render
SERVER_URL = "https://your-render-app-name.onrender.com/upload"

class FileSharerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR File Sharer")

        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack()

        self.label = tk.Label(self.frame, text="Choose a file to upload and generate QR code")
        self.label.pack(pady=10)

        self.choose_btn = tk.Button(self.frame, text="Choose File", command=self.choose_file)
        self.choose_btn.pack(pady=5)

        self.qr_label = tk.Label(self.frame)
        self.qr_label.pack(pady=10)

        self.link_label = tk.Label(self.frame, fg="blue", cursor="hand2", wraplength=400)
        self.link_label.pack(pady=5)

        self.file_path = ""

    def choose_file(self):
        filetypes = [("Documents", "*.pdf *.doc *.docx *.txt *.xls *.xlsx *.ppt *.pptx *.csv *.zip")]
        self.file_path = filedialog.askopenfilename(title="Select File", filetypes=filetypes)

        if self.file_path:
            self.upload_file()

    def upload_file(self):
        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(SERVER_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.display_qr_and_link(data['qr_image'], data['link'])
            else:
                messagebox.showerror("Error", f"Upload failed: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {str(e)}")

    def display_qr_and_link(self, qr_url, download_link):
        # Download the QR image
        qr_response = requests.get(qr_url, stream=True)
        if qr_response.status_code == 200:
            with open("temp_qr.png", 'wb') as f:
                for chunk in qr_response:
                    f.write(chunk)

            img = Image.open("temp_qr.png")
            img = img.resize((250, 250))
            photo = ImageTk.PhotoImage(img)

            self.qr_label.configure(image=photo)
            self.qr_label.image = photo

            self.link_label.config(text=download_link)
            self.link_label.bind("<Button-1>", lambda e: self.root.clipboard_append(download_link))
            messagebox.showinfo("Success", "File uploaded!\nLink copied on click.")

        else:
            messagebox.showerror("Error", "Failed to fetch QR code")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSharerApp(root)
    root.mainloop()
