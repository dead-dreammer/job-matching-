#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:





# In[ ]:





# In[8]:


# job_matching_ai_display.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

# --- Step 1: Load Dataset ---
df = pd.read_csv(r"C:\Users\udayk\OneDrive\Documents\hackathon project\job_matching_dataset.csv")

# --- Step 2: Encode categorical columns ---
categorical_cols = ["preferred_field", "preferred_location", "job_field", "job_location", "job_title"]
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# --- Step 3: Compute smarter match score ---
def compute_match_score(row):
    score = 0
    if row["preferred_field"] == row["job_field"]:
        score += 40
    if row["preferred_location"] == row["job_location"]:
        score += 30
    expected = row["expected_salary"]
    offered = row["job_salary"]
    salary_diff = abs(expected - offered) / expected
    if salary_diff < 0.1:
        score += 20
    elif salary_diff < 0.2:
        score += 10
    if str(row["preferred_field"]).lower() in str(row["job_title"]).lower():
        score += 10
    return score

df["smart_match_score"] = df.apply(compute_match_score, axis=1)

# --- Step 4: Classification labels ---
def classify_score(score):
    if score <= 30:
        return "Weak"
    elif score <= 60:
        return "Medium"
    else:
        return "Strong"

df["match_category"] = df["smart_match_score"].apply(classify_score)

# --- Step 5: Prepare data ---
X = df.drop(columns=["match_score", "match_score_percentage", "smart_match_score", "match_category"], errors="ignore")
y_reg = df["smart_match_score"]
y_clf = df["match_category"]

# --- Step 6: Train/test split ---
X_train, X_test, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_clf, test_size=0.2, random_state=42)

# --- Step 7a: Train regression model ---
reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
reg_model.fit(X_train, y_train_reg)

# --- Step 7b: Train classification model ---
clf_model = RandomForestClassifier(n_estimators=100, random_state=42)
clf_model.fit(X_train_c, y_train_c)

# --- Step 8: Candidate input ---
print("=== Candidate Information ===")
preferred_field = input("Enter your field (e.g., Finance): ")
expected_salary = int(input("Enter your expected salary: "))
preferred_location = input("Enter your location (e.g., Durban): ")

# --- Step 9: Loop through jobs & predict best matches ---
job_results = []

for idx, job in df.iterrows():
    job_data = {
        "preferred_field": label_encoders["preferred_field"].transform([preferred_field])[0],
        "expected_salary": expected_salary,
        "preferred_location": label_encoders["preferred_location"].transform([preferred_location])[0],
        "job_field": job["job_field"],
        "job_salary": job["job_salary"],
        "job_location": job["job_location"],
        "job_title": job["job_title"],
    }
    job_df = pd.DataFrame([job_data])
    score = reg_model.predict(job_df)[0]
    category = clf_model.predict(job_df)[0]

    # Decode label encoded values for display
    job_title_name = label_encoders["job_title"].inverse_transform([job["job_title"]])[0]
    job_field_name = label_encoders["job_field"].inverse_transform([job["job_field"]])[0]
    job_location_name = label_encoders["job_location"].inverse_transform([job["job_location"]])[0]

    job_results.append((job_title_name, job_field_name, job_location_name, score, category))

# --- Step 10: Rank jobs ---
job_results.sort(key=lambda x: x[3], reverse=True)

print("\n=== Top Job Matches ===")
for job_title, job_field, job_location, score, category in job_results[:10]:
    print(f"Job: {job_title} | Field: {job_field} | Location: {job_location} | Score: {score:.2f} | Category: {category}")


# In[ ]:




