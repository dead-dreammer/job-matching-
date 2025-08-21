from flask import Blueprint, request, render_template, send_file
from Database.models import FormalJob
from Database.__init__ import db
from weasyprint import HTML
import tempfile
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


employee = Blueprint('employee', __name__)

# Globals to hold job data and ML model
jobs_query_global = []
df_global = None
model_global = None
encoders = {}  # for label encoding categorical values


# 🔹 Match scoring helper
def compute_match_score(row, preferred_field, expected_salary, preferred_location):
    score = 0
    if preferred_field and str(row["job_field"]).lower() == preferred_field.lower():
        score += 1
    if preferred_location and str(row["job_location"]).lower() == preferred_location.lower():
        score += 1
    if expected_salary and row["job_salary"] <= expected_salary:
        score += 1
    return score


# 🔹 Train ML model on jobs
def train_ml_model(df):
    global encoders
    df_encoded = df.copy()

    # Encode categorical features
    for col in ["job_field", "job_location", "job_title"]:
        enc = LabelEncoder()
        df_encoded[col] = enc.fit_transform(df_encoded[col])
        encoders[col] = enc

    X = df_encoded[["job_field", "job_location", "job_title", "job_salary"]]
    y = df_encoded["job_salary"]  # predicting salary as a proxy for job ranking

    # Split + train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model


@employee.route('/formal/browse', methods=['GET', 'POST'])
def employee_formal_browse():
    global jobs_query_global, df_global, model_global

    # 🔹 Always load jobs fresh from DB
    jobs_query_global = FormalJob.query.all()
    if not jobs_query_global:
        return render_template('EmployerFormalDisplay.html', jobs=[])

    # Build DataFrame
    df_global = pd.DataFrame([{
        "job_field": job.job_field,
        "job_location": job.location,
        "job_title": job.title,
        "job_salary": job.salary,
        "description": job.description,
        "requirements": job.requirements
    } for job in jobs_query_global])

    # 🔹 Train ML model once if not trained
    if model_global is None and not df_global.empty:
        model_global = train_ml_model(df_global)

    jobs_list = []

    # ------------------ Case 1: Filters applied (POST) ------------------
    if request.method == "POST":
        preferred_field = request.form.get("job_field")
        salary_val = request.form.get("salary")
        expected_salary = int(salary_val) if salary_val else None
        preferred_location = request.form.get("location")

        for idx, row in df_global.iterrows():
            # Rule-based score
            rule_score = compute_match_score(row, preferred_field, expected_salary, preferred_location)

            # ML score
            ml_score = 0
            if model_global is not None:
                features = pd.DataFrame([[row["job_field"], row["job_location"], row["job_title"], row["job_salary"]]],
                                        columns=["job_field", "job_location", "job_title", "job_salary"])

                # Encode categorical features before prediction
                for col in ["job_field", "job_location", "job_title"]:
                    if col in encoders:
                        features[col] = encoders[col].transform(features[col])

                ml_score = model_global.predict(features)[0]

            final_score = 0.6 * ml_score + 0.4 * rule_score

            jobs_list.append({
                "job_field": row["job_field"],
                "title": row["job_title"],
                "salary": row["job_salary"],
                "location": row["job_location"],
                "description": row["description"],
                "requirements": row["requirements"],
                "rule_score": rule_score,
                "ml_score": ml_score,
                "final_score": final_score
            })

        # ✅ Apply filters only when user selects
        if preferred_field:
            jobs_list = [job for job in jobs_list if job["job_field"].lower() == preferred_field.lower()]
        if preferred_location:
            jobs_list = [job for job in jobs_list if job["location"].lower() == preferred_location.lower()]

        # Sort by salary + ML score
        jobs_list.sort(key=lambda x: (x["salary"], x["final_score"]), reverse=True)

    # ------------------ Case 2: No filters (GET) ------------------
    else:
        for idx, row in df_global.iterrows():
            jobs_list.append({
                "job_field": row["job_field"],
                "title": row["job_title"],
                "salary": row["job_salary"],
                "location": row["job_location"],
                "description": row["description"],
                "requirements": row["requirements"]
            })

    return render_template('EmployerFormalDisplay.html', jobs=jobs_list)


# 🔹 CV Generator
@employee.route('/cv-gen', methods=['GET', 'POST'])
def cv_gen():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        skills = request.form.get('skills').split(',')
        experience = request.form.get('experience')

        rendered_html = render_template(
            'cv_template.html',
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            experience=experience
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            HTML(string=rendered_html).write_pdf(pdf_file.name)
            return send_file(pdf_file.name, as_attachment=True, download_name=f"{name}_CV.pdf")

    return render_template('form.html')
