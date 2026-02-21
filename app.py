"""
SMARTWATT-NEXUS: Electricity Consumption Monitoring & Prediction System
Main Flask Application
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timedelta
import numpy as np
from io import BytesIO
import csv

# Initialize Flask App
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
# Load config from environment with safe defaults for local development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smartwatt_nexus_secret_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///smartwatt_nexus.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)
CORS(app)

# ML models will be imported lazily inside prediction routes to avoid heavy imports

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    meter_id = db.Column(db.String(50), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    consumption_records = db.relationship('ConsumptionRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class ConsumptionRecord(db.Model):
    """Consumption Record Model"""
    __tablename__ = 'consumption_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    consumption_kwh = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<ConsumptionRecord {self.id}>'

class Alert(db.Model):
    """Alert Model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'HIGH_CONSUMPTION', 'ANOMALY', etc
    message = db.Column(db.String(255), nullable=False)
    consumption_value = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Alert {self.id}>'

class Prediction(db.Model):
    """ML Prediction Model"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    predicted_consumption = db.Column(db.Float, nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # LSTM, REGRESSION, ANN
    prediction_date = db.Column(db.Date, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.id}>'

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        # meter_id is optional (device pairing will be done separately)
        meter_id = data.get('meter_id')

        # Validation
        if not all([username, email, password, name]):
            return jsonify({'error': 'All fields are required'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            name=name,
            meter_id=meter_id if meter_id else None
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    
    return render_template('register.html')


# ==================== IOT / DEVICE ROUTES ====================

@app.route('/api/device/register', methods=['POST'])
def register_device():
    """Associate a meter/device (Arduino) with a user by meter_id"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json() or {}
    meter_id = data.get('meter_id')

    if not meter_id:
        return jsonify({'error': 'meter_id is required'}), 400

    # ensure uniqueness
    existing = User.query.filter_by(meter_id=meter_id).first()
    if existing and existing.id != session['user_id']:
        return jsonify({'error': 'This meter is already registered to another user'}), 400

    user = User.query.get(session['user_id'])
    user.meter_id = meter_id
    db.session.commit()
    return jsonify({'success': True, 'message': 'Device registered', 'meter_id': meter_id})


@app.route('/api/iot/data', methods=['POST'])
def iot_data():
    """Endpoint for Arduino / Smart Meter to post consumption readings.
    Payload: { "meter_id": "METER001", "consumption_kwh": 2.5, "timestamp": "2026-02-21T12:34:00" }
    """
    data = request.get_json() or {}
    meter_id = data.get('meter_id')
    consumption_kwh = data.get('consumption_kwh')
    ts = data.get('timestamp')

    if not meter_id or consumption_kwh is None:
        return jsonify({'error': 'meter_id and consumption_kwh are required'}), 400

    user = User.query.filter_by(meter_id=meter_id).first()
    if not user:
        return jsonify({'error': 'Unknown meter_id'}), 404

    try:
        if ts:
            timestamp = datetime.fromisoformat(ts)
            date_only = timestamp.date()
        else:
            timestamp = datetime.utcnow()
            date_only = timestamp.date()
    except Exception:
        timestamp = datetime.utcnow()
        date_only = timestamp.date()

    record = ConsumptionRecord(
        user_id=user.id,
        consumption_kwh=float(consumption_kwh),
        timestamp=timestamp,
        date=date_only
    )
    db.session.add(record)
    db.session.commit()

    # Optionally check for anomaly/alerts
    check_consumption_anomaly(user.id, float(consumption_kwh))

    return jsonify({'success': True, 'message': 'Data received'}), 201

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User Logout"""
    session.clear()
    return redirect(url_for('login'))

# ==================== MAIN ROUTES ====================

@app.route('/')
def index():
    """Home/Dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with Current Consumption & Predictions"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Get today's consumption
    today = datetime.utcnow().date()
    today_consumption = db.session.query(db.func.sum(ConsumptionRecord.consumption_kwh)).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date == today
    ).scalar() or 0
    
    # Get last 7 days consumption
    seven_days_ago = today - timedelta(days=7)
    last_7_days = db.session.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date >= seven_days_ago
    ).all()
    
    # Get predictions
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.prediction_date.desc()).limit(7).all()
    
    # Get alerts
    alerts = Alert.query.filter_by(user_id=user_id, is_read=False).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=user,
                         today_consumption=today_consumption,
                         last_7_days=last_7_days,
                         predictions=predictions,
                         alerts=alerts)

@app.route('/daily-usage')
def daily_usage():
    """Daily Usage Report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('daily_usage.html')

@app.route('/reports')
def reports():
    """Consumption Reports"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/bill-estimation')
