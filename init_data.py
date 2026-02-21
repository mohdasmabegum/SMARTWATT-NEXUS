"""
Data initialization script - Add sample data for testing
Run this script to populate the database with sample consumption data
"""
from app import app, db, User, ConsumptionRecord, Prediction
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

def init_sample_data():
    """Initialize database with sample data"""
    
    with app.app_context():
        # Clear existing data (optional)
        # db.drop_all()
        db.create_all()
        
        print("Creating sample users...")
        
        # Create sample users
        users = [
            User(
                username='demo_user',
                email='demo@example.com',
                password=generate_password_hash('password123'),
                name='Demo User',
                meter_id='METER001'
            ),
            User(
                username='test_user',
                email='test@example.com',
                password=generate_password_hash('password123'),
                name='Test User',
                meter_id='METER002'
            )
        ]
        
        for user in users:
            existing = User.query.filter_by(username=user.username).first()
            if not existing:
                db.session.add(user)
        
        db.session.commit()
        
        print("Creating sample consumption records...")
        
        # Create sample consumption records
        today = datetime.utcnow().date()
        user = User.query.filter_by(username='demo_user').first()
        
        if user:
            # Generate 30 days of sample data
            for i in range(30, 0, -1):
                date = today - timedelta(days=i)
                
                # Create 2-4 records per day with realistic variation
                records_per_day = random.randint(2, 4)
                daily_consumption = random.uniform(20, 60)
                
                for j in range(records_per_day):
                    consumption = daily_consumption / records_per_day
                    time_offset = timedelta(hours=random.randint(0, 23), 
                                          minutes=random.randint(0, 59))
                    
                    record = ConsumptionRecord(
                        user_id=user.id,
                        consumption_kwh=consumption,
                        timestamp=datetime.combine(date, datetime.min.time()) + time_offset,
                        date=date
                    )
                    db.session.add(record)
            
            db.session.commit()
            
            print("Creating sample predictions...")
            
            # Create sample predictions
            tomorrow = today + timedelta(days=1)
            predictions = [
                Prediction(
                    user_id=user.id,
                    predicted_consumption=random.uniform(30, 55),
                    model_type='LSTM',
                    prediction_date=tomorrow,
                    confidence=0.85
                ),
                Prediction(
                    user_id=user.id,
                    predicted_consumption=random.uniform(30, 55),
                    model_type='REGRESSION',
                    prediction_date=tomorrow,
                    confidence=0.78
                ),
                Prediction(
                    user_id=user.id,
                    predicted_consumption=random.uniform(30, 55),
                    model_type='ANN',
                    prediction_date=tomorrow,
                    confidence=0.82
                )
            ]
            
            for prediction in predictions:
                db.session.add(prediction)
            
            db.session.commit()
        
        print("✓ Sample data initialization complete!")
        print("\nSample Credentials:")
        print("Username: demo_user")
        print("Password: password123")
        print("Meter ID: METER001")
        print("\nAlternative Credentials:")
        print("Username: test_user")
        print("Password: password123")
        print("Meter ID: METER002")

if __name__ == '__main__':
    init_sample_data()
    print("\n✓ Database ready! You can now log in.")
