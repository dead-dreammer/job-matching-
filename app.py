from flask import Flask, render_template # Import necessary libraries

# Create an instance of the Flask application
app = Flask(__name__) # The __name__ variable tells Flask where to look for templates and static files

# Create a route for the homapage
@app.route('/') 
# Function will run if user accesses the above root
def home():
    # Renders the html file
    return render_template('') # -- HTML FILE GOES HERE -- 

# Server will only run if this file is executed directly
# Prevents the server from running if the file is imported into another module
if __name__ == '__main__':
    # Runs the Flask development server with debugging enabled
    app.run(debug = True)