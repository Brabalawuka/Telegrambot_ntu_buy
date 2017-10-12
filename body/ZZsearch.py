"""
This module provides the following functions:

    1) search_amazon(keywords)
    2) search_carousell(input)
    3) carousell_price(input)

Note that search_amazon is not called in the main body
It is a feature initially introduced, but then removed in a later version.
However I decided not to delete the code and kept it.
"""


import requests
import numpy
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup



def search_amazon(input):

    '''
    This function uses requests and bs4 modules to get the url of the first item returned by google search,
    from all web pages of Amazon website. It shows more correct results than search directly from amazon.

    '''
    input_keyword = (input.split())
    keywords = ""
    for element in input_keyword:
        keywords += str(element) + "+"



    #This part converts the input keywords from the "xxxx xxxx xxxx" format into "xxxx+xxxx+xxxx+" format
    #It enables easier search for correct product url in the Carousell and the Amazon website




    myurl=("https://www.google.com.sg/search?safe=off&q="+keywords+"site%3Aamazon.com")
    Page=requests.get(myurl)
    soup=BeautifulSoup(Page.text,"lxml")
    url=soup.find("h3").find("a").get("href")
    amazon_url= parse_qs(urlparse(url).query)['q'][0]

    return amazon_url



def search_carousell(input):

    '''
    This function simply returns the url of the search page of the relevant item posted by the user
    '''

    input_keyword = (input.split())
    keywords = ""
    for element in input_keyword:
        keywords += str(element) + "+"

    # This part converts the input keywords from the "xxxx xxxx xxxx" format into "xxxx+xxxx+xxxx+" format
    # It enables easier search for correct product url in the Carousell and the Amazon website

    carousell_url = ("https://sg.carousell.com/search/products/?query=" + keywords)
    return carousell_url

def carousell_price(input):

    '''
    This function includes an algorithm that returns a suggested selling price from us by comparing the
    item posted by the users and similar items on carousell

    '''

    input_keyword = (input.split())
    keywords = ""
    for element in input_keyword:
        keywords += str(element) + "+"

    #This part simply dose the same thing, converting format.

    carousell_url = ("https://sg.carousell.com/search/products/?query="+keywords)
    Page = requests.get(carousell_url)
    soup = BeautifulSoup(Page.text,"lxml")
    price_tag = soup.find_all(id = "productCardPrice")
    price_list = []
    new_price = []
    for single_tag in price_tag:
        price = single_tag.get('title')
        price_num = float(''.join(ele for ele in price if ele.isdigit() or ele == '.'))
        new_price.append(price_num)

    # This part scraps the prices of all relevant items in first page and converts them form the format
    # such as "S$2,600.23" or "S$34.50" into a float number format

    for item_price in new_price:
        if  0 < item_price < 6000:
            price_list.append(item_price)
        if len(price_list) >= 20:
            break
    price_list = sorted(price_list,key = float,reverse=True)
    wanted_price_list = []

    # This part filters out abnormally high price which is over 6000sgd
    # and gets a final price list with 20 sample price from price high to low.

    if len(price_list) >= 5:
        for each_item in price_list:
            if   0.5 <= price_list[2] / each_item <= 2:
                wanted_price_list.append(each_item)
            else:
                pass
        suggested_price = int(numpy.mean(wanted_price_list))

        return suggested_price

    # To avoid getting irrelevant price such as "iphone 6s case" instead of "iphone 6s" due to search engine inaccuracy,
    # this parts find the third highest price in the previous list as an sample price and no other price should over the
    # limit of as much as its half or its twice.
    # This suggest price is a mean of the number list.


    else:
        return ("No suggested price")

    #No suggested price provided if insufficient sample is found on carousell.














