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
