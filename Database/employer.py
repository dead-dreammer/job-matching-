from flask import Blueprint
from flask import request, jsonify, session, render_template
from . import employer
from Database.models import InformalJob
from Database.__init__ import db

employer = Blueprint('employer', __name__)

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
            created_by=session.get('user_id')
        )

        db.session.add(new_job)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Job posted successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Display informal jobs
@employer.route('/formal/post')
def formal_post():
   
    return render_template('EmployerPost.html')
