from flask import Flask, request, send_file, render_template, make_response
from werkzeug.utils import secure_filename
import os
import zipfile
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_and_download(files):
    zip_buffer = zipfile.ZipFile('converted_files.zip', 'w')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            output_filename = f"{os.path.splitext(filename)[0]}_formato.txt"
            file_contents = convert_file(file)
            zip_buffer.writestr(output_filename, file_contents)
        else:
            return "Error: los archivos deben tener extensión .txt."
    zip_buffer.close()
    return send_file('converted_files.zip', as_attachment=True)

def convert_file(file):
    lines = file.read().decode('utf-8').splitlines()
    converted_data = []
    for line in lines:
        match = re.search(r'\d+(?=[^\d]*$)', line)
        if match:
            quantity = match.group(0)
        else:
            quantity = "No se encontró cantidad"
        barcode = line[:13].strip()
        description = re.sub(r'\d', '', line[13:-len(quantity)]).strip().replace(';', ' ').replace('  ', ' ').strip()
        converted_data.append(f"{barcode};{description};{quantity}")
    return '\n'.join(converted_data)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('file')
        if len(files) == 0:
            return "No se seleccionaron archivos."
        return convert_and_download(files)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3500)
