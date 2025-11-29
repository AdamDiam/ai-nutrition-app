# Username: AdamDiam (admin)
# Password: 1234

# Username: Demo (user)
# Password: 1234

import os
import io
from pathlib import Path
from datetime import datetime, date

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import base64
import json
import bcrypt

USERS_FILE = "users.json"
SECURITY_QUESTION = "What is your favourite color?"

def get_security_question() -> str:
    return tr("security_question")

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def update_last_login(username: str):
    users = load_users()
    if username in users:
        users[username]["last_login"] = datetime.utcnow().isoformat()
        save_users(users)

def get_base64_logo(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

LOGO_BASE64 = get_base64_logo("assets/logo.png")

def load_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

BG_BASE64 = load_base64_image("assets/bg_pattern.png")

# ----------------- CONFIG & OPENAI -----------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

st.set_page_config(
    page_title="02Hero Nutrition Helper",
    page_icon="🍽️",
    layout="wide",
)

st.markdown(
    f"""
    <style>
    /* 1) Pattern background σε όλη τη σελίδα */
    body {{
        background-image: url('data:image/png;base64,{BG_BASE64}');
        background-size: 120px 120px;
        background-repeat: repeat;
        background-attachment: fixed;
    }}

    .stApp {{
        background: transparent;
    }}

    .main .block-container {{
        background: transparent;
        padding-top: 2rem;
    }}

            /* 🔹 Panel για ΟΛΕΣ τις φόρμες (login, signup κτλ.) */
    [data-testid="stForm"] {{
        max-width: 480px;
        margin: 2.5rem auto 3rem auto;   /* κέντρο + αποστάσεις */
        background: rgba(0, 0, 0, 0.82);
        border-radius: 18px;
        padding: 1.8rem 2.2rem;
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.55);
    }}

    [data-testid="stForm"] * {{
        color: #F7F7F7 !important;
    }}


    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <style>
    /* Κάνει κόκκινο ΜΟΝΟ το κουμπί μέσα στο delete-section */
    .delete-section button {
        background-color: #b91c1c !important;
        border-color: #b91c1c !important;
        color: white !important;
    }

    /* Στυλ για "popup" κάρτα επιβεβαίωσης */
    .delete-confirm-card {
        border: 1px solid #b91c1c;
        background-color: #0f172a;
        padding: 1.2rem;
        border-radius: 0.75rem;
        margin-top: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- LANGUAGE TEXTS -----------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "el"

TEXT = {
    "el": {
        "title": "02Hero – AI Nutrition Helper",
        "subtitle": "Έξυπνη διατροφή με τη βοήθεια του AI, προσαρμοσμένη σε εσένα.",
        "intro": "Δώσε τα στοιχεία σου και άσε το AI να σου φτιάξει ένα εβδομαδιαίο πρόγραμμα διατροφής με βάση τον στόχο σου.",
        "username": "Όνομα χρήστη (π.χ. email ή ψευδώνυμο)",
        "age": "Ηλικία",
        "sex": "Φύλο",
        "male": "Άνδρας",
        "female": "Γυναίκα",
        "height": "Ύψος (cm)",
        "weight": "Βάρος (kg)",
        "activity": "Επίπεδο δραστηριότητας",
        "goal": "Στόχος",
        "activity_opts": ["Low", "Medium", "High"],
        "goal_opts": ["Lose fat", "Maintain", "Gain muscle"],
        "allergies": "Αλλεργίες / τροφές προς αποφυγή",
        "allergies_ph": "π.χ. αλλεργία σε ξηρούς καρπούς, δυσανεξία στη λακτόζη, δεν τρώω θαλασσινά",
        "prefs": "Αγαπημένα φαγητά που θα ήθελες να υπάρχουν στο πρόγραμμα",
        "prefs_ph": "π.χ. κοτόπουλο, ζυμαρικά, γιαούρτι με μέλι, σαλάτες με τόνο",
        "submit": "Υπολογισμός & Πρόγραμμα AI",
        "back": "← Αλλαγή στοιχείων & νέο πρόγραμμα",
        "plan_title": "Εβδομαδιαίο πρόγραμμα διατροφής από το AI",
        "macros_title": "Εκτίμηση ημερήσιων θερμίδων & macros",
        "download": "📥 Κατέβασε το πρόγραμμα σε Excel",
        "download_shop": "🛒 Κατέβασε τη λίστα αγορών (txt)",
        "disclaimer": "⚠️ Το πρόγραμμα αυτό είναι ενδεικτικό και δεν αντικαθιστά ιατρική ή εξατομικευμένη διαιτολογική συμβουλή.",
        "qa_title": "Κάνε μια ερώτηση για το πρόγραμμα ή τη διατροφή σου",
        "qa_your_q": "Η ερώτησή σου:",
        "qa_button": "Ρώτα το AI",
        "changes_title": "Αλλαγές στο πρόγραμμα",
        "changes_desc": "Αν κάτι δεν σου ταιριάζει (π.χ. δεν θέλεις γαλακτοκομικά, θέλεις πιο απλά βραδινά κτλ.), γράψ' το εδώ και το AI θα προσαρμόσει τον πίνακα:",
        "changes_ph": "π.χ. έχω αντίσταση στην ινσουλίνη, δεν θέλω ψωμί/ζυμαρικά το βράδυ",
        "changes_button": "Προσαρμογή προγράμματος με βάση τα σχόλιά μου",
        "need_feedback": "Γράψε πρώτα τι θα ήθελες να αλλάξει.",
        "history_title": "Ιστορικό",
        "sidebar_title": "02Hero",
        "sidebar_sub": "AI Nutrition Helper",
        "footer": "Created by Adam / 02Hero Coaching",
        "about_title": "About us & πώς να χρησιμοποιείς το 02Hero",
        "about_text": (
            "Το 02Hero Nutrition Helper είναι ένα προσωπικό project coaching που "
            "χρησιμοποιεί AI (μοντέλα της OpenAI) για να δημιουργεί ιδέες διατροφής "
            "με βάση τα στοιχεία και τους στόχους σου.\n\n"
            "➡️ **Τι κάνει καλά:**\n"
            "- Σε βοηθάει να οργανωθείς και να έχεις ένα ξεκάθαρο εβδομαδιαίο πλάνο.\n"
            "- Σου δίνει ιδέες για γεύματα, ποσότητες και στόχους macros.\n"
            "- Προσαρμόζεται στα σχόλιά σου (π.χ. αλλεργίες, προτιμήσεις).\n\n"
            "⚠️ **Τι ΔΕΝ κάνει:**\n"
            "- Δεν αντικαθιστά ιατρό, ενδοκρινολόγο ή κλινικό διαιτολόγο.\n"
            "- Δεν λαμβάνει υπόψη ιατρικό ιστορικό ή εξετάσεις αίματος.\n\n"
            "📌 Δες το πρόγραμμα σαν ένα **έξυπνο προσχέδιο**: ένα δυνατό σημείο εκκίνησης "
            "για να οργανώσεις τη διατροφή σου ή να το συζητήσεις με κάποιον ειδικό, "
            "όχι σαν αυστηρή ιατρική οδηγία."
        ),
        # menu items
        "menu_home": "🏠 Αρχική",
        "menu_new_plan": "📅 Νέο πλάνο διατροφής",
        "menu_progress": "📈 Καταγραφή προόδου",
        "menu_profile": "👤 Προφίλ χρήστη",
        "menu_about": "ℹ️ Σχετικά με εμάς & τις υπηρεσίες μας",
        "shopping_title": "Λίστα αγορών για 7 ημέρες",
        "save_data": "💾 Αποθήκευση στοιχείων (σήμερα)",
        "saved_ok": "✅ Τα στοιχεία σου αποθηκεύτηκαν για σήμερα.",
        "saved_err_no_user": "Βάλε πρώτα όνομα χρήστη για να αποθηκεύσω το ιστορικό.",
        "history_plan_label": "Δες παλιό πρόγραμμα από:",
        "history_no_plan": "Δεν βρέθηκε αποθηκευμένο πρόγραμμα για αυτή την εγγραφή.",
        "login_title": "Σύνδεση",
        "login_button": "Συνέχεια",
        "home_welcome": "Καλώς ήρθες",
        "home_new_plan": "Δημιούργησε νέο πρόγραμμα διατροφής",
        "home_progress": "Κατέγραψε την πρόοδό σου",
        "home_view_plans": "Δες παλιότερα προγράμματά σου",
        "home_profile": "Ενημέρωσε το προφίλ σου",
        "profile_title": "Προφίλ χρήστη",
        "profile_save": "💾 Αποθήκευση προφίλ",
        "profile_saved": "✅ Το προφίλ σου αποθηκεύτηκε.",
        "progress_quick_log": "Γρήγορη καταγραφή σημερινού βάρους",
        "progress_weight_today": "Σημερινό βάρος (kg)",
        "progress_save": "💾 Αποθήκευση σημερινού βάρους",
        "progress_saved": "✅ Το βάρος σου για σήμερα αποθηκεύτηκε.",
        "security_question": "Ποιο είναι το αγαπημένο σου χρώμα;",
        "security_answer_label": "Απάντηση στην ερώτηση",
# Auth – κοινά
        "login_title": "Σύνδεση",
        "login_username": "Όνομα χρήστη",
        "login_password": "Κωδικός",
        "login_button": "Σύνδεση",
        "login_new_user_cta": "🆕 Νέος χρήστης; Δημιούργησε λογαριασμό",
        "login_forgot_password": "Ξέχασες τον κωδικό;",
        "login_err_no_username": "❌ Συμπλήρωσε όνομα χρήστη.",
        "login_err_no_password": "❌ Συμπλήρωσε κωδικό.",
        "login_err_no_user": "❌ Ο χρήστης δεν υπάρχει.",
        "login_err_wrong_password": "❌ Λάθος κωδικός.",
        "login_success": "✅ Επιτυχής σύνδεση!",

        # Signup
        "signup_title": "🆕 Δημιουργία λογαριασμού",
        "signup_username": "Όνομα χρήστη (login)",
        "signup_fullname": "Ονοματεπώνυμο",
        "signup_password": "Κωδικός",
        "signup_password_confirm": "Επιβεβαίωση κωδικού",
        "signup_security_answer": "Απάντηση στη μυστική ερώτηση",
        "signup_button": "Δημιουργία λογαριασμού",
        "signup_err_username_missing": "Βάλε όνομα χρήστη.",
        "signup_err_username_exists": "Το όνομα χρήστη υπάρχει ήδη.",
        "signup_err_password_missing": "Βάλε κωδικό.",
        "signup_err_password_mismatch": "Οι κωδικοί δεν ταιριάζουν.",
        "signup_err_security_missing": "Βάλε απάντηση στη μυστική ερώτηση.",
        "signup_success": "✅ Ο λογαριασμός δημιουργήθηκε. Μπορείς τώρα να συνδεθείς.",
        "signup_back_to_login": "Μετάβαση στη σελίδα σύνδεσης",

        # Forgot password
        "forgot_title": "🔑 Επαναφορά κωδικού",
        "forgot_intro": "Συμπλήρωσε τα στοιχεία σου για να αλλάξεις τον κωδικό.",
        "forgot_username": "Όνομα χρήστη",
        "forgot_new_password": "Νέος κωδικός",
        "forgot_new_password_confirm": "Επιβεβαίωση νέου κωδικού",
        "forgot_button": "Αλλαγή κωδικού",
        "forgot_err_no_user": "Ο χρήστης δεν βρέθηκε.",
        "forgot_err_no_username": "Συμπλήρωσε όνομα χρήστη.",
        "forgot_err_no_answer": "Συμπλήρωσε την απάντηση στη μυστική ερώτηση.",
        "forgot_err_no_stored_answer": "Για αυτόν τον χρήστη δεν έχει οριστεί μυστική απάντηση. Επικοινώνησε με τον διαχειριστή.",
        "forgot_err_wrong_answer": "Η απάντηση στη μυστική ερώτηση δεν είναι σωστή.",
        "forgot_err_no_password": "Βάλε νέο κωδικό.",
        "forgot_err_password_mismatch": "Οι κωδικοί δεν ταιριάζουν.",
        "forgot_success": "✅ Ο κωδικός ενημερώθηκε. Μπορείς τώρα να συνδεθείς.",
        "forgot_back_to_login": "Πίσω στη σελίδα σύνδεσης",

        # Security question (που έχουμε ήδη)
        "security_question": "Ποιο είναι το αγαπημένο σου χρώμα;",
        "security_answer_label": "Απάντηση στη μυστική ερώτηση",

        # Logout
        "logout_button": "🚪 Αποσύνδεση",
    },
    "en": {
        "security_question": "What is your favourite color?",
        "security_answer_label": "Answer to the secret question",
        "title": "02Hero – AI Nutrition Helper",
        "subtitle": "Smart, AI-powered nutrition tailored to you.",
        "intro": "Enter your details and let the AI create a weekly meal plan based on your goal.",
        "username": "User name (e.g. email or nickname)",
        "age": "Age",
        "sex": "Sex",
        "male": "Male",
        "female": "Female",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "activity": "Activity level",
        "goal": "Goal",
        "activity_opts": ["Low", "Medium", "High"],
        "goal_opts": ["Lose fat", "Maintain", "Gain muscle"],
        "allergies": "Allergies / foods to avoid",
        "allergies_ph": "e.g. nut allergy, lactose intolerance, no seafood",
        "prefs": "Favourite foods you’d like to see in your plan",
        "prefs_ph": "e.g. chicken, pasta, yogurt with honey, tuna salads",
        "submit": "Calculate & Generate AI Plan",
        "back": "← Change details & new plan",
        "plan_title": "Weekly nutrition plan from AI",
        "macros_title": "Estimated daily calories & macros",
        "download": "📥 Download plan as Excel",
        "download_shop": "🛒 Download shopping list (txt)",
        "disclaimer": "⚠️ This plan is indicative and does not replace medical or personalised dietitian advice.",
        "qa_title": "Ask a question about your plan or nutrition",
        "qa_your_q": "Your question:",
        "qa_button": "Ask AI",
        "changes_title": "Changes to the plan",
        "changes_desc": "If something doesn’t work for you (e.g. you don’t want dairy, prefer simpler dinners), write it here and the AI will adjust the table:",
        "changes_ph": "e.g. I have insulin resistance, prefer low carbs at night",
        "changes_button": "Adjust plan based on my comments",
        "need_feedback": "Write what you’d like to change first.",
        "history_title": "History",
        "sidebar_title": "02Hero",
        "sidebar_sub": "AI Nutrition Helper",
        "footer": "Created by Adam / 02Hero Coaching",
        "about_title": "About us & how to use 02Hero",
        "about_text": (
            "02Hero Nutrition Helper is a personal coaching project that uses AI "
            "(OpenAI models) to generate nutrition ideas based on your details and goals.\n\n"
            "➡️ **What it’s good at:**\n"
            "- Helps you organise and visualise a weekly plan.\n"
            "- Suggests meals, quantities and macro targets.\n"
            "- Adapts to your comments (e.g. allergies, preferences).\n\n"
            "⚠️ **What it’s NOT:**\n"
            "- It does not replace a doctor, endocrinologist or registered dietitian.\n"
            "- It does not take into account full medical history or lab results.\n\n"
            "📌 Treat the plan as a **smart draft**: a strong starting point to organise "
            "your diet or discuss with a professional, not as strict medical advice."
        ),
        "menu_home": "🏠 Home",
        "menu_new_plan": "📅 New nutrition plan",
        "menu_progress": "📈 Progress tracking",
        "menu_profile": "👤 User profile",
        "menu_about": "ℹ️ About us & our services",
        "shopping_title": "Shopping list for 7 days",
        "save_data": "💾 Save today's data",
        "saved_ok": "✅ Your data for today has been saved.",
        "saved_err_no_user": "Please enter a user name first so I can save your history.",
        "history_plan_label": "View past plan from:",
        "history_no_plan": "No saved plan found for this entry.",
        "login_title": "Log in",
        "login_button": "Continue",
        "home_welcome": "Welcome",
        "home_new_plan": "Create a new nutrition plan",
        "home_progress": "Track your progress",
        "home_view_plans": "View your past plans",
        "home_profile": "Update your profile",
        "profile_title": "User profile",
        "profile_save": "💾 Save profile",
        "profile_saved": "✅ Your profile has been saved.",
        "progress_quick_log": "Quick log of today's weight",
        "progress_weight_today": "Today's weight (kg)",
        "progress_save": "💾 Save today's weight",
        "progress_saved": "✅ Your weight for today has been saved.",
# Auth – common
        "login_title": "Login",
        "login_username": "Username",
        "login_password": "Password",
        "login_button": "Login",
        "login_new_user_cta": "🆕 New here? Create an account",
        "login_forgot_password": "Forgot password?",
        "login_err_no_username": "❌ Please enter a username.",
        "login_err_no_password": "❌ Please enter a password.",
        "login_err_no_user": "❌ User does not exist.",
        "login_err_wrong_password": "❌ Incorrect password.",
        "login_success": "✅ Login successful!",

        # Signup
        "signup_title": "🆕 Create an account",
        "signup_username": "Username (login)",
        "signup_fullname": "Full name",
        "signup_password": "Password",
        "signup_password_confirm": "Confirm password",
        "signup_security_answer": "Answer to the secret question",
        "signup_button": "Create account",
        "signup_err_username_missing": "Please enter a username.",
        "signup_err_username_exists": "This username already exists.",
        "signup_err_password_missing": "Please enter a password.",
        "signup_err_password_mismatch": "Passwords do not match.",
        "signup_err_security_missing": "Please enter an answer to the secret question.",
        "signup_success": "✅ Account created. You can now log in.",
        "signup_back_to_login": "Back to login page",

        # Forgot password
        "forgot_title": "🔑 Reset password",
        "forgot_intro": "Fill in your details to change your password.",
        "forgot_username": "Username",
        "forgot_new_password": "New password",
        "forgot_new_password_confirm": "Confirm new password",
        "forgot_button": "Change password",
        "forgot_err_no_user": "User not found.",
        "forgot_err_no_username": "Please enter a username.",
        "forgot_err_no_answer": "Please enter the answer to the secret question.",
        "forgot_err_no_stored_answer": "No secret answer stored for this user. Contact the administrator.",
        "forgot_err_wrong_answer": "The answer to the secret question is not correct.",
        "forgot_err_no_password": "Please enter a new password.",
        "forgot_err_password_mismatch": "Passwords do not match.",
        "forgot_success": "✅ Password updated. You can now log in.",
        "forgot_back_to_login": "Back to login page",

        # Security question
        "security_question": "What is your favourite color?",
        "security_answer_label": "Answer to the secret question",

        # Logout
        "logout_button": "🚪 Logout",
    },
}

DAY_LABELS = {
    "el": ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
MEAL_LABELS = {
    "el": ["Πρωινό", "Δεκατιανό", "Μεσημεριανό", "Απογευματινό", "Βραδινό", "Πριν τον ύπνο"],
    "en": ["Breakfast", "Mid-morning snack", "Lunch", "Afternoon snack", "Dinner", "Before bed"],
}


def tr(key: str) -> str:
    return TEXT[st.session_state["lang"]][key]


# ----------------- STORAGE -----------------
DATA_DIR = Path("user_data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.csv"
PROFILE_FILE = DATA_DIR / "profiles.csv"


def calculate_targets(age, sex, height_cm, weight_kg, activity, goal):
    """Rough calories & macros."""
    if sex == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_factors = {"Low": 1.2, "Medium": 1.4, "High": 1.6}
    tdee = bmr * activity_factors.get(activity, 1.4)

    if goal == "Lose fat":
        calories = tdee - 400
    elif goal == "Gain muscle":
        calories = tdee + 300
    else:
        calories = tdee

    protein_g = 2.0 * weight_kg
    fat_g = 0.8 * weight_kg
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    carbs_kcal = max(calories - protein_kcal - fat_kcal, 0)
    carbs_g = carbs_kcal / 4

    return {
        "calories": int(round(calories)),
        "protein_g": int(round(protein_g)),
        "carbs_g": int(round(carbs_g)),
        "fat_g": int(round(fat_g)),
    }


def markdown_table_to_df(md: str):
    if not md:
        return None
    lines = [l.strip() for l in md.splitlines() if l.strip().startswith("|")]
    if len(lines) < 3:
        return None
    header_line = lines[0].strip("|")
    headers = [h.strip() for h in header_line.split("|")]
    data_lines = lines[2:]
    rows = []
    for dl in data_lines:
        parts = [p.strip() for p in dl.strip("|").split("|")]
        if len(parts) == len(headers):
            rows.append(parts)
    if not rows:
        return None
    return pd.DataFrame(rows, columns=headers)


def save_history_for_today(username, age, sex, height, weight, activity, goal, targets, plan_markdown):
    """Save/update one entry per user per day."""
    username = (username or "").strip()
    if not username:
        return False

    today_str = date.today().isoformat()
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "date": today_str,
        "username": username,
        "age": age,
        "sex": sex,
        "height_cm": height,
        "weight_kg": weight,
        "activity": activity,
        "goal": goal,
        "calories": targets["calories"],
        "protein_g": targets["protein_g"],
        "carbs_g": targets["carbs_g"],
        "fat_g": targets["fat_g"],
        "plan_markdown": plan_markdown,
    }

    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame(columns=row.keys())

    for col in row.keys():
        if col not in df.columns:
            df[col] = pd.NA

    mask = (df["username"] == username) & (df["date"] == today_str)
    df = df[~mask]

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)
    return True


def load_profile(username: str):
    username = (username or "").strip()
    if not username or not PROFILE_FILE.exists():
        return
    df = pd.read_csv(PROFILE_FILE)
    row = df[df["username"] == username]
    if row.empty:
        return
    row = row.iloc[0]
    for field in ["age", "sex", "height_cm", "weight_kg", "activity", "goal", "allergies", "preferred_foods"]:
        if field in row and pd.notna(row[field]):
            if field == "age":
                st.session_state["age"] = int(row[field])
            elif field == "height_cm":
                st.session_state["height"] = int(row[field])
            elif field == "weight_kg":
                st.session_state["weight"] = float(row[field])
            elif field in ["activity", "goal"]:
                st.session_state[field] = str(row[field])
            elif field == "sex":
                st.session_state["sex"] = str(row[field])
            elif field == "allergies":
                st.session_state["allergies"] = str(row[field])
            elif field == "preferred_foods":
                st.session_state["preferred_foods"] = str(row[field])


def save_profile(username: str):
    username = (username or "").strip()
    if not username:
        return False

    row = {
        "username": username,
        "age": int(st.session_state["age"]),
        "sex": st.session_state["sex"],
        "height_cm": int(st.session_state["height"]),
        "weight_kg": float(st.session_state["weight"]),
        "activity": st.session_state["activity"],
        "goal": st.session_state["goal"],
        "allergies": st.session_state["allergies"],
        "preferred_foods": st.session_state["preferred_foods"],
    }

    if PROFILE_FILE.exists():
        df = pd.read_csv(PROFILE_FILE)
    else:
        df = pd.DataFrame(columns=row.keys())

    for col in row.keys():
        if col not in df.columns:
            df[col] = pd.NA

    df = df[df["username"] != username]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(PROFILE_FILE, index=False)
    return True

def delete_account(username: str):
    """Delete user completely and log them out."""
    username = (username or "").strip()
    if not username:
        return

    # 1) Remove from users.json
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)

    # 2) Remove user-specific data folder (if you use one)
    import os, shutil
    user_folder = f"user_data/{username}"
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)

    # 3) Clear session and go to login
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["page"] = "login"

    st.success("Ο λογαριασμός σου διαγράφηκε με επιτυχία.")
    st.rerun()

@st.dialog("⚠️ Διαγραφή λογαριασμού")
def delete_dialog(username: str):
    st.write(
        "Αυτή η ενέργεια **δεν μπορεί να αναιρεθεί**. "
        "Όλα τα δεδομένα σου θα χαθούν οριστικά."
    )

    confirm_text = st.text_input(
        "Για επιβεβαίωση, γράψε το όνομα χρήστη σου:",
        placeholder=username,
        key="dialog_delete_confirm_input",
    )

    col1, col2 = st.columns(2)
    with col1:
        confirm = st.button("Ναι, διαγραφή", key="dialog_do_delete")
    with col2:
        cancel = st.button("Άκυρο", key="dialog_cancel_delete")

    if confirm:
        if confirm_text.strip().lower() == username.lower():
            delete_account(username)
        else:
            st.error("Το όνομα χρήστη δεν ταιριάζει. Η διαγραφή ακυρώθηκε.")

    if cancel:
        # Κλείνει το dialog χωρίς να κάνει τίποτα
        st.rerun()

def admin_page():
    st.title("🛠 Admin Panel")

    users = load_users()

    # ---- SECTION 1: Existing users ----
    st.subheader("👥 Υπάρχοντες χρήστες")
    if not users:
        st.info("Δεν υπάρχουν χρήστες ακόμα.")
    else:
        for username, info in users.items():
            role = info.get("role", "user")
            fullname = info.get("fullname", "")
            last_login = info.get("last_login", "—")
            st.markdown(
                f"- **{username}** ({role}) – {fullname} — "
                f"_Last login_: {last_login}"
            )

    st.write("---")

    # ---- SECTION 2: Create new user ----
    st.subheader("➕ Δημιουργία νέου χρήστη")
    with st.form("create_user_form"):
        new_username = st.text_input("Όνομα χρήστη (login)").strip()
        new_fullname = st.text_input("Ονοματεπώνυμο").strip()
        new_role = st.selectbox("Ρόλος", ["user", "admin"])
        new_password = st.text_input("Κωδικός", type="password")
        new_password2 = st.text_input("Επιβεβαίωση κωδικού", type="password")
        security_answer = st.text_input(
            f"{tr('security_answer_label')} ({get_security_question()})"
        ).strip()

        submit_create = st.form_submit_button("Δημιουργία")

    if submit_create:
        if not new_username:
            st.error("Βάλε όνομα χρήστη.")
        elif new_username in users:
            st.error("Αυτό το όνομα χρήστη υπάρχει ήδη.")
        elif not new_password:
            st.error("Βάλε κωδικό.")
        elif new_password != new_password2:
            st.error("Οι κωδικοί δεν ταιριάζουν.")
        elif not security_answer:
            st.error("Βάλε απάντηση στην ερώτηση.")
        else:
            users[new_username] = {
                "password": hash_password(new_password),
                "fullname": new_fullname,
                "role": new_role,
                # store lowercase answer for easy comparison
                "security_answer": security_answer.lower(),
            }
            save_users(users)
            st.success(f"✅ Ο χρήστης **{new_username}** δημιουργήθηκε.")
            st.rerun()

    st.write("---")

    # ---- SECTION 3: Change password ----
    st.subheader("🔑 Αλλαγή κωδικού χρήστη")
    if users:
        usernames_list = list(users.keys())
        with st.form("change_password_form"):
            target_user = st.selectbox("Επίλεξε χρήστη", usernames_list)
            new_pass = st.text_input("Νέος κωδικός", type="password")
            new_pass2 = st.text_input("Επιβεβαίωση νέου κωδικού", type="password")
            submit_change = st.form_submit_button("Αλλαγή κωδικού")

        if submit_change:
            if not new_pass:
                st.error("Βάλε νέο κωδικό.")
            elif new_pass != new_pass2:
                st.error("Οι κωδικοί δεν ταιριάζουν.")
            else:
                users[target_user]["password"] = hash_password(new_pass)
                save_users(users)
                st.success(f"✅ Ο κωδικός του **{target_user}** ενημερώθηκε.")
                st.rerun()

    st.write("---")

    # ---- SECTION 4: Delete user ----
    st.subheader("🗑 Διαγραφή χρήστη")
    if users:
        with st.form("delete_user_form"):
            delete_user = st.selectbox("Επίλεξε χρήστη για διαγραφή", list(users.keys()))
            confirm = st.checkbox("Επιβεβαίωση διαγραφής")
            submit_delete = st.form_submit_button("Διαγραφή")

        if submit_delete:
            if not confirm:
                st.error("Πρέπει να επιβεβαιώσεις τη διαγραφή.")
            elif delete_user == st.session_state.get("username"):
                st.error("Δεν μπορείς να διαγράψεις τον εαυτό σου ενώ είσαι συνδεδεμένος.")
            else:
                users.pop(delete_user, None)
                save_users(users)
                st.success(f"✅ Ο χρήστης **{delete_user}** διαγράφηκε.")
                st.rerun()

def signup_page():
    users = load_users()

    # flag για επιτυχημένη εγγραφή
    if "signup_success" not in st.session_state:
        st.session_state["signup_success"] = False

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.title(tr("signup_title"))

        # ---- SIGNUP FORM ----
        with st.form("signup_form"):
            username = st.text_input(tr("signup_username")).strip()
            fullname = st.text_input(tr("signup_fullname")).strip()
            password = st.text_input(tr("signup_password"), type="password")
            password2 = st.text_input(tr("signup_password_confirm"), type="password")
            security_answer = st.text_input(
                f"{tr('signup_security_answer')} ({get_security_question()})"
            ).strip()
            submit_signup = st.form_submit_button(tr("signup_button"))

        # ---- HANDLE SUBMIT ----
        if submit_signup:
            if not username:
                st.error(tr("signup_err_username_missing"))
                return
            if username in users:
                st.error(tr("signup_err_username_exists"))
                return
            if not password:
                st.error(tr("signup_err_password_missing"))
                return
            if password != password2:
                st.error(tr("signup_err_password_mismatch"))
                return
            if not security_answer:
                st.error(tr("signup_err_security_missing"))
                return

            users[username] = {
                "password": hash_password(password),
                "fullname": fullname,
                "role": "user",
                "security_answer": security_answer.lower(),
            }
            save_users(users)

            st.session_state["signup_success"] = True
            st.success(tr("signup_success"))

        # ---- BACK TO LOGIN BUTTON (πάντα έξω από το if submit_signup) ----
        if st.session_state["signup_success"]:
            if st.button(tr("signup_back_to_login")):
                st.session_state["signup_success"] = False
                st.session_state["page"] = "login"
                st.session_state["logged_in"] = False
                st.rerun()
        # 🔥 PANEL WRAPPER — τελειώνει εδώ
        st.markdown("</div>", unsafe_allow_html=True)



def forgot_password_page():
    users = load_users()
    if not users:
        st.warning("Δεν υπάρχουν εγγεγραμμένοι χρήστες.")
        return

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.title(tr("forgot_title"))
        st.write(tr("forgot_intro"))

        with st.form("forgot_password_form"):
            username_input = st.text_input(tr("forgot_username"))
            security_answer_input = st.text_input(
                f"{tr('security_answer_label')}: {get_security_question()}"
            )
            new_pass = st.text_input(tr("forgot_new_password"), type="password")
            new_pass2 = st.text_input(tr("forgot_new_password_confirm"), type="password")
            submit_reset = st.form_submit_button(tr("forgot_button"))

        if submit_reset:
            username_clean = username_input.strip()

            if not username_clean:
                st.error(tr("forgot_err_no_username"))
                return

            username_map = {u.lower(): u for u in users.keys()}
            if username_clean.lower() not in username_map:
                st.error(tr("forgot_err_no_user"))
                return

            actual_key = username_map[username_clean.lower()]
            user_data = users.get(actual_key, {})

            stored_answer = user_data.get("security_answer")
            if not stored_answer:
                st.error(tr("forgot_err_no_stored_answer"))
                return

            if not security_answer_input.strip():
                st.error(tr("forgot_err_no_answer"))
                return

            if stored_answer != security_answer_input.strip().lower():
                st.error(tr("forgot_err_wrong_answer"))
                return

            if not new_pass:
                st.error(tr("forgot_err_no_password"))
                return
            if new_pass != new_pass2:
                st.error(tr("forgot_err_password_mismatch"))
                return

            users[actual_key]["password"] = hash_password(new_pass)
            save_users(users)
            st.success(tr("forgot_success"))

            if st.button(tr("forgot_back_to_login")):
                st.session_state["page"] = "login"
                st.rerun()

# ----------------- SESSION STATE -----------------
defaults = {
    "username": "",
    "age": 27,
    "sex": "male",
    "height": 170,
    "weight": 79.0,
    "activity": "Medium",
    "goal": "Lose fat",
    "allergies": "",
    "preferred_foods": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "plan" not in st.session_state:
    st.session_state["plan"] = None
if "show_form" not in st.session_state:
    st.session_state["show_form"] = True
if "qa_history" not in st.session_state:
    st.session_state["qa_history"] = []
if "qa_input" not in st.session_state:
    st.session_state["qa_input"] = ""
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ----------------- LANGUAGE BUTTONS (πάνω αριστερά) -----------------
lang_col1, _ = st.columns([0.15, 0.85])
with lang_col1:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("GR", use_container_width=True):
            st.session_state["lang"] = "el"
            st.rerun()
    with c2:
        if st.button("EN", use_container_width=True):
            st.session_state["lang"] = "en"
            st.rerun()

# ----------------- SIDEBAR NAV (μόνο όταν είναι logged in) -----------------
if st.session_state["logged_in"]:
    with st.sidebar:
        # --- LOGO & BRAND ---
        st.markdown(
            "<div style='text-align:center; margin-top:1rem; margin-bottom:0.5rem;'>",
            unsafe_allow_html=True,
        )
        st.image("assets/logo.png", width=230)

        st.markdown("---")
        st.markdown(f"**{tr('sidebar_title')}**")
        st.markdown(f"<span style='font-size:0.85rem; opacity:0.8;'>{tr('sidebar_sub')}</span>", unsafe_allow_html=True)
        st.markdown("---")

        # Κύριες ενέργειες
        if st.button(tr("menu_home"), use_container_width=True, type="secondary"):
            st.session_state["page"] = "home"

        if st.button(tr("menu_new_plan"), use_container_width=True, type="secondary"):
            st.session_state["page"] = "new_plan"

        st.markdown("---")

        # Δευτερεύουσες επιλογές
        if st.button(tr("menu_progress"), use_container_width=True):
            st.session_state["page"] = "progress"

        if st.button(tr("menu_profile"), use_container_width=True):
            st.session_state["page"] = "profile"

        if st.button(tr("menu_about"), use_container_width=True):
            st.session_state["page"] = "about"

        # --- ADMIN BUTTON (only for admin role) ---
        if st.session_state.get("role") == "admin":
            st.markdown("---")
            if st.button("🛠 Admin panel", use_container_width=True):
                st.session_state["page"] = "admin"
                st.rerun()

        st.markdown("---")
        if st.button(tr("logout_button"), use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = "user"
            st.session_state["page"] = "login"
            st.rerun()

# ----------------- TITLE -----------------
st.markdown(
    f"<h1 style='text-align:center; margin-top:1.0rem; color:#111; text-shadow:0 0 6px rgba(255,255,255,0.6);'>{tr('title')}</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center; opacity:0.85;color:#111; text-shadow:0 0 6px rgba(255,255,255,0.6);'>{tr('subtitle')}</p>",
    unsafe_allow_html=True,
)



# ----------------- LOGIN / SIGNUP / FORGOT PASSWORD ROUTING -----------------
if not st.session_state.get("logged_in", False):

    # 1) Forgot password page
    if st.session_state.get("page") == "forgot_password":
        forgot_password_page()
        st.stop()

    # 2) Signup page
    if st.session_state.get("page") == "signup":
        signup_page()
        st.stop()

    # 3) Διαφορετικά: LOGIN
    st.session_state["page"] = "login"

    outer_left, outer_center, outer_right = st.columns([1, 2, 1])
    with outer_center:

        # --- LOGO πάνω από τη φόρμα ---
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:1.5rem; margin-bottom:1.5rem;">
                <img src="data:image/png;base64,{LOGO_BASE64}"
                     style="width:380px; max-width:90%; height:auto; display:block; margin:0 auto;">
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

        users = load_users()

        # --- LOGIN FORM (ΟΛΑ ΜΕΣΑ ΣΤΟ ΙΔΙΟ ΠΛΑΙΣΙΟ) ---
        with st.form("login_form_main"):
            st.subheader(tr("login_title"))  # ΤΙΤΛΟΣ ΜΕΣΑ ΣΤΗ ΦΟΡΜΑ

            username_input = st.text_input(tr("login_username"))
            password_input = st.text_input(tr("login_password"), type="password")

            # Κουμπί Σύνδεσης
            submit_login = st.form_submit_button(
                tr("login_button"),
                use_container_width=True,
            )

            # Κουμπί: Νέος χρήστης
            signup_clicked = st.form_submit_button(
                tr("login_new_user_cta"),
                use_container_width=True,
            )

            # Κουμπί: Ξέχασες τον κωδικό;
            forgot_clicked = st.form_submit_button(
                tr("login_forgot_password"),
                use_container_width=True,
            )

        # --- Routing για τα δύο βοηθητικά κουμπιά ---
        if signup_clicked:
            st.session_state["page"] = "signup"
            st.rerun()

        if forgot_clicked:
            st.session_state["page"] = "forgot_password"
            st.rerun()

        # --- LOGIN LOGIC ---
        if submit_login:
            username_clean = username_input.strip()

            if not username_clean:
                st.error(tr("login_err_no_username"))
            elif not password_input:
                st.error(tr("login_err_no_password"))
            else:
                users = load_users()
                username_map = {u.lower(): u for u in users.keys()}

                if username_clean.lower() not in username_map:
                    st.error(tr("login_err_no_user"))
                else:
                    actual_key = username_map[username_clean.lower()]
                    stored_hash = users[actual_key]["password"]

                    if not check_password(password_input, stored_hash):
                        st.error(tr("login_err_wrong_password"))
                    else:
                        st.success(tr("login_success"))
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = actual_key
                        st.session_state["role"] = users[actual_key].get("role", "user")
                        update_last_login(actual_key)
                        load_profile(actual_key)
                        st.session_state["page"] = "home"
                        st.rerun()

    st.stop()

# ----------------- ROUTING ΑΝΑΛΟΓΑ ΜΕ ΤΗ ΣΕΛΙΔΑ -----------------

page = st.session_state["page"]

# HOME / DASHBOARD
if page == "home":
    lang = st.session_state["lang"]
    username = (st.session_state.get("username") or "").strip()

    # Καλωσόρισμα
    st.subheader(f"{tr('home_welcome')} {username or ''}".strip())
    st.write("")
    st.write(tr("intro"))

    st.write("")
    st.markdown("### 🚀 Ξεκίνα από εδώ")

    # Κύριο, μεγάλο CTA – μόνο του
    primary_cta = st.button(
        "📅 " + tr("home_new_plan"),
        use_container_width=True,
        type="secondary",
    )
    if primary_cta:
        st.session_state["page"] = "new_plan"
        st.rerun()

    st.write("")
    st.markdown("### Άλλες επιλογές")

    # ΟΛΕΣ οι άλλες επιλογές κάθετα μία-μία
    if st.button("📈 " + tr("home_progress"), use_container_width=True):
        st.session_state["page"] = "progress"
        st.rerun()

    if st.button("👤 " + tr("home_profile"), use_container_width=True):
        st.session_state["page"] = "profile"
        st.rerun()

    if st.button("📚 " + tr("home_view_plans"), use_container_width=True):
        st.session_state["page"] = "progress"
        st.rerun()

    # Λίγη σύνοψη από το ιστορικό αν υπάρχει
    if username and HISTORY_FILE.exists():
        df_hist = pd.read_csv(HISTORY_FILE)
        user_hist = df_hist[df_hist["username"] == username].copy()
        if not user_hist.empty:
            user_hist["timestamp"] = pd.to_datetime(user_hist["timestamp"])
            user_hist = user_hist.sort_values("timestamp")
            last_row = user_hist.iloc[-1]
            start_row = user_hist.iloc[0]
            diff = round(last_row["weight_kg"] - start_row["weight_kg"], 1)

            if lang == "el":
                st.markdown(
                    f"""
                    <div style="
                        margin-top:1.5rem; 
                        padding:1rem 1.2rem; 
                        border-radius:0.75rem;
                        background-color: rgba(255,255,255,0.03);
                        border: 1px solid rgba(255,255,255,0.12);
                    ">
                        <div style="font-weight:600; margin-bottom:0.5rem;">
                            Μικρή σύνοψη προόδου
                        </div>
                        <div style="font-size:0.9rem; line-height:1.5;">
                            • Τελευταία καταγραφή βάρους: <b>{last_row['weight_kg']} kg</b><br>
                            • Πρώτη καταγραφή: <b>{start_row['weight_kg']} kg</b><br>
                            • Αλλαγή: <b>{diff} kg</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        margin-top:1.5rem; 
                        padding:1rem 1.2rem; 
                        border-radius:0.75rem;
                        background-color: rgba(255,255,255,0.03);
                        border: 1px solid rgba(255,255,255,0.12);
                    ">
                        <div style="font-weight:600; margin-bottom:0.5rem;">
                            Quick progress summary
                        </div>
                        <div style="font-size:0.9rem; line-height:1.5;">
                            • Last recorded weight: <b>{last_row['weight_kg']} kg</b><br>
                            • First recorded weight: <b>{start_row['weight_kg']} kg</b><br>
                            • Change: <b>{diff} kg</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



# PROFILE PAGE
elif page == "profile":
    st.subheader(tr("profile_title"))
    st.write("")

    with st.form("profile_form"):
        st.session_state["age"] = st.number_input(
            tr("age"), min_value=10, max_value=90, value=int(st.session_state["age"])
        )

        sex_label = tr("male") if st.session_state["sex"] == "male" else tr("female")
        sex_choice = st.selectbox(
            tr("sex"),
            [tr("male"), tr("female")],
            index=0 if sex_label == tr("male") else 1,
        )
        st.session_state["sex"] = "male" if sex_choice == tr("male") else "female"

        st.session_state["height"] = st.number_input(
            tr("height"), min_value=120, max_value=220, value=int(st.session_state["height"])
        )
        st.session_state["weight"] = st.number_input(
            tr("weight"), min_value=40.0, max_value=200.0, value=float(st.session_state["weight"])
        )

        activity_opts = tr("activity_opts")
        goal_opts = tr("goal_opts")

        st.session_state["activity"] = st.selectbox(
            tr("activity"),
            activity_opts,
            index=activity_opts.index(st.session_state["activity"]),
        )
        st.session_state["goal"] = st.selectbox(
            tr("goal"),
            goal_opts,
            index=goal_opts.index(st.session_state["goal"]),
        )

        st.session_state["allergies"] = st.text_area(
            tr("allergies"),
            value=st.session_state["allergies"],
            placeholder=tr("allergies_ph"),
        )
        st.session_state["preferred_foods"] = st.text_area(
            tr("prefs"),
            value=st.session_state["preferred_foods"],
            placeholder=tr("prefs_ph"),
        )

        save_profile_btn = st.form_submit_button(tr("profile_save"))

    if save_profile_btn:
        if not (st.session_state.get("username") or "").strip():
            st.warning(tr("saved_err_no_user"))
        else:
            save_profile(st.session_state["username"])
            st.success(tr("profile_saved"))

    st.write("---")

    # ---------- DELETE ACCOUNT SECTION ----------
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader("⚠️ Διαγραφή λογαριασμού")
        st.caption("Αυτή η ενέργεια είναι οριστική και δεν μπορεί να αναιρεθεί.")
    with col_btn:
        delete_clicked = st.button(
            "🗑️ Διαγραφή",
            key="open_delete",
            use_container_width=True,
            type="primary",  # <-- αυτό
        )

    if delete_clicked:
        delete_dialog(st.session_state.get("username", ""))

    if st.session_state.get("confirm_delete", False):
        # "Popup-style" block – σαν διάλογος επιβεβαίωσης
        st.error(
            "### Είσαι σίγουρος ότι θέλεις να διαγράψεις τον λογαριασμό σου;\n"
            "Αυτή η ενέργεια **δεν μπορεί να αναιρεθεί**. Όλα τα δεδομένα σου θα χαθούν.",
            icon="⚠️",
        )

        username = st.session_state.get("username", "")
        confirm_text = st.text_input(
            "Για επιβεβαίωση, γράψε το όνομα χρήστη σου:",
            placeholder=username,
            key="delete_confirm_input",
        )

        c1, c2 = st.columns(2)
        with c1:
            confirm_delete = st.button("Ναι, διαγραφή", key="do_delete")
        with c2:
            cancel_delete = st.button("Άκυρο", key="cancel_delete")

        if confirm_delete:
            if confirm_text.strip().lower() == username.lower():
                st.session_state["confirm_delete"] = False
                delete_account(username)
            else:
                st.error("Το όνομα χρήστη δεν ταιριάζει. Η διαγραφή ακυρώθηκε.")
                st.session_state["confirm_delete"] = False

        if cancel_delete:
            st.session_state["confirm_delete"] = False
            st.rerun()


# ADMIN PAGE
elif page == "admin":
    # extra safety: only allow admin role
    if st.session_state.get("role") == "admin":
        admin_page()
    else:
        st.error("Δεν έχεις δικαίωμα πρόσβασης σε αυτή τη σελίδα.")

# FORGOT PASSWORD PAGE
elif page == "forgot_password":
    forgot_password_page()

# NEW PLAN PAGE
elif page == "new_plan":
    if st.session_state["show_form"]:
        st.write(tr("intro"))

        with st.form("user_input_form"):
            st.session_state["age"] = st.number_input(
                tr("age"), min_value=10, max_value=90, value=int(st.session_state["age"])
            )

            sex_label = tr("male") if st.session_state["sex"] == "male" else tr("female")
            sex_choice = st.selectbox(
                tr("sex"),
                [tr("male"), tr("female")],
                index=0 if sex_label == tr("male") else 1,
            )
            st.session_state["sex"] = "male" if sex_choice == tr("male") else "female"

            st.session_state["height"] = st.number_input(
                tr("height"), min_value=120, max_value=220, value=int(st.session_state["height"])
            )
            st.session_state["weight"] = st.number_input(
                tr("weight"), min_value=40.0, max_value=200.0, value=float(st.session_state["weight"])
            )

            activity_opts = tr("activity_opts")
            goal_opts = tr("goal_opts")

            st.session_state["activity"] = st.selectbox(
                tr("activity"),
                activity_opts,
                index=activity_opts.index(st.session_state["activity"]),
            )
            st.session_state["goal"] = st.selectbox(
                tr("goal"),
                goal_opts,
                index=goal_opts.index(st.session_state["goal"]),
            )

            st.session_state["allergies"] = st.text_area(
                tr("allergies"),
                value=st.session_state["allergies"],
                placeholder=tr("allergies_ph"),
            )
            st.session_state["preferred_foods"] = st.text_area(
                tr("prefs"),
                value=st.session_state["preferred_foods"],
                placeholder=tr("prefs_ph"),
            )

            submitted = st.form_submit_button(tr("submit"))

        if submitted:
            if not client:
                st.error("OPENAI_API_KEY is missing in your .env file.")
            else:
                with st.spinner(
                    "Generating your plan with AI..."
                    if st.session_state["lang"] == "en"
                    else "Φτιάχνω το πρόγραμμα με AI..."
                ):
                    age = int(st.session_state["age"])
                    sex = st.session_state["sex"]
                    height = int(st.session_state["height"])
                    weight = float(st.session_state["weight"])
                    activity = st.session_state["activity"]
                    goal = st.session_state["goal"]
                    allergies = st.session_state["allergies"].strip()
                    prefs = st.session_state["preferred_foods"].strip()

                    targets = calculate_targets(age, sex, height, weight, activity, goal)

                    lang = st.session_state["lang"]

                    if lang == "el":
                        allergies_text = allergies or "καμία συγκεκριμένη"
                        prefs_text = prefs or "δεν δήλωσε συγκεκριμένα αγαπημένα φαγητά"
                        header = "| Γεύμα / Ημέρα | " + " | ".join(DAY_LABELS["el"]) + " |"
                        row_names = ", ".join(MEAL_LABELS["el"])
                        user_desc = f"""
Στοιχεία χρήστη:
- Ηλικία: {age}
- Φύλο: {sex}
- Ύψος: {height} cm
- Βάρος: {weight} kg
- Δραστηριότητα: {activity}
- Στόχος: {goal}
- Αλλεργίες / τροφές προς αποφυγή: {allergies_text}
- Αγαπημένα φαγητά: {prefs_text}

Εκτίμηση ημερήσιων αναγκών:
- Θερμίδες: περίπου {targets['calories']} kcal/ημέρα
- Πρωτεΐνη: περίπου {targets['protein_g']} γρ/ημέρα
- Υδατάνθρακες: περίπου {targets['carbs_g']} γρ/ημέρα
- Λίπος: περίπου {targets['fat_g']} γρ/ημέρα
"""
                        plan_prompt = f"""
You are an experienced nutrition coach.

{user_desc}

Φτιάξε ένα εβδομαδιαίο πρόγραμμα διατροφής σε μορφή πίνακα Markdown.

Προδιαγραφές πίνακα:
- Η πρώτη γραμμή (κεφαλίδα) να είναι ΑΚΡΙΒΩΣ:
  {header}
- Η πρώτη στήλη να είναι τα γεύματα στη σειρά:
  {row_names}.
- Κάθε κελί να περιγράφει σύντομα το γεύμα της ημέρας με απλά ελληνικά φαγητά
  και ενδεικτικές ποσότητες (π.χ. 150 γρ. κοτόπουλο, 1 φέτα ψωμί ολικής κτλ.).
- Το πρόγραμμα να ταιριάζει με τον στόχο του χρήστη και τα macros.

Σημαντικό:
- Επέστρεψε ΜΟΝΟ τον πίνακα σε μορφή Markdown.
- Μην γράψεις επιπλέον κείμενο.
"""
                    else:
                        allergies_text = allergies or "none specified"
                        prefs_text = prefs or "no specific favourite foods given"
                        header = "| Meal / Day | " + " | ".join(DAY_LABELS["en"]) + " |"
                        row_names = ", ".join(MEAL_LABELS["en"])
                        user_desc = f"""
User details:
- Age: {age}
- Sex: {sex}
- Height: {height} cm
- Weight: {weight} kg
- Activity: {activity}
- Goal: {goal}
- Allergies / foods to avoid: {allergies_text}
- Favourite foods: {prefs_text}

Estimated daily targets:
- Calories: ~{targets['calories']} kcal/day
- Protein: ~{targets['protein_g']} g/day
- Carbs: ~{targets['carbs_g']} g/day
- Fat: ~{targets['fat_g']} g/day
"""
                        plan_prompt = f"""
You are an experienced nutrition coach.

{user_desc}

Create a weekly meal plan as a Markdown table.

Table specs:
- Header row MUST be exactly:
  {header}
- First column must be the meals in this order:
  {row_names}.
- Each cell should briefly describe that day's meal with simple foods
  and approximate quantities (e.g. 150 g chicken, 1 slice wholegrain bread, etc.).
- The plan should roughly match the user's goal and macros.

Important:
- Return ONLY the table in Markdown format.
- Do NOT add any explanation or extra text.
"""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful, precise nutrition assistant.",
                            },
                            {"role": "user", "content": plan_prompt},
                        ],
                    )
                    st.session_state["plan"] = response.choices[0].message.content
                    st.session_state["show_form"] = False
                    st.session_state["qa_history"] = []
                    st.session_state["qa_input"] = ""
                    st.rerun()

    else:
        # BACK BUTTON for new plan
        if st.button(tr("back")):
            st.session_state["show_form"] = True
            st.session_state["plan"] = None
            st.session_state["qa_history"] = []
            st.session_state["qa_input"] = ""
            st.rerun()

        age = int(st.session_state["age"])
        sex = st.session_state["sex"]
        height = int(st.session_state["height"])
        weight = float(st.session_state["weight"])
        activity = st.session_state["activity"]
        goal = st.session_state["goal"]
        targets = calculate_targets(age, sex, height, weight, activity, goal)

        st.subheader(tr("plan_title"))
        df_plan = markdown_table_to_df(st.session_state["plan"])
        lang = st.session_state["lang"]

        if df_plan is not None:
            visual_df = df_plan.copy()

            def multiline_cell(val):
                if isinstance(val, str):
                    return val.replace(", ", "<br>")
                return val

            visual_df = visual_df.applymap(multiline_cell)
            html_table = visual_df.to_html(index=False, escape=False)

            subtitle = (
                "Εβδομαδιαίο πρόγραμμα (οπτική μορφή)"
                if lang == "el"
                else "Weekly plan (visual view)"
            )
            st.markdown(f"##### {subtitle}")
            st.markdown(
                f"<div style='overflow-x:auto;'>{html_table}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Δεν μπόρεσα να μετατρέψω το πρόγραμμα σε πίνακα.")

        st.subheader(tr("macros_title"))
        if lang == "el":
            st.markdown(
                f"""
- Θερμίδες: **≈ {targets['calories']} kcal/ημέρα**
- Πρωτεΐνη: **≈ {targets['protein_g']} γρ/ημέρα**
- Υδατάνθρακες: **≈ {targets['carbs_g']} γρ/ημέρα**
- Λίπος: **≈ {targets['fat_g']} γρ/ημέρα**
"""
            )
        else:
            st.markdown(
                f"""
- Calories: **≈ {targets['calories']} kcal/day**
- Protein: **≈ {targets['protein_g']} g/day**
- Carbs: **≈ {targets['carbs_g']} g/day**
- Fat: **≈ {targets['fat_g']} g/day**
"""
            )

        st.markdown(
            f"<p style='font-size:0.9rem; opacity:0.8;'>{tr('disclaimer')}</p>",
            unsafe_allow_html=True,
        )

        # Download Excel
        if df_plan is not None:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_plan.to_excel(writer, index=False, sheet_name="Diet Plan")
                writer.close()
            st.download_button(
                label=tr("download"),
                data=buffer.getvalue(),
                file_name="diet_plan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # Shopping list download (txt)
        if df_plan is not None:
            items = []
            for col in df_plan.columns[1:]:
                for cell in df_plan[col]:
                    if isinstance(cell, str):
                        for part in cell.split(","):
                            part = part.strip()
                            if part:
                                items.append(part)

            unique_items = sorted(set(items))
            shopping_text = "\n".join(f"- {item}" for item in unique_items)

            st.markdown("---")
            st.subheader(tr("shopping_title"))
            st.download_button(
                label=tr("download_shop"),
                data=shopping_text.encode("utf-8"),
                file_name="shopping_list.txt",
                mime="text/plain",
            )

        # Save today's data (plan + metrics)
        st.markdown("---")
        if st.button(tr("save_data")):
            if not (st.session_state.get("username") or "").strip():
                st.warning(tr("saved_err_no_user"))
            else:
                ok = save_history_for_today(
                    st.session_state["username"],
                    age,
                    sex,
                    height,
                    weight,
                    activity,
                    goal,
                    targets,
                    st.session_state["plan"],
                )
                if ok:
                    st.success(tr("saved_ok"))

        st.write("---")

        # Q&A SECTION
        st.subheader(tr("qa_title"))

        if st.session_state["qa_history"]:
            for msg in st.session_state["qa_history"][-6:]:
                who = (
                    "Εσύ"
                    if (msg["role"] == "user" and lang == "el")
                    else ("You" if msg["role"] == "user" else "AI")
                )
                st.markdown(f"**{who}:** {msg['content']}")

        with st.form("qa_form"):
            st.session_state["qa_input"] = st.text_input(
                tr("qa_your_q"),
                value=st.session_state["qa_input"],
            )
            send_q = st.form_submit_button(tr("qa_button"))

        if send_q and st.session_state["qa_input"].strip():
            question = st.session_state["qa_input"].strip()
            st.session_state["qa_history"].append({"role": "user", "content": question})

            plan_text = st.session_state["plan"]

            if lang == "el":
                qa_prompt = f"""
Είσαι έμπειρος διατροφολόγος.

Ο χρήστης έχει το παρακάτω εβδομαδιαίο πρόγραμμα διατροφής (πίνακας Markdown):

{plan_text}

Ο χρήστης ρωτάει:
{question}

Απάντησε στα ελληνικά, σύντομα, φιλικά και πρακτικά.
Μην ξαναγράψεις όλο το πρόγραμμα, απάντησε μόνο στην ερώτηση.
"""
            else:
                qa_prompt = f"""
You are an experienced nutrition coach.

The user has the following weekly diet plan (Markdown table):

{plan_text}

The user asks:
{question}

Answer in English, short, friendly and practical.
Do NOT rewrite the entire plan, just answer the question.
"""

            with st.spinner("Το AI σκέφτεται..." if lang == "el" else "AI is thinking..."):
                qa_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.4,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful, practical nutrition coach.",
                        },
                        {"role": "user", "content": qa_prompt},
                    ],
                )
            answer = qa_resp.choices[0].message.content
            st.session_state["qa_history"].append(
                {"role": "assistant", "content": answer}
            )

            st.session_state["qa_input"] = ""
            st.rerun()

        st.write("---")

        # CHANGES SECTION
        st.subheader(tr("changes_title"))
        st.write(tr("changes_desc"))

        with st.form("changes_form"):
            feedback = st.text_area(
                "Τι θα ήθελες να αλλάξει στο πρόγραμμα;"
                if lang == "el"
                else "What would you like to change in the plan?",
                placeholder=tr("changes_ph"),
            )
            apply_changes = st.form_submit_button(tr("changes_button"))

        if apply_changes:
            if not feedback.strip():
                st.warning(tr("need_feedback"))
            else:
                if lang == "el":
                    adjust_prompt = f"""
Εδώ είναι το τωρινό εβδομαδιαίο πρόγραμμα διατροφής σε πίνακα Markdown:

{st.session_state["plan"]}

Ο χρήστης έγραψε τα εξής σχόλια / αλλαγές που θέλει:
{feedback}

Φτιάξε ΝΕΟ πρόγραμμα, με την ίδια ακριβώς μορφή πίνακα (ίδιες στήλες, ίδιες ημέρες, ίδια γεύματα),
αλλά προσαρμοσμένο στις επιθυμίες του χρήστη.

Πολύ σημαντικό:
- Γράψε μόνο τον πίνακα σε μορφή Markdown.
- Μην προσθέσεις επιπλέον κείμενο.
"""
                else:
                    adjust_prompt = f"""
Here is the current weekly diet plan as a Markdown table:

{st.session_state["plan"]}

The user wants the following changes:
{feedback}

Create a NEW plan, with the exact same table structure (same days, same meal rows),
but adjusted to the user's comments.

Important:
- Return ONLY the table in Markdown format.
- Do NOT add any extra text.
"""

                with st.spinner(
                    "Προσαρμόζω το πρόγραμμα..." if lang == "el" else "Adjusting the plan..."
                ):
                    new_resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        temperature=0,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful nutrition assistant.",
                            },
                            {"role": "user", "content": adjust_prompt},
                        ],
                    )
                st.session_state["plan"] = new_resp.choices[0].message.content
                st.rerun()

