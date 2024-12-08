from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
import zipfile
from excel_to_sql import create_database

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {'sql'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_zip_file(excel_dir):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = os.path.join(app.config['UPLOAD_FOLDER'], f'excel_files_{timestamp}.zip')
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(excel_dir):
            for file in files:
                if file.endswith('.xlsx'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
    
    return zip_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a .sql file'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create output directory
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'excel_output')
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                os.remove(os.path.join(output_dir, file))
        else:
            os.makedirs(output_dir)
        
        # Convert SQL to Excel
        create_database(filepath)
        
        # Create ZIP file of Excel files
        zip_file = create_zip_file(output_dir)
        
        # Clean up
        os.remove(filepath)
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))
        os.rmdir(output_dir)
        
        # Send ZIP file
        return send_file(
            zip_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='excel_files.zip'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
