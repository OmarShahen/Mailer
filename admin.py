from Person import person
class admin(person):

    def __init__(self,name,email,password,gender,dateOfBirth,city,country,contact):
        person.__init__(self,name,email,password,gender,dateOfBirth,city,country,contact)

