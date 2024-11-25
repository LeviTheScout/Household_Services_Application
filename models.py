from app import app
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(128), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin', 'customer', 'professional'
    is_blocked = db.Column(db.Boolean, default=False)
    
    # Relationship for Customer
    customer = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    # Relationship for ServiceProfessional
    professional = db.relationship('ServiceProfessional', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username} ({self.user_type})>"

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_requests = db.relationship("ServiceRequest", backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.user.username}>"

class ServiceProfessional(db.Model):
    __tablename__ = 'service_professional'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.Date, default=datetime.datetime.utcnow)
    description = db.Column(db.String(256), nullable=True)
    experience = db.Column(db.String(64), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service_requests = db.relationship("ServiceRequest", backref='professional', lazy=True)
    is_approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ServiceProfessional {self.user.username}>"

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    professionals = db.relationship("ServiceProfessional", backref='service', lazy=True)
    requests = db.relationship("ServiceRequest", backref='service', lazy=True)

    def __repr__(self):
        return f"<Service {self.name}>"



class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    date_of_request = db.Column(db.Date, default=datetime.datetime.utcnow)
    date_of_completion = db.Column(db.Date, nullable=True)
    service_status = db.Column(db.String(20), nullable=False, default="requested") 
    remarks = db.Column(db.String(256), nullable=True)

    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(256), nullable=True)


    def close_request(self):
        self.service_status = "closed"
        self.date_of_completion = datetime.datetime.utcnow()

    def __repr__(self):
        return f"<ServiceRequest {self.id} - Status: {self.service_status}>"

with app.app_context():
    # Create database tables
    db.create_all()

    # Ensure an admin exists
    admin_user = User.query.filter_by(user_type='admin').first()
    if not admin_user:
        passhash = generate_password_hash('admin123')
        admin_user = User(
            username='admin',
            passhash=passhash,
            name='Admin',
            user_type='admin',
            address='123',
            pincode=123
        )
        db.session.add(admin_user)

    # Add default services if they don't exist
    default_services = [
        {"name": "Salon", "price": 300.0, "time_required": "1 hour", "description": "Home Salon Services"},
        {"name": "Cleaning", "price": 400.0, "time_required": "3 hours", "description": "Home Cleaning Services"},
        {"name": "Electrician", "price": 200.0, "time_required": "1.5 hours", "description": "Electrical Repairs and Installations"},
        {"name": "Plumbing", "price": 250.0, "time_required": "1.5 hours", "description": "Plumbing Repairs and Installations"}
    ]

    for service_data in default_services:
        service = Service.query.filter_by(name=service_data["name"]).first()
        if not service:
            service = Service(**service_data)
            db.session.add(service)

    db.session.commit()