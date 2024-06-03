from flask import Flask, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
import os
from utils import analyze_image, compare_images
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # 16MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///image_analysis.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class ImageResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result = analyze_image(filepath)
            new_result = ImageResult(filename=filename, result=result)
            db.session.add(new_result)
            db.session.commit()
            return render_template('result.html', result=result, image_url=filename)
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/history')
def history():
    results = ImageResult.query.order_by(ImageResult.timestamp.desc()).all()
    return render_template('history.html', results=results)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if len(files) != 2:
            return redirect(request.url)
        filenames = []
        for file in files:
            if file.filename == '':
                return redirect(request.url)
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filenames.append(filename)
        diff_image_path = compare_images(filenames[0], filenames[1])
        return render_template('compare_result.html', diff_image_path=diff_image_path)
    return render_template('compare.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True)
