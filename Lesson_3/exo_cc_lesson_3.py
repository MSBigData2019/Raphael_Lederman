import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd


def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def get_data_for_page(page_url):
    res = requests.get(page_url)
    soup = _handle_request_result_and_build_soup(res)
    info = soup.findAll("p", class_="darty_prix_barre_remise")
    percentage = 0
    for el in info:
        percentage += int(el.text[:1]+el.text[2:-1])
    nb_discount = len(info)
    return [nb_discount,percentage/nb_discount]


def get_data_for_list(brands, nb_page):
    website_prefix = "https://www.darty.com/nav/recherche?s=relevence&text="
    nb_discount = []
    mean_percentage = []
    for brand in brands:
        count = 0
        percentage = 0
        for i in range(1, nb_page):
            url = website_prefix + brands[i-1] + "&o=" + str(30*i)
            count += get_data_for_page(url)[0]
            percentage += get_data_for_page(url)[1]
        nb_discount.append(count)
        mean_percentage.append(percentage)
    return [nb_discount, mean_percentage]



def main():
    brands = ['dell', 'acer']
    list_darty = []
    list_darty = get_data_for_list(brands, 3)
    print(list_darty)


if __name__ == '__main__':
    main()