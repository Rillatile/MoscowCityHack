from db.models import CoordinateData


class CoordinateData:
    def save(data):
        cd = CoordinateData(
            lat = data['lat'].replace(',', '.'),
            lon = data['lon'].replace(',', '.'),
            street = data['street'].lower(),
            house = data['house'].lower(),
            raw_values = data['raw_values'],
            processed_value = data['value']
        )
        
        cd.save()
