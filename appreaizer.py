import os
import io
import webbrowser
from threading import Timer
from flask import Flask, request, render_template_string, send_file
from PIL import Image

app = Flask(__name__)

# The visual webpage (HTML & CSS styling)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Resizer Tool</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; text-align: center; padding: 40px 20px; margin: 0; }
        .container { background: white; padding: 30px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 450px; width: 100%; }
        h1 { color: #333; margin-top: 0; }
        .form-group { margin-bottom: 20px; text-align: left; }
        label { display: block; font-weight: bold; margin-bottom: 8px; color: #555; }
        input[type="file"], input[type="number"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        button { background-color: #007BFF; color: white; padding: 14px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }
        button:hover { background-color: #0056b3; }
        .footer { font-size: 12px; color: #888; margin-top: 25px; border-top: 1px solid #eee; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖼️ Image Resizer</h1>
        <p style="color: #666; margin-bottom: 25px;">Resize your images locally. No files are uploaded to the internet.</p>
        
        <form action="/resize" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label>Select Image:</label>
                <input type="file" name="image" accept="image/*" required>
            </div>
            <div class="form-group">
                <label>Target Width (pixels):</label>
                <input type="number" name="width" placeholder="e.g. 800" required min="1">
            </div>
            <div class="form-group">
                <label>Target Height (pixels):</label>
                <input type="number" name="height" placeholder="e.g. 600" required min="1">
            </div>
            <button type="submit">Resize & Download</button>
        </form>
        
        <div class="footer">Runs entirely offline on your device.</div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/resize', methods=['POST'])
def resize():
    file = request.files.get('image')
    width = int(request.form.get('width'))
    height = int(request.form.get('height'))

    if not file:
        return "No file uploaded", 400

    try:
        # Read the uploaded image into memory
        img = Image.open(file.stream)
        
        # Keep original format (PNG, JPEG, etc.) or default to PNG
        img_format = img.format if img.format else 'PNG'
        
        # Resize using high-quality LANCZOS scaling
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Save the resized image directly to a byte buffer in memory
        img_io = io.BytesIO()
        resized_img.save(img_io, format=img_format)
        img_io.seek(0)
        
        # Generate new filename (e.g., photo_resized.jpg)
        filename, ext = os.path.splitext(file.filename)
        new_filename = f"{filename}_resized{ext}"
        
        # Send the file back to the browser for automatic download
        return send_file(img_io, mimetype=f'image/{img_format.lower()}', as_attachment=True, download_name=new_filename)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # The browser auto-opener (useful when running as a desktop .exe)
    Timer(1.5, open_browser).start()
    
    # Run the Flask app on localhost
    app.run(host="127.0.0.1", port=5000)
