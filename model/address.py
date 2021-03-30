from app import db

address_to_city = db.Table('address_to_city',
                           db.Column('address_id', db.Integer, db.ForeignKey('address.id')),
                           db.Column('city_postal_code', db.Integer, db.ForeignKey('city.postal_code'))
                           )


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)  # OneToOne
    # city_postal_code = db.Column(db.Integer)  # ManyToMany
    country = db.Column(db.String(60), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)  # OneToOne
    bicycle_store = db.relationship('BicycleStore', backref='address', uselist=False)
    repair_station = db.relationship('RepairStation', backref='address', uselist=False)
    parking_zone = db.relationship('ParkingZone', backref='address', uselist=False)
