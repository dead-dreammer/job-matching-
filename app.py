from flask import Flask, render_template, request, jsonify, send_file
from Database.auth import auth
from Database.__init__ import db, create_database
from Database.employer import employer
from Database.employee import employee
import tempfile
from weasyprint import HTML
from flask import session



app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = 'dalziel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# Register blueprint
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(employer, url_prefix='/employer')
app.register_blueprint(employee, url_prefix='/employee')

# Create DB if not exists
with app.app_context():
    create_database(app)

@app.after_request
def add_header(response):

    response.headers["Cache-Control"] = "no-store"
    return response


@app.route('/') 
def home():
    return render_template('Index.html')

@app.route('/profile')
def profile():
    return render_template('Profile.html')

@app.route('/about')
def about():
    return render_template('AboutUs.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('LoginPage.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    return render_template('SignUp.html')


# Employer routes
@app.route('/choice')
def choice():
    return render_template('Choice.html')

@app.route('/employer/choice')
def employer_choice():
    return render_template('EmployerChoice.html')

@app.route('/employer/pay')
def employer_pay():
    return render_template('payment_form.html')

@app.route('/employer/formal/post', methods=['GET', 'POST'])
def employer_formal_post():
    return render_template('EmployerFormalPost.html')

@app.route('/employer/formal/display')
def employer_formal_display():
    return render_template('EmployerFormalDisplay.html')

@app.route('/employer/informal/post', methods=['GET', 'POST'])
def employer_informal_post():
    return render_template('EmployerInformalPost.html')

@app.route('/employer/informal/display')
def employer_informal_display():
    return render_template('EmployerInformalDisplay.html')

# Employee routes
@app.route('/employee/choice')
def employee_choice():
    return render_template('EmployeeChoice.html')

@app.route('/employee/formal/browse')
def employee_formal_browse():
    return render_template('EmployerFormalDisplay.html' )

@app.route('/employee/informal/browse')
def employee_informal_browse():
    return render_template('EmployerInformalDisplay.html')

@app.route('/employee/cv-gen', methods=['GET', 'POST'])
def employee_cv_gen():
    if request.method == 'POST':
        from weasyprint import HTML
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        skills = request.form.get('skills').split(",") if request.form.get('skills') else []
        education = request.form.get('education')
        experience = request.form.get('experience')
        projects = request.form.get('projects')
        additional = request.form.get('additional')

        rendered_html = render_template(
            'cv_template.html',
            name=name,
            email=email,
            phone=phone,
            address=address,
            skills=[s.strip() for s in skills],  # clean up whitespace
            education=education,
            experience=experience,
            projects=projects,
            additional=additional
        )

        #  generate pdf here inside POST
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            HTML(string=rendered_html).write_pdf(pdf_file.name)
            return send_file(pdf_file.name, as_attachment=True, download_name=f"{name}_CV.pdf")

    # GET: just show the form
    return render_template('cv_form.html')




# Server will only run if this file is executed directly
# Prevents the server from running if the file is imported into another module
if __name__ == '__main__':
    # Runs the Flask development server with debugging enabled
    app.run(host="0.0.0.0", port=5000)