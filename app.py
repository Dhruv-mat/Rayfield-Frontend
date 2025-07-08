from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import csv
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# CSV file to store user credentials
CSV_FILE = 'users.csv'
PARAMETERS_FILE = 'parameters.csv'

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
            writer.writerow(['user_email', 'timestamp', 'parameter_name', 'parameter_value'])

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

def save_parameter(user_email, parameter_name, parameter_value):
    """Save parameter to CSV file"""
    with open(PARAMETERS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_email, datetime.now().isoformat(), parameter_name, parameter_value])

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

@app.route('/save-parameters', methods=['POST'])
def save_parameters():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_email = session['user_email']
    
    # Save each parameter
    for param_name, param_value in data.items():
        if param_value:  # Only save non-empty values
            save_parameter(user_email, param_name, param_value)
    
    return jsonify({'success': True, 'message': 'Parameters saved successfully'})

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', user_email=session['user_email'])

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file and file.filename.endswith('.csv'):
        # Save uploaded file
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filename = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        return jsonify({'success': True, 'message': f'File uploaded successfully as {filename}'})
    else:
        return jsonify({'success': False, 'message': 'Please upload a valid CSV file'}), 400

if __name__ == '__main__':
    init_csv()
    app.run(debug=True, host='0.0.0.0', port=5000)