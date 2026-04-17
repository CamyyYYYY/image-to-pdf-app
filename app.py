from flask import Flask, request, render_template_string, send_file
from PIL import Image, ImageOps
import pillow_heif
from io import BytesIO
import uuid

app = Flask(__name__)
pillow_heif.register_heif_opener()

MAX_IMAGES = 30

HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Image to PDF Converter</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f6f7fb;
        }
        .box {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        }
        input, button {
            margin-top: 12px;
        }
        .error {
            color: red;
            margin-top: 15px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1>Image → PDF Converter</h1>
        <form method="POST" action="/convert" enctype="multipart/form-data">
            <input type="file" name="images" multiple accept="image/*,.heic,.heif" required><br>
            <input type="text" name="pdf_name" placeholder="PDF name" value="converted_images"><br>
            <button type="submit">Convert to PDF</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def safe_pdf_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "converted_images.pdf"

    cleaned = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
    if not cleaned:
        cleaned = f"converted_images_{uuid.uuid4().hex[:8]}"

    if not cleaned.lower().endswith(".pdf"):
        cleaned += ".pdf"

    return cleaned

def load_image_to_rgb(file_storage) -> Image.Image:
    img = Image.open(file_storage.stream)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML, error=None)

@app.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("images")
    pdf_name = safe_pdf_name(request.form.get("pdf_name", "converted_images"))

    valid_files = [f for f in files if f and f.filename.strip() != ""]

    if not valid_files:
        return render_template_string(HTML, error="No images selected.")

    if len(valid_files) > MAX_IMAGES:
        return render_template_string(HTML, error=f"You can upload up to {MAX_IMAGES} images only.")

    try:
        pil_images = [load_image_to_rgb(f) for f in valid_files]

        pdf_buffer = BytesIO()
        pil_images[0].save(
            pdf_buffer,
            format="PDF",
            save_all=True,
            append_images=pil_images[1:]
        )
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=pdf_name,
            mimetype="application/pdf"
        )

    except Exception as e:
        return render_template_string(HTML, error=f"Conversion failed: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)