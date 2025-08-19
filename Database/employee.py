from flask import Blueprint, request, jsonify, session, render_template, send_file
from Database.models import InformalJob
from Database.__init__ import db
from weasyprint import HTML
import tempfile

employee = Blueprint('employee', __name__)

@employee.route('/cv-gen', methods=['GET', 'POST'])
def cv_gen():
    if request.method == 'POST':
        from weasyprint import HTML  # lazy import only when needed
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        skills = request.form.get('skills').split(',')
        experience = request.form.get('experience')

        rendered_html = render_template('cv_template.html',
                                        name=name,
                                        email=email,
                                        phone=phone,
                                        skills=skills,
                                        experience=experience)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            HTML(string=rendered_html).write_pdf(pdf_file.name)
            return send_file(pdf_file.name, as_attachment=True, download_name=f"{name}_CV.pdf")

    return render_template('form.html')