def bill_estimation():
    """Bill Estimation Page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('bill_estimation.html')

@app.route('/predictions')
def predictions():
    """ML Predictions Page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('predictions.html')

# ==================== API ROUTES ====================

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get User Profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'name': user.name,
        'meter_id': user.meter_id,
        'created_at': user.created_at.isoformat()
    })

@app.route('/api/consumption/add', methods=['POST'])
def add_consumption():
    """Add Consumption Record"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    consumption_kwh = data.get('consumption_kwh')
    
    if not consumption_kwh:
        return jsonify({'error': 'Consumption value required'}), 400
    
    user_id = session['user_id']
    today = datetime.utcnow().date()
    
    # Create consumption record
    record = ConsumptionRecord(
        user_id=user_id,
        consumption_kwh=consumption_kwh,
        date=today
    )
    
    db.session.add(record)
    db.session.commit()
    
    # Check for anomalies
    check_consumption_anomaly(user_id, consumption_kwh)
    
    return jsonify({'success': True, 'message': 'Consumption recorded'}), 201

@app.route('/api/consumption/daily', methods=['GET'])
def get_daily_consumption():
    """Get Daily Consumption Data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    days = request.args.get('days', 30, type=int)
    
    start_date = (datetime.utcnow().date()) - timedelta(days=days)
    
    records = db.session.query(
        ConsumptionRecord.date,
        db.func.sum(ConsumptionRecord.consumption_kwh).label('total')
    ).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date >= start_date
    ).group_by(ConsumptionRecord.date).order_by(ConsumptionRecord.date).all()
    
    return jsonify([{
        'date': str(r.date),
        'consumption': float(r.total)
    } for r in records])

@app.route('/api/consumption/current', methods=['GET'])
def get_current_consumption():
    """Get Current Consumption (Today)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    today = datetime.utcnow().date()
    
    total = db.session.query(db.func.sum(ConsumptionRecord.consumption_kwh)).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date == today
    ).scalar() or 0
    
    return jsonify({'consumption': float(total), 'date': str(today)})

@app.route('/api/predictions/generate', methods=['POST'])
def generate_predictions():
    """Generate ML Predictions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get historical data
    records = ConsumptionRecord.query.filter_by(user_id=user_id).order_by(ConsumptionRecord.date).all()
    
    if len(records) < 5:
        return jsonify({'error': 'Insufficient data for predictions'}), 400
    
    consumption_data = [r.consumption_kwh for r in records[-30:]]
    
    # Import ML models lazily to avoid heavy startup imports; fall back to simple average predictor
    try:
        from utils.ml_models import LSTMPredictor, RegressionPredictor, ANNPredictor
    except Exception:
        class _FallbackPredictor:
            @staticmethod
            def predict(data):
                if not data:
                    return 0.0
                return float(sum(data) / len(data))

        LSTMPredictor = RegressionPredictor = ANNPredictor = _FallbackPredictor

    # Generate predictions using different models
    try:
        lstm_pred = float(LSTMPredictor.predict(consumption_data))
    except Exception:
        lstm_pred = float(sum(consumption_data) / len(consumption_data))

    try:
        regression_pred = float(RegressionPredictor.predict(consumption_data))
    except Exception:
        regression_pred = float(sum(consumption_data) / len(consumption_data))

    try:
        ann_pred = float(ANNPredictor.predict(consumption_data))
    except Exception:
        ann_pred = float(sum(consumption_data) / len(consumption_data))
    
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    
    # Store predictions
    for model_type, pred_value, confidence in [
        ('LSTM', lstm_pred, 0.85),
        ('REGRESSION', regression_pred, 0.78),
        ('ANN', ann_pred, 0.82)
    ]:
        prediction = Prediction(
            user_id=user_id,
            predicted_consumption=pred_value,
            model_type=model_type,
            prediction_date=tomorrow,
            confidence=confidence
        )
        db.session.add(prediction)
    
    db.session.commit()
    
    return jsonify({
        'lstm': float(lstm_pred),
        'regression': float(regression_pred),
        'ann': float(ann_pred),
        'average': float((lstm_pred + regression_pred + ann_pred) / 3)
    })

