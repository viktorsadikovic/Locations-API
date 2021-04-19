from app import db
from models import RepairStation, Address, Location
from utilities import validate_request, update_address


def parse_to_json(repair_station):
    return {
        'id': repair_station.id,
        'available': repair_station.available,
        'street_name': repair_station.address.street_name,
        'street_number': repair_station.address.street_number,
        'city_name': repair_station.address.city_name,
        'city_postal_code': repair_station.address.city_postal_code,
        'country': repair_station.address.country,
        'latitude': repair_station.address.location.latitude,
        'longitude': repair_station.address.location.longitude
    }


def get_all_repair_stations():
    response = {'message': None, 'repair_stations': None}
    repair_stations = db.session.query(RepairStation).all()

    response['message'] = 'The repair stations were successfully found'
    response['repair_stations'] = [parse_to_json(repair_station) for repair_station in repair_stations]

    return response, 200


def get_available_repair_stations():
    response = {'message': None, 'repair_stations': None}
    all_repair_stations = db.session.query(RepairStation).all()
    available_repair_stations = []
    for repair_station in all_repair_stations:
        available_repair_stations = [repair_station for repair_station in all_repair_stations if
                                     repair_station.available]

    response['message'] = 'The avalilable repair stations were successfully found'
    response['repair_stations'] = [parse_to_json(repair_station) for repair_station in available_repair_stations]

    return response, 200


def get_single_repair_station(repair_station_id):
    response = {'message': None, 'repair_station': None}
    repair_station = db.session.query(RepairStation).filter_by(id=repair_station_id).first()

    if repair_station:
        response['message'] = f'The repair station with id {repair_station_id} was successfully found'
        response['repair_station'] = parse_to_json(repair_station)
        return response, 200
    else:
        response['message'] = f'The repair station with id {repair_station_id} does not exist'
        return response, 404

def add_repair_station(repair_station_body):
    response = {'message': None, 'repair_station': None}
    invalid_parameters = validate_request(repair_station_body)

    if len(invalid_parameters) != 0:
        response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

        return response, 400
    else:
        street_name, street_number = repair_station_body['street_name'], repair_station_body['street_number']
        city_postal_code = repair_station_body['city_postal_code']

        address = db.session.query(Address) \
            .filter_by(street_name=street_name, street_number=street_number, city_postal_code=city_postal_code) \
            .first()

        if address is None:
            city_name, country = repair_station_body['city_name'], repair_station_body['country']
            address = Address(street_name=street_name, street_number=street_number,
                              city_name=city_name, city_postal_code=city_postal_code,
                              country=country)

            latitude, longitude = repair_station_body['latitude'], repair_station_body['longitude']
            location = Location(latitude=latitude, longitude=longitude, address=address)

            db.session.add(location)
            db.session.add(address)
            db.session.commit()
            db.session.refresh(address)
            db.session.refresh(location)

        if address.repair_station:
            response['message'] = "A repair station is already registered on that address"
            response['repair_station'] = parse_to_json(address.repair_station)

            return response, 409
        else:
            capacity = repair_station_body['capacity']
            repair_station = RepairStation(capacity=capacity, address=address)
            db.session.add(repair_station)
            db.session.commit()
            db.session.refresh(repair_station)

            response['message'] = 'The repair station was successfully added'
            response['repair_station'] = parse_to_json(repair_station)

            return response, 200

def edit_repair_station(repair_station_id, repair_station_body):
    response = {'message': None, 'repair_station': None}
    repair_station = db.session.query(RepairStation).filter_by(id=repair_station_id).first()

    if repair_station:
        invalid_parameters = validate_request(repair_station_body)

        if len(invalid_parameters) != 0:
            response['message'] = 'The following parameters are invalid: {}'.format(', '.join(invalid_parameters))

            return response, 400
        else:

            repair_station.availability = repair_station_body['availability']
            repair_station = update_address(model=repair_station, request_body=repair_station_body)
            db.session.commit()

            response['message'] = f'The repair station with id {repair_station_id} was successfully updated'
            response['repair_station'] = parse_to_json(repair_station)

            return response, 200
    else:
        response['message'] = f'The repair station with id {repair_station_id} does not exist'

        return response, 404



def delete_repair_station(repair_station_id):
    response = {'message': None}
    repair_station = db.session.query(RepairStation).filter_by(id=repair_station_id).first()

    if repair_station:
        db.session.delete(repair_station)
        db.session.commit()

        response['message'] = f'The repair station with id {repair_station_id} was successfully deleted'

        return response, 200

    else:
        response['message'] = f'The repair station with id {repair_station_id} does not exist'

        return response, 404
