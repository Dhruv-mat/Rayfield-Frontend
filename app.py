from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import csv
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configure Flask for large file uploads
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# CSV file to store user credentials
CSV_FILE = 'users.csv'
PARAMETERS_FILE = 'parameters.csv'
UPLOADS_FOLDER = 'uploads'

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['email', 'password_hash', 'created_at'])
            # Add a default admin user (email: admin@rayfield.com, password: admin123)
            writer.writerow(['admin@rayfield.com', hash_password('admin123'), datetime.now().isoformat()])
    
    # Initialize parameters CSV file
    if not os.path.exists(PARAMETERS_FILE):
        with open(PARAMETERS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user_email', 'timestamp', 'filename', 'location', 'unit', 'source_type'])
    
    # Create uploads folder
    if not os.path.exists(UPLOADS_FOLDER):
        os.makedirs(UPLOADS_FOLDER)

def verify_user(email, password):
    """Verify user credentials against CSV file"""
    if not os.path.exists(CSV_FILE):
        return False
    
    password_hash = hash_password(password)
    
    with open(CSV_FILE, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email and row['password_hash'] == password_hash:
                return True
    return False

def save_upload_parameters(user_email, filename, location, unit, source_type):
    """Save parameter to CSV file"""
    with open(PARAMETERS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_email, datetime.now().isoformat(), filename, location, unit, source_type])

@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if verify_user(email, password):
        session['user_email'] = email
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/upload-data', methods=['POST'])
def upload_data():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Check if file is present
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    file = request.files['file']
    location = request.form.get('location')
    unit = request.form.get('unit')
    source_type = request.form.get('source_type')
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not all([location, unit, source_type]):
        return jsonify({'success': False, 'message': 'Please fill in all parameters'}), 400
    
    if file and file.filename.endswith('.csv'):
                # Validate file size (optional - Flask already handles MAX_CONTENT_LENGTH)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > 400 * 1024 * 1024:  # 400MB limit
                return jsonify({'success': False, 'message': 'File too large. Maximum size is 400MB'}), 400
            
            # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOADS_FOLDER, filename)
        
            # Save file in chunks for large files
            try:
                file.save(file_path)
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error saving file: {str(e)}'}), 500
        
            # Save parameters
        save_upload_parameters(session['user_email'], filename, location, unit, source_type)
        
            # Get file info for response
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            return jsonify({
                'success': True, 
                'message': f'Large CSV file ({file_size_mb}MB) uploaded successfully with parameters'
            })
        else:
        return jsonify({'success': False, 'message': 'Please upload a valid CSV file'}), 400
    
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', user_email=session['user_email'])

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_csv()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)