# SMARTWATT NEXUS - API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication Endpoints

### Register User
Create a new user account.

**Endpoint:** `POST /register`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "meter_id": "METER123456",
    "password": "SecurePassword123"
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Registration successful"
}
```

**Error Response (400):**
```json
{
    "error": "Username already exists"
}
```

---

### Login User
Authenticate user and start session.

**Endpoint:** `POST /login`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "SecurePassword123"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Login successful"
}
```

**Error Response (401):**
```json
{
    "error": "Invalid username or password"
}
```

---

### Logout User
End user session.

**Endpoint:** `GET /logout`

**Response:** Redirects to login page

---

## User Profile Endpoints

### Get User Profile
Retrieve current user's profile information.

**Endpoint:** `GET /api/user/profile`

**Headers:** (requires session authentication)

**Success Response (200):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "name": "John Doe",
    "meter_id": "METER123456",
    "created_at": "2026-02-21T10:30:00"
}
```

**Error Response (401):**
```json
{
    "error": "Not authenticated"
}
```

---

## Consumption Data Endpoints

### Add Consumption Record
Record electricity consumption for the current day.

**Endpoint:** `POST /api/consumption/add`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "consumption_kwh": 25.5
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Consumption recorded"
}
```

---

### Get Current Consumption
Get today's total consumption.

**Endpoint:** `GET /api/consumption/current`

**Query Parameters:** None

**Success Response (200):**
```json
{
    "consumption": 45.75,
    "date": "2026-02-21"
}
```

---

### Get Daily Consumption
Get consumption data for a specified period.

**Endpoint:** `GET /api/consumption/daily`

**Query Parameters:**
- `days` (integer, optional): Number of days to retrieve (default: 30)
  - Valid values: 7, 14, 30, 60, 90, 365

**Example Request:**
```
GET /api/consumption/daily?days=30
```

**Success Response (200):**
```json
[
    {
        "date": "2026-01-22",
        "consumption": 32.45
    },
    {
        "date": "2026-01-23",
        "consumption": 28.90
    },
    {
        "date": "2026-01-24",
        "consumption": 35.60
    }
]
```

---

## ML Prediction Endpoints

### Generate Predictions
Generate new ML predictions using LSTM, Regression, and ANN models.

**Endpoint:** `POST /api/predictions/generate`

**Headers:** (requires session authentication)

**Request Body:** None

**Success Response (200):**
```json
{
    "lstm": 45.32,
    "regression": 42.15,
    "ann": 44.78,
    "average": 44.08
}
```

**Error Response (400):**
```json
{
    "error": "Insufficient data for predictions"
}
```

---

### Get Predictions
Retrieve stored predictions.

**Endpoint:** `GET /api/predictions/get`

**Query Parameters:** None

**Success Response (200):**
```json
[
    {
        "date": "2026-02-22",
        "model": "LSTM",
        "predicted_consumption": 45.32,
        "confidence": 0.85
    },
    {
        "date": "2026-02-22",
        "model": "REGRESSION",
        "predicted_consumption": 42.15,
        "confidence": 0.78
    },
    {
        "date": "2026-02-22",
        "model": "ANN",
        "predicted_consumption": 44.78,
        "confidence": 0.82
    }
]
```

---

## Bill Estimation Endpoints

### Estimate Bill
Calculate estimated electricity bill for a specified period.

**Endpoint:** `GET /api/bill/estimate`

**Query Parameters:**
- `days` (integer, optional): Number of days to calculate for (default: 30)
  - Valid values: 7, 15, 30, 60, 90, 365

**Example Request:**
```
GET /api/bill/estimate?days=30
```

**Success Response (200):**
```json
{
    "consumption": 985.45,
    "bill_amount": 3845.67,
    "fixed_charge": 100.00,
    "tax": 394.57,
    "total_bill": 4340.24,
    "period_days": 30
}
```

### Bill Calculation Details

**TS Electric Department Tariff (2026):**
- 0-50 units: ₹2.80/unit
- 51-100 units: ₹3.40/unit
- 101-200 units: ₹4.60/unit
- 201-500 units: ₹6.00/unit
- 500+ units: ₹7.50/unit

**Formula:**
```
Energy Charges = Sum of (units in each slab × slab rate)
Subtotal = Energy Charges + Fixed Charge (₹100)
Tax = Subtotal × 10%
Total Bill = Subtotal + Tax
```

---

## Alert Endpoints

### Get User Alerts
Retrieve user's alerts and notifications.

**Endpoint:** `GET /api/alerts/get`

**Query Parameters:** None

