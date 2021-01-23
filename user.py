from Person import person
from datetime import datetime

class user(person):

    no_Of_Users = 0
    no_of_inbox = 0
    no_of_outbox = 0
    id_number = 11
    
    def __init__(self,name,email,password,gender,dateOfBirth,city,country,contact):
        person.__init__(self,name,email,password,gender,dateOfBirth,city,country,contact)
        self.active = True
        self.account_creaion_date = datetime.now()
        user.no_Of_Users += 1
        self.user_id = user.id_number
        user.id_number += 1
        self.appPassword = None
        self.inbox_mails = []
        self.outbox_mails = []
        self.trash_mails = []



    def get_active(self):
        return self.active
        
    def get_active_str(self):
        if self.active == True:
            return "online"
        else:
            return "offline"

    def set_active_online(self):
        self.active = True
    
    def set_active_offline(self):
        self.active = False
    
    def add_to_outbox(self, mail):
        user.no_of_outbox += 1
        mail['id'] = "01" + str(user.no_of_outbox)
        self.outbox_mails.append(mail)
    
    def get_all_outbox(self):
        return self.outbox_mails
    
    def add_inbox(self, mail):
        user.no_of_inbox += 1
        mail['id'] = "10" + str(user.no_of_inbox)
        self.inbox_mails.append(mail)
        
    def get_all_inbox(self):
        return self.inbox_mails
    def add_trash(self, mail):
        self.trash_mails.append(mail)
    def get_all_trash(self):
        return self.trash_mails

    def get_user_id(self):
        return self.user_id
    
    def get_account_creation_date(self):
        return self.account_creaion_date
    
        

