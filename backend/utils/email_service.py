import logging

logger = logging.getLogger(__name__)

def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Mock email service function for password resets."""
    reset_link = f"http://localhost:5500/frontend/login.html?token={reset_token}"
    logger.info(f"[MOCK EMAIL] Password reset requested for {email}. Token link: {reset_link}")
    print(f"\n========================================================")
    print(f"[MOCK EMAIL SERVICE] Password Reset Sent To: {email}")
    print(f"Reset Link: {reset_link}")
    print(f"========================================================\n")
    return True

def send_notification_email(email: str, subject: str, body: str) -> bool:
    """Mock email dispatcher for event notifications."""
    print(f"[MOCK EMAIL] Notification to {email} | Subject: {subject} | Body: {body}")
    return True
