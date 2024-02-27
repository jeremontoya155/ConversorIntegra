from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import re
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_and_download(files):
    converted_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_file_path)
            output_filename = f"{os.path.splitext(filename)[0]}_formato.txt"
            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            convert_file(input_file_path, output_file_path)
            converted_files.append(output_file_path)
        else:
            return "Error: los archivos deben tener extensión .txt."
    return converted_files

def convert_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()
        converted_data = []
        for line in lines:
            match = re.search(r'\d+(?=[^\d]*$)', line)
            if match:
                quantity = match.group(0)
            else:
                quantity = "No se encontró cantidad"
            barcode = line[:13]
            # Extraer solo letras para la descripción y reemplazar dobles ";" con uno solo
            description = re.sub(r'\d', '', line[13:-len(quantity)]).strip().replace(';', '').replace(' ', ' ')
            converted_data.append(f"{barcode};{description};{quantity}\n")
    with open(output_file_path, 'w') as output_file:
        for line in converted_data:
            output_file.write(line)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No se han cargado archivos."

        files = request.files.getlist('file')
        converted_files = convert_and_download(files)

        if isinstance(converted_files, list) and converted_files:
            zip_filename = 'converted_files.zip'
            with zipfile.ZipFile(zip_filename, 'w') as zip_file:
                for converted_file in converted_files:
                    zip_file.write(converted_file, os.path.basename(converted_file))
            return send_file(zip_filename, as_attachment=True)
        else:
            return converted_files

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=3500)
