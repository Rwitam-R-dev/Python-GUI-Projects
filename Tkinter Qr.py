import tkinter as tk
import qrcode
from PIL import ImageTk, Image
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import pyperclip


def generate_qr_code():
    text = entry.get("1.0", tk.END).strip()

    if not text:
        qr_image = Image.new("RGB", (200, 200), color="white")
        qr_photo = ImageTk.PhotoImage(qr_image)
        label.config(image=qr_photo)
        label.image = qr_photo
        messagebox.showwarning("Warning", "Please enter a text for QR code generation.")
        return

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Use default error correction (L)
            box_size=10,
            border=4
        )
        qr.add_data(text)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")

        size = size_var.get()
        if size != 100:
            qr_image = resize_qr_code(qr_image, size)

        save_filename = save_filename_var.get()
        if save_filename:
            save_qr_image(qr_image, save_filename)

        qr_photo = ImageTk.PhotoImage(qr_image)
        label.config(image=qr_photo)
        label.image = qr_photo

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating QR code:\n{str(e)}")

def resize_qr_code(qr_image, size_percent):
    new_size = int(qr_image.size[0] * (size_percent / 100))
    resized_qr_image = qr_image.resize((new_size, new_size), Image.ANTIALIAS)
    return resized_qr_image

def save_qr_image(qr_image, filename):
    try:
        qr_image.save(filename)
        messagebox.showinfo("Information", f"QR code image saved as {filename}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the QR code image:\n{str(e)}")

def copy_qr_image():
    qr_image = label.image
    if qr_image:
        try:
            image = Image.fromarray(qr_image)
            image_bytes = image.tobytes()
            pyperclip.copy(image_bytes)
            messagebox.showinfo("Information", "QR code image has been copied to the clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while copying the QR code image:\n{str(e)}")
    else:
        messagebox.showwarning("Warning", "No QR code image to copy.")

def clear_text():
    entry.delete("1.0", tk.END)
    qr_image = Image.new("RGB", (200, 200), color="white")
    qr_photo = ImageTk.PhotoImage(qr_image)
    label.config(image=qr_photo)
    label.image = qr_photo

def on_entry_return(event):
    generate_qr_code()

window = tk.Tk()
window.title("QR Code Generator")

entry = tk.Text(window, height=5, wrap=tk.WORD)
entry.pack(padx=10, pady=10)

options_frame = ttk.LabelFrame(window, text="Options")
options_frame.pack(padx=10, pady=5)

size_label = ttk.Label(options_frame, text="Resize QR Code (%):")
size_label.grid(row=0, column=0, sticky="w")

size_var = tk.IntVar()
size_var.set(100)

size_scale = tk.Scale(options_frame, from_=10, to=200, variable=size_var, orient=tk.HORIZONTAL)
size_scale.grid(row=0, column=1, padx=10)

save_filename_label = ttk.Label(options_frame, text="Save Filename:")
save_filename_label.grid(row=1, column=0, sticky="w")

save_filename_var = tk.StringVar()
save_filename_entry = ttk.Entry(options_frame, textvariable=save_filename_var)
save_filename_entry.grid(row=1, column=1, padx=10)

generate_button = ttk.Button(window, text="Generate QR Code", command=generate_qr_code)
generate_button.pack(pady=10)

label = ttk.Label(window)
label.pack()

copy_image_button = ttk.Button(window, text="Copy QR Code Image", command=copy_qr_image)
copy_image_button.pack(pady=5)

clear_button = ttk.Button(window, text="Clear Text", command=clear_text)
clear_button.pack(pady=5)

entry.bind("<Return>", on_entry_return)

window.mainloop()
