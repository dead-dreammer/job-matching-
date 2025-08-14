from flask import Flask, render_template # Import necessary libraries

# Create an instance of the Flask application
app = Flask(__name__) # The __name__ variable tells Flask where to look for templates and static files

# Create routes for all pages
@app.route('/') 
def home():
    return render_template('Index.html')

@app.route('/about')
def about():
    return render_template('AboutUs.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/login')
def login():
    return render_template('LoginPage.html')

@app.route('/signup')
def signup():
    return render_template('SignUp.html')

# Server will only run if this file is executed directly
# Prevents the server from running if the file is imported into another module
if __name__ == '__main__':
    # Runs the Flask development server with debugging enabled
    app.run(debug = True)