


# List of essential files:

1) body.py	
This python file is the main body which contains codes associated with the operation of the telegram bot.

2) Goods.py
This python file contains functions associated with the communication between the bot and the json data file. There is also a function for outputing data to an Excel document, which was introduced in an earlier version of the bot, but removed from the main body in a later version.

3) GoodsData.json
This json file stores all data of goods posted in json format. 

4) ZZsearch.py
This python file contails functions concerned with scraping and analysing data from Carousell.

5) Procfile 
This file assigns the main working python file for heroku.

6) Requirements.txt
This txt file includes all required external library for heroku to install


More comments on how the bot works  are available inside the .py files.

# List of required external libraries:

1) telepot
2) openpyxl
3) requests
4) numpy
5) bs4
6) lxml
7) urllib