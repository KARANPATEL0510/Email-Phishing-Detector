from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
import mysql.connector # type: ignore
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup # type: ignore

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
logging.basicConfig(level=logging.DEBUG)

# Database Connection
def get_db_connection():
    try:
        return mysql.connector.connect(host="localhost", user="root", password="rootpassword", database="epd")
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

#  User Registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username, email, password = data.get('username'), data.get('email'), data.get('password')

        if not username or not email or not password:
            return jsonify({"success": False, "message": "All fields are required"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection failed"}), 500
        
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User already exists"}), 400

        # Insert user
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully!"})

    except Exception as e:
        logging.error(f"Error in /register: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

#  User Login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email, password = data.get('email'), data.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': 'Login successful!', 'token': 'your_token_here'}), 200
        else:
            return jsonify({'message': 'Invalid email or password.'}), 401
        
    except Exception as e:
        logging.error(f"Error in /login: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# 🔹 Forgot Password
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email, new_password = data.get('email'), data.get('new_password')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if not cursor.fetchone():
            return jsonify({"error": "User not found"}), 404

        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        conn.commit()

        return jsonify({"message": "Password updated successfully"})

    except Exception as e:
        logging.error(f"Error in /forgot-password: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Phishing Detection
def detect_phishing_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        return {"message": "Invalid URL format."}

    phishing_keywords = [
        "secure-", "bank-", "update-", "login-", "verify-", "account-", "securebanking", "securebanking-verification",
        "confirm-", "authenticate-", "security-", "fraud-", "warning-", "alert-", "notify-", "recover-", "protection-",
        "paypal-", "appleid-", "microsoft-", "google-", "amazon-", "netflix-", "facebook-", "instagram-", "whatsapp-",
        "twitter-", "support-", "helpdesk-", "customer-", "billing-", "package-", "shipping-", "track-", "delivery-",
        "ups-", "fedex-", "dhl-", "taxrefund-", "irs-", "covid-", "medicare-", "healthcare-", "mail-", "inbox-",
        "message-", "newmessage-"
    ]
    phishing_extensions = [
        ".xyz", ".tk", ".ru", ".cn", ".kp", ".ir", ".sy", ".cf", ".ml", ".ga", ".gq", ".top", ".win", ".vip",
        ".best", ".live", ".online", ".site", ".store", ".fun", ".co", ".cm", ".om", ".net"
    ]

    if any(keyword in parsed_url.netloc for keyword in phishing_keywords):
        return {"message": "Phishing detected: Suspicious keyword in URL."}

    if any(parsed_url.netloc.endswith(ext) for ext in phishing_extensions):
        return {"message": "Phishing detected: Suspicious domain extension."}

    return {"message": "Safe and trusted"}

def detect_phishing_email(email_content):
    soup = BeautifulSoup(email_content, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]

    for link in links:
        result = detect_phishing_url(link)
        if "Phishing detected" in result["message"]:
            return {"message": "Phishing detected in email content."}

    phishing_words = ["urgent", "verify", "update payment", "confirm identity", "click here", "you won"]
    if any(word in email_content.lower() for word in phishing_words):
        return {"message": "Phishing detected: Suspicious email content."}

    return {"message": "Email content is safe."}

@app.route('/api/check', methods=['POST'])
def check_phishing():
    data = request.json
    url, email_content = data.get('url'), data.get('emailContent')

    if url:
        return jsonify(detect_phishing_url(url))
    elif email_content:
        return jsonify(detect_phishing_email(email_content))
    
    return jsonify({"message": "No input provided."})

if __name__ == '__main__':
    app.run(debug=True)