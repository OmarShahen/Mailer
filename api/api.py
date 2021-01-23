from flask import Flask, request, jsonify, session, Blueprint, redirect, url_for
import sqlite3

users_api_bp = Blueprint('users_api_bp', __name__)


@users_api_bp.route('/users', methods = ['GET'])
def get_all_users():
    sqlite_connection = sqlite3.connect('Mail_DB.db')
    select_all_users_query = """SELECT user_id, user_name, user_email, user_gender, user_date_of_birth, user_city,
                                user_country, user_contact, user_account_creation_date, user_active FROM user;"""
    users_data = sqlite_connection.execute(select_all_users_query)
    all_users = []
    user_record = {}
    for data in users_data:

        user_record['ID'] = data[0]
        user_record['NAME'] = data[1]
        user_record['EMAIL'] = data[2]
        user_record['GENDER'] = data[3]
        user_record['DATE_OF_BIRTH'] = data[4]
        user_record['CITY'] = data[5]
        user_record['COUNTRY'] = data[6]
        user_record['CONTACT'] = data[7]
        user_record['ACCOUNT_CREATION_DATE'] = data[8]
        user_record['ACTIVE'] = data[9]
        all_users.append(user_record)
        user_record = {}
    return jsonify(all_users)

@users_api_bp.route('/users/<int:id>', methods = ['GET', 'DELETE'])
def get_user(id):
    sqlite_connection = sqlite3.connect('Mail_DB.db')
    if request.method == 'GET':

        select_user_query = """SELECT user_id, user_name, user_email, user_gender, user_date_of_birth, user_city,
                           user_country, user_contact, user_account_creation_date, user_active FROM user WHERE user_id = ?;"""
        user_data = sqlite_connection.execute(select_user_query, (id,))
        user_record = {}
        for data in user_data:
            user_record['ID'] = data[0]
            user_record['NAME'] = data[1]
            user_record['EMAIL'] = data[2]
            user_record['GENDER'] = data[3]
            user_record['DATE_OF_BIRTH'] = data[4]
            user_record['CITY'] = data[5]
            user_record['COUNTRY'] = data[6]
            user_record['CONTACT'] = data[7]
            user_record['ACCOUNT_CREATION_DATE'] = data[8]
            user_record['ACTIVE'] = data[9]
        sqlite_connection.close()
        return jsonify(user_record)

    elif request.method == 'DELETE':
        user_delete_query = """DELETE FROM USER WHERE ID = ?;"""
        sqlite_connection.execute(user_delete_query, (id,))
        sqlite_connection.commit()
        sqlite_connection.close()
        check_message = {"response": "Deleted Successfully"}
        return jsonify(check_message)


@users_api_bp.route('/users/new', methods = ['GET'])
def get_register_form():
    return redirect(url_for('forms_bp.registerForm'))

#@users_api_bp.route('/users/edit', methods = ['GET'])
#def get_edit_form():
 #   return redirect(url_for('user_profile_bp.edit_profile_form'))

 