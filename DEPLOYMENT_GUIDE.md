# Mystery Club - PythonAnywhere Deployment Guide

## Prerequisites
- A PythonAnywhere account (free or paid)
- Basic familiarity with file uploads and web app configuration

## Step 1: Upload Files to PythonAnywhere

1. **Log in to PythonAnywhere** and go to the **Files** tab
2. **Create a new directory** called `mystery_club` in your home directory
3. **Upload all project files** to `/home/yourusername/mystery_club/`:
   - `app.py`
   - `requirements.txt`
   - `wsgi.py`
   - `templates/` folder (with all HTML files)
   - `static/` folder (with CSS files)
   - `data/` folder (will be created automatically)

## Step 2: Install Dependencies

1. **Open a Bash console** from the PythonAnywhere dashboard
2. **Navigate to your project directory**:
   ```bash
   cd mystery_club
   ```
3. **Install required packages**:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

## Step 3: Configure Web App

1. **Go to the Web tab** in your PythonAnywhere dashboard
2. **Click "Add a new web app"**
3. **Choose "Manual configuration"** and select **Python 3.10**
4. **Set the source code directory** to: `/home/yourusername/mystery_club`
5. **Edit the WSGI configuration file**:
   - Click on the WSGI configuration file link
   - Replace the contents with the code from `wsgi.py`
   - **Update the path** in line 7: change `yourusername` to your actual username
   ```python
   path = '/home/yourusername/mystery_club'  # Update this line
   ```

## Step 4: Configure Static Files

1. **In the Web tab**, scroll down to the **Static files** section
2. **Add a new static file mapping**:
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/mystery_club/static/`

## Step 5: Test and Launch

1. **Click "Reload" button** in the Web tab
2. **Visit your web app URL**: `https://yourusername.pythonanywhere.com`
3. **Test the login** with default credentials:
   - Username: `admin`
   - Password: `admin123`

## Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default password in production by modifying the `ADMIN_USER` variable in `app.py`.

## Features Available

### 1. **Admin Authentication**
- Secure login with session management
- Protected routes for all admin functions

### 2. **Attendance Tracking**
- Add and manage club members
- Log attendance with date, session name, and hours
- Download attendance records as CSV

### 3. **Financial Management**
- Track income and expenses by category
- Visual charts showing financial overview
- Download financial records as CSV

### 4. **Event Planning**
- Create and manage events with date, time, and location
- Interactive calendar view using FullCalendar.js
- Download event list as CSV

## Data Storage

- All data is stored in CSV files in the `data/` directory
- Files are automatically created when first accessed
- Easy to backup, restore, and import into Excel

## CSV File Structure

### Members (`data/members.csv`)
```
Member Name,Email,Join Date
```

### Attendance (`data/attendance.csv`)
```
Date,Member Name,Session Name,Hours,Notes
```

### Finances (`data/finances.csv`)
```
Date,Type,Category,Amount,Description
```

### Events (`data/events.csv`)
```
Event Name,Date,Time,Location,Description
```

## Troubleshooting

### Common Issues:

1. **500 Internal Server Error**
   - Check the error log in the Web tab
   - Ensure all file paths are correct in `wsgi.py`
   - Verify all dependencies are installed

2. **Static files not loading**
   - Check static file mapping in Web tab
   - Ensure CSS/JS files are in the correct directory

3. **CSV files not found**
   - The app will automatically create CSV files on first use
   - Ensure the `data/` directory exists and is writable

4. **Login not working**
   - Verify the secret key is set in `app.py`
   - Check that Flask-Login is properly installed

### Performance Tips:

1. **For better performance** on free accounts:
   - Keep CSV files small (under 1000 records)
   - Consider upgrading to a paid account for larger datasets

2. **Backup your data regularly**:
   - Download CSV files from the admin interface
   - Keep local copies of important records

## Security Considerations

1. **Change default credentials** immediately after deployment
2. **Use a strong secret key** in production
3. **Regularly backup your data**
4. **Monitor access logs** for suspicious activity

## Support

For technical issues:
- Check PythonAnywhere help documentation
- Review error logs in the Web tab
- Ensure all file permissions are correct

## File Structure Summary

```
mystery_club/
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI configuration for PythonAnywhere
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── attendance.html
│   ├── finances.html
│   └── events.html
├── static/              # Static files (CSS, JS)
│   └── css/
│       └── style.css
└── data/               # CSV data files (auto-created)
    ├── members.csv
    ├── attendance.csv
    ├── finances.csv
    └── events.csv
```

Your Mystery Club web application is now ready for deployment on PythonAnywhere!

