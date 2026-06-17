# 🛡️ Email Phishing & AI Content Detector

[![React Frontend](https://img.shields.io/badge/Frontend-React%2018-blue?logo=react&logoColor=white)](https://react.dev/)
[![Flask Backend](https://img.shields.io/badge/Backend-Flask%20(Python)-green?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database MongoDB](https://img.shields.io/badge/Database-MongoDB-mediumseagreen?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Styling Tailwind](https://img.shields.io/badge/Styling-TailwindCSS%203-38bdf8?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

A comprehensive, multi-layered security web application designed to detect email phishing links, analyze sender credibility, inspect message content, and recognize AI-generated text. The system features a responsive React dashboard, a Python (Flask) analytics backend, and a local MongoDB instance to archive scans for security auditing.

---

## 🌟 Key Features

### 1. 🔍 Multi-Layer Content Analyzer
*   **Email Body Scan**: Checks email text against social engineering triggers, urgency patterns, grammatical/casing irregularities, and credential harvesting templates.
*   **Website URL Inspection**: Detects suspicious hostnames, domain redirect patterns, lookalike brand spoofing (e.g., fake UTI domains), and sketchy Top-Level Domains (TLDs like `.xyz`, `.tk`).
*   **Sender Email ID Checker**: Examines sender addresses to flag role-based profiles (like `admin` or `support`) attempting impersonation through free email providers (such as Gmail or Yahoo).

### 2. 🤖 AI Writing & Linguistic Variance Analysis
*   **Type-Token Ratio (TTR)**: Analyzes vocabulary richness and repetition frequencies to identify automated templated writing patterns.
*   **Sentence-Length Variance**: Tracks structural variations in sentence length to differentiate between human writing style and uniform machine output.
*   **Transition Word Mapping**: Analyzes the rate and structure of logical connectors (e.g., *furthermore*, *moreover*, *consequently*) commonly overused by LLMs.

### 3. 📊 Advanced Security Reporting
*   Calculates a normalized **Suspicion Score (%)** based on ten contributing risk vectors.
*   Provides clear, actionable **Security Recommendations** and flags high-risk content for manual audit.
*   Maintains lists of verified positive and negative indicators for easy user review.
*   Features a **Recent Audit Feed** showing historic scans pulled directly from MongoDB.

---

## 💻 Tech Stack

*   **Frontend**: React (v18), Axios, TailwindCSS (v3.4), React Router DOM (v6), React Hot Toast (v2), Lucide React, Heroicons.
*   **Backend**: Python 3.x, Flask, PyMongo (database driver), BeautifulSoup4 (HTML parser for links), Urllib (URL parsing).
*   **Database**: MongoDB (Local community server).

---

## 📁 Project Structure

```text
Email-Phishing-Detector/
├── check_mongo.py                  # Database connection utility checker
└── Email Phishing Detector/        # Main project workspace
    ├── README.md                   # System documentation
    ├── .gitignore                  # Git exclusions configuration
    ├── package.json                # Frontend package configurations
    ├── tailwind.config.js          # Styling layouts
    ├── src/                        # React frontend codebase
    │   ├── App.js                  # Main router setup
    │   ├── index.js                # Core entry point
    │   ├── index.css               # Base Tailwind CSS rules
    │   └── components/             # App views & dashboard
    │       ├── Main_page.js        # Main dashboard and scanner UI
    │       ├── login.js            # User authenticator
    │       ├── registration.js     # User registration
    │       └── forgot_password.js  # Password recovery UI
    └── backend/                    # Python Flask backend
        ├── app.py                  # Main API server and risk engine
        ├── ai_detector.py          # Linguistic & AI stylometric analyzer
        └── test_scoring.py         # Test scenarios for scoring algorithms
```

---

## 🚀 Getting Started & Installation

### 📋 Prerequisites
Make sure you have the following installed on your machine:
*   [Node.js](https://nodejs.org/) & `npm`
*   [Python 3.x](https://www.python.org/)
*   [MongoDB Community Server](https://www.mongodb.com/try/download/community)

---

### Step 1: Start MongoDB
Ensure that your MongoDB service is running on `localhost:27017`.
*   **Windows**: Press `Win + R`, type `services.msc`, and ensure the **MongoDB Server** service is running. Alternatively, verify via MongoDB Compass.
*   You can run the health check script in the root directory to confirm connectivity:
    ```bash
    python check_mongo.py
    ```

---

### Step 2: Set Up and Run the Flask Backend
1.  Navigate to the `backend` directory:
    ```bash
    cd "Email Phishing Detector/backend"
    ```
2.  *(Optional but Recommended)* Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    
    # Activation on Windows Command Prompt:
    venv\Scripts\activate
   
    ```
3.  Install the required dependencies:
    ```bash
    pip install flask flask-cors pymongo beautifulsoup4
    ```
4.  Start the Flask API server:
    ```bash
    python app.py
    ```
    *The server will boot up locally at `http://127.0.0.1:5000`.*

---

### Step 3: Set Up and Run the React Frontend
1.  Open a new terminal in the `Email Phishing Detector` folder (where `package.json` resides):
    ```bash
    cd "Email Phishing Detector"
    ```
2.  Install the Node packages:
    ```bash
    npm install
    ```
3.  Start the React application:
    ```bash
    npm start
    ```
    *This will start the UI server at `http://localhost:3000`.*

---

## 👥 Contributors & Support

Feel free to reach out to the project team:

*   **Anuj Suvarna** — [anujsuvarna7@gmail.com](mailto:anujsuvarna7@gmail.com)
*   **Simran Busi** — [honey040304@gmail.com](mailto:honey040304@gmail.com)
*   **Justin Fernandes** — [justin.fds2005@example.com](mailto:justin.fds2005@example.com)
*   **Karan Patel** — [karanp24680@gmail.com](mailto:karanp24680@gmail.com)

---

## ⚠️ Security Notice
This software is intended for security education, testing, and helper auditing. It relies on deterministic patterns, linguistic statistics, and fuzzy signature lookups. It is not an absolute replacement for organizational email firewalls (like SPF/DKIM/DMARC filters) and enterprise mail transfer agent protection. Use responsibly.

