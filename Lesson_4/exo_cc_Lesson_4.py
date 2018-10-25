import requests
import unittest
from bs4 import BeautifulSoup
import re

google_map_key = "AIzaSyDe0IYNjx3GnU-A7B7qY6tW5u_RCCVF9iU"
api_url = "https://maps.googleapis.com/maps/api/distancematrix/json?parameters"
def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup

def get_biggest_cities(url, nb):
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    cities = []
    table = soup.find("table", class_ = "odTable").findAll("a")
    for el in table:
        city = re.search(r'([^\s]+)', el.text)
        if city:
            cities.append(city.group(0))
    return cities[:nb]

def get_distances_for_cities(city_a, city_b):
    url = "https://fr.distance.to/"+city_a+"/"+city_b
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    info = soup.find("span", class_ = "value km").text
    return info


def main():
    url1 = "http://www.linternaute.com/ville/classement/villes/population"
    cities=[]
    cities = get_biggest_cities(url1, 5)
    distances = {}
    for city_a in cities:
        for city_b in cities:
            if city_a != city_b:
                if str(city_a+","+city_b) not in distances and str(city_b+","+city_a) not in distances:
                    distance = get_distances_for_cities(city_a, city_b)
                    distances[str(city_a+","+city_b)] = distance
    print(distances)


if __name__ == '__main__':
    main()