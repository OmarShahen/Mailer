from flask import Blueprint, render_template, session, request, redirect, url_for, current_app, jsonify, send_from_directory, abort, flash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import validator
import json
from Forms.forms import check_authentication


def get_user_id(user_email):
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    select_user_query = """SELECT user_id FROM user WHERE user_email = ?;"""
    select_user_query_data = (user_email,)
    user_record = sqlite_connection.execute(
        select_user_query, select_user_query_data)
    user_id = 0
    for data in user_record:
        user_id = data[0]
    sqlite_connection.close()
    return user_id


def get_user_email(user_id):
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    select_user_query = """SELECT user_email FROM user WHERE user_id = ?;"""
    select_user_query_data = (user_id,)
    user_record = sqlite_connection.execute(
        select_user_query, select_user_query_data)
    user_email = ""
    for data in user_record:
        user_email = data[0]
    sqlite_connection.close()
    return user_email


def check_attachment_exist(mail_id):
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    search_file_query = """SELECT * FROM attachment WHERE mail_id = ?;"""
    search_file_query_data = (mail_id,)
    file_list = sqlite_connection.execute(
        search_file_query, search_file_query_data).fetchall()
    if len(file_list) == 0:
        sqlite_connection.close()
        return False
    else:
        sqlite_connection.close()
        return True


def get_attachments(mail_id):
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    select_attachment_query = """SELECT attachment_file FROM attachment WHERE mail_id = ?;"""
    mail_attachments = sqlite_connection.execute(
        select_attachment_query, (mail_id,))
    file_list = []
    for file in mail_attachments:
        file_list.append(file)
    sqlite_connection.close()
    return file_list


def check_files_numbers(files):
    for file in files:
        if file.filename == "":
            return False
    return True


def check_file_extension(files):
    for file in files:
        if '.' not in file.filename:
            return False
        splite_file = file.filename.split('.')
        if splite_file[1].upper() not in current_app.config['ALLOWED_EXTENSIONS']:
            return False
    return True


def validate_file_extension(file):
    if '.' not in file:
        return False
    splite_file = file.split('.')
    if splite_file[1].upper() not in current_app.config['ALLOWED_EXTENSIONS']:
        return False
    return True


def month_with_day(full_date):
    date = datetime.strptime(full_date, '%Y-%m-%d %H:%M:%S.%f')
    return date.strftime('%b %d')


def remove_milli_seconds(full_date):
    date = datetime.strptime(full_date, '%Y-%m-%d %H:%M:%S.%f')
    return date.strftime('%Y-%m-%d %H:%M:%S')


def sort_mails(all_mails):
    counter = 0
    while(counter < len(all_mails)):
        i = 0
        while(i < len(all_mails)-1):
            if all_mails[i]["mail_id"] < all_mails[i+1]["mail_id"]:
                temp = all_mails[i]
                all_mails[i] = all_mails[i+1]
                all_mails[i+1] = temp
            i += 1
        counter += 1
    return all_mails


def return_outbox(sender_id):

    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    select_single_outbox = """SELECT * FROM mail WHERE sender_id = ? AND sender_trashed = ?
                              AND multiple_receivers = ? ORDER BY  mail_id DESC;"""
    db_single_outbox = sqlite_connection.execute(
        select_single_outbox, (sender_id, 0, 0))
    single_outbox = []
    mail_data = {}
    for mail in db_single_outbox:
        mail_data['mail_id'] = mail[0]
        mail_data['sender_id'] = mail[1]
        mail_data['sender_mail'] = get_user_email(mail[1])
        mail_data['receiver_id'] = mail[2]
        mail_data['receiver_mail'] = get_user_email(mail[2])
        mail_data['mail_subject'] = mail[3]
        mail_data['mail_body'] = mail[4]
        mail_data['mail_date'] = remove_milli_seconds(mail[5])
        mail_data['mail_seen'] = mail[6]

        if check_attachment_exist(mail[0]):
            mail_data['mail_attachments'] = get_attachments(mail[0])

        single_outbox.append(mail_data)
        mail_data = {}

    # Multiple receivers mails extraction
    multiple_outbox = []
    select_distinct_mail_dates = """SELECT DISTINCT mail_date FROM mail WHERE multiple_receivers = ?
                                    AND sender_id = ? AND sender_trashed = ?;"""
    db_distinct_dates = sqlite_connection.execute(
        select_distinct_mail_dates, (1, sender_id, 0))
    distinct_mail_dates = []
    for mail_date in db_distinct_dates:
        distinct_mail_dates.append(mail_date[0])

    for mail_date in distinct_mail_dates:
        select_multi_receivers_mail_query = """SELECT * FROM mail WHERE multiple_receivers = ?
                                               AND mail_date = ? AND sender_trashed = 0 AND sender_id = ?;"""
        db_mail_output = sqlite_connection.execute(
            select_multi_receivers_mail_query, (1, mail_date, get_user_id(session["email"])))
        mail_data = {}
        receivers_mails = []
        for mail in db_mail_output:
            mail_data["mail_id"] = mail[0]
            mail_data["sender_id"] = mail[1]
            mail_data["receiver_mail"] = "Multiple Receivers"
            mail_data["sender_mail"] = get_user_email(mail[1])
            receivers_mails.append(get_user_email(mail[2]))
            mail_data["mail_subject"] = mail[3]
            mail_data["mail_body"] = mail[4]
            mail_data["mail_date"] = remove_milli_seconds(mail[5])
            mail_data["mail_seen"] = mail[6]
        mail_data["receivers_mails"] = receivers_mails
        multiple_outbox.append(mail_data)
        mail_data = {}
    outbox = multiple_outbox + single_outbox
    outbox = sort_mails(outbox)
    sqlite_connection.close()
    return outbox


