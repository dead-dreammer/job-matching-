import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load dataset
df = pd.read_csv("job_matching_dataset.csv")

# Encode categorical fields
label_encoders = {}
for col in ['preferred_field', 'preferred_location', 'job_field', 'job_location']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Scale salary
scaler = StandardScaler()
df[['expected_salary', 'job_salary']] = scaler.fit_transform(df[['expected_salary', 'job_salary']])

# Example user input
user_input = {
    "preferred_field": "Finance",
    "expected_salary": 18000,
    "preferred_location": "Cape Town"
}


# Encode user input
user_encoded = {
    "preferred_field": label_encoders["preferred_field"].transform([user_input["preferred_field"]])[0],
    "preferred_location": label_encoders["preferred_location"].transform([user_input["preferred_location"]])[0],
    "expected_salary": scaler.transform([[user_input["expected_salary"], 0]])[0][0]  # Use first value
}

# Rule-based scoring
job_matches = []
for _, job in df.iterrows():
    field_match = int(user_encoded["preferred_field"] == job["job_field"])
    location_match = int(user_encoded["preferred_location"] == job["job_location"])
    salary_diff = abs(user_encoded["expected_salary"] - job["job_salary"])
    salary_score = max(0, 1 - salary_diff)  # the closer the better

    total_score = 0.5 * field_match + 0.3 * location_match + 0.2 * salary_score
    job_matches.append((job["job_title"], total_score, job["job_location"], job["job_salary"]))

# Sort by best match
sorted_matches = sorted(job_matches, key=lambda x: x[1], reverse=True)

# Display
print("\nTop Job Matches:\n")
for title, score, location_code, salary in sorted_matches[:10]:
    location = label_encoders["job_location"].inverse_transform([int(location_code)])[0]
    print(f"{title} | Score: {score:.2f} | Location: {location} | Salary: {int(salary)}")
