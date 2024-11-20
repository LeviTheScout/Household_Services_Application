
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Customer, ServiceProfessional
    is_active = db.Column(db.Boolean, default=True)  # Can be used for access control

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"


class Admin(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('admin', uselist=False))


class Customer(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('customer', uselist=False))


class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('service_professional', uselist=False))
    is_approved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<ServiceProfessional {self.user.username} - {'Approved' if self.is_approved else 'Pending Approval'}>"


# Default Admin creation logic
def create_default_admin():
    admin_email = "admin@example.com"
    admin_username = "admin"
    existing_admin = User.query.filter_by(role='Admin').first()
    if not existing_admin:
        admin_user = User(username=admin_username, email=admin_email, password="admin123", role="Admin")
        db.session.add(admin_user)
        db.session.commit()
        admin = Admin(user=admin_user)
        db.session.add(admin)
        db.session.commit()
        print("Default admin created.")
    else:
        print("Admin already exists.")


from app import app
from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash
db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)
    address=db.Column(db.String(128),nullable=False)
    pincode=db.Column(db.Integer,nullable=False)
    service_requests = db.relationship("ServiceRequest", backref='customer', lazy=True)
    #for admin actions
    is_blocked = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<Customer {self.username}>"
    
class ServiceProfessional(db.Model):
    __tablename__ = 'service_professional'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    address=db.Column(db.String(128),nullable=False)
    pincode=db.Column(db.Integer,nullable=False)
    date_created = db.Column(db.Date, default=datetime.datetime.utcnow)
    description = db.Column(db.String(256), nullable=True)
    experience = db.Column(db.String(64), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service_requests = db.relationship("ServiceRequest", backref='professional', lazy=True)
    #for admin actions
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    is_admin=db.Column(db.Boolean,default=False)
    def __repr__(self):
        return f"<ServiceProfessional {self.username}>"

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

    def close_request(self):
        self.service_status = "closed"
        self.date_of_completion = datetime.datetime.utcnow()

    def __repr__(self):
        return f"<ServiceRequest {self.id} - Status: {self.service_status}>"

with app.app_context():
    # Create database tables
    db.create_all()

    # Ensure an admin exists
    admin = ServiceProfessional.query.filter_by(is_admin=True).first()
    if not admin:
        passhash = generate_password_hash('admin123')
        admin = ServiceProfessional(username='admin', passhash=passhash, name='Admin', is_admin=True, address='123', pincode=123)
        db.session.add(admin)

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