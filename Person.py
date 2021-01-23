class person:

    def __init__(self,name,email,password,gender,dateOfBirth,city,country,contact):

        self.name = name
        self.email = email
        self.password = password
        self.gender = gender
        self.dateOfBirth = dateOfBirth
        self.city = city
        self.country = country
        self.contact = contact
    
    def set_name(self,name):
        self.name = name
    def get_name(self):
        return self.name
    
    def set_email(self,email):
        self.email = email
    def get_email(self):
        return self.email
    
    def set_password(self,password):
        self.password = password
    def get_password(self):
        return self.password
        
    def set_gender(self,gender):
        self.gender = gender
    def get_gender(self):
        return self.gender
    
    def set_dateOfBirth(self,dateOfBirth):
        self.dateOfBirth = dateOfBirth
    def get_dateOfBirth(self):
        return self.dateOfBirth
    
    def set_city(self,city):
        self.city = city
    def get_city(self):
        return self.city
    
    def set_country(self,country):
        self.country = country
    def get_country(self):
        return self.country

    def set_contact(self,contact):
        self.contact = contact
    def get_contact(self):
        return self.contact
    
        
    
    def __str__(self):
        return self.name +" "+ self.password +" "+ self.email +" "+ self.gender +" "+ self.dateOfBirth +" "+ self.city +" "+ self.country +" "+ self.contact

    