def return_inbox(user_id):
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    get_inbox_query = """SELECT * FROM mail WHERE receiver_id = ?  AND receiver_trashed = ? ORDER BY mail_id DESC;"""
    get_inbox_query_data = (user_id, 0)
    user_inbox = sqlite_connection.execute(
        get_inbox_query, get_inbox_query_data)
    mail_data = {}
    inbox = []
    for mail in user_inbox:
        mail_data['mail_id'] = mail[0]
        mail_data['sender_id'] = mail[1]
        mail_data['sender_mail'] = get_user_email(mail[1])
        mail_data['receiver_id'] = mail[2]
        mail_data['receiver_mail'] = get_user_email(mail[2])
        mail_data['mail_subject'] = mail[3]
        mail_data['mail_body'] = mail[4]
        mail_data['mail_date'] = remove_milli_seconds(mail[5])
        mail_data['mail_seen'] = mail[6]
        inbox.append(mail_data)
        mail_data = {}
    sqlite_connection.close()
    return inbox


def sort_mails_by_date(all_mails):
    date_formate = "%Y-%m-%d %H:%M:%S"
    counter = 0
    while(counter < len(all_mails)):
        i = 0
        while(i < len(all_mails)-1):
            if(datetime.strptime(all_mails[i]["mail_date"], date_formate) < datetime.strptime(all_mails[i+1]["mail_date"], date_formate)):
                temp = all_mails[i]
                all_mails[i] = all_mails[i+1]
                all_mails[i+1] = temp
            i += 1
        counter += 1
    return all_mails


user_mail_bp = Blueprint('user_mail_bp', __name__,
                         template_folder='templates', static_folder='static/user_mail')


@user_mail_bp.route('/compose-mail')
def compose_email():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    return render_template('User_Mail/composeEmail.html', max_length=current_app.config["MAX_CONTENT_LENGTH"], userName=session['email'], user_mail=session["email"])


@user_mail_bp.route('/compose-mail/<user_mail>')
def compose_to_email(user_mail):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    user = [user_mail]
    return render_template('User_Mail/composeEmail.html', max_length=current_app.config["MAX_CONTENT_LENGTH"], userName=session['email'], to=user, user_mail=session["email"])


@user_mail_bp.route("/compose-mail/multiple-users", methods=["POST"])
def send_multi_users():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    allReceiversMails = json.loads(request.form["allMail"])
    if(len(allReceiversMails) == 1):
        return redirect(url_for("user_mail_bp.compose_to_email", user_mail=allReceiversMails[0]))
    return render_template("User_Mail/composeEmail.html", userName=session['email'], to=allReceiversMails, max_length=current_app.config["MAX_CONTENT_LENGTH"])


