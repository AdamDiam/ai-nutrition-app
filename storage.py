# storage.py
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from config import DATA_DIR, HISTORY_FILE, PROFILE_FILE


def save_history_for_today(
    username: str,
    age: int,
    sex: str,
    height: int,
    weight: float,
    activity: str,
    goal: str,
    targets: dict,
    plan_markdown: str,
) -> bool:
    """
    Αποθηκεύει στο history.csv ΜΙΑ εγγραφή ανά μέρα & χρήστη,
    μαζί με το markdown του πλάνου (στήλη plan_markdown).
    """
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE)
    else:
        df = pd.DataFrame()

    today = pd.to_datetime("today").normalize()

    # Αν υπάρχει ήδη εγγραφή για σήμερα & αυτόν τον χρήστη, σβήστην
    if not df.empty and {"username", "date"} <= set(df.columns):
        df["date"] = pd.to_datetime(df["date"]).dt.normalize()
        df = df[~((df["username"] == username) & (df["date"] == today))]

    new_row = {
        "username": username,
        "date": today,
        "timestamp": pd.Timestamp.now(),
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
        "plan_markdown": plan_markdown or "",
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)
    return True


def load_profile(username: str, session_state):
    username = (username or "").strip()
    if not username or not PROFILE_FILE.exists():
        return

    df = pd.read_csv(PROFILE_FILE)
    row = df[df["username"] == username]
    if row.empty:
        return
    row = row.iloc[0]

    mapping = {
        "age": ("age", int),
        "sex": ("sex", str),
        "height_cm": ("height", int),
        "weight_kg": ("weight", float),
        "activity": ("activity", str),
        "goal": ("goal", str),
        "allergies": ("allergies", str),
        "preferred_foods": ("preferred_foods", str),
    }
    for col, (state_key, cast) in mapping.items():
        if col in row and pd.notna(row[col]):
            session_state[state_key] = cast(row[col])


def save_profile(username: str, session_state) -> bool:
    username = (username or "").strip()
    if not username:
        return False

    row = {
        "username": username,
        "age": int(session_state["age"]),
        "sex": session_state["sex"],
        "height_cm": int(session_state["height"]),
        "weight_kg": float(session_state["weight"]),
        "activity": session_state["activity"],
        "goal": session_state["goal"],
        "allergies": session_state["allergies"],
        "preferred_foods": session_state["preferred_foods"],
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

def load_user_history(username: str) -> pd.DataFrame:
    """
    Φέρνει το ιστορικό ενός χρήστη από το history.csv.
    Κάνει αυτόματο parsing των timestamp/date χωρίς fixed format.
    """
    if not HISTORY_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(HISTORY_FILE)
    if df.empty or "username" not in df.columns:
        return pd.DataFrame()

    # Κρατάμε μόνο τον συγκεκριμένο χρήστη
    df = df[df["username"] == username].copy()

    # Parse timestamp χωρίς format (δουλεύει και για παλιές και για νέες εγγραφές)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Parse / φτιάξε date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    else:
        if "timestamp" in df.columns:
            df["date"] = df["timestamp"].dt.normalize()

    # Ταξινόμηση από το παλιότερο στο νεότερο
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")

    return df