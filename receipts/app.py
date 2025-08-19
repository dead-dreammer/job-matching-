from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

transactions = []

# ---------------------------
# Luhn Algorithm Validator
# ---------------------------
def luhn_check(card_number: str) -> bool:
    card_number = card_number.replace(" ", "")  # remove spaces if any
    if not card_number.isdigit():
        return False
    
    total = 0
    reverse_digits = card_number[::-1]

    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        # Double every second digit
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0

@app.route('/')
def home():
    return render_template('payment_form.html')

@app.route('/pay', methods=['POST'])
def pay():
    employer_name = request.form.get('employer_name')
    job_title = request.form.get('job_title')
    amount = request.form.get('amount')
    card_number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvv = request.form.get('cvv')

    # Check if fields are filled
    if not all([employer_name, job_title, amount, card_number, expiry, cvv]):
        return render_template("payment_form.html", error="⚠️ Please fill all fields!")

    # Validate card number with Luhn’s Algorithm
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
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    transactions.append(transaction)

    return redirect(url_for('transaction_page', transaction_id=transaction["id"]))


@app.route('/transaction/<int:transaction_id>')
def transaction_page(transaction_id):
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    if not transaction:
        return "Transaction not found", 404
    return render_template('receipt.html', transaction=transaction)

@app.route('/release/<int:transaction_id>', methods=['POST'])
def release_funds(transaction_id):
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    if not transaction:
        return "Transaction not found", 404

    # Simulate releasing funds
    transaction["status"] = "PAID_OUT"
    transaction["released_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return redirect(url_for('transaction_page', transaction_id=transaction_id))

@app.route('/transactions')
def all_transactions():
    return {"transactions": transactions}

if __name__ == "__main__":
    app.run(debug=True)