@app.route('/api/predictions/get', methods=['GET'])
def get_predictions():
    """Get Stored Predictions"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.prediction_date.desc()).limit(30).all()
    
    return jsonify([{
        'date': str(p.prediction_date),
        'model': p.model_type,
        'predicted_consumption': float(p.predicted_consumption),
        'confidence': float(p.confidence)
    } for p in predictions])

@app.route('/api/bill/estimate', methods=['GET'])
def estimate_bill():
    """Estimate Electricity Bill"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    days = request.args.get('days', 30, type=int)
    
    # TS Electric Department rates (per unit costs)
    # These are example rates, update with actual TS rates
    slab_rates = [
        {'from': 0, 'to': 50, 'rate': 2.80},        # 0-50 units: Rs. 2.80/unit
        {'from': 50, 'to': 100, 'rate': 3.40},      # 51-100 units: Rs. 3.40/unit
        {'from': 100, 'to': 200, 'rate': 4.60},     # 101-200 units: Rs. 4.60/unit
        {'from': 200, 'to': 500, 'rate': 6.00},     # 201-500 units: Rs. 6.00/unit
        {'from': 500, 'to': float('inf'), 'rate': 7.50}  # 500+ units: Rs. 7.50/unit
    ]
    
    start_date = (datetime.utcnow().date()) - timedelta(days=days)
    today = datetime.utcnow().date()
    
    total_consumption = db.session.query(db.func.sum(ConsumptionRecord.consumption_kwh)).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date >= start_date,
        ConsumptionRecord.date <= today
    ).scalar() or 0
    
    total_consumption = float(total_consumption)
    
    # Calculate bill based on slabs
    bill_amount = 0
    consumed = 0
    
    for slab in slab_rates:
        if consumed >= total_consumption:
            break
        
        slab_limit = min(slab['to'], total_consumption)
        units_in_slab = max(0, slab_limit - consumed)
        bill_amount += units_in_slab * slab['rate']
        consumed = slab_limit
    
    # Add taxes and charges
    fixed_charge = 100  # Fixed monthly charge
    tax_rate = 0.10  # 10% tax
    
    subtotal = bill_amount + fixed_charge
    tax_amount = subtotal * tax_rate
    total_bill = subtotal + tax_amount
    
    return jsonify({
        'consumption': total_consumption,
        'bill_amount': round(float(bill_amount), 2),
        'fixed_charge': fixed_charge,
        'tax': round(float(tax_amount), 2),
        'total_bill': round(float(total_bill), 2),
        'period_days': days
    })

@app.route('/api/alerts/get', methods=['GET'])
def get_alerts():
    """Get User Alerts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    alerts = Alert.query.filter_by(user_id=user_id).order_by(Alert.created_at.desc()).limit(20).all()
    
    return jsonify([{
        'id': a.id,
        'type': a.alert_type,
        'message': a.message,
        'consumption_value': float(a.consumption_value),
        'created_at': a.created_at.isoformat(),
        'is_read': a.is_read
    } for a in alerts])

@app.route('/api/reports/download', methods=['GET'])
def download_report():
    """Download Consumption Report as CSV"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    days = request.args.get('days', 30, type=int)
    
    start_date = (datetime.utcnow().date()) - timedelta(days=days)
    
    records = db.session.query(ConsumptionRecord).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date >= start_date
    ).order_by(ConsumptionRecord.date).all()
    
    # Create CSV content as a string and return as attachment
    csv_lines = ["Date,Consumption (kWh),Time"]
    for record in records:
        csv_lines.append(f"{record.date},{record.consumption_kwh},{record.timestamp.time()}")

    csv_data = "\n".join(csv_lines) + "\n"
    filename_id = user.meter_id if user.meter_id else (user.username or str(user.id))
    return send_file(
        BytesIO(csv_data.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'consumption_report_{filename_id}.csv'
    )

# ==================== UTILITY FUNCTIONS ====================

def check_consumption_anomaly(user_id, current_consumption):
    """Check for consumption anomalies and create alerts"""
    
    # Get average consumption from last 7 days
    seven_days_ago = (datetime.utcnow().date()) - timedelta(days=7)
    avg_consumption = db.session.query(db.func.avg(ConsumptionRecord.consumption_kwh)).filter(
        ConsumptionRecord.user_id == user_id,
        ConsumptionRecord.date >= seven_days_ago
    ).scalar()
    
    if avg_consumption:
        # Alert if consumption is 30% higher than average
        threshold = avg_consumption * 1.3
        
        if current_consumption > threshold:
            alert = Alert(
                user_id=user_id,
                alert_type='HIGH_CONSUMPTION',
                message=f'High consumption detected: {current_consumption:.2f} kWh (30% above average)',
                consumption_value=current_consumption
            )
            db.session.add(alert)
            db.session.commit()

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Ensure database tables exist
    with app.app_context():
        db.create_all()

    # Bind to all interfaces for container deployments; use env PORT if provided
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.environ.get('FLASK_ENV', 'development') != 'production', host='0.0.0.0', port=port)

# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
