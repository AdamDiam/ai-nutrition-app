# ai_layer.py
import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


def calculate_targets(age, sex, height_cm, weight_kg, activity, goal):
    """Same logic as before, just moved here."""
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

def generate_weekly_plan(
    lang: str,
    age: int,
    sex: str,        # "male" or "female"
    height: int,
    weight: float,
    activity: str,
    goal: str,
    allergies: str,
    preferred_foods: str,
) -> str:
    """
    Call OpenAI and return ONLY the Markdown table for the weekly plan.
    """
    if client is None:
        raise RuntimeError("OpenAI client is not configured (missing API key).")

    sex_gr = "άνδρας" if sex == "male" else "γυναίκα"
    sex_en = "male" if sex == "male" else "female"

    if lang == "el":
        plan_prompt = f"""
Είμαι {age} ετών, {sex_gr}, ύψος {height} cm και βάρος {weight} kg.
Επίπεδο δραστηριότητας: {activity}.
Στόχος: {goal}.

Αλλεργίες / τρόφιμα προς αποφυγή: {allergies or "καμία"}.
Αγαπημένα φαγητά: {preferred_foods or "ό,τι ταιριάζει στον στόχο"}.

Θέλω ένα ΕΒΔΟΜΑΔΙΑΙΟ πρόγραμμα διατροφής σε μορφή πίνακα Markdown
με **στήλες = ημέρες** και **γραμμές = τύποι γευμάτων**.

Στήλες (με αυτή τη σειρά):
- Γεύμα
- Δευτέρα
- Τρίτη
- Τετάρτη
- Πέμπτη
- Παρασκευή
- Σάββατο
- Κυριακή

Γραμμές (με αυτή τη σειρά):
- Πρωινό
- Δεκατιανό
- Μεσημεριανό
- Απογευματινό
- Βραδινό
- Πριν τον ύπνο

Σε κάθε κελί γράψε:
• σύντομη περιγραφή του γεύματος  
• + ενδεικτική ποσότητα (π.χ. "κοτόπουλο με ρύζι (150 g κοτόπουλο, 100 g ρύζι)")

Πολύ σημαντικό:
- Επιστρέφεις ΜΟΝΟ τον πίνακα σε Markdown.
- Καμία εξήγηση πριν ή μετά.
"""
    else:
        plan_prompt = f"""
I am {age} years old, {sex_en}, {height} cm tall and {weight} kg.
Activity level: {activity}.
Goal: {goal}.

Allergies / foods to avoid: {allergies or "none"}.
Favourite foods: {preferred_foods or "anything that fits the goal"}.

Create a WEEKLY meal plan as a Markdown table
with **columns = days** and **rows = meal types**.

Columns (in this exact order):
- Meal
- Monday
- Tuesday
- Wednesday
- Thursday
- Friday
- Saturday
- Sunday

Rows (in this exact order):
- Breakfast
- Mid-morning snack
- Lunch
- Afternoon snack
- Dinner
- Before bed

In each cell include:
• a short description of the meal  
• + approximate quantity (e.g. "chicken with rice (150 g chicken, 100 g rice)")

Very important:
- Return ONLY the table in Markdown.
- No explanation before or after.
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

    return response.choices[0].message.content

def answer_plan_question(lang: str, plan_markdown: str, question: str) -> str:
    """
    Χρησιμοποιεί το τωρινό εβδομαδιαίο πλάνο και την ερώτηση
    και γυρνάει μια καθαρή απάντηση κειμένου από το AI.
    """
    if client is None:
        raise RuntimeError("OpenAI client is not configured (missing API key).")

    if lang == "el":
        qa_prompt = f"""
Αυτό είναι το εβδομαδιαίο πρόγραμμα διατροφής του χρήστη σε πίνακα Markdown:

{plan_markdown}

Ο χρήστης ρωτάει:
{question}

Απάντησε στα ελληνικά, με πρακτικές και συγκεκριμένες συμβουλές.
Μπορείς να αναφέρεσαι στο πλάνο, αλλά ΜΗΝ ξαναγράφεις όλο τον πίνακα.
"""
    else:
        qa_prompt = f"""
Here is the user's weekly nutrition plan as a Markdown table:

{plan_markdown}

The user asks:
{question}

Answer in clear, practical English.
You may refer to parts of the plan but do NOT rewrite the whole table.
"""

    response = client.chat.completions.create(
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
    return response.choices[0].message.content


def adjust_weekly_plan(lang: str, current_plan_md: str, feedback: str) -> str:
    """
    Παίρνει το τωρινό πλάνο (Markdown) + feedback χρήστη
    και γυρνάει ΝΕΟ πλάνο (πάλι μόνο Markdown table).
    """
    if client is None:
        raise RuntimeError("OpenAI client is not configured (missing API key).")

    if lang == "el":
        adjust_prompt = f"""
Εδώ είναι το τωρινό εβδομαδιαίο πρόγραμμα διατροφής σε πίνακα Markdown:

{current_plan_md}

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

{current_plan_md}

The user wants the following changes:
{feedback}

Create a NEW plan, with the exact same table structure (same days, same meal rows),
but adjusted to the user's comments.

Important:
- Return ONLY the table in Markdown format.
- Do NOT add any extra text.
"""

    response = client.chat.completions.create(
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
    return response.choices[0].message.content
