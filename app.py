from flask import Flask, render_template
from Database.auth import auth
from Database.__init__ import db, create_database
from Database.employer import employer
from Database.employee import employee

app = Flask(__name__)
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
    return render_template('form.html')

# Server will only run if this file is executed directly
# Prevents the server from running if the file is imported into another module
if __name__ == '__main__':
    # Runs the Flask development server with debugging enabled
    app.run(debug = True)