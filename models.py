from app import app
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)
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
    date_created = db.Column(db.Date, default=datetime.datetime.utcnow)
    description = db.Column(db.String(256), nullable=True)
    experience = db.Column(db.String(64), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    service_requests = db.relationship("ServiceRequest", backref='professional', lazy=True)
    #for admin actions
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

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
    db.create_all()