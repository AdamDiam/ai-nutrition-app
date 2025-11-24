import os
import io
from pathlib import Path
from datetime import datetime, date

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# ----------------- CONFIG & OPENAI -----------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

st.set_page_config(
    page_title="02Hero Nutrition Helper",
    page_icon="🍽️",
    layout="wide",
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
    },
    "en": {
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
        st.markdown(f"### {tr('sidebar_title')}")
        st.markdown(tr("sidebar_sub"))
        st.markdown("---")

        if st.button(tr("menu_home"), use_container_width=True):
            st.session_state["page"] = "home"
        if st.button(tr("menu_new_plan"), use_container_width=True):
            st.session_state["page"] = "new_plan"
        if st.button(tr("menu_progress"), use_container_width=True):
            st.session_state["page"] = "progress"
        if st.button(tr("menu_profile"), use_container_width=True):
            st.session_state["page"] = "profile"
        if st.button(tr("menu_about"), use_container_width=True):
            st.session_state["page"] = "about"

# ----------------- TITLE -----------------
st.markdown(
    f"<h1 style='text-align:center; margin-top:1.0rem;'>{tr('title')}</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center; opacity:0.85;'>{tr('subtitle')}</p>",
    unsafe_allow_html=True,
)
st.write("")

# ----------------- LOGIN PAGE -----------------
if not st.session_state["logged_in"] or st.session_state["page"] == "login":
    st.session_state["page"] = "login"
    st.subheader(tr("login_title"))
    username_input = st.text_input(tr("username"), value=st.session_state["username"])
    if st.button(tr("login_button")):
        if not username_input.strip():
            st.warning(tr("saved_err_no_user"))
        else:
            st.session_state["username"] = username_input.strip()
            st.session_state["logged_in"] = True
            # load profile αν υπάρχει
            load_profile(st.session_state["username"])
            st.session_state["page"] = "home"
            st.rerun()
    st.write("---")
    st.markdown(
        f"<p style='text-align:center; font-size:0.85rem; opacity:0.7;'>{tr('footer')}</p>",
        unsafe_allow_html=True,
    )
    st.stop()

# ----------------- ROUTING ΑΝΑΛΟΓΑ ΜΕ ΤΗ ΣΕΛΙΔΑ -----------------

page = st.session_state["page"]

# HOME / DASHBOARD
if page == "home":
    lang = st.session_state["lang"]
    username = (st.session_state.get("username") or "").strip()

    st.subheader(f"{tr('home_welcome')} {username or ''}".strip())
    st.write("")
    st.write(tr("intro"))

    # Κάρτες επιλογών
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📅 " + tr("home_new_plan"), use_container_width=True):
            st.session_state["page"] = "new_plan"
            st.rerun()
        if st.button("👤 " + tr("home_profile"), use_container_width=True):
            st.session_state["page"] = "profile"
            st.rerun()
    with c2:
        if st.button("📈 " + tr("home_progress"), use_container_width=True):
            st.session_state["page"] = "progress"
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
            if lang == "el":
                st.markdown("### Μικρή σύνοψη")
                st.markdown(
                    f"- Τελευταία καταγραφή βάρους: **{last_row['weight_kg']} kg**\n"
                    f"- Πρώτη καταγραφή: **{start_row['weight_kg']} kg**\n"
                    f"- Αλλαγή: **{round(last_row['weight_kg'] - start_row['weight_kg'], 1)} kg**"
                )
            else:
                st.markdown("### Quick summary")
                st.markdown(
                    f"- Last recorded weight: **{last_row['weight_kg']} kg**\n"
                    f"- First recorded weight: **{start_row['weight_kg']} kg**\n"
                    f"- Change: **{round(last_row['weight_kg'] - start_row['weight_kg'], 1)} kg**"
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
