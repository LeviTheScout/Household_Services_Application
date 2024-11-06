from app import app
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy(app)

class Customer(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(32),unique=True)
    passhash=db.Column(db.String(256),nullable=False)
    name=db.Column(db.String(64),nullable=True)
    service_requested=db.relationship("Service_request",backref='customer',lazy=False)

# class Service_type(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(32),unique=True)
#     services=db.relationship("Service",backref='service_type',lazy=True)

class Services(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),nullable=False)
    price=db.Column(db.Float,nullable=False)
    description=db.Column(db.String(256),nullable=True)
    providers=services=db.relationship("Service_prof",backref='service',lazy=True)
    requests=db.relationship("Service_request",backref='service',lazy=False)
    # service_type_id=db.Column(db.Integer,db.ForeignKey('service_type.id'),nullable=False)

class Service_prof(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),nullable=True)
    username=db.Column(db.String(32),unique=True)
    passhash=db.Column(db.String(256),nullable=False)
    date_created=db.Column(db.Date)
    description=db.Column(db.String(256),nullable=True)
    #want to get service this person provides
    experience=db.Column(db.String(256),nullable=True)
    service_requests=db.relationship("Service_request",backref='professional',lazy=False)

class Service_request(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    service_id=db.Column(db.Integer,db.ForeignKey('service.id'),nullable=False)
    customer_id=db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=False)
    professional_id=db.Column(db.Integer,db.ForeignKey('professional.id'),nullable=False)
    date_of_request=db.Column(db.Date)
    date_of_completion=db.Column(db.Date)
    #service_status
    remarks=db.Column(db.String(256),nullable=True)
    




