from app import db
from model.address import address_to_city


class City(db.Model):
    postal_code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    addresses = db.relationship('Address', secondary=address_to_city, backref=db.backref('cities', lazy='dynamic'))
