from flask import Blueprint, request, jsonify, session
from Database.models import InformalJob, FormalJob, Company, User
from Database.__init__ import db

employer = Blueprint('employer', __name__)

# ---------------------------
# Informal Job Posting
# ---------------------------
@employer.route('/informal/post', methods=['POST'])
def informal_post():
    # Ensure user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'You must be logged in'}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # Create Informal Job
    try:
        new_job = InformalJob(
            title=data.get('title'),
            field=data.get('field'),
            pay_rate=data.get('payRate'),
            location=data.get('location'),
            description=data.get('description'),
            requirements=data.get('requirements'),
            created_by=user_id  # Link by user ID
        )
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Informal job posted successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ---------------------------
# Formal Job Posting
# ---------------------------
@employer.route('/formal/post', methods=['POST'])
def formal_post():
    if not session.get('user_id'):
        return jsonify({"error": "You must be logged in"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # Get user and company info from session
    company_id = session.get('company_id')
    user_id = session.get('user_id')
    if not company_id:
        return jsonify({"error": "You must be linked to a company to post a formal job"}), 400

    # Validate required fields
    required_fields = ['title', 'job_field', 'salary', 'location', 'description', 'requirements']
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Create and save job
    new_job = FormalJob(
        title=data.get('title'),
        job_field=data.get('job_field'),
        salary=data.get('salary'),
        location=data.get('location'),
        description=data.get('description'),
        requirements=data.get('requirements'),
        company_id=company_id,
        created_by=user_id
    )

    try:
        db.session.add(new_job)
        db.session.commit()
        return jsonify({"success": True, "message": "Job posted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------------------
# Payment & Transactions
# ---------------------------
transactions = []

# Luhn Algorithm Validator
def luhn_check(card_number: str) -> bool:
    card_number = card_number.replace(" ", "")
    if not card_number.isdigit():
        return False
    total = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

# Display payment form
@employer.route('/pay')
def pay_home():
    return render_template('payment_form.html')

# Process payment
@employer.route('/payment', methods=['POST'])
def pay():
    employer_name = request.form.get('employer_name')
    job_title = request.form.get('job_title')
    amount = request.form.get('amount')
    card_number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvv = request.form.get('cvv')

    # Check required fields
    if not all([employer_name, job_title, amount, card_number, expiry, cvv]):
        return render_template("payment_form.html", error="⚠️ Please fill all fields!")

    # Validate card
    if not luhn_check(card_number):
        return render_template("payment_form.html", error="⚠️ Invalid card number!")

    transaction = {
        "id": len(transactions) + 1,
        "employer_name": employer_name,
        "job_title": job_title,
        "amount": amount,
        "card_number": card_number,
        "expiry": expiry,
        "cvv": cvv,
        "status": "IN_ESCROW",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    transactions.append(transaction)

    return redirect(url_for('employer.transaction_page', transaction_id=transaction["id"]))

# View transaction receipt
@employer.route('/transaction/<int:transaction_id>')
def transaction_page(transaction_id):
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    if not transaction:
        return "Transaction not found", 404
    return render_template('receipt.html', transaction=transaction)

# Release funds
@employer.route('/release/<int:transaction_id>', methods=['POST'])
def release_funds(transaction_id):
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    if not transaction:
        return "Transaction not found", 404

    transaction["status"] = "PAID_OUT"
    transaction["released_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return redirect(url_for('employer.transaction_page', transaction_id=transaction_id))

# List all transactions
@employer.route('/transactions')
def all_transactions():
    return {"transactions": transactions}
