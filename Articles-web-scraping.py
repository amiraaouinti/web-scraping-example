import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymongo
from pymongo import MongoClient
import time
from datetime import datetime



def conn_data():
    uri = 'specify the uri'
    client = MongoClient(uri)
    db = client.ilboursa
    collection = db.articles
    return collection

# scraping all the articles
def scrap_articles(collection):
    pattern = '%Y-%m-%d %H:%M:%S'


    for page in range(1,2):
        source = requests.get('https://www.ilboursa.com/marches/actualites_bourse_tunis.aspx?p='+ str(page) +'')
        soup = BeautifulSoup(source.text, 'html.parser')
        results = soup.find_all('tr')
        for ligne in results:
            li = ligne.span.text
            date_object = datetime.strptime(li, '%d/%m/%Y %H:%M')
            date_object = str(date_object)
            date = int(time.mktime(time.strptime(date_object, pattern)))

            titre = ligne.a.text[13:]
            lien = ligne.a['href']
            link = 'https://www.ilboursa.com/marches/'+lien+''
            cotation = ligne.find('td', class_='alri').text
            link_scrap = requests.get('https://www.ilboursa.com/marches/'+lien+'')
            tag_lien = BeautifulSoup(link_scrap.text, 'html.parser')

            site = tag_lien.find_all('div', class_='clearfix')
            site_2 = site[2]
            site_3 = site[3]
            resu = site_3.img
            if resu:
                site = site_3
            else:
                site = site_2

            ind_img = site.img['src']
            if "https://" not in ind_img: 
                img_link = ind_img[3:]
                image = 'https://www.ilboursa.com/' +str(img_link) +''
            else:
                image = ind_img

            if cotation:
                tags_acc = tag_lien.find_all('div', class_='cartouche_qt')
                for tag in tags_acc:
                    societe = tag.span.text
                    collection.insert_one({
                        'date':date,
                        'titre':titre,
                        'lien':link,
                        'image':image,
                        'cotation':cotation,
                        'societe':societe})

            else:
                societe = ''
                collection.insert_one({
                        'date':date,
                        'titre':titre,
                        'lien':link,
                        'image':image,
                        'cotation':cotation,
                        'societe':societe})
        else:
            pass


collection = conn_data()
scraping = scrap_articles(collection)

print('ok')
print(list(collection.find()))