@user_mail_bp.route('/sending-mail', methods=['POST', 'GET'])
def sending_email():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sender_mail = session['email']
    receiver_mail = request.form['recievers']
    all_receivers = receiver_mail.split(" ")
    mail_subject = request.form['subject']
    mail_body = request.form['mailInfo'].strip()
    mail_date = datetime.now()

    sender_id = get_user_id(session['email'])
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    insert_mail_query = """INSERT INTO mail (sender_id, receiver_id, mail_subject, mail_body, mail_date, multiple_receivers)
                            VALUES(?, ?, ?, ?, ?, ?);"""
    multiple_receivers = 1
    if len(all_receivers) == 1:
        multiple_receivers = 0
    for receiver in all_receivers:
        insert_mail_query_data = (sender_id, get_user_id(
            receiver), mail_subject, mail_body, mail_date, multiple_receivers)
        sqlite_connection.execute(insert_mail_query, insert_mail_query_data)

    uploaded_files = request.files.getlist("user_files")
    if check_files_numbers(uploaded_files):
        if check_file_extension(uploaded_files) == False:
            flash('Not Allowed Extension', "danger")
            return redirect(url_for('user_mail_bp.compose_email'))

        os.makedirs(current_app.config['USER_ATTACHMENTS'], exist_ok=True)
        for user_file in uploaded_files:
            file_name = secure_filename(user_file.filename)
            user_file.save(os.path.join(
                current_app.config['USER_ATTACHMENTS'], file_name))

            save_attachment_query = """INSERT INTO attachment(mail_id, attachment_file)
                                       VALUES(?, ?);"""
            sqlite_select_query = """SELECT mail_id FROM mail WHERE sender_id = ? AND mail_date = ?;"""
            sqlite_select_query_data = (sender_id, mail_date)
            mail_ids = sqlite_connection.execute(
                sqlite_select_query, sqlite_select_query_data)
            for mail_id in mail_ids:
                sqlite_connection.execute(
                    save_attachment_query, (mail_id[0], user_file.filename))

    sqlite_connection.commit()
    sqlite_connection.close()

    return redirect(url_for('user_mail_bp.compose_email'))


@user_mail_bp.route('/All-Users/pick-multiple-receivers')
def add_multiple_receivers():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    return redirect(url_for("user_profile_bp.view_all_users"))


@user_mail_bp.route("/outbox")
def see_outbox():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    outbox = return_outbox(get_user_id(session["email"]))
    return render_template("User_Mail/outbox.html", outbox_mails=outbox, user_mail=session["email"])


@user_mail_bp.route("/inbox")
def see_inbox():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    inbox = return_inbox(get_user_id(session["email"]))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")
    select_name = "SELECT user_name FROM user WHERE user_email = ?;"
    db_user_name = sqlite_connection.execute(select_name, (session["email"],))
    user_name = ""
    for user in db_user_name:
        user_name = user[0]
    sqlite_connection.close()
    return render_template("User_Mail/inbox.html", inbox_mails=inbox, user_mail=session["email"], user_name=user_name)


@user_mail_bp.route("/unseen/inbox/<user_mail>")
def unseen_inbox(user_mail):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")
    select_unseen_mail = """SELECT mail_id FROM mail WHERE receiver_id = ? AND mail_seen = ? AND receiver_trashed = ?;"""
    values = (get_user_id(user_mail), 0, 0)
    db_unseen_mails = sqlite_connection.execute(select_unseen_mail, values)
    counter = 0
    for mail in db_unseen_mails:
        counter += 1
    sqlite_connection.close()
    return jsonify({"unseen_mails": counter})


@user_mail_bp.route("/view-mail/<mail_id>")
def view_mail(mail_id):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    select_mail_query = """SELECT sender_id, mail_subject, mail_body, mail_date, mail_id FROM mail WHERE mail_id = ?;"""
    mail_record = sqlite_connection.execute(select_mail_query, (mail_id,))
    mail_data = {}
    for data in mail_record:
        mail_data['sender_mail'] = get_user_email(data[0])
        mail_data['mail_subject'] = data[1]
        mail_data['mail_body'] = data[2]
        mail_data['mail_date'] = remove_milli_seconds(data[3])
        mail_data['mail_id'] = data[4]

    if check_attachment_exist(mail_id):

        select_attachment_query = """SELECT attachment_file FROM attachment WHERE mail_id = ?;"""
        attach_record = sqlite_connection.execute(
            select_attachment_query, (mail_id,))
        attachments = []
        for file in attach_record:
            attachments.append(file[0])
        mail_data['attachments'] = attachments

    update_query = """UPDATE mail SET mail_seen = ? WHERE mail_id = ?;"""
    update_query_data = (1, mail_id)
    sqlite_connection.execute(update_query, update_query_data)
    sqlite_connection.commit()
    sqlite_connection.close()
    return render_template('User_Mail/view_mail.html', mail=mail_data, user_mail=session["email"])


