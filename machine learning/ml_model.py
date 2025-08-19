import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# --- Step 1: Load Dataset ---
df = pd.read_csv(r"C:\Users\dalzi\OneDrive\Desktop\Job-matching\job-matching-\machine learning\job_matching_dataset_modified.csv")

# --- Step 2: Encode categorical columns ---
categorical_cols = ["job_field", "job_location", "job_title"]
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

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

# Restore readable job names
df["job_field_name"] = label_encoders["job_field"].inverse_transform(df["job_field"])
df["job_location_name"] = label_encoders["job_location"].inverse_transform(df["job_location"])
df["job_title_name"] = label_encoders["job_title"].inverse_transform(df["job_title"])

# --- Step 4: Generate pseudo training labels from rule-based system ---
# Use a fixed dummy preference (so scores vary between jobs)
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

# --- Step 5b: Evaluate Model ---
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("=== ML Model Performance ===")
print(f"R² Score: {r2:.4f}")
print(f"RMSE: {rmse:.2f}")

# --- Step 6: User input ---
print("\n=== Candidate Information ===")
preferred_field = input("Enter your field (e.g., Finance): ")
expected_salary = int(input("Enter your expected salary: "))
preferred_location = input("Enter your location (e.g., Durban): ")

# --- Step 7: Hybrid scoring ---
job_results = []
for idx, job in df.iterrows():
    # Rule-based score
    rule_score = compute_match_score(job, preferred_field, expected_salary, preferred_location)

    # ML score (use DataFrame with same feature names to avoid warning)
    job_features = pd.DataFrame([[job["job_field"],
                                  job["job_location"],
                                  job["job_title"],
                                  job["job_salary"]]],
                                columns=["job_field", "job_location", "job_title", "job_salary"])
    ml_score = model.predict(job_features)[0]

    # Hybrid (weighted average)
    final_score = (0.6 * ml_score) + (0.4 * rule_score)

    job_results.append((job["job_field_name"],
                        job["job_title_name"],
                        job["job_salary"],
                        job["job_location_name"],
                        rule_score,
                        ml_score,
                        final_score))

# --- Step 8: Sort & Display Results ---
# Filter jobs to respect user’s chosen field & location
filtered_jobs = [job for job in job_results if job[0].lower() == preferred_field.lower()
                 and job[3].lower() == preferred_location.lower()]

# Sort by salary descending, then final_score descending
filtered_jobs.sort(key=lambda x: (x[2], x[6]), reverse=True)

if not filtered_jobs:
    print("\nNo jobs found for that field & location.")
else:
    print("\n=== Top Job Matches (Hybrid ML + Rule-based) ===")
    for job_field, job_title, job_salary, job_location, rule_score, ml_score, final_score in filtered_jobs:
        print(f"Field: {job_field} | Job: {job_title} | Salary: {job_salary} | Location: {job_location} | "
              f"Rule Score: {rule_score:.2f} | ML Score: {ml_score:.2f} | Final Score: {final_score:.2f}")
