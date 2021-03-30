from app import db


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parking_zone_id = db.Column(db.Integer, db.ForeignKey('parking_zone.id'), primary_key=True)  # ManyToOne
    available = db.Column(db.Boolean, nullable=False)
