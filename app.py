from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import uuid
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
TODO_CSV = 'data/todo.csv'

# Initialize CSV files if they don't exist
def init_csv_files():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize attendance.csv with ID
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Date', 'Member Name', 'Session Name', 'Hours', 'Status', 'Notes'])
    
    # Initialize members.csv with ID
    if not os.path.exists(MEMBERS_CSV):
        with open(MEMBERS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Member Name', 'Email', 'Join Date'])

def init_finances_csv():
    if not os.path.exists(FINANCES_CSV):
        with open(FINANCES_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Date', 'Type', 'Category', 'Amount', 'Description'])

def init_events_csv():
    if not os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Event Name', 'Date', 'Time', 'Location', 'Description'])

def init_todo_csv():
    if not os.path.exists(TODO_CSV):
        with open(TODO_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Title', 'Due Date', 'Completed', 'Created Date'])

# Helper functions for CSV operations with unique IDs
def read_csv_with_id(file_path):
    """Read CSV file and return list of dictionaries with IDs"""
    records = []
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            records = list(reader)
    return records

def write_csv_with_id(file_path, records, fieldnames):
    """Write records to CSV file with proper headers"""
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

def delete_record_by_id(file_path, record_id, fieldnames):
    """Delete a record by ID from CSV file"""
    records = read_csv_with_id(file_path)
    records = [record for record in records if record.get('ID') != record_id]
    write_csv_with_id(file_path, records, fieldnames)
    return len([r for r in read_csv_with_id(file_path) if r.get('ID') == record_id]) == 0

# Helper functions for attendance
def get_members():
    init_csv_files()
    return read_csv_with_id(MEMBERS_CSV)

def add_member(name, email):
    member_id = str(uuid.uuid4())
    with open(MEMBERS_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([member_id, name, email, datetime.now().strftime('%Y-%m-%d')])
    return member_id

def get_attendance_records():
    init_csv_files()
    return read_csv_with_id(ATTENDANCE_CSV)

def add_attendance_record(date, member_name, session_name, hours, status, notes):
    record_id = str(uuid.uuid4())
    with open(ATTENDANCE_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([record_id, date, member_name, session_name, hours, status, notes])
    return record_id

def add_bulk_attendance(date, session_name, hours, attendance_data):
    """Add attendance for multiple members at once"""
    records_added = 0
    for member_name, status in attendance_data.items():
        if status in ['Present', 'Absent']:
            add_attendance_record(date, member_name, session_name, hours, status, '')
            records_added += 1
    return records_added

# Financial functions
def get_financial_records():
    init_finances_csv()
    return read_csv_with_id(FINANCES_CSV)

def add_financial_record(date, record_type, category, amount, description):
    record_id = str(uuid.uuid4())
    with open(FINANCES_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([record_id, date, record_type, category, amount, description])
    return record_id

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
    init_events_csv()
    return read_csv_with_id(EVENTS_CSV)

def add_event(name, date, time, location, description):
    event_id = str(uuid.uuid4())
    with open(EVENTS_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([event_id, name, date, time, location, description])
    return event_id

# Todo functions
def get_todos():
    init_todo_csv()
    return read_csv_with_id(TODO_CSV)

def add_todo(title, due_date=''):
    todo_id = str(uuid.uuid4())
    with open(TODO_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([todo_id, title, due_date, 'False', datetime.now().strftime('%Y-%m-%d')])
    return todo_id

def toggle_todo_completion(todo_id):
    """Toggle the completion status of a todo item"""
    records = read_csv_with_id(TODO_CSV)
    for record in records:
        if record['ID'] == todo_id:
            record['Completed'] = 'True' if record['Completed'] == 'False' else 'False'
            break
    
    fieldnames = ['ID', 'Title', 'Due Date', 'Completed', 'Created Date']
    write_csv_with_id(TODO_CSV, records, fieldnames)

def clear_completed_todos():
    """Remove all completed todo items"""
    records = read_csv_with_id(TODO_CSV)
    active_records = [record for record in records if record['Completed'] == 'False']
    fieldnames = ['ID', 'Title', 'Due Date', 'Completed', 'Created Date']
    write_csv_with_id(TODO_CSV, active_records, fieldnames)
    return len(records) - len(active_records)

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
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get summary data for dashboard
    members_count = len(get_members())
    recent_events = get_events()[:3]  # Get 3 most recent events
    financial_summary = get_financial_summary()
    pending_todos = len([todo for todo in get_todos() if todo['Completed'] == 'False'])
    
    return render_template('dashboard.html', 
                         members_count=members_count,
                         recent_events=recent_events,
                         financial_summary=financial_summary,
                         pending_todos=pending_todos)

@app.route('/attendance')
@login_required
def attendance():
    members = get_members()
    attendance_records = get_attendance_records()
    return render_template('attendance.html', members=members, attendance_records=attendance_records)

@app.route('/finances')
@login_required
def finances():
    summary = get_financial_summary()
    return render_template('finances.html', summary=summary)

@app.route('/events')
@login_required
def events():
    events_list = get_events()
    return render_template('events.html', events=events_list)

@app.route('/todo')
@login_required
def todo():
    todos = get_todos()
    return render_template('todo.html', todos=todos)

# Form handling routes
@app.route('/add_member', methods=['POST'])
@login_required
def add_member_route():
    name = request.form['name']
    email = request.form['email']
    add_member(name, email)
    flash('Member added successfully!', 'success')
    return redirect(url_for('attendance'))

@app.route('/add_attendance', methods=['POST'])
@login_required
def add_attendance():
    date = request.form['date']
    session_name = request.form['session_name']
    hours = request.form['hours']
    
    # Handle bulk attendance
    attendance_data = {}
    for key, value in request.form.items():
        if key.startswith('attendance_'):
            member_name = key.replace('attendance_', '').replace('_', ' ')
            attendance_data[member_name] = value
    
    records_added = add_bulk_attendance(date, session_name, hours, attendance_data)
    flash(f'Attendance recorded for {records_added} members!', 'success')
    return redirect(url_for('attendance'))

@app.route('/add_financial_record', methods=['POST'])
@login_required
def add_financial_record_route():
    date = request.form['date']
    record_type = request.form['type']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']
    
    # Validate amount
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            flash('Amount must be a positive number!', 'error')
            return redirect(url_for('finances'))
    except ValueError:
        flash('Invalid amount format!', 'error')
        return redirect(url_for('finances'))
    
    add_financial_record(date, record_type, category, amount, description)
    flash('Financial record added successfully!', 'success')
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
    flash('Event added successfully!', 'success')
    return redirect(url_for('events'))

@app.route('/add_todo', methods=['POST'])
@login_required
def add_todo_route():
    title = request.form['title']
    due_date = request.form.get('due_date', '')
    
    add_todo(title, due_date)
    flash('Goal added successfully!', 'success')
    return redirect(url_for('todo'))

# Delete routes
@app.route('/delete_member/<member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    fieldnames = ['ID', 'Member Name', 'Email', 'Join Date']
    if delete_record_by_id(MEMBERS_CSV, member_id, fieldnames):
        flash('Member deleted successfully!', 'success')
    else:
        flash('Error deleting member!', 'error')
    return redirect(url_for('attendance'))

@app.route('/delete_attendance/<record_id>', methods=['POST'])
@login_required
def delete_attendance_record(record_id):
    fieldnames = ['ID', 'Date', 'Member Name', 'Session Name', 'Hours', 'Status', 'Notes']
    if delete_record_by_id(ATTENDANCE_CSV, record_id, fieldnames):
        flash('Attendance record deleted successfully!', 'success')
    else:
        flash('Error deleting attendance record!', 'error')
    return redirect(url_for('attendance'))

@app.route('/delete_financial/<record_id>', methods=['POST'])
@login_required
def delete_financial_record(record_id):
    fieldnames = ['ID', 'Date', 'Type', 'Category', 'Amount', 'Description']
    if delete_record_by_id(FINANCES_CSV, record_id, fieldnames):
        flash('Financial record deleted successfully!', 'success')
    else:
        flash('Error deleting financial record!', 'error')
    return redirect(url_for('finances'))

@app.route('/delete_event/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    fieldnames = ['ID', 'Event Name', 'Date', 'Time', 'Location', 'Description']
    if delete_record_by_id(EVENTS_CSV, event_id, fieldnames):
        flash('Event deleted successfully!', 'success')
    else:
        flash('Error deleting event!', 'error')
    return redirect(url_for('events'))

@app.route('/delete_todo/<todo_id>', methods=['POST'])
@login_required
def delete_todo(todo_id):
    fieldnames = ['ID', 'Title', 'Due Date', 'Completed', 'Created Date']
    if delete_record_by_id(TODO_CSV, todo_id, fieldnames):
        flash('Goal deleted successfully!', 'success')
    else:
        flash('Error deleting goal!', 'error')
    return redirect(url_for('todo'))

@app.route('/toggle_todo/<todo_id>', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    toggle_todo_completion(todo_id)
    flash('Goal status updated!', 'success')
    return redirect(url_for('todo'))

@app.route('/clear_completed_todos', methods=['POST'])
@login_required
def clear_completed():
    cleared_count = clear_completed_todos()
    flash(f'Cleared {cleared_count} completed goals!', 'success')
    return redirect(url_for('todo'))

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

@app.route('/download_todos')
@login_required
def download_todos():
    return send_file(TODO_CSV, as_attachment=True, download_name='todos.csv')

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
            'id': event['ID'],
            'title': event['Event Name'],
            'start': f"{event['Date']}T{event['Time']}",
            'description': event['Description'],
            'location': event['Location']
        })
    
    return jsonify(calendar_events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

