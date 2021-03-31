from app import db

from model.parking_spot import ParkingSpot


class ParkingZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)  # OneToOne
    parking_spots = db.relationship('ParkingSpot', backref='parking_zone')