# PROGRESS PAGE (ιστορικό + γρήγορο log + παλιά πλάνα)
elif page == "progress":
    import altair as alt

    lang = st.session_state["lang"]
    username = (st.session_state.get("username") or "").strip()

    st.subheader(tr("progress_quick_log"))

    # Quick log of today's weight
    quick_weight = st.number_input(
        tr("progress_weight_today"),
        min_value=30.0,
        max_value=300.0,
        value=float(st.session_state["weight"]),
    )
    if st.button(tr("progress_save")):
        if not username:
            st.warning(tr("saved_err_no_user"))
        else:
            age = int(st.session_state["age"])
            sex = st.session_state["sex"]
            height = int(st.session_state["height"])
            activity = st.session_state["activity"]
            goal = st.session_state["goal"]
            targets = calculate_targets(age, sex, int(height), float(quick_weight), activity, goal)
            ok = save_history_for_today(
                username,
                age,
                sex,
                height,
                quick_weight,
                activity,
                goal,
                targets,
                st.session_state.get("plan") or "",
            )
            if ok:
                st.success(tr("progress_saved"))

    st.write("---")

    if username and HISTORY_FILE.exists():
        df_hist = pd.read_csv(HISTORY_FILE)
        user_hist = df_hist[df_hist["username"] == username].copy()

        if not user_hist.empty:
            if "timestamp" in user_hist.columns:
                user_hist["timestamp"] = pd.to_datetime(user_hist["timestamp"])
                user_hist = user_hist.sort_values("timestamp")

                if lang == "el":
                    y_label = "Βάρος (kg)"
                    x_label = "Ημερομηνία"
                else:
                    y_label = "Weight (kg)"
                    x_label = "Date"

                plot_df = user_hist[["timestamp", "weight_kg"]].copy()

                st.subheader(f"{tr('history_title')} ({username})")

                chart = (
                    alt.Chart(plot_df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "timestamp:T",
                            axis=alt.Axis(title=x_label, format="%d/%m"),
                        ),
                        y=alt.Y(
                            "weight_kg:Q",
                            axis=alt.Axis(title=y_label),
                        ),
                        tooltip=[
                            alt.Tooltip(
                                "timestamp:T",
                                title=x_label,
                                format="%d/%m/%Y %H:%M",
                            ),
                            alt.Tooltip("weight_kg:Q", title=y_label),
                        ],
                    )
                    .properties(height=280)
                )

                st.altair_chart(chart, use_container_width=True)

            # επιλογή για να δει παλιό πρόγραμμα
            if "plan_markdown" in user_hist.columns:
                user_hist = user_hist.sort_values("timestamp", ascending=False)
                options = [
                    f"{row['timestamp']}  |  {row.get('goal', '')}"
                    for _, row in user_hist.iterrows()
                ]
                st.markdown("")
                selected = st.selectbox(
                    tr("history_plan_label"),
                    options,
                    index=0,
                )
                sel_ts = selected.split("  |  ")[0]
                sel_row = user_hist[user_hist["timestamp"].astype(str) == sel_ts].iloc[0]
                old_plan_md = sel_row.get("plan_markdown")

                if isinstance(old_plan_md, str) and old_plan_md.strip():
                    old_df = markdown_table_to_df(old_plan_md)
                    if old_df is not None:
                        st.markdown("##### " + (tr("plan_title") + " (history)"))
                        vis_old = old_df.copy()

                        def multiline_old(val):
                            if isinstance(val, str):
                                return val.replace(", ", "<br>")
                            return val

                        vis_old = vis_old.applymap(multiline_old)
                        html_old = vis_old.to_html(index=False, escape=False)
                        st.markdown(
                            f"<div style='overflow-x:auto;'>{html_old}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info(tr("history_no_plan"))
                else:
                    st.info(tr("history_no_plan"))
        else:
            if lang == "el":
                st.info("Δεν υπάρχει ακόμη ιστορικό για αυτόν τον χρήστη.")
            else:
                st.info("No history yet for this user.")
    else:
        if lang == "el":
            st.info("Δεν υπάρχει ακόμη ιστορικό ή δεν έχεις ορίσει όνομα χρήστη.")
        else:
            st.info("No history yet or no user name defined.")

# ABOUT PAGE
elif page == "about":
    st.subheader(tr("about_title"))
    st.markdown(tr("about_text"))

# ----------------- FOOTER -----------------
st.write("---")
st.markdown(
    f"<p style='text-align:center; font-size:0.85rem; opacity:0.7;'>{tr('footer')}</p>",
    unsafe_allow_html=True,
)
