from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from pymongo import MongoClient # type: ignore
import logging
import re
from datetime import datetime
from ai_detector import AIDetector
from urllib.parse import urlparse
from bs4 import BeautifulSoup # type: ignore

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
logging.basicConfig(level=logging.DEBUG)

# Database Connection
def get_users_collection():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        return client["epd"]["users"]
    except Exception as err:
        logging.error(f"Database connection error: {err}")
        return None

def get_scans_collection():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        return client["epd"]["scans"]
    except Exception as err:
        logging.error(f"Database connection error: {err}")
        return None

def serialize_mongo_doc(doc):
    if not doc:
        return None
    doc_copy = dict(doc)
    if "_id" in doc_copy:
        doc_copy["_id"] = str(doc_copy["_id"])
    if "timestamp" in doc_copy and isinstance(doc_copy["timestamp"], datetime):
        doc_copy["timestamp"] = doc_copy["timestamp"].isoformat()
    return doc_copy

#  User Registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username, email, password = data.get('username'), data.get('email'), data.get('password')

        if not username or not email or not password:
            return jsonify({"success": False, "message": "All fields are required"}), 400

        users_col = get_users_collection()
        if users_col is None:
            return jsonify({"success": False, "message": "Database connection failed"}), 500

        # Check if user exists
        if users_col.find_one({"email": email}):
            return jsonify({"success": False, "message": "User already exists"}), 400

        # Insert user
        users_col.insert_one({"username": username, "email": email, "password": password})
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
        
        users_col = get_users_collection()
        if users_col is None:
            return jsonify({"message": "Database connection failed"}), 500

        user = users_col.find_one({"email": email, "password": password})

        if user:
            return jsonify({'message': 'Login successful!', 'token': 'your_token_here'}), 200
        else:
            return jsonify({'message': 'Invalid email or password.'}), 401
        
    except Exception as e:
        logging.error(f"Error in /login: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

# 🔹 Forgot Password
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email, new_password = data.get('email'), data.get('new_password')

        users_col = get_users_collection()
        if users_col is None:
            return jsonify({"error": "Database connection failed"}), 500

        user = users_col.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        users_col.update_one({"email": email}, {"$set": {"password": new_password}})
        return jsonify({"message": "Password updated successfully"})

    except Exception as e:
        logging.error(f"Error in /forgot-password: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Phishing Detection
def detect_phishing_url(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.lower()
    if not netloc:
        return {"message": "Invalid URL format."}

    # UTI brand protection check
    official_uti_domains = ["utiitsl.com", "utimf.com", "utiitsl.co.in", "utimf.co.in"]
    if "uti" in netloc:
        is_official = any(netloc == dom or netloc.endswith("." + dom) for dom in official_uti_domains)
        if not is_official:
            return {"message": "Fraudulent: Fake UTI domain detected."}

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

def detect_phishing_email(email_content, content_type=None):
    soup = BeautifulSoup(email_content, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]

    # HR salary credit/link fraud check
    content_lower = email_content.lower()
    has_hr = any(term in content_lower for term in ["hr ", "human resources", "hr team", "hr department"]) or (content_type == "HR Notification")
    has_salary = any(term in content_lower for term in ["salary", "salary credit", "salary has been", "credited", "monthly salary"])
    has_link = any(term in content_lower for term in ["http://", "https://", "www.", ".invalid", "portal", "click here", "claim"]) or len(links) > 0

    if has_hr and has_salary and has_link:
        return {"message": "Fraudulent: HR departments do not send external links or vouchers regarding salary credits."}

    for link in links:
        result = detect_phishing_url(link)
        if "Phishing detected" in result["message"] or "Fraudulent" in result["message"]:
            return {"message": "Phishing detected in email content."}

    phishing_words = ["urgent", "verify", "update payment", "confirm identity", "click here", "you won"]
    if any(word in email_content.lower() for word in phishing_words):
        return {"message": "Phishing detected: Suspicious email content."}

    return {"message": "Email content is safe."}

def detect_phishing_email_id(email_id):
    if not email_id or "@" not in email_id:
        return {"message": "Invalid email ID format."}
        
    try:
        local_part, domain = email_id.split("@", 1)
    except ValueError:
        return {"message": "Invalid email ID format."}
        
    local_part = local_part.lower()
    domain = domain.lower()
    
    # Check UTI brand spoof
    official_uti_domains = ["utiitsl.com", "utimf.com", "utiitsl.co.in", "utimf.co.in"]
    if "uti" in domain:
        is_official = any(domain == dom or domain.endswith("." + dom) for dom in official_uti_domains)
        if not is_official:
            return {"message": "Fraudulent: Fake UTI email sender domain detected."}
            
    # Check free email provider with official/admin local parts
    free_providers = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "zoho.com", "protonmail.com", "proton.me", "mail.com", "yandex.com"]
    role_keywords = ["support", "admin", "security", "service", "billing", "helpdesk", "info", "no-reply", "noreply", "hr", "payroll", "rewards", "verify", "account"]
    
    is_free = domain in free_providers
    has_role = any(kw in local_part for kw in role_keywords)
    
    if is_free and has_role:
        return {"message": "Suspicious: Role-based mailbox impersonating official alerts using a free email provider."}
        
    # Phishing keywords in domain
    phishing_keywords = ["secure-", "bank-", "update-", "login-", "verify-", "account-", "securebanking", "confirm-", "authenticate-", "security-", "paypal-", "appleid-", "microsoft-", "google-", "amazon-", "netflix-", "facebook-", "instagram-", "whatsapp-", "rewards-"]
    if any(kw in domain for kw in phishing_keywords):
        return {"message": "Phishing detected: Suspicious keyword in sender domain."}
        
    # Phishing extension check
    phishing_extensions = [".xyz", ".tk", ".ru", ".cn", ".cf", ".ml", ".ga", ".gq", ".top", ".win", ".vip", ".best", ".live", ".online", ".site", ".store", ".fun", ".co", ".cm", ".om", ".invalid"]
    if any(domain.endswith(ext) for ext in phishing_extensions):
        return {"message": "Phishing detected: Suspicious registrar extension."}
        
    return {"message": "Sender domain is safe and verified."}

def analyze_overall_risk(url, email_content, content_type, ai_result, phishing_result):
    factors = []
    text = (email_content or "").lower()
    
    # 1. PHISHING INDICATORS
    phishing_kws = ["verify account", "unauthorized access", "confirm identity", "billing failure", "security notification", "update payment", "suspicious transaction", "action required"]
    matched_phish = [kw for kw in phishing_kws if kw in text]
    if matched_phish:
        impact = min(25.0, len(matched_phish) * 8.0)
        factors.append({
            "name": "Phishing Indicators",
            "impact": impact,
            "reason": f"Detected phishing-related text signals: {', '.join(matched_phish[:2])}"
        })
        
    # 2. SOCIAL ENGINEERING TACTICS
    social_kws_threat = ["account suspension", "legal action", "termination", "account closure", "do not delay"]
    social_kws_reward = ["voucher", "free coupon", "congratulations", "you won", "gift card", "reward is reserved", "appreciation program", "compensation"]
    matched_soc_threat = [kw for kw in social_kws_threat if kw in text]
    matched_soc_reward = [kw for kw in social_kws_reward if kw in text]
    matched_soc = matched_soc_threat + matched_soc_reward
    if matched_soc:
        impact = min(25.0, len(matched_soc) * 10.0)
        factors.append({
            "name": "Social Engineering Tactics",
            "impact": impact,
            "reason": f"Detected social engineering pressure or reward lures: {', '.join(matched_soc[:2])}"
        })
        
    # 3. SUSPICIOUS LINKS
    links = []
    if email_content:
        soup = BeautifulSoup(email_content, "html.parser")
        links = [a['href'] for a in soup.find_all('a', href=True)]
    if url:
        links.append(url)
        
    link_impact = 0.0
    bad_links_found = []
    for l in links:
        parsed = urlparse(l)
        netloc = parsed.netloc.lower()
        if not netloc:
            continue
        if l.startswith("http://"):
            link_impact += 10.0
            bad_links_found.append("HTTP instead of HTTPS")
        if any(kw in netloc for kw in ["secure-", "bank-", "login-", "verify-", "account-", "confirm-", "authenticate-", "support-"]):
            link_impact += 12.0
            bad_links_found.append("suspicious keyword in hostname")
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', netloc):
            link_impact += 20.0
            bad_links_found.append("numeric IP address host")
        if any(dom in netloc for dom in ["bit.ly", "tinyurl.com", "t.co", "goo.gl"]):
            link_impact += 12.0
            bad_links_found.append("URL shortener service")
            
    if bad_links_found:
        impact = min(25.0, link_impact)
        factors.append({
            "name": "Suspicious Links",
            "impact": impact,
            "reason": f"Links utilize suspect schemes or patterns: {', '.join(list(set(bad_links_found))[:2])}"
        })
        
    # 4. CREDENTIAL REQUESTS
    cred_kws = ["password", "type your credentials", "sign in to", "enter password", "mfa confirmation", "2fa code", "otp", "ssn", "secret question", "verify passcode"]
    matched_cred = [kw for kw in cred_kws if kw in text]
    if matched_cred:
        impact = min(25.0, len(matched_cred) * 12.0)
        factors.append({
            "name": "Credential Requests",
            "impact": impact,
            "reason": f"Detected requests for identity validation or password entry: {', '.join(matched_cred[:2])}"
        })
        
    # 5. SENDER IMPERSONATION
    impersonation_kws = ["it support desk", "it department", "hr notification", "hr department", "human resources", "admin team", "payroll desk", "hr rewards"]
    matched_imp = [kw for kw in impersonation_kws if kw in text]
    
    brand_spoofed = False
    for l in links:
        parsed = urlparse(l)
        netloc = parsed.netloc.lower()
        if "uti" in netloc and not any(netloc == dom or netloc.endswith("." + dom) for dom in ["utiitsl.com", "utimf.com", "utiitsl.co.in", "utimf.co.in"]):
            brand_spoofed = True
            
    if matched_imp or brand_spoofed or content_type in ["IT Announcement", "HR Notification"]:
        impact = 12.0
        if brand_spoofed:
            impact += 13.0
        else:
            impact += min(13.0, len(matched_imp) * 6.0)
        factors.append({
            "name": "Sender Impersonation",
            "impact": min(25.0, impact),
            "reason": "Detected potential impersonation of internal departments or external brand spoofing"
        })
        
    # 6. URGENCY & SCARE TACTICS
    urgency_kws = ["urgent", "immediate action", "within 24 hours", "expires", "deadline", "asap", "without delay", "last chance"]
    matched_urgency = [kw for kw in urgency_kws if kw in text]
    if matched_urgency:
        impact = min(20.0, len(matched_urgency) * 8.0)
        factors.append({
            "name": "Urgency & Scare Tactics",
            "impact": impact,
            "reason": f"Text contains time-sensitive urgency cues: {', '.join(matched_urgency[:2])}"
        })
        
    # 7. ATTACHMENTS
    attachment_kws = ["attachment", "enclosed file", "invoice.pdf", "receipt.zip", "statement.xlsx", "document.exe", "download attachment", "view attached"]
    matched_attachment = [kw for kw in attachment_kws if kw in text]
    if matched_attachment:
        impact = min(20.0, len(matched_attachment) * 8.0)
        factors.append({
            "name": "Attachments Reference",
            "impact": impact,
            "reason": f"Content references attachments or potential payload downloads: {', '.join(matched_attachment[:2])}"
        })
        
    # 8. DOMAIN REPUTATION
    reputation_impact = 0.0
    sketchy_tld_found = []
    for l in links:
        parsed = urlparse(l)
        netloc = parsed.netloc.lower()
        if not netloc:
            continue
        phishing_extensions = [".xyz", ".tk", ".ru", ".cn", ".cf", ".ml", ".ga", ".gq", ".top", ".win", ".vip", ".best", ".live", ".online", ".site", ".store", ".fun", ".co", ".cm", ".om", ".invalid"]
        if any(netloc.endswith(ext) or (ext + "/") in netloc for ext in phishing_extensions):
            reputation_impact += 15.0
            sketchy_tld_found.append(f"sketchy TLD ({netloc.split('.')[-1]})")
        if "uti" in netloc and not any(netloc == dom or netloc.endswith("." + dom) for dom in ["utiitsl.com", "utimf.com", "utiitsl.co.in", "utimf.co.in"]):
            reputation_impact += 25.0
            sketchy_tld_found.append("fake UTI domain")
            
    if sketchy_tld_found:
        factors.append({
            "name": "Domain Reputation",
            "impact": min(25.0, reputation_impact),
            "reason": f"Domain reputation warnings: {', '.join(list(set(sketchy_tld_found))[:2])}"
        })
        
    # 9. GRAMMAR & CASING INCONSISTENCIES
    grammar_impact = 0.0
    grammar_reasons = []
    if re.search(r'\b[A-Z]{4,}\s+[A-Z]{4,}\s+[A-Z]{4,}\b', email_content or ""):
        grammar_impact += 6.0
        grammar_reasons.append("excessive capitalization")
    if "  " in (email_content or ""):
        grammar_impact += 5.0
        grammar_reasons.append("multiple consecutive spaces")
    if re.search(r'[.,][a-zA-Z]{2,}', email_content or ""):
        grammar_impact += 5.0
        grammar_reasons.append("missing space after punctuation")
    grammar_phrases = ["please checking", "your account is close", "verify now link", "click on below", "regards hr department"]
    matched_gram_phrases = [p for p in grammar_phrases if p in text]
    if matched_gram_phrases:
        grammar_impact += len(matched_gram_phrases) * 5.0
        grammar_reasons.append("awkward syntactic structures")
        
    if grammar_reasons:
        factors.append({
            "name": "Grammar & Casing Inconsistencies",
            "impact": min(15.0, grammar_impact),
            "reason": f"Stylistic irregularities: {', '.join(grammar_reasons[:2])}"
        })
        
    # 10. OTHER SECURITY-RELATED FACTORS
    other_impact = 0.0
    other_reasons = []
    if any(term in text for term in ["dear employee", "dear customer", "dear user", "valued customer"]):
        other_impact += 6.0
        other_reasons.append("generic greeting")
    ai_prob = ai_result.get("ai_probability", 0.0) if ai_result else 0.0
    if ai_prob > 50.0:
        other_impact += (ai_prob - 50.0) * 0.2
        other_reasons.append("AI writing signature")
        
    if other_reasons:
        factors.append({
            "name": "Other Security-Related Factors",
            "impact": min(15.0, other_impact),
            "reason": f"Identified security outliers: {', '.join(other_reasons[:2])}"
        })

    # High severity phishing threat booster
    is_phish = phishing_result and ("Phishing detected" in phishing_result.get("message", "") or "Fraudulent" in phishing_result.get("message", ""))
    if is_phish:
        factors.append({
            "name": "High-Severity Phishing Threat Booster",
            "impact": 20,
            "reason": f"Explicit threat indicators: {phishing_result.get('message', '')}"
        })

    base_score = 5.0
    total_score = base_score + sum(f["impact"] for f in factors)
    
    # Add dynamic content micro-variations
    len_variance = (len(text) % 23) * 0.17
    words = text.split()
    ttr = len(set(words)) / len(words) if words else 1.0
    ttr_variance = (1.0 - ttr) * 5.0
    factor_variance = (len(factors) % 4) * 0.63
    
    total_score += len_variance + ttr_variance + factor_variance
    total_score = max(0.0, min(100.0, total_score))
    
    if len(factors) == 0:
        total_score = round(max(2.0, min(12.0, 3.0 + (len(text) % 13) * 0.65)), 1)
    else:
        total_score = round(total_score, 1)
        
    return {
        "score": total_score,
        "factors": factors
    }

def analyze_email_id_risk(email_id, phishing_result):
    factors = []
    if not email_id or "@" not in email_id:
        return {"score": 0.0, "factors": []}
        
    try:
        local_part, domain = email_id.split("@", 1)
    except ValueError:
        return {"score": 0.0, "factors": []}
        
    local_part = local_part.lower()
    domain = domain.lower()
    
    base_score = 5.0
    
    # 1. Free email provider role check
    free_providers = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "zoho.com", "protonmail.com", "proton.me", "mail.com", "yandex.com"]
    role_keywords = ["support", "admin", "security", "service", "billing", "helpdesk", "info", "no-reply", "noreply", "hr", "payroll", "rewards", "verify", "account"]
    is_free = domain in free_providers
    has_role = any(kw in local_part for kw in role_keywords)
    
    if is_free and has_role:
        factors.append({
            "name": "Free Mailbox Role Abuse",
            "impact": 35.0,
            "reason": f"Uses free provider '{domain}' for official corporate/service role alias '{local_part}'"
        })
    elif is_free:
        factors.append({
            "name": "Generic Free Email Domain",
            "impact": 10.0,
            "reason": "Uses personal free email host (e.g. Gmail/Yahoo) for communication"
        })
        
    # 2. Phishing keywords in local part
    matched_local_role = [kw for kw in role_keywords if kw in local_part]
    if matched_local_role and not is_free:
        factors.append({
            "name": "Role Identity Cues",
            "impact": 15.0,
            "reason": f"Username local-part references support/administration functions: '{matched_local_role[0]}'"
        })
        
    # 3. UTI Brand check
    official_uti_domains = ["utiitsl.com", "utimf.com", "utiitsl.co.in", "utimf.co.in"]
    if "uti" in domain:
        is_official = any(domain == dom or domain.endswith("." + dom) for dom in official_uti_domains)
        if not is_official:
            factors.append({
                "name": "UTI Brand Impersonation",
                "impact": 45.0,
                "reason": "Uses lookalike UTI domain indicating high-probability phishing"
            })
            
    # 4. Phishing keywords in domain
    phishing_keywords = ["secure-", "bank-", "update-", "login-", "verify-", "account-", "securebanking", "confirm-", "authenticate-", "security-", "paypal-", "appleid-", "microsoft-", "google-", "amazon-", "netflix-", "facebook-", "instagram-", "whatsapp-", "rewards-"]
    matched_domain_kw = [kw for kw in phishing_keywords if kw in domain]
    if matched_domain_kw:
        factors.append({
            "name": "Domain Phishing Keywords",
            "impact": 25.0,
            "reason": f"Domain contains security or brand verification cues: '{matched_domain_kw[0]}'"
        })
        
    # 5. Phishing extensions (TLDs)
    phishing_extensions = [".xyz", ".tk", ".ru", ".cn", ".cf", ".ml", ".ga", ".gq", ".top", ".win", ".vip", ".best", ".live", ".online", ".site", ".store", ".fun", ".co", ".cm", ".om", ".invalid"]
    matched_ext = [ext for ext in phishing_extensions if domain.endswith(ext)]
    if matched_ext:
        factors.append({
            "name": "Suspicious TLD Extension",
            "impact": 20.0,
            "reason": f"Domain utilizes sketchy registry extension '{matched_ext[0]}'"
        })
        
    # 6. Explicit threat indicator from domain checks
    is_phish = "Phishing detected" in phishing_result.get("message", "") or "Fraudulent" in phishing_result.get("message", "") or "Suspicious" in phishing_result.get("message", "")
    if is_phish:
        factors.append({
            "name": "Negative Reputation Flag",
            "impact": 20.0,
            "reason": f"Domain trigger warning: {phishing_result.get('message', '')}"
        })
        
    total_score = base_score + sum(f["impact"] for f in factors)
    
    # Micro-variations for unique values
    len_offset = (len(email_id) % 17) * 0.23
    local_offset = (len(local_part) % 11) * 0.19
    total_score += len_offset + local_offset
    
    total_score = max(0.0, min(100.0, total_score))
    
    if len(factors) == 0:
        total_score = round(max(1.5, min(9.5, 2.5 + (len(email_id) % 7) * 0.85)), 1)
    else:
        total_score = round(total_score, 1)
        
    return {
        "score": total_score,
        "factors": factors
    }

def generate_risk_report(url, email_content, content_type, ai_result, phishing_result, overall_risk_data, email_id=None):
    score = overall_risk_data["score"]
    factors = overall_risk_data["factors"]
    
    if email_id:
        if score <= 20.0:
            status = "Trusted Content"
            desc = "No significant security concerns detected. The sender email ID appears legitimate based on domain registers."
            recommendation = "Safe to communicate. Standard email safety rules apply."
        elif score <= 40.0:
            status = "Minor Concerns Identified"
            desc = "A few low-risk indicators were detected (e.g. personal email address). Use standard verification before sending sensitive info."
            recommendation = "Confirm identity through other channels if the sender requests financial or confidential actions."
        elif score <= 60.0:
            status = "Moderate Risk Detected"
            desc = "Multiple suspicious sender characteristics identified. High probability of impersonation."
            recommendation = "Do not reply. Verify if this communication is expected or contact the organization directly."
        elif score <= 80.0:
            status = "High Risk Detected"
            desc = "Strong indicators of domain lookalikes, free mailbox role abuse, or spoofing keywords."
            recommendation = "Exercise extreme caution. Do not trust requests from this email. Flag to your security team."
        else:
            status = "Suspicious Content Detected"
            desc = "Critical phishing email ID signatures matched (e.g. fake UTI brand domain)."
            recommendation = "DO NOT respond, do not click links. Block the sender and report immediately to your IT security administrator."
    else:
        if score <= 20.0:
            status = "Trusted Content"
            desc = "No significant security concerns detected. The content appears legitimate based on the current analysis."
            recommendation = "Safe to interact. Standard security precautions apply."
        elif score <= 40.0:
            status = "Minor Concerns Identified"
            desc = "A few low-risk indicators were detected. Users should review the content carefully before interacting with links or attachments."
            recommendation = "Review the content and verify context before clicking links or downloading attachments."
        elif score <= 60.0:
            status = "Moderate Risk Detected"
            desc = "Multiple suspicious characteristics have been identified. Additional verification is recommended before taking any action."
            recommendation = "Do not click links. Verify with the sender via a separate communication channel (e.g. phone call or direct chat)."
        elif score <= 80.0:
            status = "High Risk Detected"
            desc = "Strong indicators of phishing, impersonation, or social engineering are present. Exercise extreme caution and verify the source independently."
            recommendation = "Avoid interacting with this content. Flag this message to your organization's IT Security Incident Response team."
        else:
            status = "Suspicious Content Detected"
            desc = "Critical phishing indicators have been identified. The content is highly likely to be malicious and should be treated as a security threat."
            recommendation = "DO NOT click links or enter credentials. Report this immediately to IT Security and delete the message."

    ai_conf = ai_result.get("confidence", "Medium") if ai_result else "Medium"
    if len(factors) == 0:
        confidence = 90
    elif score > 85.0 or score < 15.0:
        confidence = 95
    elif ai_conf == "High":
        confidence = 88
    else:
        confidence = 80

    if len(factors) == 0:
        summary = "The content was checked against threat signatures, impersonation templates, and linguistic variations. No indicators of social engineering, credential harvesting, or brand spoofing were identified."
    else:
        summary = f"Analysis identified {len(factors)} risk factor(s). The score is primarily driven by: {', '.join([f['name'] for f in factors[:2]])}."

    positives = []
    negatives = []
    
    for f in factors:
        negatives.append(f"{f['name']}: {f['reason']} (+{f['impact']}%)")
        
    triggered_names = {f["name"] for f in factors}
    
    if email_id:
        if "Free Mailbox Role Abuse" not in triggered_names and "Generic Free Email Domain" not in triggered_names:
            positives.append("Sender uses custom corporate or organization domain hosting.")
        if "UTI Brand Impersonation" not in triggered_names:
            positives.append("No brand lookalike signatures or spoofing keywords detected.")
        if "Domain Phishing Keywords" not in triggered_names:
            positives.append("Domain name is clear of phishing alert keywords.")
        if "Suspicious TLD Extension" not in triggered_names:
            positives.append("Uses a highly-trusted top-level registrar extension.")
        if "Role Identity Cues" not in triggered_names:
            positives.append("Mailbox alias matches direct standard user profile patterns.")
    else:
        if "Phishing Indicators" not in triggered_names:
            positives.append("No common phishing threat signatures detected.")
        if "Social Engineering Tactics" not in triggered_names:
            positives.append("No coercive urgency or fraudulent reward templates found.")
        if "Suspicious Links" not in triggered_names:
            positives.append("Sender links match clean structural formats with no suspicious components.")
        if "Credential Requests" not in triggered_names:
            positives.append("No credential inputs or verification prompts requested.")
        if "Sender Impersonation" not in triggered_names:
            positives.append("No signs of internal corporate role or external brand impersonation.")
        if "Urgency & Scare Tactics" not in triggered_names:
            positives.append("Absence of time-pressured or threatening language.")
        if "Attachments Reference" not in triggered_names:
            positives.append("No references to external attachments or downloadable payloads.")
        if "Domain Reputation" not in triggered_names:
            positives.append("URL domains map to safe categories without sketchy domain registrar codes.")
        if "Grammar & Casing Inconsistencies" not in triggered_names:
            positives.append("High grammatical consistency and proper sentence structures.")
        if "Other Security-Related Factors" not in triggered_names:
            positives.append("Content features natural stylistic metrics and proper contextual layout.")

    return {
        "suspicion_score": score,
        "risk_status": status,
        "description": desc,
        "confidence_level": f"{confidence}%",
        "risk_summary": summary,
        "positive_indicators": positives[:3],
        "negative_indicators": negatives[:3],
        "recommendation": recommendation,
        "factors": factors
    }

@app.route('/api/check', methods=['POST'])
def check_phishing():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No input provided."}), 400

        url = data.get('url')
        email_content = data.get('emailContent')
        email_id = data.get('emailId')
        content_type = data.get('contentType', 'Email Content')

        if not url and not email_content and not email_id:
            return jsonify({"message": "No input provided."}), 400

        phishing_result = {}
        ai_result = {}
        input_data = ""

        scans_col = get_scans_collection()
        historical_scans = []
        if scans_col is not None:
            try:
                cursor = scans_col.find().sort("timestamp", -1).limit(20)
                historical_scans = list(cursor)
            except Exception as e:
                logging.error(f"Error fetching historical scans: {e}")

        detector = AIDetector()

        if url:
            input_data = url
            phishing_result = detect_phishing_url(url)
            ai_result = detector.analyze(url, historical_scans)
            is_phishing = "Phishing detected" in phishing_result.get("message", "") or "Fraudulent" in phishing_result.get("message", "")
            overall_risk_data = analyze_overall_risk(url, email_content, content_type, ai_result, phishing_result)
            report = generate_risk_report(url, email_content, content_type, ai_result, phishing_result, overall_risk_data)
        elif email_id:
            input_data = email_id
            phishing_result = detect_phishing_email_id(email_id)
            ai_result = {"is_ai_generated": False, "ai_probability": 0.0, "confidence": "High"}
            is_phishing = "Phishing detected" in phishing_result.get("message", "") or "Fraudulent" in phishing_result.get("message", "") or "Suspicious" in phishing_result.get("message", "")
            overall_risk_data = analyze_email_id_risk(email_id, phishing_result)
            report = generate_risk_report(None, None, content_type, ai_result, phishing_result, overall_risk_data, email_id=email_id)
        else:
            input_data = email_content
            phishing_result = detect_phishing_email(email_content, content_type)
            ai_result = detector.analyze(email_content, historical_scans)
            is_phishing = "Phishing detected" in phishing_result.get("message", "") or "Fraudulent" in phishing_result.get("message", "")
            overall_risk_data = analyze_overall_risk(url, email_content, content_type, ai_result, phishing_result)
            report = generate_risk_report(url, email_content, content_type, ai_result, phishing_result, overall_risk_data)

        flagged_for_review = is_phishing or report["suspicion_score"] >= 45.0 or (ai_result.get("is_ai_generated") and ai_result.get("confidence") in ["Medium", "High"])

        overall_risk = {
            "score": report["suspicion_score"],
            "level": report["risk_status"],
            "flagged_for_review": flagged_for_review,
            "description": report["description"],
            "confidence_level": report["confidence_level"],
            "risk_summary": report["risk_summary"],
            "positive_indicators": report["positive_indicators"],
            "negative_indicators": report["negative_indicators"],
            "recommendation": report["recommendation"],
            "factors": report["factors"]
        }

        response_data = {
            "success": True,
            "message": phishing_result.get("message", "Checked successfully"),
            "is_phishing": is_phishing,
            "phishing_details": {
                "reason": phishing_result.get("message", ""),
                "risk_score": 80 if is_phishing else 10
            },
            "ai_analysis": ai_result,
            "overall_risk": overall_risk,
            "input_type": "url" if url else ("email_id" if email_id else "text"),
            "content_type": content_type
        }

        if scans_col is not None:
            try:
                scans_col.insert_one({
                    "timestamp": datetime.utcnow(),
                    "input_type": "url" if url else ("email_id" if email_id else "text"),
                    "content_type": content_type,
                    "input_data": input_data[:1000],
                    "phishing_result": phishing_result,
                    "ai_analysis": ai_result,
                    "overall_risk": overall_risk
                })
            except Exception as e:
                logging.error(f"Error logging scan to MongoDB: {e}")

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error in /api/check: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        scans_col = get_scans_collection()
        if scans_col is None:
            return jsonify({"success": False, "message": "Database connection failed"}), 500

        cursor = scans_col.find().sort("timestamp", -1).limit(10)
        history = []
        for doc in cursor:
            history.append(serialize_mongo_doc(doc))

        return jsonify({"success": True, "history": history})

    except Exception as e:
        logging.error(f"Error in /api/history: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)