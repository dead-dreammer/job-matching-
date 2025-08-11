from flask import Flask, render_template, request, send_file
import pdfkit
import os

app = Flask(__name__)


path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/generate_cv', methods=['POST'])
def generate_cv():
    # Get data from form as a dictionary
    data = request.form.to_dict()

    # Render the HTML template with form data
    rendered = render_template('cv_template.html', **data)

    # Define where to save the PDF
    pdf_path = os.path.join(os.getcwd(), 'cv_output.pdf')

    # Generate PDF from HTML string
    try:
        pdfkit.from_string(rendered, pdf_path, configuration=config)
    except Exception as e:
        return f"PDF generation failed: {str(e)}"

    # Send the generated PDF as a downloadable file
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
