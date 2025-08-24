from flask import Flask, render_template, request, jsonify
from Database.auth import auth
from Database.__init__ import db, create_database
from flask import session



app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = 'dalziel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

# Register blueprint
app.register_blueprint(auth, url_prefix='/auth')


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

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('LoginPage.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    return render_template('SignUp.html')

if __name__ == '__main__':
    # Runs the Flask development server with debugging enabled
    app.run(host="0.0.0.0", port=5000)