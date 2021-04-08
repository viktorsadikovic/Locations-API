from app import db
from models import ParkingSpot, ParkingZone


def parse_to_json(parking_spot):
    return {
        'id': parking_spot.id,
        'parking_zone': {
            'id': parking_spot.parking_zone.id,
            'capacity': parking_spot.parking_zone.capacity,
            'street_name': parking_spot.parking_zone.address.street_name,
            'street_number': parking_spot.parking_zone.address.street_number,
            'city_name': parking_spot.parking_zone.address.city_name,
            'city_postal_code': parking_spot.parking_zone.address.city_postal_code,
            'country': parking_spot.parking_zone.address.country,
            'latitude': parking_spot.parking_zone.address.location.latitude,
            'longitude': parking_spot.parking_zone.address.location.longitude
        },
        'available': parking_spot.available
    }


def get_all_free_parking_spots():
    response = {'message': None, 'parking_spots': None}
    free_parking_spots = db.session.query(ParkingSpot).filter_by(available=True).all()

    response['message'] = 'The parking spots were successfully found'
    response['parking_spots'] = [parse_to_json(parking_spot) for parking_spot in free_parking_spots]

    return response, 200


def get_free_parking_spots_per_zone(parking_zone_id):
    response = {'message': None, 'parking_spots': None}
    parking_zone = db.session.query(ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        free_parking_spots = [parking_spot for parking_spot in parking_zone.parking_spots if parking_spot.available]

        response['message'] = 'The parking spots were successfully found'
        response['parking_spots'] = [parse_to_json(parking_spot) for parking_spot in free_parking_spots]

        return response, 200
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


def reserve_parking_spot(parking_zone_id, parking_spot_id):
    response = {'message': None, 'parking_spot': None}
    parking_spot = db.session.query(ParkingSpot).filter_by(id=parking_spot_id, parking_zone_id=parking_zone_id).first()

    if parking_spot:
        parking_spot.available = False
        db.session.commit()
        db.session.refresh(parking_spot)

        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} was successfully reserved'
        response['parking_spot'] = parse_to_json(parking_spot)

        return response, 200
    else:
        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} does not exist'

        return response, 404


def free_parking_spot(parking_zone_id, parking_spot_id):
    response = {'message': None, 'parking_spot': None}
    parking_spot = db.session.query(ParkingSpot).filter_by(id=parking_spot_id, parking_zone_id=parking_zone_id).first()

    if parking_spot:
        parking_spot.available = True
        db.session.commit()
        db.session.refresh(parking_spot)

        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} was successfully freed'
        response['parking_spot'] = parse_to_json(parking_spot)

        return response, 200
    else:
        response['message'] = f'The parking spot with id {parking_spot_id} and ' \
                              f'parking zone id {parking_zone_id} does not exist'

        return response, 404


def add_parking_spot(parking_zone_id):
    response = {'message': None, 'parking_spot': None}
    parking_zone = db.session.query(ParkingZone).filter_by(id=parking_zone_id).first()

    if parking_zone:
        num_parking_spots = len(parking_zone.parking_spots)

        if num_parking_spots < parking_zone.capacity:
            parking_spot = ParkingSpot(id=(num_parking_spots + 1), parking_zone=parking_zone, available=True)
            db.session.add(parking_spot)
            db.session.commit()
            db.session.refresh(parking_spot)

            response['message'] = f'The parking spot with id {parking_spot.id} and ' \
                                  f'parking zone id {parking_zone_id} was successfully added'
            response['parking_spot'] = parse_to_json(parking_spot)

            return response, 200
        else:
            response['message'] = f'The parking zone with id {parking_zone_id} is out of capacity'

            return response, 400
    else:
        response['message'] = f'The parking zone with id {parking_zone_id} does not exist'

        return response, 404


def delete_parking_spot(parking_zone_id, parking_spot_id):
    response = {'message': None}
    parking_spot = db.session.query(ParkingSpot).filter_by(id=parking_spot_id, parking_zone_id=parking_zone_id).first()

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
