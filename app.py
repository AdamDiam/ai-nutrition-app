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
import shutil
from config import TEXT, DAY_LABELS, tr_raw, DATA_DIR, HISTORY_FILE, PROFILE_FILE, USERS_FILE
from storage import save_history_for_today, load_profile, save_profile, load_user_history
from ai_layer import (
    client,
    calculate_targets,
    markdown_table_to_df,
    generate_weekly_plan,
    answer_plan_question,
    adjust_weekly_plan,
)
from auth_utils import (
    load_users,
    save_users,
    hash_password,
    check_password,
    update_last_login,
)

def load_local_css(path: str):
    try:
        with open(path) as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {path}")

if "signup_step" not in st.session_state:
    st.session_state.signup_step = 1

def get_security_question() -> str:
    return tr("security_question")

def load_base64(path: str) -> str:
    """Γυρνάει base64 για εικόνες. Αν λείπει το αρχείο, δεν ρίχνει error."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        # Μπορείς να βάλεις εδώ ένα default χρώμα / κενό background
        return ""


LOGO_BASE64 = load_base64("assets/logo.png")
BG_BASE64   = load_base64("assets/bg_pattern.png")

st.set_page_config(
    page_title="02Hero Nutrition Helper",
    page_icon="🍽️",
    layout="wide",
)

load_local_css("assets/style.css")

st.markdown(
    f"""
    <style>
    /* Πιο σκοτεινό overlay για καλύτερη αντίθεση */
    body {{
        background-image:
            linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
            url('data:image/png;base64,{BG_BASE64}');
        background-size: 120px 120px;
        background-repeat: repeat;
        background-attachment: fixed;
    }}

    .stApp {{
        background-color: transparent;
    }}

    /* Οι ετικέτες να γράφουν πάνω στο pattern */
    label,
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stPasswordInput label,
    .stCheckbox label {{
        color: #ffffff !important;
        text-shadow: 0 0 6px rgba(0, 0, 0, 0.95);
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- LANGUAGE TEXTS -----------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "el"

def tr(key: str) -> str:
    lang = st.session_state.get("lang", "el")
    return tr_raw(lang, key)

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
    user_folder = f"user_data/{username}"
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)

    # 3) Clear session and go to login
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = "user"
    st.session_state["new_user"] = False
    st.session_state["page"] = "login"

    st.success(tr("delete_success"))
    st.rerun()

@st.dialog(tr("delete_dialog_title"))
def delete_dialog(username: str):
    st.write(tr("delete_dialog_body"))

    confirm_text = st.text_input(
        tr("delete_dialog_confirm_label"),
        placeholder=username,
        key="dialog_delete_confirm_input",
    )

    col1, col2 = st.columns(2)
    with col1:
        confirm = st.button(tr("delete_dialog_yes"), key="dialog_do_delete")
    with col2:
        cancel = st.button(tr("delete_dialog_cancel"), key="dialog_cancel_delete")

    if confirm:
        if confirm_text.strip().lower() == username.lower():
            delete_account(username)
        else:
            st.error(tr("delete_dialog_error_mismatch"))

    if cancel:
        # Κλείνει το dialog χωρίς να κάνει τίποτα
        st.rerun()

@st.dialog(tr("onboard_title"))
def onboarding_dialog():
    st.write(tr("onboard_body"))

    if st.button(tr("onboard_button"), use_container_width=True):
        st.session_state["onboarding_seen"] = True
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

    # current step in signup wizard
    if "signup_step" not in st.session_state:
        st.session_state["signup_step"] = 1

    # κεντράρισμα signup
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.title(tr("signup_title"))

        step = st.session_state["signup_step"]

        # -------- PROGRESS BAR (κόκκινο/μπλε) --------
        step1_active = "active" if step >= 1 else ""
        step2_active = "active" if step >= 2 else ""
        line_filled = "filled" if step >= 2 else ""

        st.markdown(
            f"""
            <div class="signup-progress">
                <div class="step {step1_active}">
                    <div class="circle">1</div>
                    <div class="label">{tr('signup_step1_label')}</div>
                </div>
                <div class="line {line_filled}"></div>
                <div class="step {step2_active}">
                    <div class="circle">2</div>
                    <div class="label">{tr('signup_step2_label')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Ό,τι ακολουθεί (forms των βημάτων) μπαίνει στο fade container
        st.markdown("<div class='fade-container'>", unsafe_allow_html=True)

        # ===================== STEP 1: CREDENTIALS =====================
        if step == 1:
            with st.form("signup_step1"):
                username = st.text_input(tr("signup_username")).strip()
                fullname = st.text_input(tr("signup_fullname")).strip()
                password = st.text_input(tr("signup_password"), type="password")
                password2 = st.text_input(tr("signup_password_confirm"), type="password")
                security_answer = st.text_input(
                    f"{tr('signup_security_answer')} ({get_security_question()})"
                ).strip()

                next_btn = st.form_submit_button(
                    "➡️ Επόμενο βήμα" if st.session_state["lang"] == "el" else "➡️ Next step"
                )

            if next_btn:
                # Validation
                if not username:
                    st.error(tr("signup_err_username_missing"))
                    st.stop()
                if username in users:
                    st.error(tr("signup_err_username_exists"))
                    st.stop()
                if not password:
                    st.error(tr("signup_err_password_missing"))
                    st.stop()
                if password != password2:
                    st.error(tr("signup_err_password_mismatch"))
                    st.stop()
                if not security_answer:
                    st.error(tr("signup_err_security_missing"))
                    st.stop()

                # Store temporary credentials στο session
                st.session_state["temp_signup"] = {
                    "username": username,
                    "fullname": fullname,
                    "password": password,
                    "security_answer": security_answer,
                }

                st.session_state["signup_step"] = 2
                st.rerun()

        # ===================== STEP 2: PROFILE INFO =====================
        elif step == 2:
            # safety: αν πας κατευθείαν στο step 2 χωρίς temp data, γύρνα πίσω
            if "temp_signup" not in st.session_state:
                st.session_state["signup_step"] = 1
                st.rerun()

            with st.form("signup_step2"):
                age = st.number_input(tr("age"), min_value=10, max_value=90, value=25)

                sex_choice = st.selectbox(
                    tr("sex"),
                    [tr("male"), tr("female")],
                    index=0,
                )
                sex = "male" if sex_choice == tr("male") else "female"

                height = st.number_input(tr("height"), min_value=120, max_value=220, value=175)
                weight = st.number_input(tr("weight"), min_value=40.0, max_value=200.0, value=70.0)

                activity_opts = tr("activity_opts")
                goal_opts = tr("goal_opts")

                activity = st.selectbox(tr("activity"), activity_opts)
                goal = st.selectbox(tr("goal"), goal_opts)

                allergies = st.text_area(tr("allergies"), placeholder=tr("allergies_ph"))
                preferred_foods = st.text_area(tr("prefs"), placeholder=tr("prefs_ph"))

                col_back, col_finish = st.columns(2)
                with col_back:
                    back_btn = st.form_submit_button(
                        "⬅️ Πίσω" if st.session_state["lang"] == "el" else "⬅️ Back"
                    )
                with col_finish:
                    finish_btn = st.form_submit_button(tr("signup_button"))

            if back_btn:
                st.session_state["signup_step"] = 1
                st.rerun()

            if finish_btn:
                data = st.session_state["temp_signup"]

                # Save user credentials στο users.json
                users[data["username"]] = {
                    "password": hash_password(data["password"]),
                    "fullname": data["fullname"],
                    "role": "user",
                    "security_answer": data["security_answer"].lower(),
                }
                save_users(users)

                # Store profile data σε session
                st.session_state.update({
                    "username": data["username"],
                    "logged_in": True,
                    "role": "user",
                    "new_user": True,
                    "age": int(age),
                    "sex": sex,
                    "height": int(height),
                    "weight": float(weight),
                    "activity": activity,
                    "goal": goal,
                    "allergies": allergies,
                    "preferred_foods": preferred_foods,
                })

                # Save σε profiles.csv
                save_profile(data["username"],st.session_state)

                # reset wizard
                st.session_state["signup_step"] = 1
                st.session_state.pop("temp_signup", None)

                # πάμε κατευθείαν στο νέο πλάνο
                st.session_state["page"] = "new_plan"
                st.success(tr("signup_success"))
                st.rerun()

        # κλείσιμο fade container
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
    "age": 25,
    "sex": "male",
    "height": 175,
    "weight": 70.0,
    "activity": "Medium",
    "goal": "Maintain",
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
if "role" not in st.session_state:
    st.session_state["role"] = "user"
if "new_user" not in st.session_state:
    st.session_state["new_user"] = False
if "onboarding_seen" not in st.session_state:
    st.session_state["onboarding_seen"] = False


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
        st.markdown(
            f"<span style='font-size:0.85rem; opacity:0.8;'>{tr('sidebar_sub')}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        is_new = st.session_state.get("new_user", False)

        if is_new:
            # 👉 ΝΕΟΣ χρήστης: μόνο Νέο Πλάνο, Προφίλ, Σχετικά
            if st.button(tr("menu_new_plan"), use_container_width=True, type="secondary"):
                st.session_state["page"] = "new_plan"
                st.rerun()

            st.markdown("---")

            if st.button(tr("menu_profile"), use_container_width=True):
                st.session_state["page"] = "profile"
                st.rerun()

            if st.button(tr("menu_about"), use_container_width=True):
                st.session_state["page"] = "about"
                st.rerun()

        else:
            # 👉 ΚΑΝΟΝΙΚΟΣ χρήστης: πλήρες μενού
            if st.button(tr("menu_home"), use_container_width=True, type="secondary"):
                st.session_state["page"] = "home"
                st.rerun()

            if st.button(tr("menu_new_plan"), use_container_width=True, type="secondary"):
                st.session_state["page"] = "new_plan"
                st.rerun()

            st.markdown("---")

            if st.button(tr("menu_progress"), use_container_width=True):
                st.session_state["page"] = "progress"
                st.rerun()

            if st.button(tr("menu_profile"), use_container_width=True):
                st.session_state["page"] = "profile"
                st.rerun()

            if st.button(tr("menu_about"), use_container_width=True):
                st.session_state["page"] = "about"
                st.rerun()

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
            st.session_state["new_user"] = False
            st.session_state["page"] = "login"
            st.rerun()

# ----------------- TITLE -----------------
st.markdown(
    f"<h1 style='text-align:center; margin-top:1.0rem;'>{tr('title')}</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center; opacity:0.85;'>{tr('subtitle')}</p>",
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

    # 3) Otherwise show LOGIN
    st.session_state["page"] = "login"

    outer_left, outer_center, outer_right = st.columns([1, 2, 1])
    with outer_center:
        # --- CENTERED LOGO ONLY ON AUTH PAGES ---
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

        st.subheader(tr("login_title"))

        users = load_users()

        with st.form("login_form_main"):
            username_input = st.text_input(tr("login_username"))
            password_input = st.text_input(tr("login_password"), type="password")

            submit_login = st.form_submit_button(
                tr("login_button"),
                use_container_width=True
            )

            st.write("")  # μικρό κενό

            signup_clicked = st.form_submit_button(
                tr("login_new_user_cta"),
                use_container_width=True,
            )

            forgot_clicked = st.form_submit_button(
                tr("login_forgot_password"),
                use_container_width=True,
            )

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
                        load_profile(actual_key,st.session_state)

                        # 👉 Όλοι οι “normal” χρήστες πάνε στο new_plan
                        if st.session_state["role"] == "admin":
                            st.session_state["page"] = "admin"
                        else:
                            st.session_state["page"] = "new_plan"

                        st.rerun()

# ----------------- ROUTING ΑΝΑΛΟΓΑ ΜΕ ΤΗ ΣΕΛΙΔΑ -----------------

page = st.session_state.get("page", "login")

# Αν είμαι logged_in αλλά έχω σελίδα login / signup / forgot, στείλε με στο new_plan
if st.session_state.get("logged_in", False) and page in {"login", "signup", "forgot_password"}:
    page = "new_plan"
    st.session_state["page"] = "new_plan"

# Αν ΔΕΝ είμαι logged_in, βεβαιώσου ότι είμαι στη login
if not st.session_state.get("logged_in", False) and page != "login":
    page = "login"
    st.session_state["page"] = "login"

# Αν είναι νέος χρήστης, έχει συνδεθεί, είναι στο new_plan και δεν έχει δει ακόμα το onboarding → δείξε popup
if (
    st.session_state.get("logged_in", False)
    and st.session_state.get("new_user", False)
    and not st.session_state.get("onboarding_seen", False)
    and page == "new_plan"
):
    onboarding_dialog()

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
    user_hist = load_user_history(username)

    if user_hist is not None:
        last_row = user_hist.iloc[-1]
        start_row = user_hist.iloc[0]
        diff = round(last_row["weight_kg"] - start_row["weight_kg"], 1)

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
                    {tr("home_summary_title")}
                </div>
                <div style="font-size:0.9rem; line-height:1.5;">
                    • {tr("home_summary_last")}: <b>{last_row['weight_kg']} kg</b><br>
                    • {tr("home_summary_first")}: <b>{start_row['weight_kg']} kg</b><br>
                    • {tr("home_summary_change")}: <b>{diff} kg</b>
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
            save_profile(st.session_state["username"], st.session_state)
            st.success(tr("profile_saved"))

    st.write("---")

    # ---------- DELETE ACCOUNT SECTION ----------
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader(tr("profile_delete_title"))
        st.caption(tr("profile_delete_caption"))
    with col_btn:
        delete_clicked = st.button(
            tr("profile_delete_button"),
            key="open_delete",
            use_container_width=True,
            type="primary",
        )

    if delete_clicked:
        delete_dialog(st.session_state.get("username", ""))

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
                try:
                    lang = st.session_state["lang"]

                    age = int(st.session_state["age"])
                    sex_raw = st.session_state["sex"]  # "male" ή "female"
                    height = int(st.session_state["height"])
                    weight = float(st.session_state["weight"])
                    activity = st.session_state["activity"]
                    goal = st.session_state["goal"]
                    allergies = st.session_state["allergies"]
                    prefs = st.session_state["preferred_foods"]

                    with st.spinner(
                            "Generating your plan with AI..."
                            if lang == "en"
                            else "Φτιάχνω το πρόγραμμα με AI..."
                    ):
                        plan_md = generate_weekly_plan(
                            lang=lang,
                            age=age,
                            sex=sex_raw,
                            height=height,
                            weight=weight,
                            activity=activity,
                            goal=goal,
                            allergies=allergies,
                            preferred_foods=prefs,
                        )

                    st.session_state["plan"] = plan_md
                    st.session_state["show_form"] = False
                    st.session_state["qa_history"] = []
                    st.session_state["qa_input"] = ""
                    st.rerun()

                except Exception:
                    msg = (
                        "Κάτι πήγε στραβά με το AI. Δοκίμασε ξανά σε λίγο."
                        if st.session_state["lang"] == "el"
                        else "Something went wrong with the AI. Please try again later."
                    )
                    st.error(msg)



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
            # ---- 1) Φτιάχνουμε dict: day -> [meals] ----
            meal_col = df_plan.columns[0]
            day_cols = df_plan.columns[1:]  # Δευτέρα, Τρίτη, ...

            day_dict = {day: [] for day in day_cols}

            for _, row in df_plan.iterrows():
                meal_name = str(row[meal_col]).strip()
                if not meal_name:
                    continue

                for day in day_cols:
                    content = str(row[day]).strip()
                    if content and content != "-":
                        day_dict[day].append(
                            {"meal": meal_name, "content": content}
                        )

            # ---- 2) ORDERED DAYS & SHORT LABELS ----
            if lang == "el":
                ordered_days = [
                    "Δευτέρα", "Τρίτη", "Τετάρτη",
                    "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"
                ]
                day_short = ["Δ", "Τ", "Τ", "Π", "Π", "Σ", "Κ"]
            else:
                ordered_days = [
                    "Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"
                ]
                day_short = ["M", "T", "W", "T", "F", "S", "S"]

            # ---- 3) Επιλογή τρόπου προβολής (απλό radio) ----
            if lang == "el":
                opt_day = "Μια μέρα κάθε φορά"
                opt_week = "Όλη η εβδομάδα"
            else:
                opt_day = "One day at a time"
                opt_week = "Full week"

            # radio οριζόντιο, χωρίς label
            choice = st.radio(
                label="",
                options=[opt_day, opt_week],
                horizontal=True,
                label_visibility="collapsed",
            )

            # Εσωτερική λογική: 'day' ή 'week'
            view_mode = "day" if choice == opt_day else "week"

            # ===================== MODE 1: ΜΙΑ ΜΕΡΑ ΚΑΘΕ ΦΟΡΑ =====================
            if view_mode == "day":
                # ---- 4) SETUP CAROUSEL INDEX ----
                if "day_index" not in st.session_state:
                    st.session_state["day_index"] = 0

                st.session_state["day_index"] %= len(ordered_days)
                current_index = st.session_state["day_index"]
                current_day = ordered_days[current_index]
                meals = day_dict.get(current_day, [])

                # ---- 5) Navigation arrows + title ----
                nav_prev, nav_title, nav_next = st.columns([1, 4, 1])

                with nav_prev:
                    st.markdown("<div class='day-nav-arrow'>", unsafe_allow_html=True)
                    if st.button("❮", key="day_prev"):
                        st.session_state["day_index"] = (current_index - 1) % len(ordered_days)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                with nav_title:
                    st.markdown(
                        f"<h3 style='text-align:center; margin-bottom:0;'>{current_day}</h3>",
                        unsafe_allow_html=True,
                    )

                with nav_next:
                    st.markdown("<div class='day-nav-arrow'>", unsafe_allow_html=True)
                    if st.button("❯", key="day_next"):
                        st.session_state["day_index"] = (current_index + 1) % len(ordered_days)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # ---- 6) Day pills row (MTWTFSS / ΔΤΤΠΠΣΚ) ----
                pill_html = "<div class='day-pill-row'>"
                for idx, label in enumerate(day_short):
                    active = " active" if idx == current_index else ""
                    pill_html += f"<span class='day-pill{active}'>{label}</span>"
                pill_html += "</div>"
                st.markdown(pill_html, unsafe_allow_html=True)

                # ---- 7) SHOW SINGLE DAY CARD ----
                card_html = (
                    f"<div class='day-card' id='day-card-{current_index}'>"
                    "<div class='day-card-inner'>"
                )
                card_html += "<div class='day-card-subtitle'>WEEKLY PLAN</div>"
                card_html += (
                    f"<h3 class='day-card-title' "
                    f"style=\"font-family:'Anton', system-ui, sans-serif;\">"
                    f"{current_day}</h3>"
                )

                for m in meals:
                    card_html += (
                        "<div class='meal-card'>"
                        f"<div class='meal-title'>{m['meal']}</div>"
                        f"<div class='meal-content'>{m['content']}</div>"
                        "</div>"
                    )

                card_html += "</div></div>"
                st.markdown(card_html, unsafe_allow_html=True)

                # ===================== MODE 2: ΟΛΗ Η ΕΒΔΟΜΑΔΑ =====================
            else:
                st.write("")  # μικρό κενό

                # GRID layout για όλες τις μέρες
                st.markdown("<div class='week-grid'>", unsafe_allow_html=True)

                for day in ordered_days:
                    meals = day_dict.get(day, [])

                    card_html = (
                        "<div class='week-card'>"
                        "<div class='day-card day-card-compact'>"
                        "<div class='day-card-inner'>"
                    )
                    card_html += "<div class='day-card-subtitle'>WEEKLY PLAN</div>"
                    card_html += f"<h3 class='day-card-title'>{day}</h3>"

                    for m in meals:
                        card_html += (
                            "<div class='meal-card'>"
                            f"<div class='meal-title'>{m['meal']}</div>"
                            f"<div class='meal-content'>{m['content']}</div>"
                            "</div>"
                        )

                    card_html += "</div></div></div>"

                    st.markdown(card_html, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Δεν μπόρεσα να μετατρέψω το πρόγραμμα σε πίνακα.")

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
                    # μετά την πρώτη αποθήκευση δεν θεωρείται πια "νέος"
                    st.session_state["new_user"] = False

        # ---------------- Q&A SECTION (χωρίς έξτρα ---) ----------------
        st.markdown("")
        st.subheader(tr("qa_title"))

        if st.session_state["qa_history"]:
            for msg in st.session_state["qa_history"][-6:]:
                who = (
                    "Εσύ"
                    if (msg["role"] == "user" and lang == "el")
                    else ("You" if msg["role"] == "user" else "AI")
                )
                st.markdown(f"**{who}:** {msg['content']}")

        # Απλό input + button (χωρίς form)
        st.session_state["qa_input"] = st.text_input(
            tr("qa_your_q"),
            value=st.session_state["qa_input"],
        )
        send_q = st.button(tr("qa_button"))

        # λογική Q&A ΕΞΩ από τη φόρμα
        if send_q and st.session_state["qa_input"].strip():
            if not client:
                st.error(
                    "Δεν υπάρχει διαθέσιμο AI αυτή τη στιγμή."
                    if lang == "el"
                    else "AI is not available right now."
                )
            else:
                question = st.session_state["qa_input"].strip()
                st.session_state["qa_history"].append(
                    {"role": "user", "content": question}
                )

                plan_text = st.session_state["plan"]

                try:
                    with st.spinner(
                            "Το AI σκέφτεται..." if lang == "el" else "AI is thinking..."
                    ):
                        answer = answer_plan_question(lang, plan_text, question)

                    st.session_state["qa_history"].append(
                        {"role": "assistant", "content": answer}
                    )
                    st.session_state["qa_input"] = ""
                    st.rerun()

                except Exception:
                    err_msg = (
                        "Κάτι πήγε στραβά με την απάντηση του AI. Προσπάθησε ξανά αργότερα."
                        if lang == "el"
                        else "Something went wrong while getting the AI answer. Please try again later."
                    )
                    st.error(err_msg)

        # ---------------- CHANGES SECTION (χωρίς extra πλαίσιο) ----------------
        st.subheader(tr("changes_title"))
        st.write(tr("changes_desc"))

        feedback = st.text_area(
            "Τι θα ήθελες να αλλάξει στο πρόγραμμα;"
            if lang == "el"
            else "What would you like to change in the plan?",
            placeholder=tr("changes_ph"),
        )
        apply_changes = st.button(tr("changes_button"))

        if apply_changes:
            if not feedback.strip():
                st.warning(tr("need_feedback"))
            elif not client:
                st.error(
                    "Το AI δεν είναι διαθέσιμο αυτή τη στιγμή."
                    if lang == "el"
                    else "AI is not available right now."
                )
            else:
                try:
                    with st.spinner(
                            "Προσαρμόζω το πρόγραμμα..." if lang == "el" else "Adjusting the plan..."
                    ):
                        new_plan_md = adjust_weekly_plan(
                            lang=lang,
                            current_plan_md=st.session_state["plan"],
                            feedback=feedback,
                        )

                    st.session_state["plan"] = new_plan_md
                    st.rerun()

                except Exception:
                    err_msg = (
                        "Κάτι πήγε στραβά με την προσαρμογή του πλάνου. Προσπάθησε ξανά."
                        if lang == "el"
                        else "Something went wrong while adjusting the plan. Please try again."
                    )
                    st.error(err_msg)

    # st.write("---")


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

    user_hist = load_user_history(username)

    if user_hist is not None:
        if "timestamp" in user_hist.columns:
            plot_df = user_hist[["timestamp", "weight_kg"]].copy()

            if lang == "el":
                y_label = "Βάρος (kg)"
                x_label = "Ημερομηνία"
            else:
                y_label = "Weight (kg)"
                x_label = "Date"

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
            # Κρατάμε μόνο εγγραφές που έχουν πραγματικό plan
            plans_df = user_hist.copy()
            plans_df["plan_markdown"] = plans_df["plan_markdown"].fillna("")
            plans_df = plans_df[plans_df["plan_markdown"].str.strip() != ""]

            if plans_df.empty:
                st.info(tr("history_no_plan"))
            else:
                plans_df = plans_df.sort_values("timestamp", ascending=False)

                options = [
                    f"{row['timestamp']}  |  {row.get('goal', '')}"
                    for _, row in plans_df.iterrows()
                ]

                st.markdown("")
                selected = st.selectbox(
                    tr("history_plan_label"),
                    options,
                    index=0,
                )

                sel_ts = selected.split("  |  ")[0]
                sel_row = plans_df[plans_df["timestamp"].astype(str) == sel_ts].iloc[0]
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
                        html_old = vis_old.to_html(
                            index=False,
                            escape=False,
                            classes="diet-table",
                            border=0,
                        )
                        st.markdown(
                            f"<div style='overflow-x:auto;'>{html_old}</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info(tr("history_no_plan"))
                else:
                    st.info(tr("history_no_plan"))
        else:
            st.info(tr("history_no_plan"))

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