@user_mail_bp.route("/view-mail/mail-body/<mail_id>")
def get_mail_body(mail_id):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")
    select_mail_query = "SELECT mail_body FROM mail WHERE mail_id = ?;"
    db_output = sqlite_connection.execute(select_mail_query, (mail_id,))
    mail_body = ""
    for mail in db_output:
        mail_body = mail[0]
    sqlite_connection.close()
    return jsonify(mail_body)


@user_mail_bp.route("/download-file/<file_name>")
def download_file(file_name):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    try:
        return send_from_directory(current_app.config['USER_ATTACHMENTS'], filename=secure_filename(file_name), as_attachment=True)

    except FileNotFoundError:
        abort(404)


@user_mail_bp.route("/view-file/<file_name>")
def view_file(file_name):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    try:
        return send_from_directory(current_app.config['USER_ATTACHMENTS'], filename=secure_filename(file_name), as_attachment=False)
    except FileNotFoundError:
        abort(404)


@user_mail_bp.route("/all-mail")
def see_all_mail():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    inbox = return_inbox(get_user_id(session["email"]))
    outbox = return_outbox(get_user_id(session["email"]))
    all_mail = sort_mails(inbox + outbox)
    return render_template("User_Mail/view_all_mail.html", all_mail=all_mail, user_email=session["email"])


@user_mail_bp.route("/trash/inbox/<mail_id>")
def inbox_to_trash(mail_id):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")
    update_query = """UPDATE mail SET receiver_trashed = ? WHERE mail_id = ?;"""
    sqlite_connection.execute(update_query, (1, mail_id))
    sqlite_connection.commit()
    sqlite_connection.close()
    return redirect(url_for("user_mail_bp.see_inbox"))


@user_mail_bp.route("/trash/view/all-mail")
def trash():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")
    user_id = get_user_id(session["email"])

    select_inbox_trash = """SELECT mail_id, sender_id, mail_subject, mail_date FROM mail WHERE
                             receiver_id = ? AND receiver_trashed = ?;"""
    db_inbox_trash = sqlite_connection.execute(
        select_inbox_trash, (user_id, 1))
    mail_data = {}
    inbox_trash = []
    for mail in db_inbox_trash:
        mail_data["mail_id"] = mail[0]
        mail_data["sender_mail"] = get_user_email(mail[1])
        mail_data["mail_subject"] = mail[2]
        mail_data["mail_date"] = remove_milli_seconds(mail[3])
        mail_data["mail_identity"] = True
        mail_data["outbox_status"] = False
        inbox_trash.append(mail_data)
        mail_data = {}

    select_outbox_single_trash = """SELECT mail_id, sender_id, mail_subject, mail_date FROM mail WHERE
                                    sender_id = ? AND sender_trashed = ? AND multiple_receivers = ?;"""
    db_outbox_single_trash = sqlite_connection.execute(
        select_outbox_single_trash, (user_id, 1, 0))
    outbox_single_trash = []
    for mail in db_outbox_single_trash:
        mail_data["mail_id"] = mail[0]
        mail_data["sender_mail"] = get_user_email(mail[1])
        mail_data["mail_subject"] = mail[2]
        mail_data["mail_date"] = remove_milli_seconds(mail[3])
        mail_data["mail_identity"] = False
        mail_data["outbox_status"] = True
        outbox_single_trash.append(mail_data)
        mail_data = {}

    select_distinct_mail_dates = """SELECT DISTINCT mail_date FROM mail WHERE sender_id = ? AND sender_trashed = ?
                                    AND multiple_receivers = ?;"""
    db_distinct_dates = sqlite_connection.execute(
        select_distinct_mail_dates, (user_id, 1, 1))

    outbox_multiple_trash = []
    for mail_date in db_distinct_dates:
        select_multiple_trash_mail_query = """SELECT mail_id, sender_id, mail_subject, mail_date FROM mail
                                              WHERE sender_id = ? AND sender_trashed = ? AND multiple_receivers = ?
                                              AND mail_date = ?;"""
        db_multiple_trash_mail = sqlite_connection.execute(
            select_multiple_trash_mail_query, (user_id, 1, 1, mail_date[0]))
        for mail in db_multiple_trash_mail:
            mail_data["mail_id"] = mail[0]
            mail_data["sender_mail"] = "Multiple Receivers"
            mail_data["mail_subject"] = mail[2]
            mail_data["mail_date"] = remove_milli_seconds(mail[3])
            mail_data["mail_identity"] = False
            mail_data["outbox_status"] = True + True
            outbox_multiple_trash.append(mail_data)
            mail_data = {}
            break

    all_mail = sort_mails_by_date(
        inbox_trash + outbox_single_trash + outbox_multiple_trash)
    sqlite_connection.close()
    return render_template("User_Mail/view_trash.html", all_mail=all_mail, user_mail=session["email"])


