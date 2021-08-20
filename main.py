from tier import get_nearest_tier_scooters_by_address
from voi import VOI


def main():
    tier_scooters = get_nearest_tier_scooters_by_address("Marienplatz")
    for scooter in tier_scooters:
        print(scooter)

    voi = VOI()
    voi_scooters = voi.get_nearest_scooters_by_address("Marienplatz")
    for scooter in voi_scooters:
        print(scooter)


if __name__ == '__main__':
    main()
