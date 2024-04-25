from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'resume_templates'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    resume_templates = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', resume_templates=resume_templates)

@app.route('/view/<filename>', methods=['GET'])
def view_resume(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=False)

@app.route('/edit/<filename>', methods=['GET', 'POST'])
def edit_resume(filename):
    if request.method == 'POST':
        edited_pdf_data = request.form['edited_pdf']
        edited_pdf_bytes = base64.b64decode(edited_pdf_data.split(",")[1])
        edited_filename = filename.split('.')[0] + '_edited.pdf'
        edited_file_path = os.path.join(app.config['UPLOAD_FOLDER'], edited_filename)
        with open(edited_file_path, 'wb') as f:
            f.write(edited_pdf_bytes)
        return redirect(url_for('index'))
    return render_template('edit.html', filename=filename)

@app.route('/download/<filename>', methods=['GET'])
def download_resume(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        file = request.files['resume']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
