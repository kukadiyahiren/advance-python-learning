<p align="center">
  <img src="static/images/advanced_python_ai_web_suite_preview_small.jpg" alt="Advanced Python AI Web Suite" width="100%">
</p>

<h1 align="center">Advanced Python AI Web Suite</h1>

<p align="center">
Full-stack AI web application combining Flask, FastAPI, DeepFace, OCR, and real-time NSE stock analytics.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#demo">Demo</a> •
  <a href="#installation">Installation</a>
</p>

<p align="center">

![Stars](https://img.shields.io/github/stars/kukadiyahiren/advance-python-learning?style=social)
![Forks](https://img.shields.io/github/forks/kukadiyahiren/advance-python-learning?style=social)
![Views](https://komarev.com/ghpvc/?username=kukadiyahiren&repo=advance-python-learning&color=blue)
![Downloads](https://img.shields.io/github/downloads/kukadiyahiren/advance-python-learning/total)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-Web_App-black)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688)
![DeepFace](https://img.shields.io/badge/AI-DeepFace-purple)
![OCR](https://img.shields.io/badge/OCR-Image_Text-orange)
![NSE](https://img.shields.io/badge/Stocks-NSE_Data-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

</p>

<p align="center">
Full-stack AI web application combining Flask, FastAPI, DeepFace, OCR, and NSE stock analytics.
</p>

# Advanced Python Learning Project

A comprehensive Flask web application with FastAPI integration, featuring user management, image gallery, stock market dashboard, and AI-powered image processing.

## 🚀 Features

- **User Authentication** - Secure login system with session management
- **User Management** - Full CRUD operations via FastAPI REST API
- **Image Gallery** - Upload and manage images with OCR text extraction
- **Stock Market Dashboard** - Real-time Indian stock market data (NSE)
- **AI Hair Style Processing** - Gender detection and hair style variants using DeepFace
- **FastAPI Integration** - Modern REST API for user operations
- **Responsive UI** - Modern glassmorphism design with smooth animations

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server
- Tesseract OCR
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/herrytest/advance-python-learning.git
cd advance-python-learning
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install flask mysql-connector-python pandas yfinance nsepython deepface easyocr opencv-python pytesseract psutil scikit-learn fastapi uvicorn pydantic
```

### 4. Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr mysql-server
```

#### macOS:
```bash
brew install tesseract mysql
```

### 5. Configure MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE laravel;
CREATE USER 'laravel'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON laravel.* TO 'laravel'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Update Database Configuration

Edit `db.py` if you need to change database credentials:

```python
DB_CONFIG = {
    'user': 'laravel',
    'password': 'password',
    'host': '127.0.0.1',
    'database': 'laravel',
    'raise_on_warnings': False
}
```

### 7. Create Uploads Directory

```bash
mkdir -p uploads
```

## 🚀 Running the Application

### Start Flask Application (Main App)

```bash
python app.py
```

The Flask app will run on: **http://localhost:5000**

### Start FastAPI Service (User Management API)

Open a new terminal and run:

```bash
source venv/bin/activate  # Activate virtual environment
uvicorn fastapi_users:app --reload --port 8000
```

Or use the startup script:

```bash
./start_fastapi.sh
```

The FastAPI service will run on: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## 🔐 Default Login Credentials

- **Username:** `admin`
- **Password:** `123456`

## 📚 API Endpoints

### User Management (FastAPI)

- `POST /api/users` - Create a new user
- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Test Endpoints

- `GET /api/test/hello` - Simple hello world
- `GET /api/test/echo/{text}` - Echo text with transformations
- `POST /api/test/calculate` - Calculator API
- `GET /api/test/status` - API and database status

### Flask Routes

- `/` - Login page
- `/dashboard` - Stock market dashboard
- `/users` - User management
- `/gallery` - Image gallery
- `/upload` - Upload images

## 🏗️ Project Structure

```
myproject/
├── app.py                  # Main Flask application
├── fastapi_users.py        # FastAPI user management service
├── db.py                   # Database functions
├── ml.py                   # Machine learning utilities
├── templates/              # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── users.html
│   ├── gallery.html
│   └── upload.html
├── static/                 # Static assets
│   ├── css/
│   └── hair_assets/
├── uploads/                # Uploaded files
├── start_fastapi.sh        # FastAPI startup script
└── README.md
```

## 🔧 Configuration

### Update Login Credentials

Edit `app.py`:

```python
USERNAME = "admin"
PASSWORD = "123456"
```

### Update Stock Symbols

Edit the `fetch_stock_data()` function in `app.py` to customize stock symbols.

## 🧪 Testing

### Test FastAPI Endpoints

```bash
# Test hello endpoint
curl http://localhost:8000/api/test/hello

# Test user list
curl http://localhost:8000/api/users

# Test calculator
curl -X POST "http://localhost:8000/api/test/calculate?num1=10&num2=5&operation=add"
```

### Test Flask Application

1. Open browser and navigate to `http://localhost:5000`
2. Login with default credentials
3. Test dashboard, gallery, and user management features

## 📦 Dependencies

### Python Packages

- **Flask** - Web framework
- **FastAPI** - Modern API framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **MySQL Connector** - Database connection
- **Pandas** - Data manipulation
- **yfinance** - Stock market data
- **nsepython** - NSE India stock data
- **DeepFace** - Face analysis and recognition
- **EasyOCR** - Optical character recognition
- **OpenCV** - Image processing
- **Pytesseract** - OCR engine
- **Scikit-learn** - Machine learning

## 🐛 Troubleshooting

### Database Connection Error

Make sure MySQL is running:
```bash
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS
```

### Tesseract Not Found

Install Tesseract OCR and verify installation:
```bash
tesseract --version
```

### Port Already in Use

Change the port in `app.py` or `fastapi_users.py`:
```python
app.run(debug=True, port=5001)  # Flask
uvicorn.run(app, port=8001)     # FastAPI
```

### CUDA/GPU Warnings

The DeepFace library will show warnings if CUDA/MPS is not available. This is normal and the app will use CPU instead.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

**Hiren Kukadiya** - [GitHub](https://github.com/kukadiyahiren)

## 🙏 Acknowledgments

- Flask and FastAPI communities
- NSE Python library developers
- DeepFace and OpenCV contributors
