import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import os
import requests
import traceback
import qrcode
from PIL import Image, ImageTk
import threading
import tempfile
import pyzipper
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

# Backend
BACKEND_URL = "https://qr-file-share-2.onrender.com/upload"

THEMES = {
    "light": {"bg": "#f7f7f7", "fg": "#1e1e1e", "card": "#ffffff", "btn_bg": "#e6e6e6", "btn_fg": "#1e1e1e"},
    "dark": {"bg": "#1f1f1f", "fg": "#ffffff", "card": "#2c2c2c", "btn_bg": "#3a3a3a", "btn_fg": "#ffffff"}
}

current_theme = "light"
selected_files = []
zip_path = ""
privacy_mode = False

def apply_theme():
    theme = THEMES[current_theme]
    root.configure(bg=theme["bg"])
    card.configure(bg=theme["card"])
    label_title.configure(bg=theme["card"], fg=theme["fg"])
    label_file_info.configure(bg=theme["card"], fg=theme["fg"])
    result_label.configure(bg=theme["card"], fg=theme["fg"])
    qr_label.configure(bg=theme["card"])
    for btn in buttons:
        btn.configure(bg=theme["btn_bg"], fg=theme["btn_fg"], activebackground=theme["btn_bg"])
    upload_btn.configure(bg=theme["btn_bg"], fg=theme["fg"])
    theme_toggle.configure(bg=theme["bg"], fg=theme["fg"], activebackground=theme["bg"])
    privacy_toggle.configure(bg=theme["bg"], fg=theme["fg"], activebackground=theme["bg"])

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

def toggle_privacy_mode(event=None):
    global privacy_mode
    privacy_mode = not privacy_mode

    if privacy_mode:
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        label_file_info.config(text="🧊 Privacy Mode Activated")
        qr_label.config(image='')
        result_label.config(text="")
    else:
        overlay.place_forget()
        label_file_info.config(text=last_file_info)
        qr_label.config(image=qr_label.image if hasattr(qr_label, "image") else '')
        result_label.config(text=last_result)

def select_files():
    global selected_files, zip_path, last_file_info
    files = filedialog.askopenfilenames(title="Select Multiple Files")
    if files:
        selected_files = files
        zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name

        protect = messagebox.askyesno("Password Protect?", "Do you want to password protect the ZIP file?")
        if protect:
            password = simpledialog.askstring("Enter Password", "Enter a password for the ZIP file:", show='*')
            if not password:
                messagebox.showerror("Error", "Password required to encrypt file.")
                return
            with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(password.encode())
                for f in selected_files:
                    zf.write(f, arcname=os.path.basename(f))
        else:
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in selected_files:
                    zipf.write(f, arcname=os.path.basename(f))

        zip_size = os.path.getsize(zip_path)
        last_file_info = f"{len(selected_files)} files zipped ({round(zip_size / 1024 / 1024, 2)} MB)"
        label_file_info.config(text=last_file_info)
        result_label.config(text="")
        qr_label.config(image='')
        progress_bar['value'] = 0
        progress_bar.pack_forget()

def threaded_upload():
    upload_btn.config(state="disabled")
    result_label.config(text="Uploading...")
    progress_bar['value'] = 0
    progress_bar.pack(pady=(0, 10))

    try:
        if not selected_files or not os.path.exists(zip_path):
            messagebox.showerror("Error", "No files selected.")
            return

        total_size = os.path.getsize(zip_path)
        if total_size > 100 * 1024 * 1024:
            messagebox.showerror("Error", "ZIP file exceeds 100MB limit.")
            return

        with open(zip_path, 'rb') as f:
            encoder = MultipartEncoder(fields={'file': ('shared_files.zip', f, 'application/zip')})

            def monitor_callback(monitor):
                percent = (monitor.bytes_read / total_size) * 100
                progress_bar['value'] = percent
                progress_label.config(text=f"{int(percent)}% uploaded")
                root.update_idletasks()

            monitor = MultipartEncoderMonitor(encoder, monitor_callback)
            response = requests.post(BACKEND_URL, data=monitor, headers={'Content-Type': monitor.content_type})

        if response.status_code == 200:
            data = response.json()
            root.after(0, lambda: show_qr_code(data["file_url"]))
        else:
            root.after(0, lambda: messagebox.showerror("Upload Failed", f"{response.status_code}: {response.text}"))
    except Exception as e:
        traceback.print_exc()
        root.after(0, lambda: messagebox.showerror("Error", str(e)))
    finally:
        upload_btn.config(state="normal")
        progress_label.config(text="")

def upload_file():
    threading.Thread(target=threaded_upload).start()

def show_qr_code(link):
    global last_result
    result_label.config(text="Generating QR...")
    qr_img = qrcode.make(link)
    qr_img = qr_img.resize((200, 200))
    img = ImageTk.PhotoImage(qr_img)
    qr_label.config(image=img)
    qr_label.image = img
    last_result = "Scan QR to download"
    result_label.config(text=last_result)
    progress_bar.pack_forget()

def resize_upload_button(event=None):
    window_width = root.winfo_width()
    btn_width = int((window_width * 0.6) // 8)
    upload_btn.config(width=btn_width)

# GUI Setup
root = tk.Tk()
root.title("QR File Sharer")
root.geometry("460x620")
root.resizable(False, False)
root.bind("<Escape>", toggle_privacy_mode)

last_file_info = "No files selected."
last_result = ""

card = tk.Frame(root, bd=2, relief="flat", padx=20, pady=20)
card.pack(pady=20, fill="both", expand=True)

label_title = tk.Label(card, text="📁 QR File Sharer", font=("Segoe UI", 16, "bold"))
label_title.pack(pady=(0, 10))

button_select = tk.Button(card, text="📂 Select Files", command=select_files, font=("Segoe UI", 10))
button_select.pack(pady=(10, 10), ipadx=10, ipady=4)

label_file_info = tk.Label(card, text=last_file_info, font=("Segoe UI", 10), anchor="w", justify="left")
label_file_info.pack(pady=(0, 12))

qr_label = tk.Label(card)
qr_label.pack(pady=10)

result_label = tk.Label(card, text="", font=("Segoe UI", 10))
result_label.pack()

upload_btn = tk.Button(root, text="⏫ Upload Zipped Files", command=upload_file, font=("Segoe UI", 12, "bold"))
upload_btn.pack(pady=(5, 5), ipadx=10, ipady=6)
root.bind("<Configure>", resize_upload_button)
resize_upload_button()

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300)
progress_label = tk.Label(root, text="", font=("Segoe UI", 9))
progress_label.pack()
progress_bar.pack_forget()

# Theme + Privacy toggles
theme_toggle = tk.Button(root, text="🌓 Toggle Theme", command=toggle_theme, relief="flat", font=("Segoe UI", 9))
theme_toggle.pack(side="left", padx=20, pady=8)

privacy_toggle = tk.Button(root, text="🔒 Ice Mode", command=toggle_privacy_mode, relief="flat", font=("Segoe UI", 9))
privacy_toggle.pack(side="right", padx=20, pady=8)

# Frosted overlay
overlay = tk.Frame(root, bg="#000000")
overlay.place_forget()

buttons = [button_select]
apply_theme()

root.mainloop()
