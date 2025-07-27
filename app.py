from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import uuid
from datetime import datetime
import logging
import traceback

app = Flask(__name__)
app.secret_key = 'mystery_club_secret_key_2024'  # Change this in production

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Initialize attendance.csv with ID
        if not os.path.exists(ATTENDANCE_CSV):
            with open(ATTENDANCE_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Date', 'Member Name', 'Session Name', 'Hours', 'Status', 'Notes'])
        
        # Initialize members.csv with ID
        if not os.path.exists(MEMBERS_CSV):
            with open(MEMBERS_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Member Name', 'Email', 'Join Date'])
    except Exception as e:
        logger.error(f"Error initializing CSV files: {str(e)}")
        logger.error(traceback.format_exc())

def init_finances_csv():
    try:
        if not os.path.exists(FINANCES_CSV):
            with open(FINANCES_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Date', 'Type', 'Category', 'Amount', 'Description'])
    except Exception as e:
        logger.error(f"Error initializing finances CSV: {str(e)}")

def init_events_csv():
    try:
        if not os.path.exists(EVENTS_CSV):
            with open(EVENTS_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Event Name', 'Date', 'Time', 'Location', 'Description'])
    except Exception as e:
        logger.error(f"Error initializing events CSV: {str(e)}")

def init_todo_csv():
    try:
        if not os.path.exists(TODO_CSV):
            with open(TODO_CSV, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Title', 'Due Date', 'Completed', 'Created Date'])
    except Exception as e:
        logger.error(f"Error initializing todo CSV: {str(e)}")

# Helper functions for CSV operations with unique IDs
def read_csv_with_id(file_path):
    """Read CSV file and return list of dictionaries with IDs"""
    records = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                records = list(reader)
                # Filter out empty records
                records = [record for record in records if any(record.values())]
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
    return records

def write_csv_with_id(file_path, records, fieldnames):
    """Write records to CSV file with proper headers"""
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        return True
    except Exception as e:
        logger.error(f"Error writing CSV file {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def delete_record_by_id(file_path, record_id, fieldnames):
    """Delete a record by ID from CSV file"""
    try:
        records = read_csv_with_id(file_path)
        original_count = len(records)
        records = [record for record in records if record.get('ID') != record_id]
        
        if write_csv_with_id(file_path, records, fieldnames):
            return len(records) < original_count
        return False
    except Exception as e:
        logger.error(f"Error deleting record {record_id} from {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# Helper functions for attendance
def get_members():
    try:
        init_csv_files()
        return read_csv_with_id(MEMBERS_CSV)
    except Exception as e:
        logger.error(f"Error getting members: {str(e)}")
        return []

def add_member(name, email):
    try:
        member_id = str(uuid.uuid4())
        with open(MEMBERS_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([member_id, name, email, datetime.now().strftime('%Y-%m-%d')])
        return member_id
    except Exception as e:
        logger.error(f"Error adding member: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def get_attendance_records():
    try:
        init_csv_files()
        return read_csv_with_id(ATTENDANCE_CSV)
    except Exception as e:
        logger.error(f"Error getting attendance records: {str(e)}")
        return []

def add_attendance_record(date, member_name, session_name, hours, status, notes):
    try:
        record_id = str(uuid.uuid4())
        with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([record_id, date, member_name, session_name, hours, status, notes])
        return record_id
    except Exception as e:
        logger.error(f"Error adding attendance record: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def add_bulk_attendance(date, session_name, hours, attendance_data):
    """Add attendance for multiple members at once"""
    try:
        records_added = 0
        for member_name, status in attendance_data.items():
            if status in ['Present', 'Absent']:
                if add_attendance_record(date, member_name, session_name, hours, status, ''):
                    records_added += 1
        return records_added
    except Exception as e:
        logger.error(f"Error adding bulk attendance: {str(e)}")
        return 0

# Financial functions
def get_financial_records():
    try:
        init_finances_csv()
        return read_csv_with_id(FINANCES_CSV)
    except Exception as e:
        logger.error(f"Error getting financial records: {str(e)}")
        return []

def add_financial_record(date, record_type, category, amount, description):
    try:
        record_id = str(uuid.uuid4())
        with open(FINANCES_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([record_id, date, record_type, category, amount, description])
        return record_id
    except Exception as e:
        logger.error(f"Error adding financial record: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def get_financial_summary():
    try:
        records = get_financial_records()
        total_income = 0
        total_expenses = 0
        
        for record in records:
            try:
                amount = float(record.get('Amount', 0))
                if record.get('Type') == 'Income':
                    total_income += amount
                elif record.get('Type') == 'Expense':
                    total_expenses += amount
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount in financial record: {record}")
                continue
        
        balance = total_income - total_expenses
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'records': records
        }
    except Exception as e:
        logger.error(f"Error getting financial summary: {str(e)}")
        return {
            'total_income': 0,
            'total_expenses': 0,
            'balance': 0,
            'records': []
        }

# Event functions
def get_events():
    try:
        init_events_csv()
        return read_csv_with_id(EVENTS_CSV)
    except Exception as e:
        logger.error(f"Error getting events: {str(e)}")
        return []

def add_event(name, date, time, location, description):
    try:
        event_id = str(uuid.uuid4())
        with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([event_id, name, date, time, location, description])
        return event_id
    except Exception as e:
        logger.error(f"Error adding event: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Todo functions
def get_todos():
    try:
        init_todo_csv()
        return read_csv_with_id(TODO_CSV)
    except Exception as e:
        logger.error(f"Error getting todos: {str(e)}")
        return []

def add_todo(title, due_date=''):
    try:
        todo_id = str(uuid.uuid4())
        with open(TODO_CSV, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([todo_id, title, due_date, 'False', datetime.now().strftime('%Y-%m-%d')])
        return todo_id
    except Exception as e:
        logger.error(f"Error adding todo: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def toggle_todo_completion(todo_id):
    """Toggle the completion status of a todo item"""
    try:
        records = read_csv_with_id(TODO_CSV)
        for record in records:
            if record['ID'] == todo_id:
                record['Completed'] = 'True' if record['Completed'] == 'False' else 'False'
                break
        
        fieldnames = ['ID', 'Title', 'Due Date', 'Completed', 'Created Date']
        return write_csv_with_id(TODO_CSV, records, fieldnames)
    except Exception as e:
        logger.error(f"Error toggling todo completion: {str(e)}")
        return False

def clear_completed_todos():
    """Remove all completed todo items"""
    try:
        records = read_csv_with_id(TODO_CSV)
        original_count = len(records)
        active_records = [record for record in records if record['Completed'] == 'False']
        fieldnames = ['ID', 'Title', 'Due Date', 'Completed', 'Created Date']
        
        if write_csv_with_id(TODO_CSV, active_records, fieldnames):
            return original_count - len(active_records)
        return 0
    except Exception as e:
        logger.error(f"Error clearing completed todos: {str(e)}")
        return 0

# Routes
@app.route('/')
def home():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            if username == ADMIN_USER.username and check_password_hash(ADMIN_USER.password_hash, password):
                login_user(ADMIN_USER)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in logout route: {str(e)}")
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get summary data for dashboard
        members_count = len(get_members())
        recent_events = get_events()[:3]  # Get 3 most recent events
        financial_summary = get_financial_summary()
        pending_todos = len([todo for todo in get_todos() if todo.get('Completed') == 'False'])
        
        return render_template('dashboard.html', 
                             members_count=members_count,
                             recent_events=recent_events,
                             financial_summary=financial_summary,
                             pending_todos=pending_todos)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error loading dashboard. Please try again.', 'error')
        return render_template('dashboard.html', 
                             members_count=0,
                             recent_events=[],
                             financial_summary={'total_income': 0, 'total_expenses': 0, 'balance': 0, 'records': []},
                             pending_todos=0)

@app.route('/attendance')
@login_required
def attendance():
    try:
        members = get_members()
        attendance_records = get_attendance_records()
        return render_template('attendance.html', members=members, attendance_records=attendance_records)
    except Exception as e:
        logger.error(f"Error in attendance route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error loading attendance data. Please try again.', 'error')
        return render_template('attendance.html', members=[], attendance_records=[])

@app.route('/finances')
@login_required
def finances():
    try:
        summary = get_financial_summary()
        return render_template('finances.html', summary=summary)
    except Exception as e:
        logger.error(f"Error in finances route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error loading financial data. Please try again.', 'error')
        return render_template('finances.html', summary={'total_income': 0, 'total_expenses': 0, 'balance': 0, 'records': []})

@app.route('/events')
@login_required
def events():
    try:
        events_list = get_events()
        return render_template('events.html', events=events_list)
    except Exception as e:
        logger.error(f"Error in events route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error loading events data. Please try again.', 'error')
        return render_template('events.html', events=[])

@app.route('/todo')
@login_required
def todo():
    try:
        todos = get_todos()
        return render_template('todo.html', todos=todos)
    except Exception as e:
        logger.error(f"Error in todo route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error loading goals data. Please try again.', 'error')
        return render_template('todo.html', todos=[])

# Form handling routes
@app.route('/add_member', methods=['POST'])
@login_required
def add_member_route():
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('attendance'))
        
        member_id = add_member(name, email)
        if member_id:
            flash('Member added successfully!', 'success')
        else:
            flash('Error adding member. Please try again.', 'error')
        
        return redirect(url_for('attendance'))
    except Exception as e:
        logger.error(f"Error in add_member route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error adding member. Please try again.', 'error')
        return redirect(url_for('attendance'))

@app.route('/add_attendance', methods=['POST'])
@login_required
def add_attendance():
    try:
        date = request.form.get('date', '').strip()
        session_name = request.form.get('session_name', '').strip()
        hours = request.form.get('hours', '').strip()
        
        if not date or not session_name or not hours:
            flash('Date, session name, and hours are required!', 'error')
            return redirect(url_for('attendance'))
        
        # Handle bulk attendance
        attendance_data = {}
        for key, value in request.form.items():
            if key.startswith('attendance_'):
                member_name = key.replace('attendance_', '').replace('_', ' ')
                attendance_data[member_name] = value
        
        records_added = add_bulk_attendance(date, session_name, hours, attendance_data)
        if records_added > 0:
            flash(f'Attendance recorded for {records_added} members!', 'success')
        else:
            flash('No attendance records were added. Please check your selections.', 'warning')
        
        return redirect(url_for('attendance'))
    except Exception as e:
        logger.error(f"Error in add_attendance route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error recording attendance. Please try again.', 'error')
        return redirect(url_for('attendance'))

@app.route('/add_financial_record', methods=['POST'])
@login_required
def add_financial_record_route():
    try:
        date = request.form.get('date', '').strip()
        record_type = request.form.get('type', '').strip()
        category = request.form.get('category', '').strip()
        amount = request.form.get('amount', '').strip()
        description = request.form.get('description', '').strip()
        
        if not all([date, record_type, category, amount, description]):
            flash('All fields are required!', 'error')
            return redirect(url_for('finances'))
        
        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                flash('Amount must be a positive number!', 'error')
                return redirect(url_for('finances'))
        except ValueError:
            flash('Invalid amount format!', 'error')
            return redirect(url_for('finances'))
        
        record_id = add_financial_record(date, record_type, category, amount, description)
        if record_id:
            flash('Financial record added successfully!', 'success')
        else:
            flash('Error adding financial record. Please try again.', 'error')
        
        return redirect(url_for('finances'))
    except Exception as e:
        logger.error(f"Error in add_financial_record route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error adding financial record. Please try again.', 'error')
        return redirect(url_for('finances'))

@app.route('/add_event', methods=['POST'])
@login_required
def add_event_route():
    try:
        name = request.form.get('name', '').strip()
        date = request.form.get('date', '').strip()
        time = request.form.get('time', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        
        if not all([name, date, time, location, description]):
            flash('All fields are required!', 'error')
            return redirect(url_for('events'))
        
        event_id = add_event(name, date, time, location, description)
        if event_id:
            flash('Event added successfully!', 'success')
        else:
            flash('Error adding event. Please try again.', 'error')
        
        return redirect(url_for('events'))
    except Exception as e:
        logger.error(f"Error in add_event route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error adding event. Please try again.', 'error')
        return redirect(url_for('events'))

@app.route('/add_todo', methods=['POST'])
@login_required
def add_todo_route():
    try:
        title = request.form.get('title', '').strip()
        due_date = request.form.get('due_date', '').strip()
        
        if not title:
            flash('Goal title is required!', 'error')
            return redirect(url_for('todo'))
        
        todo_id = add_todo(title, due_date)
        if todo_id:
            flash('Goal added successfully!', 'success')
        else:
            flash('Error adding goal. Please try again.', 'error')
        
        return redirect(url_for('todo'))
    except Exception as e:
        logger.error(f"Error in add_todo route: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error adding goal. Please try again.', 'error')
        return redirect(url_for('todo'))

# Delete routes
@app.route('/delete_member/<member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    try:
        fieldnames = ['ID', 'Member Name', 'Email', 'Join Date']
        if delete_record_by_id(MEMBERS_CSV, member_id, fieldnames):
            # Get updated records to display
            updated_records = get_members()
            return render_template('delete_success.html', 
                                 message='Member deleted successfully!',
                                 data_type='Members',
                                 records=updated_records,
                                 headers=['Member Name', 'Email', 'Join Date'],
                                 redirect_url=url_for('attendance'),
                                 download_url=url_for('download_members'))
        else:
            flash('Error deleting member!', 'error')
            return redirect(url_for('attendance'))
    except Exception as e:
        logger.error(f"Error deleting member {member_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error deleting member. Please try again.', 'error')
        return redirect(url_for('attendance'))

@app.route('/delete_attendance/<record_id>', methods=['POST'])
@login_required
def delete_attendance_record(record_id):
    try:
        fieldnames = ['ID', 'Date', 'Member Name', 'Session Name', 'Hours', 'Status', 'Notes']
        if delete_record_by_id(ATTENDANCE_CSV, record_id, fieldnames):
            # Get updated records to display
            updated_records = get_attendance_records()
            return render_template('delete_success.html', 
                                 message='Attendance record deleted successfully!',
                                 data_type='Attendance Records',
                                 records=updated_records,
                                 headers=['Date', 'Member Name', 'Session Name', 'Hours', 'Status', 'Notes'],
                                 redirect_url=url_for('attendance'),
                                 download_url=url_for('download_attendance'))
        else:
            flash('Error deleting attendance record!', 'error')
            return redirect(url_for('attendance'))
    except Exception as e:
        logger.error(f"Error deleting attendance record {record_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error deleting attendance record. Please try again.', 'error')
        return redirect(url_for('attendance'))

@app.route('/delete_financial/<record_id>', methods=['POST'])
@login_required
def delete_financial_record(record_id):
    try:
        fieldnames = ['ID', 'Date', 'Type', 'Category', 'Amount', 'Description']
        if delete_record_by_id(FINANCES_CSV, record_id, fieldnames):
            # Get updated records to display
            updated_records = get_financial_records()
            return render_template('delete_success.html', 
                                 message='Financial record deleted successfully!',
                                 data_type='Financial Records',
                                 records=updated_records,
                                 headers=['Date', 'Type', 'Category', 'Amount', 'Description'],
                                 redirect_url=url_for('finances'),
                                 download_url=url_for('download_finances'))
        else:
            flash('Error deleting financial record!', 'error')
            return redirect(url_for('finances'))
    except Exception as e:
        logger.error(f"Error deleting financial record {record_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error deleting financial record. Please try again.', 'error')
        return redirect(url_for('finances'))

@app.route('/delete_event/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    try:
        fieldnames = ['ID', 'Event Name', 'Date', 'Time', 'Location', 'Description']
        if delete_record_by_id(EVENTS_CSV, event_id, fieldnames):
            # Get updated records to display
            updated_records = get_events()
            return render_template('delete_success.html', 
                                 message='Event deleted successfully!',
                                 data_type='Events',
                                 records=updated_records,
                                 headers=['Event Name', 'Date', 'Time', 'Location', 'Description'],
                                 redirect_url=url_for('events'),
                                 download_url=url_for('download_events'))
        else:
            flash('Error deleting event!', 'error')
            return redirect(url_for('events'))
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error deleting event. Please try again.', 'error')
        return redirect(url_for('events'))

@app.route('/delete_todo/<todo_id>', methods=['POST'])
@login_required
def delete_todo(todo_id):
    try:
        fieldnames = ['ID', 'Title', 'Due Date', 'Completed', 'Created Date']
        if delete_record_by_id(TODO_CSV, todo_id, fieldnames):
            # Get updated records to display
            updated_records = get_todos()
            return render_template('delete_success.html', 
                                 message='Goal deleted successfully!',
                                 data_type='Goals',
                                 records=updated_records,
                                 headers=['Title', 'Due Date', 'Completed', 'Created Date'],
                                 redirect_url=url_for('todo'),
                                 download_url=url_for('download_todos'))
        else:
            flash('Error deleting goal!', 'error')
            return redirect(url_for('todo'))
    except Exception as e:
        logger.error(f"Error deleting todo {todo_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error deleting goal. Please try again.', 'error')
        return redirect(url_for('todo'))

@app.route('/toggle_todo/<todo_id>', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    try:
        if toggle_todo_completion(todo_id):
            flash('Goal status updated!', 'success')
        else:
            flash('Error updating goal status!', 'error')
        return redirect(url_for('todo'))
    except Exception as e:
        logger.error(f"Error toggling todo {todo_id}: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error updating goal status. Please try again.', 'error')
        return redirect(url_for('todo'))

@app.route('/clear_completed_todos', methods=['POST'])
@login_required
def clear_completed():
    try:
        cleared_count = clear_completed_todos()
        if cleared_count > 0:
            flash(f'Cleared {cleared_count} completed goals!', 'success')
        else:
            flash('No completed goals to clear.', 'info')
        return redirect(url_for('todo'))
    except Exception as e:
        logger.error(f"Error clearing completed todos: {str(e)}")
        logger.error(traceback.format_exc())
        flash('Error clearing completed goals. Please try again.', 'error')
        return redirect(url_for('todo'))

# Download routes
@app.route('/download_attendance')
@login_required
def download_attendance():
    try:
        if os.path.exists(ATTENDANCE_CSV):
            return send_file(ATTENDANCE_CSV, as_attachment=True, download_name='attendance.csv')
        else:
            flash('No attendance data to download.', 'warning')
            return redirect(url_for('attendance'))
    except Exception as e:
        logger.error(f"Error downloading attendance: {str(e)}")
        flash('Error downloading attendance data.', 'error')
        return redirect(url_for('attendance'))

@app.route('/download_members')
@login_required
def download_members():
    try:
        if os.path.exists(MEMBERS_CSV):
            return send_file(MEMBERS_CSV, as_attachment=True, download_name='members.csv')
        else:
            flash('No member data to download.', 'warning')
            return redirect(url_for('attendance'))
    except Exception as e:
        logger.error(f"Error downloading members: {str(e)}")
        flash('Error downloading member data.', 'error')
        return redirect(url_for('attendance'))

@app.route('/download_finances')
@login_required
def download_finances():
    try:
        if os.path.exists(FINANCES_CSV):
            return send_file(FINANCES_CSV, as_attachment=True, download_name='finances.csv')
        else:
            flash('No financial data to download.', 'warning')
            return redirect(url_for('finances'))
    except Exception as e:
        logger.error(f"Error downloading finances: {str(e)}")
        flash('Error downloading financial data.', 'error')
        return redirect(url_for('finances'))

@app.route('/download_events')
@login_required
def download_events():
    try:
        if os.path.exists(EVENTS_CSV):
            return send_file(EVENTS_CSV, as_attachment=True, download_name='events.csv')
        else:
            flash('No event data to download.', 'warning')
            return redirect(url_for('events'))
    except Exception as e:
        logger.error(f"Error downloading events: {str(e)}")
        flash('Error downloading event data.', 'error')
        return redirect(url_for('events'))

@app.route('/download_todos')
@login_required
def download_todos():
    try:
        if os.path.exists(TODO_CSV):
            return send_file(TODO_CSV, as_attachment=True, download_name='todos.csv')
        else:
            flash('No goal data to download.', 'warning')
            return redirect(url_for('todo'))
    except Exception as e:
        logger.error(f"Error downloading todos: {str(e)}")
        flash('Error downloading goal data.', 'error')
        return redirect(url_for('todo'))

# API routes
@app.route('/api/financial_data')
@login_required
def financial_data_api():
    try:
        summary = get_financial_summary()
        
        # Prepare data for Chart.js
        income_by_category = {}
        expense_by_category = {}
        
        for record in summary['records']:
            try:
                if record.get('Type') == 'Income':
                    category = record.get('Category', 'Other')
                    amount = float(record.get('Amount', 0))
                    income_by_category[category] = income_by_category.get(category, 0) + amount
                elif record.get('Type') == 'Expense':
                    category = record.get('Category', 'Other')
                    amount = float(record.get('Amount', 0))
                    expense_by_category[category] = expense_by_category.get(category, 0) + amount
            except (ValueError, TypeError):
                logger.warning(f"Invalid financial record: {record}")
                continue
        
        return jsonify({
            'summary': {
                'total_income': summary['total_income'],
                'total_expenses': summary['total_expenses'],
                'balance': summary['balance']
            },
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category
        })
    except Exception as e:
        logger.error(f"Error in financial_data_api: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to load financial data'}), 500

@app.route('/api/events')
@login_required
def events_api():
    try:
        events = get_events()
        
        # Format events for FullCalendar.js
        calendar_events = []
        for event in events:
            try:
                calendar_events.append({
                    'id': event.get('ID', ''),
                    'title': event.get('Event Name', 'Untitled Event'),
                    'start': f"{event.get('Date', '')}T{event.get('Time', '00:00')}",
                    'description': event.get('Description', ''),
                    'location': event.get('Location', '')
                })
            except Exception as e:
                logger.warning(f"Invalid event record: {event}, error: {str(e)}")
                continue
        
        return jsonify(calendar_events)
    except Exception as e:
        logger.error(f"Error in events_api: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Failed to load events data'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 error: {request.url}")
    flash('Page not found.', 'error')
    return redirect(url_for('dashboard'))

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    logger.error(traceback.format_exc())
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Initialize CSV files on startup
    init_csv_files()
    init_finances_csv()
    init_events_csv()
    init_todo_csv()
    
    app.run(host='0.0.0.0', debug=True)

