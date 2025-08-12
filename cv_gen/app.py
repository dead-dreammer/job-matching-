from flask import Flask, render_template, request, send_file
from weasyprint import HTML
import tempfile
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        skills = request.form.get('skills').split(',')
        experience = request.form.get('experience')

        # Render HTML with form data
        rendered_html = render_template('cv_template.html',
                                        name=name,
                                        email=email,
                                        phone=phone,
                                        skills=skills,
                                        experience=experience)

        # Create temp PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            HTML(string=rendered_html).write_pdf(pdf_file.name)
            return send_file(pdf_file.name, as_attachment=True, download_name="CV.pdf")

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
