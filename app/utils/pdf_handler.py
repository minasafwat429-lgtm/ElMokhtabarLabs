import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_report(file, test_id):
    if not file:
        return None
    
    filename = secure_filename(f"report_{test_id}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename

def get_report_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
