import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:5000/api/check"

test_cases = [
    {
        "name": "Case 1: Safe Human Content",
        "payload": {
            "emailContent": "Hey, do you want to grab some coffee this afternoon? Let me know if you are free around 3 PM.",
            "contentType": "Email Content"
        }
    },
    {
        "name": "Case 2: Minor Concerns (IT Alert but no urgency or links)",
        "payload": {
            "emailContent": "Dear Employee, please be advised that our system maintenance is scheduled for this weekend. Thank you for your patience.",
            "contentType": "IT Announcement"
        }
    },
    {
        "name": "Case 3: High Risk (HR Appreciations & Salary Links)",
        "payload": {
            "emailContent": "Dear Employee,\n\nWe are pleased to inform you that your monthly salary has been successfully credited to your registered bank account.\n\nAs part of this month's Employee Appreciation Program, eligible employees have been granted a complimentary reward voucher.\n\nTo view your reward details, please visit the employee rewards portal below:\n\n[Claim Reward Voucher]\nhttps://rewards.example.invalid/claim\n\nCongratulations! Your reward has been reserved and will remain available for the next 24 hours.\n\nRegards,\nHR Rewards Team",
            "contentType": "HR Notification"
        }
    },
    {
        "name": "Case 4: Critical Phishing & Domain Spoof (UTI Fake Domain)",
        "payload": {
            "emailContent": "URGENT ACTION REQUIRED: We detected a suspicious transaction on your account. Please log in to your account credentials portal immediately to verify identity and confirm billing details.\n\nLink: http://verify-uti-banking.xyz/login.php\n\nFailure to do so within 12 hours will result in permanent account suspension.",
            "contentType": "Email Content"
        }
    },
    {
        "name": "Case 5: Safe Sender Domain",
        "payload": {
            "emailId": "support@utiitsl.com",
            "contentType": "Email ID Check"
        }
    },
    {
        "name": "Case 6: Spoofed UTI Sender Domain",
        "payload": {
            "emailId": "alert@utiitsl-verification.online",
            "contentType": "Email ID Check"
        }
    },
    {
        "name": "Case 7: Role Abuse on Free Provider",
        "payload": {
            "emailId": "admin@gmail.com",
            "contentType": "Email ID Check"
        }
    }
]

for case in test_cases:
    print("=" * 60)
    print(f"Running: {case['name']}")
    print("-" * 60)
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(case["payload"]).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            risk = res.get("overall_risk", {})
            print(f"* Suspicion Score: {risk.get('score')}%")
            print(f"* Risk Status: {risk.get('level')}")
            print(f"* Confidence Level: {risk.get('confidence_level')}")
            print(f"* Risk Summary: {risk.get('risk_summary')}")
            print("* Positive Indicators:")
            for pos in risk.get("positive_indicators", []):
                print(f"  - {pos}")
            print("* Negative Indicators:")
            for neg in risk.get("negative_indicators", []):
                print(f"  - {neg}")
            print(f"* Recommendation: {risk.get('recommendation')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(e.read().decode("utf-8"))
    except Exception as e:
        print(f"Request failed: {e}")
    print()
