import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd


def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def get_sales(soup):
    particular_class = soup.findAll(class_="module")
    sales = particular_class[2].find_all(class_ ="stripe")[0].find_all(class_ = "data")[1].text.strip()
    return sales


def get_stock_price(soup):
    particular_class = soup.find(class_="sectionQuoteDetail").findAll("span")
    stock_price = particular_class[1].text.strip()
    return stock_price


def get_percentage_move(soup):
    percentage_move = soup.find(class_ = "valueContentPercent").find(class_ ="neg").text.strip()
    return percentage_move


def get_ownership(soup):
    particular_class = soup.findAll(class_="dataSmall")
    ownership = particular_class[2].findAll(class_="data")[0].text.strip()
    return ownership


def get_div_yield(soup):
    particular_class = soup.findAll(class_="module")
    div_yield = particular_class[4].findAll(class_="data")[3].text.strip()
    return div_yield


def get_div_yield_industry(soup):
    particular_class = soup.findAll(class_="module")
    div_yield_industry = particular_class[4].findAll(class_="data")[4].text.strip()
    return div_yield_industry


def get_div_yield_sector(soup):
    particular_class = soup.findAll(class_="module")
    div_yield_sector = particular_class[4].findAll(class_="data")[5].text.strip()
    return div_yield_sector


def get_data_for_page(page_url):
    res = requests.get(page_url)
    soup = _handle_request_result_and_build_soup(res)
    data = []
    sales = get_sales(soup)
    stock_price = get_stock_price(soup)
    percentage_move = get_percentage_move(soup)
    ownership = get_ownership(soup)
    div_yield = get_div_yield(soup)
    div_yield_industry = get_div_yield_industry(soup)
    div_yield_sector = get_div_yield_sector(soup)
    data = [sales,stock_price,percentage_move, ownership, div_yield,div_yield_industry, div_yield_sector]
    return data


def get_data_for_list(stocks):
    website_prefix = "https://www.reuters.com/finance/stocks/financial-highlights/"
    df = pd.DataFrame(columns=['4Q2018 Sales', 'Stock Price', '% Move', '% Shares Owned by Instit. Inv.', 'Div. Yield', 'Sector', 'Industry'])
    i = 0
    for stock in stocks:
        url = website_prefix + stocks[i]
        data_stock = []
        data_stock = get_data_for_page(url)
        df.loc[i] = data_stock
        del data_stock[:]
        i += 1
    return df


def main():
    stocks = ['LVMH.PA','DANO.PA', 'AIR.PA']
    df_reuters = get_data_for_list(stocks)
    print(df_reuters)


if __name__ == '__main__':
    main()