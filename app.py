import connexion
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
from flask import request, abort
from consul_functions import *

JWT_SECRET = 'MY JWT SECRET'

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def validate_request(request_body):
    invalid_parameters = []

    for key in request_body.keys():
        value = request_body[key]

        if value is None:
            invalid_parameters.append(key)
        else:
            if ((type(value) is str) and not (value.strip())) or ((type(value) is int) and (value <= 0)):
                invalid_parameters.append(key)

    return tuple(invalid_parameters)


def update_address(model, request_body):
    model.address.street_name = request_body['street_name']
    model.address.street_number = request_body['street_number']
    model.address.city_name = request_body['city_name']
    model.address.city_postal_code = request_body['city_postal_code']
    model.address.country = request_body['country']
    model.address.location.latitude = request_body['latitude']
    model.address.location.longitude = request_body['longitude']

    return model


def has_role(arg):
    def has_role_inner(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                headers = request.headers
                if 'AUTHORIZATION' in headers:
                    token = headers['AUTHORIZATION'].split(' ')[1]
                    decoded_token = decode_token(token)
                    for role in arg:
                        if role in decoded_token['roles']:
                            return fn(*args, **kwargs)
                    abort(401)
                return fn(*args, **kwargs)
            except Exception as e:
                abort(401)

        return decorated_view

    return has_role_inner


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])


@has_role(['locations_admin', 'shipping'])
def get_all_bicycle_stores():
    response = {'message': None, 'bicycle_stores': None}
    bicycle_stores = db.session.query(models.BicycleStore).all()

    response['message'] = "The bicycle stores were successfully found"
    response['bicycle_stores'] = [bicycle_store_schema.dump(store) for store in bicycle_stores]

    return response, 200


@has_role(['locations_admin', 'shipping'])
def get_single_bicycle_store(store_id):
    response = {'message': None, 'bicycle_store': None}
    bicycle_store = db.session.query(models.BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        response['message'] = f'The bicycle store with id {store_id} was successfully found'
        response['bicycle_store'] = bicycle_store_schema.dump(bicycle_store)

        return response, 200
    else:
        response['message'] = f'The bicycle store with id {store_id} does not exist'

        return response, 400


@has_role(['locations_admin'])
def add_bicycle_store(bicycle_store_body):
    response = {'message': None, 'bicycle_store': None}
    invalid_parameters = validate_request(bicycle_store_body)

    if len(invalid_parameters) != 0:
        response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

        return response, 400
    else:
        street_name, street_number = bicycle_store_body['street_name'], bicycle_store_body['street_number']
        city_postal_code = bicycle_store_body['city_postal_code']

        address = db.session.query(models.Address) \
            .filter_by(street_name=street_name, street_number=street_number, city_postal_code=city_postal_code) \
            .first()

        if address is None:
            city_name, country = bicycle_store_body['city_name'], bicycle_store_body['country']
            address = models.Address(street_name=street_name, street_number=street_number,
                                     city_name=city_name, city_postal_code=city_postal_code,
                                     country=country)

            latitude, longitude = bicycle_store_body['latitude'], bicycle_store_body['longitude']
            location = models.Location(latitude=latitude, longitude=longitude, address=address)

            db.session.add(location)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)
            db.session.refresh(location)

        name = bicycle_store_body['name']

        if address.bicycle_store:
            response['message'] = "A bicycle store is already registered on that address"
            # response['bicycle_store'] = bicycle_store_schema.dump(address.bicycle_store)

            return response, 409

        bicycle_store = models.BicycleStore(name=name, address=address)
        db.session.add(bicycle_store)
        db.session.commit()
        db.session.refresh(bicycle_store)

        response['message'] = 'The bicycle store was successfully added'
        response['bicycle_store'] = bicycle_store_schema.dump(bicycle_store)

        return response, 200


