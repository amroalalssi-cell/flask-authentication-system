# 🔐 Flask Authentication System

A modern authentication system built with **Python, Flask, and SQLite** featuring secure user authentication, password recovery, session management, and email verification workflow.

## 🎥 Project Demo

📹 Demo Video: `demo/Video Project.mp4`

## 📸 Screenshots

| Login | Dashboard |
|--------|-----------|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |
---

git clone https://github.com/amroalalssi-cell/flask-authentication-system.git


## 🚀 Features

✅ User Registration  
✅ Secure Password Hashing using Werkzeug  
✅ User Login System  
✅ Session Management  
✅ Protected Dashboard  
✅ Logout Functionality  
✅ Forgot Password  
✅ Reset Password  
✅ Two-Factor Authentication (2FA)  
✅ User Profile Page  
✅ SQLite Database Integration  

---

## 🛠️ Technologies Used

- Python 3
- Flask
- SQLite
- Werkzeug Security
- HTML
- CSS
- JavaScript

---

## 📂 Project Structure

```
auth/
│
├── app.py
├── database.db
│
├── routes/
│   └── auth.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   └── verify_code.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

---
## 📦 Requirements

- Python 3.13+
- Flask
- Werkzeug

## 📄 License

This project is for educational and portfolio purposes.

## ⚙️ Installation

### 1. Clone the project

```bash
git clone YOUR_REPOSITORY_LINK
```

### 2. Enter project folder

```bash
cd auth
```

### 3. Create virtual environment

```bash
python -m venv .venv
```

### 4. Activate environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install requirements

```bash
pip install -r requirements.txt
```

---

## ▶️ Run The Application

```bash
python app.py
```

The application will run on:

```
http://127.0.0.1:5000
```

---

## 🔐 Authentication Flow

```
Register
   |
   ↓
Database
   |
   ↓
Login
   |
   ↓
Password Verification
   |
   ↓
Generate 2FA Code
   |
   ↓
Verify Code
   |
   ↓
Dashboard
```

---

## 🗄️ Database

The project uses SQLite.

Users table stores:

- Full Name
- Username
- Email
- Hashed Password

---

## 🔒 Security

- Passwords are stored using secure hashing.
- Sessions are used to manage authentication.
- Protected routes require user login.

---

## 📌 Future Improvements

- Send 2FA codes via Email
- Add Admin/User roles
- Use SQLAlchemy ORM
- Add User Settings
- Deploy the application online

---

## 👨‍💻 Author

Amro Alalssi

amroalalssi@gmail.com

Python Flask Developer
