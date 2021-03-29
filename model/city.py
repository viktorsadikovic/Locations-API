from app import db


class City(db.Model):
    number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)