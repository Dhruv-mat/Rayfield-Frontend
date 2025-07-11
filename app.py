from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import csv
import os
import hashlib
from datetime import datetime
import subprocess
import sys

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
        print(f"CSV file {CSV_FILE} does not exist")
        return False
    
    password_hash = hash_password(password)
    print(f"Attempting login for email: {email}")
    print(f"Password hash: {password_hash}")
    
    with open(CSV_FILE, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(f"Checking row: email={row['email']}, stored_hash={row['password_hash']}")
            if row['email'] == email and row['password_hash'] == password_hash:
                print("Login successful!")
                return True
    print("Login failed - no matching credentials found")
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
            filename = file.filename  # Save with exact original filename
            file_path = os.path.join(UPLOADS_FOLDER, filename)
            
            # Save file in chunks for large files
            try:
                file.save(file_path)
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error saving file: {str(e)}'}), 500
            
            # Save parameters
            save_upload_parameters(session['user_email'], filename, location, unit, source_type)
            
            # Store upload info in session for analysis page
            session['last_upload'] = {
                'filename': filename,
                'original_filename': file.filename,
                'location': location,
                'unit': unit,
                'source_type': source_type,
                'file_size': round(file_size / (1024 * 1024), 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # Get file info for response
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            return jsonify({
                'success': True, 
                'message': f'CSV file ({file_size_mb}MB) uploaded successfully',
                'redirect': '/analysis'
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

# CSV file to store analysis parameters
ANALYSIS_PARAMETERS_FILE = 'analysis_parameters.csv'

def init_analysis_csv():
    """Initialize analysis parameters CSV file with headers if it doesn't exist"""
    if not os.path.exists(ANALYSIS_PARAMETERS_FILE):
        with open(ANALYSIS_PARAMETERS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user_email', 'timestamp', 'sensor_filename', 'num_solar_panels', 'anomaly_threshold', 'time_frame', 'expected_output'])

def save_analysis_parameters(user_email, sensor_filename, num_solar_panels, anomaly_threshold, time_frame, expected_output):
    """Save analysis parameters to CSV file"""
    with open(ANALYSIS_PARAMETERS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_email, datetime.now().isoformat(), sensor_filename, num_solar_panels, anomaly_threshold, time_frame, expected_output])

@app.route('/upload-sensor-data', methods=['POST'])
def upload_sensor_data():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        file = request.files['file']
        num_solar_panels = request.form.get('num_solar_panels')
        anomaly_threshold = request.form.get('anomaly_threshold')
        time_frame = request.form.get('time_frame')
        expected_output = request.form.get('expected_output')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not all([num_solar_panels, anomaly_threshold, time_frame, expected_output]):
            return jsonify({'success': False, 'message': 'Please fill in all parameters'}), 400
        
        if file and file.filename.endswith('.csv'):
            # Validate file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > 400 * 1024 * 1024:  # 400MB limit
                return jsonify({'success': False, 'message': 'File too large. Maximum size is 400MB'}), 400
            
            # Save uploaded file
            filename = file.filename  # Save with exact original filename
            file_path = os.path.join(UPLOADS_FOLDER, filename)
            
            # Save file
            try:
                file.save(file_path)
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error saving file: {str(e)}'}), 500
            
            # Save analysis parameters
            save_analysis_parameters(session['user_email'], filename, num_solar_panels, anomaly_threshold, time_frame, expected_output)
            
            # Update session with sensor data info
            session['sensor_upload'] = {
                'filename': filename,
                'original_filename': file.filename,
                'num_solar_panels': num_solar_panels,
                'anomaly_threshold': anomaly_threshold,
                'time_frame': time_frame,
                'expected_output': expected_output,
                'file_size': round(file_size / (1024 * 1024), 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # Get file info for response
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            return jsonify({
                'success': True, 
                'message': f'Sensor data CSV file ({file_size_mb}MB) uploaded successfully with analysis parameters',
                'redirect': '/loading'
            })
        else:
            return jsonify({'success': False, 'message': 'Please upload a valid CSV file'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500

@app.route('/analysis')
def analysis():
    if 'user_email' not in session:
        return redirect(url_for('index'))
    
    # Get last upload info from session
    upload_info = session.get('last_upload', {})
    sensor_info = session.get('sensor_upload', {})
    return render_template('analysis.html', user_email=session['user_email'], upload_info=upload_info, sensor_info=sensor_info)

@app.route('/loading')
def loading():
    if 'user_email' not in session:
        return redirect(url_for('index'))
    return render_template('loading.html', user_email=session['user_email'])

@app.route('/run-model-processing', methods=['POST'])
def run_model_processing():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Check if model_utils.py exists
        if os.path.exists('model_utils.py'):
            # Run the model_utils.py file
            result = subprocess.run([sys.executable, 'model_utils.py'], 
                                  capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                return jsonify({
                    'success': True, 
                    'message': 'Model processing completed successfully',
                    'output': result.stdout
                })
            else:
                return jsonify({
                    'success': False, 
                    'message': f'Model processing failed: {result.stderr}',
                    'error': result.stderr
                })
        else:
            # If model_utils.py doesn't exist, simulate processing
            return jsonify({
                'success': True, 
                'message': 'Model processing simulated (model_utils.py not found)',
                'output': 'Simulation completed'
            })
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False, 
            'message': 'Model processing timed out (exceeded 5 minutes)'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error running model processing: {str(e)}'
        })

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_csv()
    init_analysis_csv()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)