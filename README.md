# MAD-I Project

# 🏠 Household Services Application

A full-stack web application to connect customers with service professionals for household tasks such as cleaning, plumbing, and repairs.  
The platform supports **role-based dashboards**, **service requests**, **booking management**, and **admin oversight**.

---

## 📑 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)

---

## 🚀 Features
- **Role-based access**:
  - **Customer**: Browse services, place requests, track orders
  - **Service Professional**: Accept jobs, manage schedules
  - **Admin**: Approve professionals, monitor platform usage
- **Service request lifecycle**: From creation → assignment → completion
- **Authentication & Authorization** using Flask-Login
- **Email notifications** for important actions
- **Background jobs** using Celery + Redis
- **Data management** with SQLAlchemy ORM

---

## 🛠 Tech Stack
**Backend**: Flask, Flask-Login, Flask-SQLAlchemy  
**Frontend**: HTML, CSS, JavaScript (Vanilla / Template-based)  
**Database**: SQLite (development), PostgreSQL/MySQL (production-ready)  
**Task Queue**: Celery + Redis  
**Email Service**: Flask-Mail / SMTP  
**Others**: Jinja2 Templates, Bootstrap

---

## 📂 Project Structure
```
Household_Services_Application/
│
├── app/                      # Application package
│   ├── __init__.py           # App factory
│   ├── models.py             # Database models
│   ├── routes/               # Route definitions
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JS, Images
│   ├── forms.py              # WTForms classes
│   ├── utils/                # Helper functions
│   └── tasks.py              # Celery tasks
│
├── migrations/               # Database migrations
├── requirements.txt          # Python dependencies
├── config.py                  # App configuration
├── run.py                     # Entry point
└── README.md                  # Project documentation
```

---

## ⚙ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/LeviTheScout/Houshold_Services_Application.git
cd Houshold_Services_Application
```

### 2️⃣ Create a virtual environment & install dependencies
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3️⃣ Configure environment variables
Create a `.env` file:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///database.db
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
REDIS_URL=redis://localhost:6379/0
```

### 4️⃣ Initialize the database
```bash
flask db init
flask db migrate
flask db upgrade
```

### 5️⃣ Start Redis & Celery
```bash
redis-server
celery -A app.celery worker -l info
celery -A app.celery beat -l info
```

### 6️⃣ Run the Flask app
```bash
flask run
```
App will be available at **http://127.0.0.1:5000/**

---

## 🖥 Usage
1. **Register/Login** as a Customer, Service Professional, or Admin  
2. **Customers** can browse services and request them  
3. **Professionals** can accept and complete requests  
4. **Admins** manage users, services, and reports
   

"""
