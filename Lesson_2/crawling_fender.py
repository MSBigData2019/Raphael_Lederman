import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import unittest


def treat_url_request(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.text
        soup = BeautifulSoup(html_doc, "html.parser")
        return soup

def get_all_url(url):
    request = requests.get(url)
    text = treat_url_request(request)
    particular_class = "product-item__text-link"
    url_list = map(lambda x: x.attrs['href'], text.find_all("a", class_=particular_class))
    return url_list

def get_info_on_product(text):
    particular_class = "price-sales"
    particular_id = "feature-bullets"
    name = text.find("h1", class_="prod-name").text
    price = text.find("span", class_= particular_class).text
    readable_price = convert_string_to_int(price)
    description = []
    description = extract_features(text)
    readable_description = " ".join(str(x)+"." for x in description)
    return [name, readable_price,readable_description]

def extract_features(text):
    description = text.find_all("span", class_="")
    liste_description = []
    for el in description:
        des = re.search(r'(?<=="">)(.*?)(?=\<)',str(el))
        if des:
            liste_description.append(des.group(0))
    return (liste_description)

def convert_string_to_int(text):
    if text[-1] == "€":
        text = text[:-2]
    price = float(text.replace(",","."))
    return price

def obtain_dataframe(url_input):
    url_liste = get_all_url(url_input)
    df = pd.DataFrame(columns=['Model', 'Price', 'Description'])
    i = 0
    for url in url_liste:
        request = requests.get(url)
        text = treat_url_request(request)
        list=[]
        list = get_info_on_product(text)
        df.loc[i] = list
        del list[:]
        i += 1
    return df

def to_csv(df):
    df.to_csv("guitars-info.csv")

def main():
    to_csv(obtain_dataframe('https://shop.fender.com/fr-FR/search?q=stratocaster&qSubmit='))

# class tests(unittest.TestCase):
#     def tests_1(self):
#         self.assertEqual(convert_string_to_int("630,3 €"), 630.3)


if __name__ == '__main__':
    main()

