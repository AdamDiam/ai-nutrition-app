# auth_utils.py
import json
from datetime import datetime
import bcrypt
from config import USERS_FILE


def load_users() -> dict:
    """Διάβασε όλους τους χρήστες από το users.json."""
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_users(users: dict) -> None:
    """Αποθήκευσε όλο το users dict στο users.json."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def hash_password(password: str) -> str:
    """Κάνε hash ενός password με bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Έλεγξε αν ένα plain password ταιριάζει με το hashed."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def update_last_login(username: str) -> None:
    """Ενημέρωσε το last_login του χρήστη στο users.json."""
    users = load_users()
    if username in users:
        users[username]["last_login"] = datetime.utcnow().isoformat()
        save_users(users)
