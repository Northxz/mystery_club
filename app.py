from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mystery_club_secret_key_2024'  # Change this in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# Default admin user (in production, store this in a database or secure file)
ADMIN_USER = User(1, 'admin', generate_password_hash('admin123'))

@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':
        return ADMIN_USER
    return None

# CSV file paths
ATTENDANCE_CSV = 'data/attendance.csv'
MEMBERS_CSV = 'data/members.csv'
FINANCES_CSV = 'data/finances.csv'
EVENTS_CSV = 'data/events.csv'

# Initialize CSV files if they don't exist
def init_csv_files():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize attendance.csv
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Member Name', 'Session Name', 'Hours', 'Notes'])
    
    # Initialize members.csv
    if not os.path.exists(MEMBERS_CSV):
        with open(MEMBERS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Member Name', 'Email', 'Join Date'])

def init_finances_csv():
    if not os.path.exists(FINANCES_CSV):
        with open(FINANCES_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])

def init_events_csv():
    if not os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Event Name', 'Date', 'Time', 'Location', 'Description'])

# Helper functions for attendance
def get_members():
    members = []
    if os.path.exists(MEMBERS_CSV):
        with open(MEMBERS_CSV, 'r', newline='') as file:
            reader = csv.DictReader(file)
            members = list(reader)
    return members

def add_member(name, email):
    with open(MEMBERS_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, email, datetime.now().strftime('%Y-%m-%d')])

def get_attendance_records():
    records = []
    if os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'r', newline='') as file:
            reader = csv.DictReader(file)
            records = list(reader)
    return records

def add_attendance_record(date, member_name, session_name, hours, notes):
    with open(ATTENDANCE_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, member_name, session_name, hours, notes])

# Financial functions
def get_financial_records():
    records = []
    if os.path.exists(FINANCES_CSV):
        with open(FINANCES_CSV, 'r', newline='') as file:
            reader = csv.DictReader(file)
            records = list(reader)
    return records

def add_financial_record(date, record_type, category, amount, description):
    with open(FINANCES_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, record_type, category, amount, description])

def get_financial_summary():
    records = get_financial_records()
    total_income = sum(float(record['Amount']) for record in records if record['Type'] == 'Income')
    total_expenses = sum(float(record['Amount']) for record in records if record['Type'] == 'Expense')
    balance = total_income - total_expenses
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'records': records
    }

# Event functions
def get_events():
    events = []
    if os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, 'r', newline='') as file:
            reader = csv.DictReader(file)
            events = list(reader)
    return events

def add_event(name, date, time, location, description):
    with open(EVENTS_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, date, time, location, description])

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USER.username and check_password_hash(ADMIN_USER.password_hash, password):
            login_user(ADMIN_USER)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/attendance')
@login_required
def attendance():
    init_csv_files()
    members = get_members()
    attendance_records = get_attendance_records()
    return render_template('attendance.html', members=members, attendance_records=attendance_records)

@app.route('/finances')
@login_required
def finances():
    init_finances_csv()
    summary = get_financial_summary()
    return render_template('finances.html', summary=summary)

@app.route('/events')
@login_required
def events():
    init_events_csv()
    events_list = get_events()
    return render_template('events.html', events=events_list)

# Form handling routes
@app.route('/add_member', methods=['POST'])
@login_required
def add_member_route():
    name = request.form['name']
    email = request.form['email']
    add_member(name, email)
    flash('Member added successfully!')
    return redirect(url_for('attendance'))

@app.route('/add_attendance', methods=['POST'])
@login_required
def add_attendance():
    date = request.form['date']
    member_name = request.form['member_name']
    session_name = request.form['session_name']
    hours = request.form['hours']
    notes = request.form.get('notes', '')
    
    add_attendance_record(date, member_name, session_name, hours, notes)
    flash('Attendance record added successfully!')
    return redirect(url_for('attendance'))

@app.route('/add_financial_record', methods=['POST'])
@login_required
def add_financial_record_route():
    date = request.form['date']
    record_type = request.form['type']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']
    
    add_financial_record(date, record_type, category, amount, description)
    flash('Financial record added successfully!')
    return redirect(url_for('finances'))

@app.route('/add_event', methods=['POST'])
@login_required
def add_event_route():
    name = request.form['name']
    date = request.form['date']
    time = request.form['time']
    location = request.form['location']
    description = request.form['description']
    
    add_event(name, date, time, location, description)
    flash('Event added successfully!')
    return redirect(url_for('events'))

# Download routes
@app.route('/download_attendance')
@login_required
def download_attendance():
    return send_file(ATTENDANCE_CSV, as_attachment=True, download_name='attendance.csv')

@app.route('/download_members')
@login_required
def download_members():
    return send_file(MEMBERS_CSV, as_attachment=True, download_name='members.csv')

@app.route('/download_finances')
@login_required
def download_finances():
    return send_file(FINANCES_CSV, as_attachment=True, download_name='finances.csv')

@app.route('/download_events')
@login_required
def download_events():
    return send_file(EVENTS_CSV, as_attachment=True, download_name='events.csv')

# API routes
@app.route('/api/financial_data')
@login_required
def financial_data_api():
    summary = get_financial_summary()
    
    # Prepare data for Chart.js
    income_by_category = {}
    expense_by_category = {}
    
    for record in summary['records']:
        if record['Type'] == 'Income':
            category = record['Category']
            amount = float(record['Amount'])
            income_by_category[category] = income_by_category.get(category, 0) + amount
        elif record['Type'] == 'Expense':
            category = record['Category']
            amount = float(record['Amount'])
            expense_by_category[category] = expense_by_category.get(category, 0) + amount
    
    return jsonify({
        'summary': {
            'total_income': summary['total_income'],
            'total_expenses': summary['total_expenses'],
            'balance': summary['balance']
        },
        'income_by_category': income_by_category,
        'expense_by_category': expense_by_category
    })

@app.route('/api/events')
@login_required
def events_api():
    events = get_events()
    
    # Format events for FullCalendar.js
    calendar_events = []
    for event in events:
        calendar_events.append({
            'title': event['Event Name'],
            'start': f"{event['Date']}T{event['Time']}",
            'description': event['Description'],
            'location': event['Location']
        })
    
    return jsonify(calendar_events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

