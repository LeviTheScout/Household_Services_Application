from flask import render_template,request,redirect,url_for,flash, session
from app import app
from models import db, Service,ServiceProfessional,ServiceRequest,Customer
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps

@app.route('/login')
def login():
    
    return render_template('login.html')

# @app.route('/',methods=['POST'])
@app.route('/login',methods=['POST'])
def login_post():
    role=request.form.get('user_role')
    username=request.form.get('username')
    password=request.form.get('password')
    
    if not username or not password or not role: 
        flash('Fill the empty fields')
        return redirect(url_for('login'))
    
    user = None
    if role == 'customer':
        user = Customer.query.filter_by(username=username).first()
    elif role == 'service_professional':
        user = ServiceProfessional.query.filter_by(username=username).first()

    if user:
        if check_password_hash(user.passhash, password):
            session['user_id'] = user.id
            session['user_role'] = 'customer' if isinstance(user, Customer) else 'service_professional'
            flash('Login successful')
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong password')
    else:
        flash('User does not exist!')

    return redirect(url_for('login'))

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
    address=request.form.get('address')
    pincode=request.form.get('pincode')

    if not username or not password or not confirm_password or not role or not address or not pincode:
        flash('Fill the empty fields')
        return redirect(url_for('signup'))
    if password != confirm_password:
        flash('Password is not matching.')
        return redirect(url_for('signup'))
    user = Customer.query.filter_by(username=username).first() or ServiceProfessional.query.filter_by(username=username).first()

    if user:
        flash('Username is already taken.')
        return redirect(url_for('signup'))

    password_hash = generate_password_hash(password)
    new_user = Customer(username=username, passhash=password_hash, name=name, address=address, pincode=pincode) if role == 'customer' else ServiceProfessional(username=username, passhash=password_hash, name=name, address=address, pincode=pincode)
    
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

def authentication(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please Login to continue.')
            return redirect(url_for('login'))
    return inner

@app.route('/dashboard')
@authentication
def dashboard():
    return render_template('customerdash.html')

@app.route('/')
def home():
    return redirect(url_for('dashboard'))


@app.route('/admindash')
@authentication
def admin_dashboard():
 
    return render_template('admindash.html')

    
@app.route('/profile')
@authentication
def profile():
    user = Customer.query.get(session['user_id']) or ServiceProfessional.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/profile',methods=['POST'])
@authentication
def profile_post():
    name = request.form.get('name')
    # username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if not current_password or not new_password:
        flash('Please fill out all the required fields.')
        return redirect(url_for('profile'))
    user = Customer.query.get(session['user_id']) or ServiceProfessional.query.get(session['user_id'])


    if not check_password_hash(user.passhash, current_password):
        flash('Current password is incorrect.')
        return redirect(url_for('profile'))
    #if want to change username then check if username already exisits or not
    user.name = name
    user.passhash=generate_password_hash(new_password)
    db.session.commit()
    flash('Profile updated successfully.')
    return redirect(url_for('profile'))
    

@app.route('/logout')
@authentication
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))




