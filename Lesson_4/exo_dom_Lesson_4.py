import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

# dataframe.applymap(labda x : re.match('\d{1,4}',x)[0]).astype(int).mean()

# L'objectif est de générer un fichier de données sur le prix des Renault Zoé sur le marché de l'occasion en
# Ile de France, PACA et Aquitaine.
# Vous utiliserez leboncoin.fr comme source. Si leboncoin ne fonctionne plus vous pouvez vous rabattre sur
# d'autres sites d'annonces comme lacentrale, paruvendu, autoplus,...
# Le fichier doit être propre et contenir les infos suivantes : version ( il y en a 3), année, kilométrage,
# prix, téléphone du propriétaire, est ce que la voiture est vendue par un professionnel ou un particulier.
# Vous ajouterez une colonne sur le prix de l'Argus du modèle que vous récupérez sur ce site
# http://www.lacentrale.fr/cote-voitures-renault-zoe--2013-.html.
#
# Les données quanti (prix, km notamment) devront être manipulables (pas de string, pas d'unité).
# Vous ajouterez une colonne si la voiture est plus chere ou moins chere que sa cote moyenne.﻿


url_IDF = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-IDF"
url_PAC = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-PAC"
url_NAQ = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&regions=FR-NAQ"
url_NAQ_2 = "https://www.lacentrale.fr/listing?makesModelsCommercialNames=RENAULT%3AZOE&options=&page=2&regions=FR-NAQ"

def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def get_all_links_for_page_number(n, model, region):
    list_url = []
    url = "https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page={}&regions={}".format(model, n, region)
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    data = soup.find_all("div", class_="adContainer")
    for div in data:
        link = div.find("a", class_="linkAd")['href']
        list_url.append(link)
    return list_url


def get_argus_price(model, year):
    website_url = "https://www.lacentrale.fr/cote-auto-renault-zoe-{}-{}.html"
    model_formatted = "+".join(model.split(" "))
    url = website_url.format(model_formatted, year)
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    price = ""
    if soup.find("span", class_="jsRefinedQuot") != None:
        price = int(soup.find("span", class_="jsRefinedQuot").text.replace(" ",""))
    return price

def get_data_from_page(brand, general_model, region, url):
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    if soup.find("div", class_ = "phoneNumber1") != None:
        phone_class = soup.find("div", class_ = "phoneNumber1")
    phone = "-".join(phone_class.find("span", class_ = "bold").getText().strip().split()[:5])
    if soup.find("div", class_="bold italic mB10") != None:
        type_seller = " ".join(soup.find("div", class_ = "bold italic mB10").getText().strip().split(" ")[:2])
    info_product = soup.find("div", class_="box boxOptions infosGen")
    model = info_product.find("h3").text.strip().split(" - ")[-1]
    year = int(info_product.find('h4', text=re.compile('Année')).find_next('span').text)
    kilometers = int(info_product.find('h4', text=re.compile('Kilométrage')).find_next('span').text.replace(" ","")[:-2])
    price = int(soup.find("div", class_="mainInfos hiddenOverflow").find("strong", text=re.compile("€")) \
        .text.replace(" ", "")[:-2])
    argus_price = get_argus_price(model, year)
    if argus_price == "":
        compare = ""
    elif price > argus_price:
        compare = "+"
    elif price < argus_price:
        compare = "-"
    return [brand, general_model, model, region, year, kilometers, price, argus_price, compare, type_seller, phone]


def get_nb_pages(url):
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    nb_results = soup.find("span", class_="numAnn").text
    nb_pages = int(nb_results)/16 + 1
    return int(nb_pages)

def to_csv(df):
    df.to_csv("info-renault-zoe.csv")

def main():
    df = pd.DataFrame(columns=['Brand', 'General Model', 'Model', 'Region', 'Year', 'Kilometers', 'Price', 'Argus Price', 'Comparison', 'Type of seller', "Phone number"])
    model = "RENAULT%3AZOE"
    regions = ["FR-IDF", "FR-PAC", "FR-NAQ"]
    website_prefix = "https://www.lacentrale.fr"
    j = 0
    for region in regions:
        url = "https://www.lacentrale.fr/listing?makesModelsCommercialNames={}&options=&page={}&regions={}".format(model, 1, region)
        nb_pages = get_nb_pages(url)
        for i in range(1, nb_pages + 1):
            list_links = get_all_links_for_page_number(i, model, region)
            for link in list_links:
                car_info = get_data_from_page("Renault", "Zoe", region, website_prefix + link)
                df.loc[j] = car_info
                j += 1
    print(df)
    to_csv(df)

if __name__ == '__main__':
    main()