from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from models import *


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
