from flask import Blueprint, request, jsonify, session, render_template, send_file
from Database.models import InformalJob
from Database.models import FormalJob
from Database.__init__ import db
from weasyprint import HTML
import tempfile
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from app import app  # Import your Flask app

employee = Blueprint('employee', __name__)

with app.app_context():
    jobs_query = FormalJob.query.all()

data = []
for job in jobs_query:
    data.append({
        "job_field": job.job_field,
        "job_location": job.location,
        "job_title": job.title,
        "job_salary": job.salary
    })
df = pd.DataFrame(data)

categorical_cols = ["job_field", "job_location", "job_title"]
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

df["job_field_name"] = [job.job_field for job in jobs_query]
df["job_location_name"] = [job.location for job in jobs_query]
df["job_title_name"] = [job.title for job in jobs_query]

def compute_match_score(row, user_field, user_salary, user_location):
    score = 0
    if row["job_field_name"].lower() == user_field.lower():
        score += 40
    if row["job_location_name"].lower() == user_location.lower():
        score += 30
    salary_diff = abs(user_salary - row["job_salary"]) / user_salary
    if salary_diff < 0.1:
        score += 20
    elif salary_diff < 0.2:
        score += 10
    if user_field.lower() in row["job_title_name"].lower():
        score += 10
    return score

df["match_score"] = df.apply(lambda row: compute_match_score(row, "Finance", 20000, "Durban"), axis=1)

X = df[["job_field", "job_location", "job_title", "job_salary"]]
y = df["match_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"R²: {r2_score(y_test, model.predict(X_test)):.4f}, RMSE: {np.sqrt(mean_squared_error(y_test, model.predict(X_test))):.2f}")

@employee.route('/cv-gen', methods=['GET', 'POST'])
def cv_gen():
    if request.method == 'POST':
        from weasyprint import HTML  # lazy import only when needed
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        skills = request.form.get('skills').split(',')
        experience = request.form.get('experience')

        rendered_html = render_template('cv_template.html',
                                        name=name,
                                        email=email,
                                        phone=phone,
                                        skills=skills,
                                        experience=experience)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            HTML(string=rendered_html).write_pdf(pdf_file.name)
            return send_file(pdf_file.name, as_attachment=True, download_name=f"{name}_CV.pdf")

    return render_template('form.html')


@employee.route('/formal/browse')
def employee_formal_browse():
    jobs_list = []

    if request.method == "POST":
        preferred_field = request.form.get("field")
        expected_salary = int(request.form.get("salary"))
        preferred_location = request.form.get("location")

        for idx, row in df.iterrows():
            # Rule-based
            rule_score = compute_match_score(row, preferred_field, expected_salary, preferred_location)

            # ML prediction
            features = pd.DataFrame([[row["job_field"], row["job_location"], row["job_title"], row["job_salary"]]],
                                    columns=["job_field", "job_location", "job_title", "job_salary"])
            ml_score = model.predict(features)[0]

            final_score = 0.6 * ml_score + 0.4 * rule_score

            jobs_list.append({
                "field": row["job_field_name"],
                "title": row["job_title_name"],
                "salary": row["job_salary"],
                "location": row["job_location_name"],
                "description": getattr(jobs_query[idx], "description", ""),
                "requirements": getattr(jobs_query[idx], "requirements", ""),
                "rule_score": rule_score,
                "ml_score": ml_score,
                "final_score": final_score
            })

        # Filter jobs for user's field & location
        jobs_list = [job for job in jobs_list
                     if job["field"].lower() == preferred_field.lower()
                     and job["location"].lower() == preferred_location.lower()]

        # Sort by salary and final_score
        jobs_list.sort(key=lambda x: (x["salary"], x["final_score"]), reverse=True)

    else:
        # GET request: show all jobs
        for idx, row in df.iterrows():
            jobs_list.append({
                "field": row["job_field_name"],
                "title": row["job_title_name"],
                "salary": row["job_salary"],
                "location": row["job_location_name"],
                "description": getattr(jobs_query[idx], "description", ""),
                "requirements": getattr(jobs_query[idx], "requirements", ""),
            })

    return render_template('EmployerFormalDisplay.html', jobs=jobs_list)