@has_role(['locations_admin'])
def edit_bicycle_store(store_id, bicycle_store_body):
    response = {'message': None, 'bicycle_store': None}
    bicycle_store = db.session.query(models.BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        invalid_parameters = validate_request(bicycle_store_body)

        if len(invalid_parameters) != 0:
            response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

            return response, 400
        else:
            bicycle_store.name = bicycle_store_body['name']
            bicycle_store = update_address(model=bicycle_store, request_body=bicycle_store_body)
            db.session.commit()

            response['message'] = f'The bicycle store with id {store_id} was successfully updated'
            response['bicycle_store'] = bicycle_store_schema.dump(bicycle_store)

            return response, 200
    else:
        response['message'] = f'The bicycle store with id {store_id} does not exist'

        return response, 400


@has_role(['locations_admin'])
def delete_bicycle_store(store_id):
    response = {'message': None}
    bicycle_store = db.session.query(models.BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        db.session.delete(bicycle_store)
        db.session.commit()

        response['message'] = f'The bicycle store with id {store_id} was successfully deleted'

        return response, 200
    else:
        response['message'] = f'The bicycle store with id {store_id} does not exist'

        return response, 400


@has_role(['locations_admin', 'reserve'])
def get_all_free_parking_spots():
    response = {'message': None, 'parking_spots': None}
    free_parking_spots = db.session.query(models.ParkingSpot).filter_by(available=True).all()

    response['message'] = 'The parking spots were successfully found'
    response['parking_spots'] = [parking_spot_schema.dump(parking_spot) for parking_spot in free_parking_spots]

    return response, 200


@has_role(['locations_admin', 'reserve'])
def get_free_parking_spots_per_zone(parking_zone_id):
    response = {'message': None, 'parking_spots': None}
    parking_zone = db.session.query(models.ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        free_parking_spots = [parking_spot for parking_spot in parking_zone.parking_spots if parking_spot.available]

        response['message'] = 'The parking spots were successfully found'
        response['parking_spots'] = [parking_spot_schema.dump(parking_spot) for parking_spot in free_parking_spots]

        return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin', 'reserve'])
def reserve_parking_spot(parking_zone_id, parking_spot_id):
    response = {'message': None, 'parking_spot': None}
    parking_spot = db.session.query(models.ParkingSpot).filter_by(id=parking_spot_id,
                                                                  parking_zone_id=parking_zone_id).first()

    if parking_spot:
        parking_spot.available = False
        db.session.commit()
        db.session.refresh(parking_spot)

        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} was successfully reserved'
        response['parking_spot'] = parking_spot_schema.dump(parking_spot)

        return response, 200
    else:
        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin', 'reserve'])
def free_parking_spot(parking_zone_id, parking_spot_id):
    response = {'message': None, 'parking_spot': None}
    parking_spot = db.session.query(models.ParkingSpot).filter_by(id=parking_spot_id,
                                                                  parking_zone_id=parking_zone_id).first()

    if parking_spot:
        parking_spot.available = True
        db.session.commit()
        db.session.refresh(parking_spot)

        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} was successfully freed'
        response['parking_spot'] = parking_spot_schema.dump(parking_spot)

        return response, 200
    else:
        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin'])
def add_parking_spot(parking_zone_id):
    response = {'message': None, 'parking_spot': None}
    parking_zone = db.session.query(models.ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        num_parking_spots = len(parking_zone.parking_spots)

        if num_parking_spots < parking_zone.capacity:
            parking_spot = models.ParkingSpot(id=(num_parking_spots + 1), parking_zone=parking_zone, available=True)
            db.session.add(parking_spot)
            db.session.commit()
            db.session.refresh(parking_spot)

            response['message'] = f'The parking spot with id {parking_spot.id} and ' \
                                  f'parking zone id {parking_zone_id} was successfully added'
            response['parking_spot'] = parking_spot_schema.dump(parking_spot)

            return response, 200
        else:
            response['message'] = f'The parking zone with id {parking_zone_id} is out of capacity'

            return response, 400
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin'])
def delete_parking_spot(parking_zone_id, parking_spot_id):
    response = {'message': None}
    parking_spot = db.session.query(models.ParkingSpot).filter_by(id=parking_spot_id,
                                                                  parking_zone_id=parking_zone_id).first()

    if parking_spot:
        db.session.delete(parking_spot)
        db.session.commit()

        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} was successfully deleted'

        return response, 200
    else:
        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin', 'reserve'])
def get_all_parking_zones():
    response = {'message': None, 'parking_zones': None}
    parking_zones = db.session.query(models.ParkingZone).all()

    response['message'] = 'The parking zones were successfully found'
    response['parking_zones'] = [parking_zone_schema.dump(parking_zone) for parking_zone in parking_zones]

    return response, 200


@has_role(['locations_admin', 'reserve'])
def get_parking_zones_with_free_space():
    response = {'message': None, 'parking_zones': None}
    all_parking_zones = db.session.query(models.ParkingZone).all()
    free_parking_zones = []

    for parking_zone in all_parking_zones:
        available_spots = [parking_spot for parking_spot in parking_zone.parking_spots if parking_spot.available]

        if len(available_spots) > 0:
            free_parking_zones.append(parking_zone)

    response['message'] = 'The parking zones were successfully found'
    response['parking_zones'] = [parking_zone_schema.dump(parking_zone) for parking_zone in free_parking_zones]

    return response, 200


@has_role(['locations_admin', 'reserve'])
def get_single_parking_zone(parking_zone_id):
    response = {'message': None, 'parking_zone': None}
    parking_zone = db.session.query(models.ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        response['message'] = f'The parking zone with id {parking_zone_id} was successfully found'
        response['parking_zone'] = parking_zone_schema.dump(parking_zone)

        return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin'])
def add_parking_zone(parking_zone_body):
    response = {'message': None, 'parking_zone': None}
    invalid_parameters = validate_request(parking_zone_body)

    if len(invalid_parameters) != 0:
        response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

        return response, 400
    else:
        street_name, street_number = parking_zone_body['street_name'], parking_zone_body['street_number']
        city_postal_code = parking_zone_body['city_postal_code']

        address = db.session.query(models.Address) \
            .filter_by(street_name=street_name, street_number=street_number, city_postal_code=city_postal_code) \
            .first()

        if address is None:
            city_name, country = parking_zone_body['city_name'], parking_zone_body['country']
            address = models.Address(street_name=street_name, street_number=street_number,
                                     city_name=city_name, city_postal_code=city_postal_code,
                                     country=country)

            latitude, longitude = parking_zone_body['latitude'], parking_zone_body['longitude']
            location = models.Location(latitude=latitude, longitude=longitude, address=address)

            db.session.add(location)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)
            db.session.refresh(location)

        if address.parking_zone:
            response['message'] = "A parking zone is already registered on that address"
            response['parking_zone'] = parking_zone_schema.dump(address.parking_zone)

            return response, 409
        else:
            capacity = parking_zone_body['capacity']
            parking_zone = models.ParkingZone(capacity=capacity, address=address)
            db.session.add(parking_zone)
            db.session.commit()
            db.session.refresh(parking_zone)

            response['message'] = 'The parking zone was successfully added'
            response['parking_zone'] = parking_zone_schema.dump(parking_zone)

            return response, 200


@has_role(['locations_admin'])
def edit_parking_zone(parking_zone_id, parking_zone_body):
    response = {'message': None, 'parking_zone': None}
    parking_zone = db.session.query(models.ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        invalid_parameters = validate_request(parking_zone_body)

        if len(invalid_parameters) != 0:
            response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

            return response, 400
        else:
            parking_zone.capacity = parking_zone_body['capacity']
            parking_zone = update_address(model=parking_zone, request_body=parking_zone_body)
            db.session.commit()

            response['message'] = f'The parking zone with id {parking_zone_id} was successfully updated'
            response['parking_zone'] = parking_zone_schema.dump(parking_zone)

            return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin'])
def delete_parking_zone(parking_zone_id):
    response = {'message': None}
    parking_zone = db.session.query(models.ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        db.session.delete(parking_zone)
        db.session.commit()

        response['message'] = f'The parking zone with id {parking_zone_id} was successfully deleted'

        return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


@has_role(['locations_admin', 'reserve'])
def get_all_repair_stations():
    response = {'message': None, 'repair_stations': None}
    repair_stations = db.session.query(models.RepairStation).all()

    response['message'] = 'The repair stations were successfully found'
    response['repair_stations'] = [repair_station_schema.dump(repair_station) for repair_station in repair_stations]

    return response, 200


@has_role(['locations_admin', 'reserve'])
def get_available_repair_stations():
    response = {'message': None, 'repair_stations': None}
    all_repair_stations = db.session.query(models.RepairStation).all()
    available_repair_stations = [repair_station for repair_station in all_repair_stations if repair_station.available]

    response['message'] = 'The available repair stations were successfully found'
    response['repair_stations'] = [repair_station_schema.dump(repair_station) for repair_station in
                                   available_repair_stations]

    return response, 200


@has_role(['locations_admin', 'reserve'])
def get_single_repair_station(repair_station_id):
    response = {'message': None, 'repair_station': None}
    repair_station = db.session.query(models.RepairStation).filter_by(id=repair_station_id).first()

    if repair_station:
        response['message'] = f'The repair station with id {repair_station_id} was successfully found'
        response['repair_station'] = repair_station_schema.dump(repair_station)

        return response, 200
    else:
        response['message'] = f'The repair station with id {repair_station_id} does not exist'

        return response, 404


@has_role(['locations_admin'])
def add_repair_station(repair_station_body):
    response = {'message': None, 'repair_station': None}
    invalid_parameters = validate_request(repair_station_body)

    if len(invalid_parameters) != 0:
        response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

        return response, 400
    else:
        street_name, street_number = repair_station_body['street_name'], repair_station_body['street_number']
        city_postal_code = repair_station_body['city_postal_code']

        address = db.session.query(models.Address) \
            .filter_by(street_name=street_name, street_number=street_number, city_postal_code=city_postal_code) \
            .first()

        if address is None:
            city_name, country = repair_station_body['city_name'], repair_station_body['country']
            address = models.Address(street_name=street_name, street_number=street_number,
                                     city_name=city_name, city_postal_code=city_postal_code,
                                     country=country)

            latitude, longitude = repair_station_body['latitude'], repair_station_body['longitude']
            location = models.Location(latitude=latitude, longitude=longitude, address=address)

            db.session.add(location)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)
            db.session.refresh(location)

        if address.repair_station:
            response['message'] = 'A repair station is already registered on that address'
            response['repair_station'] = repair_station_schema.dump(address.repair_station)

            return response, 409
        else:
            available = repair_station_body['available']
            repair_station = models.RepairStation(available=available, address=address)
            db.session.add(repair_station)
            db.session.commit()
            db.session.refresh(repair_station)

            response['message'] = 'The repair station was successfully added'
            response['repair_station'] = repair_station_schema.dump(repair_station)

            return response, 200


@has_role(['locations_admin'])
def edit_repair_station(repair_station_id, repair_station_body):
    response = {'message': None, 'repair_station': None}
    repair_station = db.session.query(models.RepairStation).filter_by(id=repair_station_id).first()

    if repair_station:
        invalid_parameters = validate_request(repair_station_body)

        if len(invalid_parameters) != 0:
            response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

            return response, 400
        else:
            repair_station.available = repair_station_body['available']
            repair_station = update_address(model=repair_station, request_body=repair_station_body)
            db.session.commit()

            response['message'] = f'The repair station with id {repair_station_id} was successfully updated'
            response['repair_station'] = repair_station_schema.dump(repair_station)

            return response, 200
    else:
        response['message'] = f'The repair station with id {repair_station_id} does not exist'

        return response, 404


@has_role(['locations_admin'])
def delete_repair_station(repair_station_id):
    response = {'message': None}
    repair_station = db.session.query(models.RepairStation).filter_by(id=repair_station_id).first()

    if repair_station:
        db.session.delete(repair_station)
        db.session.commit()

        response['message'] = f'The repair station with id {repair_station_id} was successfully deleted'

        return response, 200

    else:
        response['message'] = f'The repair station with id {repair_station_id} does not exist'

        return response, 404


connexion_app.add_api("api.yml")

import models

bicycle_store_schema = models.BicycleStoreSchema()
parking_spot_schema = models.ParkingSpotSchema()
parking_zone_schema = models.ParkingZoneSchema()
repair_station_schema = models.RepairStationSchema()

register_to_consul()

if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
