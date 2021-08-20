from typing import Union, Tuple, List, Dict
from geopy.distance import distance

Coordinate = Union[Tuple[float], List[float]]


def compare_coords(coords_a: Coordinate, coords_b: Coordinate) -> float:
    return distance(coords_a, coords_b).m


def area_contains_point(area_point_a: Dict[str, float], area_point_b: Dict[str, float], point: Dict[str, str]) -> bool:
    if not area_point_a["Lat"] < area_point_b["Lat"] and area_point_a["Lng"] < area_point_b["Lng"]:
        area_point_a, area_point_b = area_point_b, area_point_a

    return area_point_a["Lat"] < float(point["lat"]) < area_point_b["Lat"] and area_point_a["Lng"] < float(point["lon"]) < area_point_b["Lng"]
