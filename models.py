from app import db


class BicycleStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)  # OneToOne


class RepairStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    available = db.Column(db.Boolean, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)  # OneToOne


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parking_zone_id = db.Column(db.Integer, db.ForeignKey('parking_zone.id'), primary_key=True)  # ManyToOne
    available = db.Column(db.Boolean, nullable=False)


class ParkingZone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)  # OneToOne
    parking_spots = db.relationship('ParkingSpot', backref='parking_zone')


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)  # OneToOne
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)  # OneToOne
    country = db.Column(db.String(60), nullable=False)
    parking_zone = db.relationship('ParkingZone', backref='address', uselist=False)
    bicycle_store = db.relationship('BicycleStore', backref='address', uselist=False)
    repair_station = db.relationship('RepairStation', backref='address', uselist=False)


address_to_city = db.Table('address_to_city',
                           db.Column('address_id', db.Integer, db.ForeignKey('address.id')),
                           db.Column('city_postal_code', db.Integer, db.ForeignKey('city.postal_code')))


class City(db.Model):
    postal_code = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    addresses = db.relationship('Address', secondary=address_to_city, backref=db.backref('cities'))


class Street(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    address = db.relationship('Address', backref='street', uselist=False)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.relationship('Address', backref='location', uselist=False)