@user_mail_bp.route("/trash/outbox/<mail_id>")
def outbox_to_trash(mail_id):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")

    check_query = """SELECT multiple_receivers FROM mail WHERE mail_id = ?;"""
    db_check_result = sqlite_connection.execute(check_query, (mail_id,))
    check_multiple = False
    for check in db_check_result:
        check_multiple = check[0]
        break
    if check_multiple:
        select_mail_date = """SELECT mail_date FROM mail WHERE mail_id = ?;"""
        db_mail_date = sqlite_connection.execute(select_mail_date, (mail_id,))
        mail_date = 0
        for date in db_mail_date:
            mail_date = date[0]
            break
        select_sender_all_mails = """SELECT mail_id FROM mail WHERE sender_id = ? AND mail_date = ?;"""
        db_no_of_mails = sqlite_connection.execute(
            select_sender_all_mails, (get_user_id(session["email"]), mail_date)).fetchall()
        update_mail_to_trash_query = """UPDATE mail SET sender_trashed = ? WHERE sender_id = ? AND mail_date = ?;"""
        for i in range(len(db_no_of_mails)):
            sqlite_connection.execute(
                update_mail_to_trash_query, (1, get_user_id(session["email"]), mail_date))
    else:
        update_mail_query = """UPDATE mail SET sender_trashed = ? WHERE mail_id = ?;"""
        sqlite_connection.execute(update_mail_query, (1, mail_id))
    sqlite_connection.commit()
    sqlite_connection.close()
    return redirect(url_for("user_mail_bp.see_outbox"))


@user_mail_bp.route("/trash/all-mail/<int:mail_id>/<int:trash_identity>")
def all_mail_to_trash(mail_id, trash_identity):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    update_query = ""

    if trash_identity == 1:
        update_query = """UPDATE mail SET receiver_trashed = ? WHERE mail_id = ?;"""
    else:
        update_query = """UPDATE mail SET sender_trashed = ? WHERE mail_id = ?;"""

    sqlite_connection.execute(update_query, (1, mail_id))
    sqlite_connection.commit()
    sqlite_connection.close()
    return redirect(url_for("user_mail_bp.see_all_mail"))


@user_mail_bp.route("/trash/inbox/recycle-mail/<int:mail_id>/<int:mail_identity>/<int:outbox_status>")
def recycle_trash(mail_id, mail_identity, outbox_status):
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    sqlite_connection = sqlite3.connect("MAIL_DB.db")

    if mail_identity:
        recycle_mail_query = """UPDATE mail SET receiver_trashed = ? WHERE mail_id = ?;"""
        sqlite_connection.execute(recycle_mail_query, (0, mail_id))
    else:
        if outbox_status == True:
            recycle_mail_query = """UPDATE mail SET sender_trashed = ? WHERE mail_id = ?;"""
            sqlite_connection.execute(recycle_mail_query, (0, mail_id))
        else:
            select_mail_date = """SELECT mail_date FROM mail WHERE mail_id = ?;"""
            db_mail_date = sqlite_connection.execute(
                select_mail_date, (mail_id,))
            mail_date = 0
            for date in db_mail_date:
                mail_date = date[0]
                break
            recycle_mails_query = """UPDATE mail SET sender_trashed = ? WHERE mail_date = ?;"""
            sqlite_connection.execute(recycle_mails_query, (0, mail_date))
    sqlite_connection.commit()
    sqlite_connection.close()
    return redirect(url_for("user_mail_bp.trash"))


@user_mail_bp.route("/validation/files", methods=["POST"])
def file_extensions_validation():
    if check_authentication() == False:
        return redirect(url_for('forms_bp.login_form_page'))
    file_extensions = json.loads(request.args.get("fileExtensions"))
    all_files = []
    file_data = {}
    for file in file_extensions:
        file_data["file_name"] = file
        if validate_file_extension(file) == False:
            file_data["valid"] = False
        else:
            file_data["valid"] = True
        all_files.append(file_data)
        file_data = {}
    return jsonify(all_files)
