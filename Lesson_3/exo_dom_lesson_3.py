import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def _handle_request_result_and_build_soup(request_result):
  if request_result.status_code == 200:
    html_doc =  request_result.text
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup

def get_top_contributors(url):
    ranking = {}
    result =[]
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    data = soup.find("tbody").findAll("td")
    rank = 0
    for el in data:
        if el.find("a") and el.find("a").nextSibling != None :
            rank += 1
            name = el.find("a").attrs["href"][19:]
            ranking[rank] = name
    return ranking

def get_stars_in_repo(contributor):
    git_api = 'https://api.github.com/users/'
    userID = "RaphaelLederman"
    token = "124943d52b479e867cba059efb356278535e3142"
    res = requests.get(url = git_api + contributor + "/repos?per_page=1000", auth = (userID, token))
    response_object = json.loads(res.text)
    result = 0
    for el in response_object:
        result += el['stargazers_count']
    if len(response_object) != 0:
        av_star = result/len(response_object)
    else:
        av_star = 0
    return av_star


def main():
    url = "https://gist.github.com/paulmillr/2657075"
    dict = get_top_contributors(url)
    dict_final = {}
    for name in dict.values():
        stars = get_stars_in_repo(name)
        dict_final[name] = stars
    sorted_dict = sorted(dict_final.items(), key=lambda kv: kv[1], reverse = True)
    print(sorted_dict)


if __name__ == '__main__':
    main()