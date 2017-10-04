import requests
import numpy
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

def split_keywords(keywords):

    #keywrods should be in a format of "xxxxx xxxxx xxxxx xxx"
    #the returned keywords should be used as kewwords in the following functions

    input_keyword = (keywords.split())
    final_keywords = ""
    for element in input_keyword:
        final_keywords += str(element) + "+"

    return final_keywords




def search_amazon(keywords):

    #keywords must be in the format of "xxxxxx+xxxxxx+xxxxx+"
    #a plus sign is required at the end#

    myurl=("https://www.google.com.sg/search?safe=off&q="+keywords+"site%3Aamazon.com")
    Page=requests.get(myurl)
    soup=BeautifulSoup(Page.text,"lxml")
    url=soup.find("h3").find("a").get("href")
    amazon_url= parse_qs(urlparse(url).query)['q'][0]

    return amazon_url

    #the function returns a webpage of the searched product in amazon

def search_carousell(keywords):

    # keywords must be in the format of "xxxxxx+xxxxxx+xxxxx"

    carousell_url = ("https://sg.carousell.com/search/products/?query=" + keywords)
    return carousell_url

def carousell_price(keywords):

    # keywords must be in the format of "xxxxxx+xxxxxx+xxxxx"

    carousell_url=("https://sg.carousell.com/search/products/?query="+keywords)
    Page=requests.get(carousell_url)
    soup=BeautifulSoup(Page.text,"lxml")
    price_tag=soup.find_all(id="productCardPrice")
    price_list=[]
    new_price=[]
    for single_tag in price_tag:
        price=single_tag.get('title')
        price_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
        re2 = re.compile(price_pattern, re.VERBOSE)
        new_price=new_price+re2.findall(price)
    new_price_int=list(map(int,(map(float,new_price))))

    for item_price in new_price_int:
        if  0 < item_price < 6000:
            price_list.append(item_price)
        if len(price_list) >= 10:
            break
    price_list=sorted(price_list,key=int,reverse=True)
    wanted_price_list=[]

    if len(wanted_price_list) >= 4:
        for each_item in price_list:
            if   0.5 <= price_list[2] / each_item <= 2:
                wanted_price_list.append(each_item)
            else:
                pass
        suggested_price=int(numpy.mean(wanted_price_list))

        return suggested_price

    else:
        return ("No suggested price")






    #     This function returns a webpage of the searched product in carousell
    #   and returns a suggested price fro the product.











