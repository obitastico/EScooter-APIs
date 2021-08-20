from typing import List, Dict, Any

import requests
from geopy import Nominatim

Zone = Scooter = Dict[str, Any]


def get_nearest_tier_scooters_by_address(address: str, scooter_count: int = 5, *, min_battery: int = 35) -> List[Scooter]:
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)

    url = f"https://platform.tier-services.io/v1/vehicle?lat={location.latitude}&lng={location.longitude}&radius=3000"
    headers = {"X-Api-Key": "bpEUTJEBTf74oGRWxaIcW7aeZMzDDODe1yBoSxi2"}
    res = requests.get(url, headers=headers)
    return list(filter(lambda x: x["attributes"]["isRentable"] and x["attributes"]["vehicleType"] == "escooter" and x["attributes"]["batteryLevel"] > min_battery, res.json()["data"]))[:scooter_count]
