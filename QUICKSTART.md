# SMARTWATT NEXUS - Quick Start Guide

## Installation & Setup

### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r ../requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Access the Web Interface
- Open your browser
- Go to `http://localhost:5000`
- You should see the login page

## First Time Setup

### Create Your Account
1. Click "Register here" link on login page
2. Fill in the registration form:
   - Full Name: Your name
   - Username: Unique username
   - Email: Your email address
   - Meter ID: Your electricity meter ID
   - Password: Strong password (min 8 chars recommended)
3. Click "Register Now"
4. You'll be redirected to login page

### Login
1. Enter your username and password
2. Click "Login"
3. You'll be taken to the dashboard

## Main Pages Overview

### 📊 Dashboard
- View today's consumption
- See 7-day average
- Check predictions for tomorrow
- View alerts and notifications
- All in one central location

### 📅 Daily Usage
- View daily consumption bar chart
- Select time period (7, 14, 30, 90 days)
- See detailed daily statistics
- Compare consumption vs average
- Identify high/low consumption days

### 🤖 Predictions
- Generate new predictions using ML models
- Compare LSTM, Regression, and ANN predictions
- View model confidence scores
- See 7-day forecast
- Understand which model performs best for your usage

### 📈 Reports
- Generate monthly, quarterly, or annual reports
- View consumption summary statistics
- Download reports as CSV
- Print reports for offline viewing
- Track consumption trends over time

### 💰 Bill Estimation
- Calculate estimated bill for any period
- See detailed bill breakdown:
  - Energy charges (based on consumption)
  - Fixed monthly charges
  - Tax (10%)
  - Total amount due
- Learn about TS Electric Department tariff slabs
- Understand progressive pricing

## Adding Consumption Data

The system needs historical consumption data to make predictions.

### Method 1: Manual Entry (Test Data)
You can add test data through the API:
```bash
# Using Python
import requests
import json

# Register and get session
response = requests.post('http://localhost:5000/login', json={
    'username': 'your_username',
    'password': 'your_password'
})

# Add consumption
requests.post('http://localhost:5000/api/consumption/add', json={
    'consumption_kwh': 25.5
})
```

### Method 2: Smart Meter Integration
Future versions will support:
- MQTT protocol for IoT devices
- REST API for smart meter data
- Direct database import

## Understanding the ML Models

### LSTM (Long Short-Term Memory) - 85% Confidence
- Analyzes your consumption patterns over time
- Best for irregular usage patterns
- Learns from your specific history
- Remembers long-term dependencies

### Regression Model - 78% Confidence
- Uses linear and random forest algorithms
- Best for stable, predictable consumption
- Fast and lightweight
- Good for baseline predictions

### Artificial Neural Networks (ANN) - 82% Confidence
- Deep learning approach
- Handles non-linear relationships
- Best for complex consumption patterns
- Most flexible model

### Ensemble Average - ~82% Confidence
- Combines all three models
- Most reliable prediction
- Recommended for important decisions

## Understanding Your Bills

### Tariff Structure (TS Electric Department)
```
Units Used          Rate per Unit
0 - 50             ₹ 2.80
51 - 100           ₹ 3.40
101 - 200          ₹ 4.60
201 - 500          ₹ 6.00
500+               ₹ 7.50
```

### Example Bill Calculation
If you consume 150 units:
- First 50 units: 50 × ₹2.80 = ₹140
- Next 50 units: 50 × ₹3.40 = ₹170
- Next 50 units: 50 × ₹4.60 = ₹230
- Subtotal: ₹540
- Fixed Charge: ₹100
- Subtotal with Fixed: ₹640
- Tax (10%): ₹64
- **Total Bill: ₹704**

## Alert System

### High Consumption Alert
- Triggered when consumption exceeds 30% above your 7-day average
- Appears on dashboard as an alert
- Helps you identify unusual usage

### Status Indicators
- 🔴 **Red**: Consumption is high (>120% of average)
- 🟡 **Yellow**: Normal consumption (80-120% of average)
- 🟢 **Green**: Low consumption (<80% of average)

## Tips for Using SMARTWATT NEXUS

### 1. Maintain Consistent Data
- Ensure consumption data is updated regularly
- Daily updates provide better predictions
- At least 7 days of data needed for predictions

### 2. Review Reports Regularly
- Check monthly reports to spot trends
- Download reports for your records
- Compare month-to-month consumption

### 3. Monitor Alerts
- Act on high consumption alerts
- Identify appliances causing spikes
- Take corrective measures

### 4. Use Predictions
- Plan your usage based on predictions
- Understand demand patterns
- Make informed decisions about appliance usage

### 5. Track Your Bill
- Regularly check bill estimates
- Understand what you're paying for
- Budget accordingly

## Common Issues & Solutions

### Issue: No data showing on dashboard
**Solution**: 
- Ensure at least one consumption record is added
- Check that database file exists (smartwatt_nexus.db)
- Restart the application

### Issue: ML predictions not generating
**Solution**:
- Ensure at least 5 days of consumption history
- Check that TensorFlow is installed
- Try refreshing the page

### Issue: Charts not displaying
**Solution**:
- Clear browser cache
- Ensure JavaScript is enabled
- Try a different browser

### Issue: Can't login
**Solution**:
- Verify username and password
- Check that database exists
- Try registering a new account

## Database Location
- File: `smartwatt_nexus.db` (in backend folder)
- Type: SQLite
- Backup: Create copies of this file for backup

## Accessing the API

All API endpoints are available at:
`http://localhost:5000/api/`

Example:
```
GET  http://localhost:5000/api/consumption/current
GET  http://localhost:5000/api/consumption/daily?days=30
POST http://localhost:5000/api/predictions/generate
GET  http://localhost:5000/api/bill/estimate?days=30
```

## System Architecture

```
Browser (Frontend)
    ↓
Flask Web Server (Port 5000)
    ↓
SQLAlchemy ORM
    ↓
SQLite Database
    ↓
ML Models (TensorFlow/Scikit-learn)
```

## Production Deployment

To deploy to production:

1. Change `debug=False` in app.py
2. Use production WSGI server (Gunicorn)
3. Set up proper database (PostgreSQL)
4. Configure email notifications
5. Set up SSL/HTTPS
6. Deploy on cloud platform (Heroku, AWS, etc.)

## Support & Documentation

- Check README.md for detailed documentation
- Review error messages in terminal
- Check Flask debug output for issues
- All features are self-documented in the UI

---

**Enjoy monitoring your electricity consumption! ⚡**
