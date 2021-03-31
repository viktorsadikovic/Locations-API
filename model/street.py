from app import db

from model.address import Address


class Street(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    address = db.relationship('Address', backref='street', uselist=False)
