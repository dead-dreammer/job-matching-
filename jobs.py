import csv
import random
from app import app, db
from Database.models import FormalJob

csv_path = r'C:\Users\dalzi\OneDrive\Desktop\Job-matching\job-matching-\jobs_with_details.csv'
# Insert jobs within Flask app context
with app.app_context():
    with open(csv_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            field = row['job_field']  # adjust to your CSV column name
            job = FormalJob(
                title=row['job_title'],  # adjust to your CSV column
                salary=float(row['job_salary']),
                job_field=field,
                description=row['description'],
                requirements=row['requirements'],
                location=row['job_location'],
                company_id=random.randint(1, 5),  # random company assignment
                created_by="Uday Kisson"  # if you have a creator, adjust accordingly
            )
            db.session.add(job)
        db.session.commit()
    print("Jobs inserted successfully!")