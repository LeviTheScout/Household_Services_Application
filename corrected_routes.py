
@app.before_first_request
def setup_admin():
    create_default_admin()


from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, Service, ServiceProfessional, ServiceRequest, Customer
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


# Authentication decorator for user access
def authentication(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        flash('Please login to continue.')
        return redirect(url_for('login'))
    return inner


# Admin-specific authentication decorator
def admin_authenticate(func):
    @wraps(func)
    def inner(*args, **kwargs):
        user = ServiceProfessional.query.get(session.get('user_id'))
        if user and session.get('user_role') == 'service_professional' and user.is_admin:
            return func(*args, **kwargs)
        flash('You are not authorized to access this page.')
        return redirect(url_for('login'))
    return inner


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('user_role')
        username = request.form.get('username')
        password = request.form.get('password')

        # Input validation
        if not username or not password or not role:
            flash('Please fill out all the fields.')
            return redirect(url_for('login'))

        # Authenticate based on role
        user = None
        if role == 'customer':
            user = Customer.query.filter_by(username=username).first()
        elif role == 'service_professional':
            user = ServiceProfessional.query.filter_by(username=username).first()

        if user and check_password_hash(user.passhash, password):
            session['user_id'] = user.id
            session['user_role'] = role
            flash('Login successful!')
            return redirect(url_for('dashboard'))

        flash('Invalid credentials. Please try again.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup/customer', methods=['GET', 'POST'])
def signup_customer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        # Input validation
        if not all([username, password, confirm_password, address, pincode]):
            flash('Please fill out all the fields.')
            return redirect(url_for('signup_customer'))

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup_customer'))

        # Check if username already exists
        user_exists = Customer.query.filter_by(username=username).first()
        if user_exists:
            flash('Username is already taken.')
            return redirect(url_for('signup_customer'))

        # Save user to database
        hashed_password = generate_password_hash(password)
        new_user = Customer(username=username, passhash=hashed_password, name=name, address=address, pincode=pincode)

        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register_customer.html')


@app.route('/signup/professional', methods=['GET', 'POST'])
def signup_professional():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')

        # Input validation
        if not all([username, password, confirm_password, address, pincode, service_type, experience]):
            flash('Please fill out all the fields.', 'danger')
            return redirect(url_for('signup_professional'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup_professional'))

        # Check if username already exists
        user_exists = ServiceProfessional.query.filter_by(username=username).first()
        if user_exists:
            flash('Username is already taken.', 'danger')
            return redirect(url_for('signup_professional'))

        # Check if service type exists
        service = Service.query.filter_by(name=service_type).first()
        if not service:
            flash('Selected service type does not exist.', 'danger')
            return redirect(url_for('signup_professional'))

        # Save professional to the database
        hashed_password = generate_password_hash(password)
        new_user = ServiceProfessional(
            username=username,
            passhash=hashed_password,
            name=name,
            address=address,
            pincode=pincode,
            experience=experience,
            service_id=service.id
        )

        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register_professional.html')

@app.route('/logout')
@authentication
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('login'))


@app.route('/dashboard')
@authentication
def dashboard():
    if session['user_role'] == 'customer':
        # Fetch data for the customer dashboard
        services = ServiceRequest.query.filter_by(customer_id=session['user_id']).all()
        return render_template('customer_dashboard.html', services=services)
    elif session['user_role'] == 'service_professional':
        # Fetch data for the service professional dashboard
        requests = ServiceRequest.query.filter_by(professional_id=session['user_id']).all()
        professional = ServiceProfessional.query.get(session['user_id'])  # Use get() to retrieve a single instance
        return render_template('professional_dashboard.html', professional=professional, requests=requests)
    
    flash("Invalid user role.")
    return redirect(url_for('logout'))

@app.route('/')
@authentication
def home():
    user = Customer.query.get(session['user_id']) or ServiceProfessional.query.get(session['user_id'])
    if session['user_role'] == 'service_professional' and user.is_admin:
        return redirect(url_for('admin'))
    return redirect(url_for('dashboard'))


@app.route('/profile', methods=['GET', 'POST'])
@authentication
def profile():
    user = Customer.query.get(session['user_id']) or ServiceProfessional.query.get(session['user_id'])

    if request.method == 'POST':
        name = request.form.get('name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if not current_password or not new_password:
            flash('Please fill out all the required fields.')
            return redirect(url_for('profile'))

        if not check_password_hash(user.passhash, current_password):
            flash('Current password is incorrect.')
            return redirect(url_for('profile'))

        user.name = name
        user.passhash = generate_password_hash(new_password)
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/admin')
@admin_authenticate
def admin_dashboard():
    services = Service.query.all()
    users = ServiceProfessional.query.filter_by(is_admin=False).all()
    return render_template('admin_dash.html', services=services, users=users)


# Route to handle admin service approval (example)

@app.route('/service_selection', methods=['POST'])
@authentication
def service_selection():
    service_name = request.form.get('service')
    if service_name:
        service = Service.query.filter_by(name=service_name).first()  # Query for the service in the Service table
        if service:
            return redirect(url_for(service_name.lower()))  # Redirect to the corresponding service route
    return redirect(url_for('dashboard'))

@app.route('/service_selection/cleaning', methods=['GET', 'POST'])
@authentication
def cleaning():
    return handle_service_request('Cleaning', 'services/cleaning.html')

@app.route('/service_selection/plumbing', methods=['GET', 'POST'])
@authentication
def plumbing():
    return handle_service_request('Plumber', 'services/plumbing.html')

@app.route('/service_selection/electrician', methods=['GET', 'POST'])
@authentication
def electrician():
    return handle_service_request('Electrician', 'services/electrician.html')

@app.route('/service_selection/salon', methods=['GET', 'POST'])
@authentication
def salon():
    return handle_service_request('Salon', 'services/salon.html')

def handle_service_request(service_name, template_name):
    if request.method == 'POST':
        service = Service.query.filter_by(name=service_name).first()
        service_id = service.id
        if not service_id:
            flash('Service ID could not be determined.', 'error')
            return redirect(url_for('dashboard'))
        
        # Ensure additional_info and professional_id are retrieved correctly
        additional_info = request.form.get('additional_info')  # Get additional info from the form
        professional_id = request.form.get('professional_id')  # Get the professional ID from the form
        
        # Check if all required fields are present
        if service_id and additional_info and professional_id:
            service_request = ServiceRequest(
                service_id=service_id,
                customer_id=session['user_id'],
                remarks=additional_info,
                professional_id=professional_id
            )
            db.session.add(service_request)
            db.session.commit()
            flash('Service request submitted successfully.')
            return redirect(url_for('dashboard'))

    # Fetch all professionals who provide the specified service
    service = Service.query.filter_by(name=service_name).first()
    professionals = ServiceProfessional.query.filter_by(service_id=service.id).all()
    
    return render_template(template_name, service=service, professionals=professionals)


@app.route('/admin/approve/<int:service_id>', methods=['POST'])
@admin_authenticate
def approve_service(service_id):
    service = Service.query.get_or_404(service_id)
    service.is_approved = True
    db.session.commit()
    flash('Service approved successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/service/close/<int:service_id>', methods=['POST'])
@authentication
def close_service(service_id):
    # Fetch the service request by ID
    service_request = ServiceRequest.query.get_or_404(service_id)
    
    if session['user_role'] == 'customer' and service_request.customer_id == session['user_id']:
        service_request.close_request()
        db.session.commit()
        flash('Service closed successfully!')
        return redirect(url_for('dashboard'))
    
    flash('Unauthorized action.')
    return redirect(url_for('dashboard'))