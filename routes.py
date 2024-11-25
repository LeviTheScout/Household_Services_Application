from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, Service, ServiceProfessional, ServiceRequest, Customer, User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy import or_,and_
from datetime import datetime  
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# Authentication decorator for user access
def authentication(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        flash('Please login to continue.','danger')
        return redirect(url_for('login'))
    return inner


# Admin-specific authentication decorator
def admin_authenticate(func):
    @wraps(func)
    def inner(*args, **kwargs):
        user = User.query.get(session.get('user_id'))
        if user and user.user_type == 'admin':
            return func(*args, **kwargs)
        flash('You are not authorized to access this page.')
        return redirect(url_for('login'))
    return inner

@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please fill out all fields.','danger')
            return redirect(url_for('admin_login'))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.passhash, password):
            if user.user_type == 'admin':
                session['user_id'] = user.id
                session['user_role'] = 'admin'
                flash('Admin login successful!','success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('You are not authorized as an admin.','danger')
                return redirect(url_for('admin_login'))

        flash('Invalid credentials. Please try again.','danger')
        return redirect(url_for('admin_login'))

    return render_template('admin/admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('user_role')
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password or not role:
            flash('Please fill out all the fields.','danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if user and user.is_blocked:
            flash('You are blocked by Admin.','danger')
            return redirect(url_for('login'))
        if user and check_password_hash(user.passhash, password):
            if role == 'customer' and user.user_type == 'customer':
                session['user_id'] = user.id
                session['user_role'] = 'customer'
                session['role_id']=user.customer.id
                flash('Login successful!','success')
                return redirect(url_for('dashboard'))
            elif role == 'service_professional':
                if user.user_type == 'admin':
                    session['user_id'] = user.id
                    session['user_role'] = 'service_professional'
                    flash('Login successful!','success')
                    return redirect(url_for('dashboard'))
                elif user.user_type == 'professional':
                    # Check if professional is approved
                    if user.professional and user.professional.is_approved:
                        session['user_id'] = user.id
                        session['user_role'] = 'service_professional'
                        session['role_id']=user.professional.id
                        flash('Login successful!','success')
                        return redirect(url_for('professional_dashboard'))
                    else:
                        flash('You are yet to be approved by admin.','danger')
                        return redirect(url_for('login'))

        flash('Invalid credentials. Please try again.','danger')
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
            flash('Please fill out all the fields.','danger')
            return redirect(url_for('signup_customer'))

        if password != confirm_password:
            flash('Passwords do not match.','danger')
            return redirect(url_for('signup_customer'))

        # Check if username already exists
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username is already taken.','danger')
            return redirect(url_for('signup_customer'))

        # Save user to database
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            passhash=hashed_password,
            name=name,
            address=address,
            pincode=pincode,
            user_type='customer'
        )

        db.session.add(new_user)
        db.session.flush()  # Get the user ID

        # Create customer profile
        new_customer = Customer(user_id=new_user.id)
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Signup successful! Please login.','success')
        return redirect(url_for('login'))

    return render_template('customer/register_customer.html')


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
        description = request.form.get('description')
        # Input validation
        if not all([username, password, confirm_password, address, pincode, service_type, experience]):
            flash('Please fill out all the fields.', 'danger')
            return redirect(url_for('signup_professional'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup_professional'))

        # Check if username already exists
        user_exists = User.query.filter_by(username=username).first()
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
        new_user = User(
            username=username,
            passhash=hashed_password,
            name=name,
            address=address,
            pincode=pincode,
            user_type='professional'
        )

        db.session.add(new_user)
        db.session.flush()  # Get the user ID

        # Create professional profile
        new_professional = ServiceProfessional(
            user_id=new_user.id,
            experience=experience,
            service_id=service.id,description=description
        )
        db.session.add(new_professional)
        db.session.commit()

        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))
    services=Service.query.all()
    return render_template('professional/register_professional.html',services=services)

@app.route('/logout')
@authentication
def logout():
    session.clear()
    flash('Logged out successfully.','success')
    return redirect(url_for('login'))


@app.route('/')
@authentication
def index():
    if session['user_role']=='customer':
        return redirect(url_for('dashboard'))
    elif session['user_role']=='service_professional':
        return redirect(url_for('professional_dashboard'))
    else:
        return redirect(url_for('admin_dashboard'))


@app.route('/dashboard')
@authentication
def dashboard():
    user = User.query.get(session['user_id'])
    if session['user_role'] == 'customer':
        # Fetch data for the customer dashboard
        customer = user.customer
        requests = ServiceRequest.query.filter_by(customer_id=customer.id).all()
        services = Service.query.all()
        return render_template('customer/customer_dashboard.html', requests=requests, services=services)
    flash("Invalid user role.")
    return redirect(url_for('logout'))

@app.route('/professional/dashboard', methods=['GET', 'POST'])
@authentication
def professional_dashboard():
    user = User.query.get(session['user_id'])
    if session['user_role'] == 'service_professional':
        professional = user.professional
        if request.method == 'POST':
            action = request.form.get('action')
            service_id = request.form.get('service_id')
            service_request = ServiceRequest.query.get(service_id)
            if service_request and service_request.professional_id == professional.id:
                if action == 'accept':
                    service_request.service_status = 'accepted'
                    flash('Service request accepted.', 'success')
                elif action == 'reject':
                    service_request.service_status = 'rejected'
                    flash('Service request rejected.', 'success')
                db.session.commit()
            else:
                flash('Invalid service request.', 'danger')
        requests = ServiceRequest.query.filter_by(professional_id=professional.id).all()
        return render_template('professional/professional_dashboard.html', professional=professional, requests=requests)
    flash("Invalid user role.")
    return redirect(url_for('logout'))

@app.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_authenticate
def admin_dashboard():
    if request.method == 'POST':
        # Handle POST requests for admin actions
        action = request.form.get('action')
        professional_id = request.form.get('professional_id')
        
        if action and professional_id:
            professional = User.query.get(professional_id)
            if professional:
                if action == 'approve':
                    professional.professional.is_approved = True
                    flash('Professional approved successfully.','success')
                elif action == 'reject':
                    professional.professional.is_approved = False
                    # Delete the professional profile when rejected
                    db.session.delete(professional.professional)
                    # Delete the user account as well
                    db.session.delete(professional)
                    flash('Professional rejected and account removed.','success')
                db.session.commit()
                return redirect(url_for('admin_dashboard'))

    # GET request - display dashboard
    services = Service.query.all()
    professionals = User.query.join(ServiceProfessional).filter(User.user_type=='professional', ServiceProfessional.is_approved==False).all()
    customers = User.query.filter_by(user_type='customer').all() 
    service_requests = ServiceRequest.query.all()
    return render_template('/admin/admin_dash.html', services=services, professionals=professionals, 
                         customers=customers, service_requests=service_requests)

@app.route('/admin/service/add', methods=['GET', 'POST'])
@admin_authenticate
def add_service():
    if request.method == 'POST':
        name = request.form.get('service_name')
        price = request.form.get('base_price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')

        if name and price:
            new_service = Service(name=name, price=price, time_required=time_required, description=description)
            db.session.add(new_service)
            db.session.commit()
            flash('Service added successfully.','success')
        else:
            flash('Please fill out all the required fields.','danger')

        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_service.html')

@app.route('/admin/service/edit/<int:service_id>', methods=['GET', 'POST'])
@admin_authenticate
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            db.session.delete(service)
            db.session.commit()
            flash('Service deleted successfully.','success')
            return redirect(url_for('admin_dashboard'))
        else:
            service.name = request.form.get('service_name')
            service.price = request.form.get('base_price')
            service.time_required = request.form.get('time_required')
            service.description = request.form.get('description')
            db.session.commit()
            flash('Service updated successfully.','success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_service.html', service=service)






@app.route('/profile', methods=['GET', 'POST'])
@authentication
def profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        name = request.form.get('name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if not current_password or not new_password:
            flash('Please fill out all the required fields.','danger')
            return redirect(url_for('profile'))

        if not check_password_hash(user.passhash, current_password):
            flash('Current password is incorrect.','danger')
            return redirect(url_for('profile'))

        user.name = name
        user.passhash = generate_password_hash(new_password)
        db.session.commit()
        flash('Profile updated successfully.','success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)



# Route to handle admin service approval (example)
@app.route('/service_selection', methods=['POST'])
@authentication
def service_selection():
    service_name = request.form.get('service')
    if service_name:
        service = Service.query.filter_by(name=service_name).first()  # Query for the service in the Service table
        if service:
            return redirect(url_for('service_request', service_name=service_name))  # Pass the service name as a parameter
    flash('Service not found.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/service_selection/<service_name>', methods=['GET', 'POST'])
@authentication
def service_request(service_name):
    if request.method == 'POST':
        service = Service.query.filter_by(name=service_name).first()
        if not service:
            flash('Service ID could not be determined.', 'danger')
            return redirect(url_for('dashboard'))
        
        additional_info = request.form.get('additional_info')
        professional_id = request.form.get('professional_id')
        date_requested = request.form.get('date_requested')
        
        if service.id and additional_info and professional_id and date_requested:
            user = User.query.get(session['user_id'])
            customer = user.customer
            
            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.id,
                remarks=additional_info,
                professional_id=professional_id,
                date_of_request=datetime.strptime(date_requested, '%Y-%m-%d').date()
            )
            db.session.add(service_request)
            db.session.commit()
            flash('Service request submitted successfully.', 'success')
            return redirect(url_for('dashboard'))

    # Fetch all approved professionals who provide the specified service
    service = Service.query.filter_by(name=service_name).first()
    professionals = ServiceProfessional.query.filter_by(
        service_id=service.id,
        is_approved=True
    ).all()
    
    return render_template('customer/service_selection.html', service=service, professionals=professionals, service_name=service_name)

@app.route('/edit_request/<int:request_id>', methods=['GET', 'POST'])
@authentication
def edit_request(request_id):
    # Fetch the service request
    service_request = ServiceRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete':
            db.session.delete(service_request)
            db.session.commit()
            flash('Service Request cancelled successfully.', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after delete

        # Update fields
        service_request.remarks = request.form.get('remarks')
        service_request.date_of_request = datetime.strptime(
            request.form.get('date_of_request'), "%Y-%m-%d"
        ).date()  # Ensure it's a `date` object

        db.session.commit()
        flash('Service request updated successfully.', 'success')
        return redirect(url_for('dashboard'))  # Redirect to dashboard after update

    return render_template('customer/edit_request.html', request=service_request)


@app.route('/close_service/<int:request_id>', methods=['GET', 'POST'])
@authentication
def close_service(request_id):
    service_request = ServiceRequest.query.filter_by(id=request_id).first()
    if request.method == 'POST':
        service_request.rating = request.form.get('rating')
        service_request.review = request.form.get('review')
        service_request.close_request()
        db.session.commit()
        flash('Service request closed successfully.','success')
        return redirect(url_for('dashboard'))
    return render_template('customer/close_service.html', request=service_request)

@app.route('/search', methods=['GET', 'POST'])
@authentication
def search():
    search_type = None
    search_term = None
    
    if session['user_role'] == 'customer':
        requests = None
        professionals = None
        services = None

        if request.method == 'POST':
            search_type = request.form.get('search_type')
            search_term = request.form.get('search_term')

            if search_type == 'services':
    # Search for professionals providing the specified service
                services = ServiceProfessional.query.join(Service, ServiceProfessional.service_id == Service.id) \
                    .join(User, ServiceProfessional.user_id == User.id) \
                    .outerjoin(ServiceRequest, ServiceRequest.professional_id == ServiceProfessional.id) \
                    .with_entities(
                        User.name.label('professional_name'),
                        User.pincode,
                        Service.name.label('service_name'),
                        db.func.avg(ServiceRequest.rating).label('average_rating'),
                        db.func.count(ServiceRequest.id).label('total_requests')
                    ) \
                    .filter(
                        Service.name.ilike(f"%{search_term}%"),  # Filter by service name
                        ServiceProfessional.is_approved == True,  # Only approved professionals
                        User.pincode == User.pincode  # Filter by pincode if provided
                    ) \
                    .group_by(
                        User.name, User.pincode, Service.name
                    ) \
                    .all()
            elif search_type == 'service_professionals':
                # Search for service professionals
                professionals = ServiceProfessional.query.join(User, ServiceProfessional.user_id == User.id) \
                    .filter(
                        User.name.ilike(f"%{search_term}%"),
                        ServiceProfessional.is_approved == True
                    ).all()
            # elif search_type == 'services':
            #     # Search for available services
            #     services = Service.query.filter(
            #         Service.name.ilike(f"%{search_term}%")
            #     ).all()

        return render_template('customer/customer_search.html', search_type=search_type, 
                                professionals=professionals, services=services)

    elif session['user_role'] == 'service_professional':

        customers = None

        if request.method == 'POST':
            search_term = request.form.get('search_term')

                # Search for customers linked to the professional's requests
            customers = Customer.query.join(User, Customer.user_id == User.id) \
                .join(ServiceRequest, ServiceRequest.customer_id == Customer.id) \
                .filter(
                    or_(
                        User.name.ilike(f"%{search_term}%"),
                        User.pincode.ilike(f"%{search_term}%"),
                        User.address.ilike(f"%{search_term}%")
                    ),
                    ServiceRequest.professional_id == session['role_id']
                ).all()

        return render_template('professional/professional_search.html', customers=customers)

    return "Unauthorized", 403

@app.route('/admin/search', methods=['GET', 'POST'])
@admin_authenticate
def admin_search():
    search_type = None

    search_term = None
    # Define valid parameters for each search type
    professionals=None
    services=None
    customers=None

    if request.method == 'POST':
        search_type = request.form.get('search_type')
        search_term = request.form.get('search_term')

        # Validate search type

        if search_type == 'customers':
                customers = Customer.query.join(User).filter(
                    or_(
                        User.name.ilike('%' + search_term + '%'),
                        User.pincode.ilike('%' + search_term + '%'),
                        User.address.ilike('%' + search_term + '%')
                    )
                ).all()
        elif search_type == 'service_professionals':
            
            professionals = ServiceProfessional.query.join(User).join(Service).filter(
                or_(
                    User.name.ilike('%' + search_term + '%'),
                    User.pincode.ilike('%' + search_term + '%'),
                    User.address.ilike('%' + search_term + '%'),
                    Service.name.ilike('%' + search_term + '%')  # Search by service name
                )
            ).all()

        elif search_type == 'services':
            services = Service.query.filter(
                or_(
                    Service.name.ilike('%' + search_term + '%'),
                    Service.description.ilike('%' + search_term + '%')
                )
            ).all()


    return render_template(
        'admin/admin_search.html',
        search_type=search_type,
        professionals=professionals,
        services=services,
        customers=customers
    )

@app.route('/professional/<int:professional_id>', methods=['GET', 'POST'])
@admin_authenticate
def professional_profile(professional_id):
    professional = ServiceProfessional.query.filter_by(id=professional_id).first()

    # Handle case where the professional does not exist
    if not professional:
        return "Professional not found", 404

    if request.method == 'POST':
        # Toggle the blocking status
        professional.user.is_blocked = not professional.user.is_blocked
        db.session.commit()
        status = "unblocked" if not professional.user.is_blocked else "blocked"
        flash(f"Professional has been successfully {status}.", "success")

    requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()
    return render_template('professional_profile.html', professional=professional, requests=requests)

@app.route('/customer/<int:customer_id>', methods=['GET', 'POST'])
@admin_authenticate
def customer_profile(customer_id):
    customer = Customer.query.filter_by(id=customer_id).first_or_404()
    
    if request.method == 'POST':
        customer.user.is_blocked = not customer.user.is_blocked  # Toggle blocked state
        db.session.commit()
        flash(f"Customer '{customer.user.name}' has been {'unblocked' if not customer.user.is_blocked else 'blocked'}.", "success")
        return redirect(request.url)
    
    requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()
    return render_template('customer_profile.html', customer=customer, requests=requests)



@app.route('/summary', methods=['GET', 'POST'])
@authentication
def summary():
    role = session.get('user_role')
    role_id = session.get('role_id')

    if role == 'customer':
        # Fetch counts for customer requests
        closed_requests = ServiceRequest.query.filter_by(customer_id=role_id, service_status='closed').count()
        accepted_requests = ServiceRequest.query.filter_by(customer_id=role_id, service_status='accepted').count()
        requested_requests = ServiceRequest.query.filter_by(customer_id=role_id, service_status='requested').count()

        # Bar chart for customer
        labels = ['Closed Requests', 'Accepted Requests', 'Requested Requests']
        counts = [closed_requests, accepted_requests, requested_requests]
        fig, ax = plt.subplots()
        ax.bar(labels, counts, color=['green', 'blue', 'orange'])
        ax.set_ylabel('Number of Requests')
        ax.set_title('Service Request Status for Customer')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()

        return render_template('customer/customer_stats.html', plot_url=plot_url)

    elif role == 'service_professional':
        # Fetch counts for professional requests
        status_labels = ['Closed Requests', 'Accepted Requests', 'Requested Requests']
        status_counts = [
            ServiceRequest.query.filter_by(professional_id=role_id, service_status='closed').count(),
            ServiceRequest.query.filter_by(professional_id=role_id, service_status='accepted').count(),
            ServiceRequest.query.filter_by(professional_id=role_id, service_status='requested').count(),
        ]

        # First chart: Request status
        fig1, ax1 = plt.subplots()
        ax1.bar(status_labels, status_counts, color=['green', 'blue', 'orange'])
        ax1.set_ylabel('Number of Requests')
        ax1.set_title('Service Request Status for Professional')
        img1 = io.BytesIO()
        plt.savefig(img1, format='png')
        img1.seek(0)
        plot_url_status = base64.b64encode(img1.getvalue()).decode('utf8')
        plt.close()

        # Fetch counts for professional ratings
        rating_labels = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars']
        rating_counts = [
            ServiceRequest.query.filter_by(professional_id=role_id, rating=1).count(),
            ServiceRequest.query.filter_by(professional_id=role_id, rating=2).count(),
            ServiceRequest.query.filter_by(professional_id=role_id, rating=3).count(),
            ServiceRequest.query.filter_by(professional_id=role_id, rating=4).count(),
            ServiceRequest.query.filter_by(professional_id=role_id, rating=5).count(),
        ]

        # Second chart: Rating distribution
        fig2, ax2 = plt.subplots()
        ax2.bar(rating_labels, rating_counts, color=['red', 'orange', 'yellow', 'green', 'blue'])
        ax2.set_ylabel('Number of Ratings')
        ax2.set_title('Rating Distribution')
        img2 = io.BytesIO()
        plt.savefig(img2, format='png')
        img2.seek(0)
        plot_url_ratings = base64.b64encode(img2.getvalue()).decode('utf8')
        plt.close()

        return render_template(
            'professional/professional_stats.html',
            plot_url_status=plot_url_status,
            plot_url_ratings=plot_url_ratings
        )

    else:
        # Redirect or show an error if the role is invalid
        flash(session['user_role'])
        return redirect(url_for('dashboard'))
    

@app.route('/admin_summary', methods=['GET', 'POST'])
@admin_authenticate
def admin_summary():
    # Count users by type
    customers_count = User.query.filter_by(user_type='customer').count()
    professionals_count = User.query.filter_by(user_type='professional').count()

    # Count service request statuses
    closed_requests = ServiceRequest.query.filter_by(service_status='closed').count()
    accepted_requests = ServiceRequest.query.filter_by(service_status='accepted').count()
    requested_requests = ServiceRequest.query.filter_by(service_status='requested').count()

    # Visualization 1: User roles
    labels_users = ['Customers', 'Service Professionals']
    counts_users = [customers_count, professionals_count]
    fig1, ax1 = plt.subplots()
    ax1.bar(labels_users, counts_users, color=['blue', 'green'])
    ax1.set_ylabel('Number of Users')
    ax1.set_title('Users Distribution')
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    plot_url_users = base64.b64encode(img1.getvalue()).decode('utf8')
    plt.close()

    # Visualization 2: Service request statuses
    labels_requests = ['Closed Requests', 'Accepted Requests', 'Requested Requests']
    counts_requests = [closed_requests, accepted_requests, requested_requests]
    fig2, ax2 = plt.subplots()
    ax2.bar(labels_requests, counts_requests, color=['green', 'blue', 'orange'])
    ax2.set_ylabel('Number of Requests')
    ax2.set_title('Service Request Statuses')
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plot_url_requests = base64.b64encode(img2.getvalue()).decode('utf8')
    plt.close()

    return render_template(
        'admin/admin_stats.html',
        plot_url_users=plot_url_users,
        plot_url_requests=plot_url_requests
    )


@app.route('/admin/users', methods=['GET', 'POST'])
@admin_authenticate
def admin_users():
    # Fetch all users, segregating by customer and professional
    customers = User.query.join(Customer).all()
    professionals = User.query.join(ServiceProfessional).all()

    # For each professional, calculate the average rating if available
    for professional in professionals:
        # Assuming you have a ServiceRequest model where ratings are stored
        service_requests = ServiceRequest.query.filter_by(professional_id=professional.professional.id).all()
        if service_requests:
            ratings = [request.rating for request in service_requests if request.rating is not None]
            professional.avg_rating = sum(ratings) / len(ratings) if ratings else 0
        else:
            professional.avg_rating = 0

    return render_template('admin/admin_users.html', customers=customers, professionals=professionals)
