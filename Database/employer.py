from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from Database.models import InformalJob
from Database.models import FormalJob
from Database.__init__ import db
import datetime

employer = Blueprint('employer', __name__)

# ---------------------------
# Informal Job Posting
# ---------------------------
@employer.route('/informal/post', methods=['POST'])
def informal_post():
    if not session.get('user_id'):
        return jsonify({'error': 'You must be logged in'}), 401

    try:
        data = request.get_json()
        new_job = InformalJob(
            title=data.get('title'),
            field=data.get('field'),
            pay_rate=data.get('payRate'),
            location=data.get('location'),
            description=data.get('description'),
            requirements=data.get('requirements'),
            created_by=session.get('user_name')
        )
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Job posted successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Display formal job post page

@employer.route('/formal/post', methods=['POST'])
def formal_post():
    data = request.get_json()  # <--- this is key for JSON requests
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    new_job = FormalJob(
        title=data.get('title'),
        salary=data.get('salary'),
        location=data.get('location'),
        description=data.get('description'),
        requirements=data.get('requirements'),
        created_by=session.get('user_name')
    )
    db.session.add(new_job)
    db.session.commit()
    return jsonify({"success": True, "message": "Job posted successfully"})


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
