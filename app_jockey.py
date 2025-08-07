from flask import Flask, render_template, request, redirect, url_for

# Create an instance of the Flask application
app = Flask(__name__)

# --- ROUTES ---

# Homepage or landing page of the job matching site
@app.route('/')
def home():
    return render_template('index.html')  # Generic homepage

# Job listings page
@app.route('/jobs')
def job_listings():
    # This would normally fetch job listings from a database
    jobs = [
        {'id': 1, 'title': 'Software Engineer', 'location': 'Cape Town'},
        {'id': 2, 'title': 'Data Analyst', 'location': 'Johannesburg'},
        {'id': 3, 'title': 'UX Designer', 'location': 'Remote'}
    ]
    return render_template('jobs.html', jobs=jobs)

# Job application form page
@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply(job_id):
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        resume = request.form.get('resume')  # In reality, you'd handle file upload here
        # Logic to save application would go here
        return redirect(url_for('thank_you'))
    return render_template('apply.html', job_id=job_id)

# Thank you page after applying
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    app.run(debug=True)
