from flask import render_template,request,redirect,url_for,flash
from app import app
from models import db, Service,ServiceProfessional,ServiceRequest,Customer
from werkzeug.security import generate_password_hash,check_password_hash

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/',methods=['POST'])
def login_post():
    role=request.form.get('user_role')
    username=request.form.get('username')
    password=request.form.get('password')
    
    if not username or not password:
        flash('Fill the empty fields')
        return redirect(url_for('login'))
    
    if role=='customer':
        customer=Customer.query.filter_by(username=username).first()
        
        if customer and check_password_hash(customer.passhash,password):
            return redirect('userdash.html')
        else:
            flash('User does not exist!')
            return redirect(url_for('signup'))
    
    elif role=='service_professional':
        professional=ServiceProfessional.query.filter_by(username=username).first()  
        if professional and check_password_hash(professional.passhash,password):
            return #do this please
        else:
            flash('User does not exist!')
            return redirect(url_for('login'))      
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('register.html')

@app.route('/signup',methods=['POST'])
def signup_post():
    username=request.form.get('username')
    password=request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    name=request.form.get('name')
    role=request.form.get('user_role')

    if not username or not password or not confirm_password:
        flash('Fill the empty fields')
        return redirect(url_for('signup'))
    if password != confirm_password:
        flash('Password is not matching.')
        return redirect(url_for('signup'))
    
    customer=Customer.query.filter_by(username=username).first()

    profesional=ServiceProfessional.query.filter_by(username=username).first()

    if customer or profesional:
        flash('Username is already taken.')
        return redirect(url_for('signup'))
    password_hash=generate_password_hash(password)

    if role=='customer':
        new_customer = Customer(username=username,passhash=password_hash, name=name)
        db.session.add(new_customer)
    elif role=='service_professional':
        new_professional=ServiceProfessional(username=username,passhash=password_hash, name=name)
        db.session.add(new_professional)

    db.session.commit()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template()

@app.route('/admindash')
def admin_dashboard():
    return render_template('admindash.html')


