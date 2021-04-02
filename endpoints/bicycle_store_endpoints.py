from app import db
from models import *
from utilities import validate_request, update_address


def parse_to_json(bicycle_store):
    return {
        'id': bicycle_store.id,
        'name': bicycle_store.name,
        'street_name': bicycle_store.address.street_name,
        'street_number': bicycle_store.address.street_number,
        'city_name': bicycle_store.address.city_name,
        'city_postal_code': bicycle_store.address.city_postal_code,
        'country': bicycle_store.address.country,
        'latitude': bicycle_store.address.location.latitude,
        'longitude': bicycle_store.address.location.longitude
    }


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
        response['message'] = f'The bicycle store with id {store_id} was successfully found'
        response['bicycle_store'] = parse_to_json(bicycle_store)

        return response, 200
    else:
        response['message'] = f'The bicycle store with id {store_id} does not exist'

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
            city_name, country = bicycle_store_body['city_name'], bicycle_store_body['country']
            address = Address(street_name=street_name, street_number=street_number,
                              city_name=city_name, city_postal_code=city_postal_code,
                              country=country)

            latitude, longitude = bicycle_store_body['latitude'], bicycle_store_body['longitude']
            location = Location(latitude=latitude, longitude=longitude, address=address)
            db.session.add(location)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)
            db.session.refresh(location)

        name = bicycle_store_body['name']

        if address.bicycle_store:
            response['message'] = "A bicycle store is already registered on that address"
            response['bicycle_store'] = parse_to_json(address.bicycle_store)

            return response, 400

        bicycle_store = BicycleStore(name=name, address=address)
        db.session.add(bicycle_store)
        db.session.commit()
        db.session.refresh(bicycle_store)

        response['message'] = 'The bicycle store was successfully added'
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
            bicycle_store = update_address(model=bicycle_store, request_body=bicycle_store_body)
            db.session.commit()

            response['message'] = f'The bicycle store with id {store_id} was successfully updated'
            response['bicycle_store'] = parse_to_json(bicycle_store)

            return response, 200
    else:
        response['message'] = f'The bicycle store with id {store_id} does not exist'

        return response, 400


def delete_bicycle_store(store_id):
    response = {'message': None}
    bicycle_store = db.session.query(BicycleStore).filter_by(id=store_id).first()

    if bicycle_store:
        db.session.delete(bicycle_store)
        db.session.commit()

        response['message'] = f'The bicycle store with id {store_id} was successfully deleted'

        return response, 200
    else:
        response['message'] = f'The bicycle store with id {store_id} does not exist'

        return response, 400
