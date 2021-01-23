from flask import Blueprint, request, jsonify


mail_bp = Blueprint('mail_bp', __name__)

@mail_bp.route('/mails', methods = ["GET"])
def view_inbox():

    data = {
        "sender": "omarredaelsayedmohamed@gmail.com",
        "receiver": "mailerfirstmailerlast@gmail.com",
        "subject": "Urgent Meeting",
        "body": "hey, omar I hope you are good,\
            there is tommorrow a meeting at 9 am with the ceo I hope you are ready."
    }
    return jsonify(data)
            

