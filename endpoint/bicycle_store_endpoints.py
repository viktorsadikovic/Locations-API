from app import db
from models import *
import json


def parse_to_json(bicycle_store):
    return {'id': bicycle_store.id,
            'name': bicycle_store.name,
            'street_name': bicycle_store.address.street_name,
            'street_number': bicycle_store.address.street_number,
            'city_name': bicycle_store.address.city_name,
            'city_postal_code': bicycle_store.address.city_postal_code,
            'country': bicycle_store.address.country,
            'latitude': bicycle_store.address.location.latitude,
            'longitude': bicycle_store.address.location.longitude
            }


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


def get_all_bicycle_stores():
    response = {'message': None, 'bicycle_stores': None}
    bicycle_stores = db.session.query(BicycleStore).all()

    response['message'] = "The bicycle stores were successfully found"
    response['bicycle_stores'] = [parse_to_json(store) for store in bicycle_stores]

    return response, 200


def get_single_bicycle_store(store_id):
    response = {'message': None, 'bicycle_store': None}
    bicycle_store = db.session.query(BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        response['message'] = f'Bicycle store with id {store_id} was successfully found'
        response['bicycle_store'] = parse_to_json(bicycle_store)
        return response, 200
    else:
        response['message'] = f'Bicycle store with id {store_id} does not exist'
        return response, 400


def add_bicycle_store(bicycle_store_body):
    response = {'message': None, 'bicycle_store': None}
    invalid_parameters = validate_request(bicycle_store_body)

    if len(invalid_parameters) != 0:
        response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))
        return response, 400
    else:
        street_name, street_number = bicycle_store_body['street_name'], bicycle_store_body['street_number']
        city_postal_code = bicycle_store_body['city_postal_code']

        address = db.session.query(Address) \
            .filter_by(street_name=street_name, street_number=street_number, city_postal_code=city_postal_code) \
            .first()

        if address is None:
            latitude, longitude = bicycle_store_body['latitude'], bicycle_store_body['longitude']
            location = Location(latitude=latitude, longitude=longitude)
            db.session.add(location)
            db.session.commit()
            db.session.refresh(location)

            city_name, country = bicycle_store_body['city_name'], bicycle_store_body['country']
            address = Address(street_name=street_name, street_number=street_number,
                              city_name=city_name, city_postal_code=city_postal_code,
                              country=country, location_id=location.id)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)

        name = bicycle_store_body['name']
        existing_bicycle_store = db.session.query(BicycleStore).filter_by(name=name, address_id=address.id).first()

        if existing_bicycle_store:
            response['message'] = "Bicycle Store Already Exists"
            response['bicycle_store'] = existing_bicycle_store
            return response, 400

        bicycle_store = BicycleStore(name=name, address_id=address.id)
        db.session.add(bicycle_store)
        db.session.commit()
        db.session.refresh(bicycle_store)

        response['message'] = 'The parking zone was successfully added'
        response['bicycle_store'] = parse_to_json(bicycle_store)
        return response, 200


def edit_bicycle_store(store_id, bicycle_store_body):
    response = {'message': None, 'bicycle_store': None}
    bicycle_store = db.session.query(BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        invalid_parameters = validate_request(bicycle_store_body)

        if len(invalid_parameters) != 0:
            response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))
            return response, 400
        else:
            bicycle_store.name = bicycle_store_body['name']
            bicycle_store.address.street_name = bicycle_store_body['street_name']
            bicycle_store.address.street_number = bicycle_store_body['street_number']
            bicycle_store.address.city_name = bicycle_store_body['city_name']
            bicycle_store.address.city_postal_code = bicycle_store_body['city_postal_code']
            bicycle_store.address.location.latitude = bicycle_store_body['latitude']
            bicycle_store.address.location.longitude = bicycle_store_body['longitude']
            bicycle_store.address.country = bicycle_store_body['country']
            db.session.commit()

            response['message'] = f'Bicycle store successfully changed'
            response['bicycle_store'] = parse_to_json(bicycle_store)
            return response, 200
    else:
        response['message'] = f'Bicycle store with id {store_id} does not exist'
        return response, 400


def delete_bicycle_store(store_id):
    response = {'message': None}
    bicycle_store = db.session.query(BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        db.session.delete(bicycle_store)
        db.session.commit()
        response['message'] = 'The bicycle store was successfully deleted'
        return response, 200
    else:
        response['message'] = f'Bicycle store with id {store_id} does not exist'
        return response, 400
