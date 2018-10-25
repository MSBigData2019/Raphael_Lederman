import requests
import unittest
from bs4 import BeautifulSoup
import pandas as pd
import re
import json

def main():
    website = "https://www.open-medicaments.fr/api/v1/medicaments?query=paracetamol"
    res = requests.get(website)
    df = pd.read_json(res.content)
    df2 = df["denomination"].str.extract(r'([\D]*)(\d+)(.*),(.*)',expand = True)
    df2["multiplicator"] = 1000
    df2["multiplicator"] = df2["multiplicator"].where(df2[2].str.strip() == "g", 1)
    df2["dosage"] = df2[1].fillna(0).astype(int)*df2["multiplicator"]
    # string = 'PARACETAMOL ZYDUS 500 mg, gélule'
    # reg = r',([\w\s]*)'
    print(df2)

if __name__ == '__main__':
    main()