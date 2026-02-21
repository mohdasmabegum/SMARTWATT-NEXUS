# SMARTWATT NEXUS - Complete Installation Guide

## System Requirements

### Minimum Requirements
- **OS**: Windows 7+, macOS 10.12+, or Linux (Ubuntu 16.04+)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB for installation
- **Browser**: Modern browser (Chrome, Firefox, Edge, Safari)

### Recommended Requirements
- **OS**: Windows 10+, macOS 11+, or Ubuntu 20.04+
- **Python**: 3.10 or higher
- **RAM**: 4GB or more
- **Disk Space**: 1GB
- **Internet**: For pip package installation

## Installation Steps

### Option 1: Windows (Recommended for Windows Users)

#### Step 1: Install Python
1. Download Python 3.10+ from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

#### Step 2: Navigate to Project
```cmd
cd "b:\Minor Project\SMARTWATT-NEXUS"
```

#### Step 3: Run Startup Script
```cmd
run_app.bat
```

This script will:
- Create virtual environment
- Install dependencies
- Initialize database
- Start the application

#### Step 4: Open Application
- Open browser
- Go to http://localhost:5000
- Login with demo credentials:
  - Username: `demo_user`
  - Password: `password123`

### Option 2: macOS/Linux

#### Step 1: Install Python
```bash
# macOS
brew install python@3.10

# Ubuntu/Debian
sudo apt-get install python3.10 python3-pip python3-venv
```

#### Step 2: Navigate to Project
```bash
cd "/path/to/SMARTWATT-NEXUS"
```

#### Step 3: Make Script Executable
```bash
chmod +x run_app.sh
```

#### Step 4: Run Startup Script
```bash
./run_app.sh
```

#### Step 5: Open Application
- Open browser
- Go to http://localhost:5000

### Option 3: Manual Installation (All Platforms)

#### Step 1: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Initialize Database
```bash
cd backend
python init_data.py
```

#### Step 4: Run Application
```bash
python app.py
```

#### Step 5: Access Application
- Open http://localhost:5000 in browser

## Post-Installation Setup

### Database Check
The application will automatically create:
- `smartwatt_nexus.db` - SQLite database file
- All required tables (Users, ConsumptionRecords, Alerts, Predictions)

### Verify Installation
1. Check terminal shows "Running on http://127.0.0.1:5000"
2. Navigate to http://localhost:5000
3. You should see login page with "SMARTWATT NEXUS" title

### Test Features
1. **Login**: Use demo_user / password123
2. **Dashboard**: View sample data and charts
3. **Daily Usage**: Check 7/14/30 day views
4. **Predictions**: Generate ML predictions
5. **Bill Estimate**: See bill calculation
6. **Reports**: Download CSV

## Troubleshooting

### Python Not Found
```
Error: 'python' is not recognized as an internal or external command
```
**Solution**:
- Install Python from https://www.python.org
- Ensure "Add Python to PATH" is checked
- Restart terminal/command prompt

### Port 5000 Already in Use
```
Address already in use
```
**Solution**:
- Edit `backend/app.py` line at the end
- Change `app.run(debug=True, port=5000)` to `app.run(debug=True, port=5001)`
- Or kill process using port 5000:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # macOS/Linux
  lsof -i :5000
  kill -9 <PID>
  ```

### Permission Denied (macOS/Linux)
```
Permission denied: './run_app.sh'
```
**Solution**:
```bash
chmod +x run_app.sh
./run_app.sh
```

### TensorFlow Installation Fails
```
ERROR: Could not install packages due to an environment error
```
**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements.txt

# If still fails, install TensorFlow separately
pip install tensorflow==2.13.0 --no-cache-dir
```

### Database Locked Error
```
sqlite3.OperationalError: database is locked
```
**Solution**:
- Close any other instances of the application
- Delete `backend/smartwatt_nexus.db`
- Restart application (database will be recreated)

### No Module Named 'flask'
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## Configuration

### Change Database
Edit `backend/app.py`:
```python
# SQLite (default)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartwatt_nexus.db'

# PostgreSQL (production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/smartwatt'
```

### Change Port
Edit `backend/app.py` (last line):
```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)  # Change port here
```

### Enable Debug Mode
Edit `backend/app.py`:
```python
app.config['DEBUG'] = True
```

### Disable Debug Mode (Production)
Edit `backend/app.py`:
```python
app.config['DEBUG'] = False
```

## Docker Installation (Optional)

### Prerequisites
- Docker installed (https://www.docker.com/get-started)

### Build Docker Image
```bash
docker build -t smartwatt-nexus .
```

### Run Docker Container
```bash
docker run -p 5000:5000 -v $(pwd)/backend:/app/backend smartwatt-nexus
```

### Access Application
- Open http://localhost:5000

## Updating Requirements

To update installed packages:
```bash
pip install --upgrade -r requirements.txt
```

## Virtual Environment Management

### Activate (Windows)
```cmd
venv\Scripts\activate
```

### Activate (macOS/Linux)
```bash
source venv/bin/activate
```

### Deactivate
```bash
deactivate
```

### Delete Virtual Environment
```bash
# Windows
rmdir /s venv

# macOS/Linux
rm -rf venv
```

## Performance Optimization

### For Production Deployment
1. Install Gunicorn: `pip install gunicorn`
2. Run with Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
3. Use production database (PostgreSQL)
4. Configure reverse proxy (Nginx)

### For Development
- Current setup is optimized for development
- Hot reload enabled
- Detailed error messages

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS in production
- [ ] Use strong database passwords
- [ ] Disable debug mode in production
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets

## Next Steps

After installation:
1. Create your account (register.html)
2. Add consumption data
3. View dashboard and charts
4. Generate ML predictions
5. Check bill estimates
6. Download reports

## Getting Help

If you encounter issues:
1. Check terminal/console for error messages
2. Review QUICKSTART.md for usage guide
3. Check README.md for detailed documentation
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**Successfully installed SMARTWATT NEXUS! ⚡**

Happy monitoring your electricity consumption!
