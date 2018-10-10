import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd

website_prefix = "https://www.imdb.com"
website_list = website_prefix + "/list/ls063284751/"


def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup


def _convert_string_to_int(string):
    if len(string) == 3:
        return float(string.strip())
    else :
        return float(string.replace(",",""))

def get_all_links_for_page_number(n):
    list_url = []
    url = website_list + "?sort=list_order,asc&st_dt=&mode=detail&page=" + str(n)
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    data = soup.findAll('h3', attrs={"class": u"lister-item-header"})
    for div in data:
      links = div.findAll('a')
      for a in links:
          list_url.append((website_prefix + a['href']))
    return list_url

def get_data_for_page(page_url):
    res = requests.get(page_url)
    soup = _handle_request_result_and_build_soup(res)
    data = []
    movie_title_finder = soup.find('h1', attrs={"class": u""})
    if movie_title_finder == None:
        movie_title = ""
    else:
        movie_title = movie_title_finder.text
    movie_time = soup.find('time').text.strip()
    star_rating = _convert_string_to_int(soup.find('span', attrs={"itemprop": u"ratingValue"}).text)
    nb_rating = _convert_string_to_int(soup.find('span', attrs={"itemprop": u"ratingCount"}).text)
    data = [movie_title,movie_time,star_rating,nb_rating]
    return data

def get_data_for_list(num_pages):
    df = pd.DataFrame(columns=['Title', 'Time', 'Rating', 'Number of votes'])
    j = 0
    for i in range(2,num_pages + 1):
        url_movies = get_all_links_for_page_number(i)
        for url in url_movies:
          results_movies = []
          results_movies = get_data_for_page(url)
          df.loc[j] = results_movies
          del results_movies[:]
          j += 1
    return df

def sort_df(dataframe):
    return dataframe


# class Lesson1Tests(unittest.TestCase):
#     def testGetLink(self):
#         self.assertEqual(get_all_links_for_page_number(2)[0] , "https://www.imdb.com/title/tt0480249/?ref_=ttls_li_tt")

def main():
    num_pages = 3
    df_imdb = get_data_for_list(num_pages)
    print(df_imdb)




if __name__ == '__main__':
    main()