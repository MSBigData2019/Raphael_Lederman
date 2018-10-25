import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from threading import Thread, RLock
import sys
import time
import os

verrou = RLock()


def get_top_users():
    """Find the top contributors from the Github page of paulmillr with webscraping"""

    req = requests.get("https://gist.github.com/paulmillr/2657075")
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, "html.parser")
        table = soup.find("table").findAll("tr")[1:]
        return [row.find("td").text.split()[0] for row in table]
    else:
        print("Status Code Error")


def star_count_t(page):
    """for a given page, return the number of stars, and the number of repos"""

    stars = [(repos["name"], repos["stargazers_count"]) for repos in page]
    return stars


def req_200(string):
    """Return the request only if code 200"""

    j = 0
    token = ""
    headers = {'Authorization': 'token {}'.format(token)}
    while True:
        req = requests.get(string, headers=headers)
        if req.status_code == 200:
            break
        else:
            time.sleep(5)
        j += 1
        if j == 50:
            break
    return req


def all_page_count_t(user):
    """Count all requiered parameters from repos pages for a given user"""

    i = 1
    all_repos = []
    req = req_200(f"https://api.github.com/users/{user}/repos?page=1&per_page=100")
    while len(req.json()) != 0:
        i += 1
        page = req.json()
        all_repos += star_count_t(page)
        req = req_200(f"https://api.github.com/users/{user}/repos?page={i}&per_page=100")
        if i == 50:
            break
    return dict(all_repos)

    return dict(all_repos)


def stars_users_t(user, stars):
    # Creation d'un dictionnaire résumant le nombre de stars et de repos pour chaque user
    repos_user = all_page_count_t(user)
    with verrou:
        stars["user"].append(user)
        stars["#_repos"].append(len(repos_user.keys()))
        stars["tot_stars"].append(sum(repos_user.values()))
        return stars


class git_crawl_user(Thread):
    """Thread in charge of loading information about a given Github user"""

    def __init__(self, user, stars):
        Thread.__init__(self)

        self.user = user

        self.stars = stars

    def run(self):
        self.stars = stars_users_t(self.user, self.stars)


# WARNING : the token has been removed so the code can be safely put on Github, it has to be re-uploaded
token = ""
headers = {'Authorization': 'token {}'.format(token)}

# Initiatilisation du dictionnaire principale
stars = {}
stars["user"] = []
stars["#_repos"] = []
stars["tot_stars"] = []

# On compte le nombre de requêtes effectués
# initiatisation
requests.get("https://api.github.com/rate_limit", headers=headers).content
r1 = requests.get("https://api.github.com/rate_limit", headers=headers).json()["rate"]["remaining"]

t1 = time.time()
# Calcul de la liste des utilisateurs les plus actifs
list_users = get_top_users()

# Creation des threads
i = 0
for user in list_users:
    thread = git_crawl_user(user, stars)
    thread.start()
    time.sleep(1)
    i += 1
    if i == 25:
        print(f"Avancement : {round(len(stars['user'])/len(list_users)*100,0)}")
        i = 0

while len(stars['user']) < len(list_users):
    pass

t2 = time.time()
time.sleep(10)
r2 = requests.get("https://api.github.com/rate_limit", headers=headers).json()["rate"]["remaining"]
print(f"\n\nTache terminé en {round((t2-t1)/60,1)} min")

print(f"\n\nRequêtes utilisés : {(r1-r2)}")

df=pd.DataFrame(stars)
df["moyenne"]=round(df["tot_stars"]/df["#_repos"])
df.sort_values("moyenne", ascending=False)
df[df["user"]=="egoist"]