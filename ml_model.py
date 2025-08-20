import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from app import app, db  # Import your Flask app and db
from Database.models import FormalJob  # Import your job model

# --- Step 1: Fetch jobs from database ---
with app.app_context():
    jobs_query = FormalJob.query.all()

# Convert to DataFrame for ML processing
data = []
for job in jobs_query:
    data.append({
        "job_field": job.job_field,
        "job_location": job.location,
        "job_title": job.title,
        "job_salary": job.salary
    })
df = pd.DataFrame(data)

# --- Step 2: Encode categorical columns ---
categorical_cols = ["job_field", "job_location", "job_title"]
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# Keep readable names for display
df["job_field_name"] = [job.job_field for job in jobs_query]
df["job_location_name"] = [job.location for job in jobs_query]
df["job_title_name"] = [job.title for job in jobs_query]

# --- Step 3: Rule-based scoring function ---
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

# --- Step 4: Generate pseudo training labels ---
df["match_score"] = df.apply(
    lambda row: compute_match_score(row, "Finance", 20000, "Durban"),
    axis=1
)

# --- Step 5: Train ML model ---
X = df[["job_field", "job_location", "job_title", "job_salary"]]
y = df["match_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Optional: Evaluate
y_pred = model.predict(X_test)
print(f"R²: {r2_score(y_test, y_pred):.4f}, RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")

# --- Step 6: Get user input ---
preferred_field = input("Enter your field (e.g., Finance): ")
expected_salary = int(input("Enter your expected salary: "))
preferred_location = input("Enter your location (e.g., Durban): ")

# --- Step 7: Compute hybrid score for DB jobs ---
job_results = []
for idx, row in df.iterrows():
    # Rule-based score
    rule_score = compute_match_score(row, preferred_field, expected_salary, preferred_location)

    # ML score
    features = pd.DataFrame([[row["job_field"], row["job_location"], row["job_title"], row["job_salary"]]],
                            columns=["job_field", "job_location", "job_title", "job_salary"])
    ml_score = model.predict(features)[0]

    # Hybrid score
    final_score = 0.6 * ml_score + 0.4 * rule_score

    job_results.append({
        "field": row["job_field_name"],
        "title": row["job_title_name"],
        "salary": row["job_salary"],
        "location": row["job_location_name"],
        "rule_score": rule_score,
        "ml_score": ml_score,
        "final_score": final_score
    })

# --- Step 8: Filter & Sort ---
filtered_jobs = [job for job in job_results
                 if job["field"].lower() == preferred_field.lower()
                 and job["location"].lower() == preferred_location.lower()]

filtered_jobs.sort(key=lambda x: (x["salary"], x["final_score"]), reverse=True)

# --- Step 9: Display top matches ---
if not filtered_jobs:
    print("No jobs found for that field & location.")
else:
    print("\n=== Top Job Matches ===")
    for job in filtered_jobs:
        print(f"Field: {job['field']} | Job: {job['title']} | Salary: {job['salary']} | "
              f"Location: {job['location']} | Rule Score: {job['rule_score']:.2f} | "
              f"ML Score: {job['ml_score']:.2f} | Final Score: {job['final_score']:.2f}")
