import json
from configparser import RawConfigParser
from typing import Dict, Any, List

import requests
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz

from exceptions import ConfigNotFound, ZoneNotFound
from geopy.geocoders import Nominatim

from helpers import area_contains_point, compare_coords

Zone = Scooter = Dict[str, Any]


class VOI:

    def __init__(self):
        parser = RawConfigParser()
        parser.read("./config.ini")
        if not parser.has_section("voi"):
            raise ConfigNotFound

        voi_config = dict(parser.items("voi"))
        url = "https://api.voiapp.io/v1/auth/session"
        data = json.dumps({"authenticationToken": voi_config["voi_auth_token"]})
        res = requests.post(url, data=data)

        if res.status_code == 200:
            res = res.json()
            if res["authenticationToken"] != voi_config["voi_auth_token"]:
                parser.set("voi", "voi_auth_token", res["authenticationToken"])
                with open("config.ini", "w") as f:
                    parser.write(f)

            self.headers = {"x-access-token": res["accessToken"]}
            url = "https://api.voiapp.io/v1/zones"

            res = requests.get(url, headers=self.headers).json()
            self.zones = [zone for zone in res["zones"] if zone["country"] == "DE"]

    def get_zone(self, city: str) -> Zone:
        translated_city = GoogleTranslator().translate(city)
        zone = max(self.zones, key=lambda x: fuzz.ratio(translated_city, x["name"]))
        if fuzz.ratio(translated_city, zone["name"]) < 70:
            raise ZoneNotFound
        return zone

    def get_nearest_scooters_by_address(self, address: str, scooter_count: int = 5, *, min_battery: int = 35) -> List[Scooter]:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(address)
        for zone in self.zones:
            if area_contains_point(zone["boundaries"]["Lo"], zone["boundaries"]["Hi"], location.raw):
                scooters = self.get_zone_scooters(zone, min_battery=min_battery)
                return sorted(scooters,
                              key=lambda x: compare_coords([location.latitude, location.longitude],
                                                           [x["location"]["lat"], x["location"]["lng"]])
                              )[:scooter_count]

    def get_zone_scooters(self, zone: Zone, min_battery: int = 20) -> List[Scooter]:
        url = f"https://api.voiapp.io/v2/rides/vehicles?zone_id={zone['zone_id']}"
        res = requests.get(url, headers=self.headers).json()
        scooters = [vehicle for vehicle in res["data"]["vehicle_groups"][0]["vehicles"] if vehicle["battery"] > min_battery]
        for scooter in scooters:
            scooter["maps_url"] = f"https://www.google.com/maps/search/{scooter['location']['lat']},+{scooter['location']['lng']}?sa=X"
        return [vehicle for vehicle in res["data"]["vehicle_groups"][0]["vehicles"] if vehicle["battery"] > min_battery]
