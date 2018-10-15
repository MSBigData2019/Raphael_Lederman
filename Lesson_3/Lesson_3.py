# link public apis https://github.com/toddmotto/public-apis
# voir api OMdb (http://www.omdbapi.com/) et DBpedia
    # exemple de requete http://www.omdbapi.com/?t=starwars&apikey=25a9f1a1
# https://jqplay.org/ : pour manipuler les apis json, permet de restructurer les jsons.
    # https://stedolan.github.io/jq/tutorial/ exemples de commandes json : pb pas possible avec pandas directement
#IFTTT : permet de générer des actions conditionnelles en passant par pleins d'apis sans passer par du code
    # https://ifttt.com/discover?s_[]=100&s_[]=2&s_[]=10&s_[]=32&s_[]=89&s_[]=51464135&s_[]=416545307

from multiprocessing import pool
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

movie = "star wars"
url = "http://www.omdbapi.com/?apikey=25a9f1a1&s="+movie+"&type=movie"
res = requests.get(url)

response_object = json.loads(res.text)
movies_list = response_object['Search']
df_movies = pd.DataFrame(movies_list)


def main():
    print(df_movies['Title'])

if __name__ == '__main__':
    main()
