from flask import Flask, send_from_directory, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Folders for images and results
IMAGE_FOLDER = "images"
XLSX_FOLDER = "output"
server_ip = "3.133.161.236"  # Set your public IP

@app.route('/list')
def listings():
    html_content = "<h2>Available Lists:</h2><ul>"
    html_content += f'<li><a href="/list_xlsx" target="_blank">List XLSX Files</a></li>'
    html_content += f'<li><a href="/list_raw_zip" target="_blank">List Raw ZIP Files</a></li>'
    html_content += f'<li><a href="/list_annotated_zip" target="_blank">List Annotated ZIP Files</a></li>'
    html_content += f'<li><a href="/list_cropped_zip" target="_blank">List Cropped ZIP Files</a></li>'
    html_content += "</ul>"
    return html_content

@app.route('/list_xlsx')
def list_xlsx():
    files = [f for f in os.listdir(XLSX_FOLDER) if f.endswith(".xlsx")]
    
    html_content = "<h2>Available XLSX Files:</h2><ul>"
    for f in files:
        url = f"http://{server_ip}:5000/download_xlsx/{f}"
        html_content += f'<li><a href="{url}" target="_blank">{f}</a></li>'
    html_content += "</ul>"
    return html_content

@app.route('/download_xlsx/<filename>')
def download_xlsx(filename):
    """Serve the requested XLSX file for download."""
    return send_from_directory(XLSX_FOLDER, filename)


@app.route('/list_raw_zip')
def list_raw_zip():
    zips = [f for f in os.listdir(IMAGE_FOLDER) if f.startswith("images_") and f.endswith(".zip")]
    html_content = "<h2>Available Raw Image ZIP Files:</h2><ul>"
    for z in zips:
        url = f"http://{server_ip}:5000/download_raw_zip/{z}"
        html_content += f'<li><a href="{url}" target="_blank">{z}</a></li>'
    html_content += "</ul>"
    return html_content

@app.route('/download_raw_zip/<filename>')
def download_raw_zip(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=True)

@app.route('/list_annotated_zip')
def list_annotated_zip():
    zips = [f for f in os.listdir(IMAGE_FOLDER) if f.startswith("annotated_") and f.endswith(".zip")]
    html_content = "<h2>Available Annotated ZIP Files:</h2><ul>"
    for z in zips:
        url = f"http://{server_ip}:5000/download_annotated_zip/{z}"
        html_content += f'<li><a href="{url}" target="_blank">{z}</a></li>'
    html_content += "</ul>"
    return html_content

@app.route('/download_annotated_zip/<filename>')
def download_annotated_zip(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=True)

@app.route('/list_cropped_zip')
def list_cropped_zip():
    zips = [f for f in os.listdir(IMAGE_FOLDER) if f.startswith("cropped_") and f.endswith(".zip")]
    html_content = "<h2>Available Cropped ZIP Files:</h2><ul>"
    for z in zips:
        url = f"http://{server_ip}:5000/download_cropped_zip/{z}"
        html_content += f'<li><a href="{url}" target="_blank">{z}</a></li>'
    html_content += "</ul>"
    return html_content

@app.route('/download_cropped_zip/<filename>')
def download_cropped_zip(filename):
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
