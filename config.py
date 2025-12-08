# config.py
from pathlib import Path

# ----------------- PATHS / FILES -----------------
DATA_DIR = Path("user_data")
DATA_DIR.mkdir(exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.csv"
PROFILE_FILE = DATA_DIR / "profiles.csv"
USERS_FILE = "users.json"

# ----------------- TRANSLATIONS -----------------
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
        "home_welcome": "Καλώς ήρθες",
        "home_new_plan": "Δημιούργησε νέο πρόγραμμα διατροφής",
        "home_progress": "Κατέγραψε την πρόοδό σου",
        "home_view_plans": "Δες παλιότερα προγράμματά σου",
        "home_profile": "Ενημέρωσε το προφίλ σου",
        "profile_title": "Προφίλ χρήστη",
        "profile_save": "💾 Αποθήκευση προφίλ",
        "profile_saved": "✅ Το προφίλ σου αποθηκεύτηκε.",
        "profile_delete_title": "⚠️ Διαγραφή λογαριασμού",
        "profile_delete_caption": "Αυτή η ενέργεια είναι οριστική και δεν μπορεί να αναιρεθεί.",
        "profile_delete_button": "🗑️ Διαγραφή",

        "delete_dialog_title": "⚠️ Διαγραφή λογαριασμού",
        "delete_dialog_body": (
            "Αυτή η ενέργεια **δεν μπορεί να αναιρεθεί**. "
            "Όλα τα δεδομένα σου θα χαθούν οριστικά."
        ),
        "delete_dialog_confirm_label": "Για επιβεβαίωση, γράψε το όνομα χρήστη σου:",
        "delete_dialog_yes": "Ναι, διαγραφή",
        "delete_dialog_cancel": "Άκυρο",
        "delete_dialog_error_mismatch": "Το όνομα χρήστη δεν ταιριάζει. Η διαγραφή ακυρώθηκε.",
        "delete_success": "Ο λογαριασμός σου διαγράφηκε με επιτυχία.",
        "progress_quick_log": "Γρήγορη καταγραφή σημερινού βάρους",
        "progress_weight_today": "Σημερινό βάρος (kg)",
        "progress_save": "💾 Αποθήκευση σημερινού βάρους",
        "progress_saved": "✅ Το βάρος σου για σήμερα αποθηκεύτηκε.",
        "security_question": "Ποιο είναι το αγαπημένο σου χρώμα;",
        "security_answer_label": "Απάντηση στην ερώτηση",
        "signup_step1_label": "1. Στοιχεία σύνδεσης",
        "signup_step2_label": "2. Στοιχεία προφίλ",
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

        # Logout
        "logout_button": "🚪 Αποσύνδεση",
        "onboard_title": "👋 Καλώς ήρθες στο 02Hero",
        "onboard_body": """
        Καλώς ήρθες στο 02Hero Nutrition Helper! 🧠💪  

        ### Πρώτη φορά – τι να κάνεις:
        1. Συμπλήρωσε τα βασικά στοιχεία σου (ηλικία, βάρος, στόχο κτλ.).
        2. Πάτα **"Υπολογισμός & Πρόγραμμα AI"** για να φτιάξει το AI το εβδομαδιαίο πλάνο σου.
        3. Κατέβασε αν θέλεις:
           - το πλάνο σε **Excel**
           - τη **λίστα αγορών** για το σούπερ μάρκετ.

        ### Τι θα ξεκλειδώσεις μετά:
        - Μετά την πρώτη αποθήκευση θα εμφανιστεί η σελίδα **"Καταγραφή Προόδου"**  
          όπου βλέπεις αλλαγή βάρους & παλαιότερα πλάνα.
        - Στο **"Προφίλ"** μπορείς να αλλάζεις ανά πάσα στιγμή τα στοιχεία σου.

        Καλή αρχή! 🚀
        """,
        "onboard_button": "Ξεκινάμε 🚀",
        "home_summary_title": "Μικρή σύνοψη προόδου",
        "home_summary_last": "Τελευταία καταγραφή βάρους",
        "home_summary_first": "Πρώτη καταγραφή",
        "home_summary_change": "Αλλαγή",

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
        "login_button": "Continue",
        "home_welcome": "Welcome",
        "home_new_plan": "Create a new nutrition plan",
        "home_progress": "Track your progress",
        "home_view_plans": "View your past plans",
        "home_profile": "Update your profile",
        "profile_title": "User profile",
        "profile_save": "💾 Save profile",
        "profile_saved": "✅ Your profile has been saved.",
        "profile_delete_title": "⚠️ Delete account",
        "profile_delete_caption": "This action is permanent and cannot be undone.",
        "profile_delete_button": "🗑️ Delete",

        "delete_dialog_title": "⚠️ Delete account",
        "delete_dialog_body": (
            "This action **cannot be undone**. "
            "All your data will be permanently deleted."
        ),
        "delete_dialog_confirm_label": "To confirm, type your username:",
        "delete_dialog_yes": "Yes, delete",
        "delete_dialog_cancel": "Cancel",
        "delete_dialog_error_mismatch": "Username does not match. Deletion cancelled.",
        "delete_success": "Your account has been successfully deleted.",
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
        "onboard_title": "👋 Welcome to 02Hero",
        "onboard_body": """
        Welcome to the 02Hero Nutrition Helper! 🧠💪  

        ### First time using the app? Here’s what to do:
        1. Fill in your basic details (age, weight, goal, etc.).
        2. Press **“Calculate & AI Meal Plan”** to generate your weekly plan.
        3. You can download:
           - the full plan in **Excel**
           - the **shopping list** for the supermarket.

        ### What unlocks after the first save:
        - After saving your first plan, the **Progress Tracking** page becomes available.
        - From your **Profile**, you can update your data anytime.

        Ready to start? 🚀
        """,
        "onboard_button": "Let's start 🚀",
        "signup_step1_label": "1. Login details",
        "signup_step2_label": "2. Profile details",
        "home_summary_title": "Quick progress summary",
        "home_summary_last": "Last recorded weight",
        "home_summary_first": "First recorded weight",
        "home_summary_change": "Change",
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


# ΜΟΛΙΣ τα επικολλήσεις, πρόσθεσε αυτό το helper:
def tr_raw(lang: str, key: str) -> str:
    """
    Χωρίς session_state – απλό helper:
    δώσε μου γλώσσα ('el' ή 'en') και key, γύρνα το string.
    """
    return TEXT.get(lang, TEXT["en"]).get(key, key)
