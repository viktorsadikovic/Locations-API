from app import db
from models import ParkingZone, Address, Location
from utilities import validate_request, update_address


def parse_to_json(parking_zone):
    return {
        'id': parking_zone.id,
        'capacity': parking_zone.capacity,
        'street_name': parking_zone.address.street_name,
        'street_number': parking_zone.address.street_number,
        'city_name': parking_zone.address.city_name,
        'city_postal_code': parking_zone.address.city_postal_code,
        'country': parking_zone.address.country,
        'latitude': parking_zone.address.location.latitude,
        'longitude': parking_zone.address.location.longitude
    }


def get_all_parking_zones():
    response = {'message': None, 'parking_zones': None}
    parking_zones = db.session.query(ParkingZone).all()

    response['message'] = 'The parking zones were successfully found'
    response['parking_zones'] = [parse_to_json(parking_zone) for parking_zone in parking_zones]

    return response, 200


def get_parking_zones_with_free_space():
    response = {'message': None, 'parking_zones': None}
    all_parking_zones = db.session.query(ParkingZone).all()
    free_parking_zones = []

    for parking_zone in all_parking_zones:
        available_spots = [parking_spot for parking_spot in parking_zone.parking_spots if parking_spot.available]

        if len(available_spots) > 0:
            free_parking_zones.append(parking_zone)

    response['message'] = 'The parking zones were successfully found'
    response['parking_zones'] = [parse_to_json(parking_zone) for parking_zone in free_parking_zones]

    return response, 200


def get_single_parking_zone(parking_zone_id):
    response = {'message': None, 'parking_zone': None}
    parking_zone = db.session.query(ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        response['message'] = f'The parking zone with id {parking_zone_id} was successfully found'
        response['parking_zone'] = parse_to_json(parking_zone)

        return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


def add_parking_zone(parking_zone_body):
    response = {'message': None, 'parking_zone': None}
    invalid_parameters = validate_request(parking_zone_body)

    if len(invalid_parameters) != 0:
        response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

        return response, 400
    else:
        street_name, street_number = parking_zone_body['street_name'], parking_zone_body['street_number']
        city_postal_code = parking_zone_body['city_postal_code']

        address = db.session.query(Address) \
            .filter_by(street_name=street_name, street_number=street_number, city_postal_code=city_postal_code) \
            .first()

        if address is None:
            city_name, country = parking_zone_body['city_name'], parking_zone_body['country']
            address = Address(street_name=street_name, street_number=street_number,
                              city_name=city_name, city_postal_code=city_postal_code,
                              country=country)

            latitude, longitude = parking_zone_body['latitude'], parking_zone_body['longitude']
            location = Location(latitude=latitude, longitude=longitude, address=address)

            db.session.add(location)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)
            db.session.refresh(location)

        if address.parking_zone:
            response['message'] = "A parking zone is already registered on that address"
            response['parking_zone'] = parse_to_json(address.parking_zone)

            return response, 409
        else:
            capacity = parking_zone_body['capacity']
            parking_zone = ParkingZone(capacity=capacity, address=address)
            db.session.add(parking_zone)
            db.session.commit()
            db.session.refresh(parking_zone)

            response['message'] = 'The parking zone was successfully added'
            response['parking_zone'] = parse_to_json(parking_zone)

            return response, 200


def edit_parking_zone(parking_zone_id, parking_zone_body):
    response = {'message': None, 'parking_zone': None}
    parking_zone = db.session.query(ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        invalid_parameters = validate_request(parking_zone_body)

        if len(invalid_parameters) != 0:
            response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

            return response, 400
        else:
            # address = parking_zone.address
            # for attr in dir(address):
            #     if (not attr.startswith('__')) and parking_zone_body[attr]:
            #         setattr(address, attr, parking_zone_body[attr])
            #
            # location = db.session.query(Location).filter_by(id=address.location_id).first()
            # for attr in dir(location):
            #     if (not attr.startswith('__')) and parking_zone_body[attr]:
            #         setattr(location, attr, parking_zone_body[attr])

            parking_zone.capacity = parking_zone_body['capacity']
            parking_zone = update_address(model=parking_zone, request_body=parking_zone_body)
            db.session.commit()

            response['message'] = f'The parking zone with id {parking_zone_id} was successfully updated'
            response['parking_zone'] = parse_to_json(parking_zone)

            return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


def delete_parking_zone(parking_zone_id):
    response = {'message': None}
    parking_zone = db.session.query(ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        db.session.delete(parking_zone)
        db.session.commit()

        response['message'] = f'The parking zone with id {parking_zone_id} was successfully deleted'

        return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404
