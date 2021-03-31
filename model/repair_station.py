from app import db


class RepairStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available = db.Column(db.Boolean, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)  # OneToOne
