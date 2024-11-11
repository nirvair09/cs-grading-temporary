from flask import Flask, request, send_file, render_template
import os
from grading_logic import process_grading

app = Flask(__name__)

# Set the folder where files will be stored temporarily
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('home.html')  # Ensure you have a home.html file for file upload UI

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400

    if file:
        # Save the uploaded file to the server
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Process the grading logic and get the output file path
        output_file = process_grading(file_path)

        # Send the output file to the user for download
        return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
