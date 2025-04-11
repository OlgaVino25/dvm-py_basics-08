import json
import requests
import os
from dotenv import load_dotenv
from geopy import distance
from pprint import pprint
import folium

with open("coffee.json", "r", encoding="CP1251") as my_file:
    file_contents = my_file.read()
file_content = json.loads(file_contents)


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def main():
    m = folium.Map(location=(55.753544, 37.621202), zoom_start=10)

    load_dotenv()
    apikey = os.getenv("APIKEY")
    city_user = input("Где вы находитесь? ")
    coords_user = fetch_coordinates(apikey, f"{city_user}")
    print(f"Ваши координаты: {coords_user}")

    generate_coffee = []

    for coffee in file_content:
        name = coffee["Name"]
        coordinates = coffee["geoData"]["coordinates"]
        distancer = distance.distance(coords_user, coordinates).km
        generate_coffee.append({
            "title": name,
            "distance": distancer,
            "latitude": coordinates[1],
            "longitude": coordinates[0]
        })

    nearest_coffee = sorted(generate_coffee, key=lambda coffee: coffee["distance"])
    five_nearest_coffee = nearest_coffee[:5]
    pprint(five_nearest_coffee, sort_dicts=False)

    for marker in five_nearest_coffee:
        folium.Marker(
            location=[marker["latitude"], marker["longitude"]],
            popup=marker["title"],
            icon=folium.Icon(color="red")
        ).add_to(m)
    m.save("index.html")


if __name__ == "__main__":
    main()
