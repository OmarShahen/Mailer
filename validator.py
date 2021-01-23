import sqlite3

def name_validator(user_name):
    non_name = "1234567890-=`!@#$%^&*()_+[]\{\}|\\/<>,.;:?"

    for i in user_name:
        for j in non_name:
            if i == j:
                return False
    return True
    
def check_user_email(user_mail):

    sqlite_connection = sqlite3.connect('MAIL_DB.db')
    search_mail_query = """SELECT user_name, user_email FROM user WHERE user_email = ?;"""
    search_mail_query_data = (user_mail,)
    users_data = sqlite_connection.execute(search_mail_query, search_mail_query_data).fetchall()
    sqlite_connection.close()

    if len(users_data) == 0:
        return False
    else:
        return True


def check_file_names(files):
    allowed_extensions = ['PDF', 'XLSX']
    for file in files:
        if "." not in file:
            print(f"This file has no dot ({file})")
            return False
        splitted_file = file.split(".")
        if splitted_file[1].upper() not in allowed_extensions:
            print(f"This extension is not allowed (.{splitted_file[1]})")
            return False
        print(f"This is a allowed extension({splitted_file[1]})") 
    return True
