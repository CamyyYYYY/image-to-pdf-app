import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pillow_heif
import os

# 🔥 Enable HEIC support
pillow_heif.register_heif_opener()

MAX_IMAGES = 30

class ImgToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image → PDF Converter (HEIC Supported)")
        self.root.geometry("400x250")

        self.images = []

        tk.Label(root, text="Select up to 30 images", font=("Arial", 14)).pack(pady=10)

        tk.Button(root, text="Select Images", command=self.select_images, width=20).pack(pady=5)
        tk.Button(root, text="Convert to PDF", command=self.convert_to_pdf, width=20).pack(pady=5)

        self.status = tk.Label(root, text="No images selected", fg="gray")
        self.status.pack(pady=10)

    def select_images(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp *.heic")]
        )

        if not files:
            return

        if len(files) > MAX_IMAGES:
            messagebox.showerror("Error", f"Max {MAX_IMAGES} images allowed.")
            return

        self.images = files
        self.status.config(text=f"{len(files)} images selected")

    def convert_to_pdf(self):
        if not self.images:
            messagebox.showerror("Error", "No images selected")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not save_path:
            return

        try:
            pil_images = []

            for file in self.images:
                img = Image.open(file)

                # Convert to RGB (required for PDF)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                else:
                    img = img.convert("RGB")

                pil_images.append(img)

            first = pil_images[0]
            rest = pil_images[1:]

            first.save(save_path, save_all=True, append_images=rest)

            messagebox.showinfo("Success", "PDF created successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ImgToPDFApp(root)
    root.mainloop()