**Success Response (200):**
```json
[
    {
        "id": 1,
        "type": "HIGH_CONSUMPTION",
        "message": "High consumption detected: 65.50 kWh (30% above average)",
        "consumption_value": 65.50,
        "created_at": "2026-02-21T15:30:00",
        "is_read": false
    },
    {
        "id": 2,
        "type": "ANOMALY",
        "message": "Unusual consumption pattern detected",
        "consumption_value": 72.30,
        "created_at": "2026-02-20T18:45:00",
        "is_read": true
    }
]
```

---

## Reports Endpoints

### Download Consumption Report
Download consumption data as CSV file.

**Endpoint:** `GET /api/reports/download`

**Query Parameters:**
- `days` (integer, optional): Number of days to include (default: 30)

**Example Request:**
```
GET /api/reports/download?days=30
```

**Success Response (200):**
- Content-Type: `text/csv`
- File: `consumption_report_<meter_id>.csv`

**CSV Format:**
```
Date,Consumption (kWh),Time
2026-01-22,32.45,10:30:00
2026-01-23,28.90,14:15:00
2026-01-24,35.60,11:45:00
```

---

## Frontend Routes (HTML Pages)

### Dashboard
**Route:** `GET /dashboard`

Main dashboard with consumption overview, alerts, and predictions.

### Daily Usage Report
**Route:** `GET /daily-usage`

Daily consumption chart and statistics with time period selection.

### ML Predictions
**Route:** `GET /predictions`

ML model predictions, comparisons, and 7-day forecast.

### Reports
**Route:** `GET /reports`

Comprehensive consumption reports with download option.

### Bill Estimation
**Route:** `GET /bill-estimation`

Bill calculator with tariff information and breakdown.

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | Request processed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Check request parameters and format |
| 401 | Unauthorized | Login required or session expired |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Server encountered an error |

---

## Data Types

### Consumption (kWh)
- **Type:** Float
- **Range:** 0.00 - 999.99
- **Unit:** Kilowatt-hours

### Date
- **Format:** YYYY-MM-DD
- **Example:** 2026-02-21

### DateTime
- **Format:** ISO 8601
- **Example:** 2026-02-21T15:30:00

### Confidence
- **Type:** Float
- **Range:** 0.0 - 1.0
- **Description:** Model confidence score (0-100%)

---

## Authentication

All protected endpoints require a valid session. Session is created after successful login.

### Session Cookie
- **Name:** session
- **Duration:** 30 days
- **Secure:** HTTPOnly
- **SameSite:** Lax

### Session Management
```python
# Session is automatically managed by Flask
# No manual token handling required
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, implement:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Examples

### Python Example
```python
import requests
import json

BASE_URL = 'http://localhost:5000'
session = requests.Session()

# Register
register_data = {
    'name': 'John Doe',
    'username': 'johndoe',
    'email': 'john@example.com',
    'meter_id': 'METER123',
    'password': 'password123'
}
response = session.post(f'{BASE_URL}/register', json=register_data)
print(response.json())

# Login
login_data = {
    'username': 'johndoe',
    'password': 'password123'
}
response = session.post(f'{BASE_URL}/login', json=login_data)
print(response.json())

# Get current consumption
response = session.get(f'{BASE_URL}/api/consumption/current')
print(response.json())

# Get daily consumption
response = session.get(f'{BASE_URL}/api/consumption/daily?days=30')
print(response.json())

# Generate predictions
response = session.post(f'{BASE_URL}/api/predictions/generate')
print(response.json())

# Get bill estimate
response = session.get(f'{BASE_URL}/api/bill/estimate?days=30')
print(response.json())
```

### JavaScript Example
```javascript
const BASE_URL = 'http://localhost:5000';

// Login
async function login(username, password) {
    const response = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });
    return response.json();
}

// Get current consumption
async function getCurrentConsumption() {
    const response = await fetch(`${BASE_URL}/api/consumption/current`);
    return response.json();
}

// Get predictions
async function getPredictions() {
    const response = await fetch(`${BASE_URL}/api/predictions/get`);
    return response.json();
}

// Generate bill estimate
async function getBillEstimate(days = 30) {
    const response = await fetch(`${BASE_URL}/api/bill/estimate?days=${days}`);
    return response.json();
}
```

### cURL Example
```bash
# Register
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "meter_id": "METER123",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'

# Get current consumption
curl -X GET http://localhost:5000/api/consumption/current \
  -b cookies.txt

# Get bill estimate
curl -X GET "http://localhost:5000/api/bill/estimate?days=30" \
  -b cookies.txt
```

---

## Versioning

- **API Version:** 1.0
- **Last Updated:** February 2026
- **Status:** Production Ready

---

**API Documentation Complete ✓**

For more information, refer to README.md or QUICKSTART.md
