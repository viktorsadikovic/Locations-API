from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested


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
    capacity = db.Column(db.Integer, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)  # OneToOne
    parking_spots = db.relationship('ParkingSpot', backref='parking_zone')


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street_name = db.Column(db.String(50), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(25), nullable=False)
    city_postal_code = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(60), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)  # OneToOne

    parking_zone = db.relationship('ParkingZone', backref='address', uselist=False)
    bicycle_store = db.relationship('BicycleStore', backref='address', uselist=False)
    repair_station = db.relationship('RepairStation', backref='address', uselist=False)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.relationship('Address', backref='location', uselist=False)


class LocationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        include_relationships = True
        load_instance = True


class AddressSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        include_relationships = True
        load_instance = True

    location = Nested(LocationSchema, many=False, exclude=("address",))


class BicycleStoreSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BicycleStore
        include_relationships = True
        load_instance = True

    address = Nested(AddressSchema, many=False, exclude=("parking_zone", "bicycle_store", "repair_station",))


class RepairStationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RepairStation
        include_relationships = True
        load_instance = True

    address = Nested(AddressSchema, many=False, exclude=("parking_zone", "bicycle_store", "repair_station",))


class ParkingZoneSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingZone
        include_relationships = True
        load_instance = True

    address = Nested(AddressSchema, many=False, exclude=("parking_zone", "bicycle_store", "repair_station",))


class ParkingSpotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ParkingSpot
        include_relationships = True
        load_instance = True

    parking_zone = Nested(ParkingZoneSchema, many=False, exclude=("parking_spots",))