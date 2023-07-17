from CustomAgentAI import db


class Product(db.Model):
    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.Text, nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    product_tech_contact = db.Column(db.Text, nullable=False)
    product_data = db.Column(db.Text, nullable=False)
    def __init__(self, product_name,product_description ,product_tech_contact,product_data):
        self.product_name=product_name
        self.product_description=product_description
        self.product_tech_contact=product_tech_contact
        self.product_data=product_data
    def __repr__(self):
        return f"{self.product_name}"


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_number = db.Column(db.Text, nullable=False)
    Sessions = db.relationship(
        "Session", backref="User", primaryjoin="User.id == Session.user_id"
    )
    def __init__(self,user_number):
        self.user_number=user_number

    def __repr__(self):
        return f"{self.user_number}"

class Session(db.Model):
    __tablename__ = "Session"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"))
    interactions = db.relationship(
        "Interaction", backref="Session", primaryjoin="Session.id == Interaction.session_id"
    )
    def __init__(self, session_id):
        self.session_id=session_id
    def __repr__(self):
        return f"{self.id}"


class Interaction(db.Model):
    __tablename__ = "Interaction"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interaction_person = db.Column(db.Text, nullable=False)
    interaction_data = db.Column(db.Text, nullable=False)    
    interaction_product = db.Column(db.Text, nullable=False)    
    session_id = db.Column(db.Integer, db.ForeignKey("Session.id"))
    def __init__(self, interaction_person,interaction_data,interaction_product=""):
        self.interaction_person=interaction_person
        self.interaction_data=interaction_data
        self.interaction_product=interaction_product
    def __repr__(self):
        return f"{self.id}"