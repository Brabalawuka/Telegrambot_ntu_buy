
# 10/10/17, based on body 0.3.1
# Added some comments, cleared up some formatting,

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from telepot.delegate import pave_event_space, create_open, per_chat_id
from Goods import save_to_json, retrieve_items, fetch_item_type
from ZZsearch import search_amazon, search_carousell, carousell_price
import time
from datetime import datetime
import json

""" 
    Codes and corresponding stages for self.stage:
    
    00: initial
    01: buy or sell
    Seller_PorR: seller's gonna post new item or remove existing item
    Seller_R: seller has chosen the index of item he wants to remove
    02: type of good
    Buyer_SelectItem: Buyer is viewing a short list of a type of goods, and will choose one to view its details
    Buyer_Viewing: Buyer is viewing an item(and most likely is not satisfied)
    
    Computers:
    11: brand
    12: model
    13: price
    14: description
    15: photo
    16: contact details
    
    Books:
    21: title
    22: author
    23: price
    24: description
    25: photo
    26: contact details
    
    Stationery:
    31: kind
    32: price
    33: description
    34: photo
    35: contact details
    
    Others:
    41: description
    42: price
    43: photo
    44: contact details 
    
    Furniture&Home and Clothing&Accessories and Electronic Gadgets:
    51: title
    52: description
    53: price
    54: photo
    55: contact details
    
"""
# The first keyboard that a user will see, asks the user whether he is a seller or a buyer
keyboard_0 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Sell', callback_data='sell')],
                                                   [InlineKeyboardButton(text='Buy', callback_data='buy')], ])

# This keyboard asks a buyer whether s/he wants to post a new item or remove a posted item
keyboard_PostOrRemove = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Post', callback_data='post')],
                                                              [InlineKeyboardButton(text='Remove',
                                                                                    callback_data='remove')], ])

keyboard_type = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Computer', callback_data='computer')],
                                                      [InlineKeyboardButton(text='Book', callback_data='book')],
                                                      [InlineKeyboardButton(text='Stationery',callback_data='stationery')],
                                                      [InlineKeyboardButton(text='Furniture&Home', callback_data='furniture&home')],
                                                      [InlineKeyboardButton(text='Clothing&Accessories', callback_data='clothing&accessories')],
                                                      [InlineKeyboardButton(text='Electronic Gadgets', callback_data='gadgets')],
                                                      [InlineKeyboardButton(text='Others', callback_data='others')],
                                                      [InlineKeyboardButton(text='Back to Start', callback_data='seller_cancel')]
                                                      ])

# These two keyboards allow the user to terminate the current conversation and go back to the initial stage
keyboard_cancel_input = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Cancel', callback_data='seller_cancel')]])
keyboard_cancel_input2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Back to Start', callback_data='seller_cancel')]])


chat_id = ""

# the 'good' variable is a dictionary used to hold all the data about the good.
# Each time the user inputs sth abt the good, the info is appended into this variable.
# In the end, save_to_json() is called to save the data into GoodsData.json
good = {}


class MainBody(telepot.helper.ChatHandler):
    """
    The MainBody class contains all codes that are responsible for the behaviour of the bot. It contains 6 methods:
    1) __init__(self, *args, **kwargs)
    2) buyer_func(self, good_type)
    3) buyer_selectItem(self, query_data)
    4) save_photo(self)
    5) on_chat_message(self, msg)
    6) on_callback_query(self, msg)
    More explanations are found under each method.
    """

    def __init__(self, *args, **kwargs):
        """
        Defines three fields that are used to control the behaviour of the bot. The fields are undated as the conversation goes on:
        1) self.stage
            A string that represents the stage of the conversation between the user and the bot.
        2) self.BuyOrSell
            A string that represents whether the user is a buyer or a seller.
        3) self.typeViewing
            A string that represents the type of item a buyer is currently viewing.
        """
        super().__init__(include_callback_query=True, *args, **kwargs)
        self.stage = '00'
        self.BuyOrSell = ''
        self.typeViewing = ""

    def buyer_func(self, good_type):
        """
        Parameter:
            good_type: a string representing the type of item a buyer wants to view

        On success, a list of items under the selected type is sent to the buyer, as well as a keyboard for selection.

        """
        good_type = good_type.lower()  # make sure good_type is in lower case

        all_typedGoods = fetch_item_type(good_type)  # creates a list that stores all items under the selected category

        if all_typedGoods == []:  # if no item posted under the selected category, reset self.stage to '01' and send keyboard_type
            self.stage = '01'
            self.sender.sendMessage(
                "There are currently no {0} for sale, maybe you'd like to look at something else?".format(good_type),
                reply_markup=keyboard_type)

        else:
            self.stage = 'Buyer_SelectItem'
            self.typeViewing = good_type
            self.sender.sendMessage(
                "There are currently {0} items for sale. We are getting you the list...".format(len(all_typedGoods)))
            answer = ""  # stores the text to be sent to users

            for posted in all_typedGoods:  # the text is formatted according to different types of items
                if good_type == 'computer':
                    s = "{0}: Brand '{1}', model '{2}', selling at price '{3}'.\n\n".format(
                        all_typedGoods.index(posted) + 1, posted['brand'],
                        posted['model'], posted['price'])

                elif good_type == 'book':
                    s = "{0}: '{1}', written by '{2}', selling at price '{3}'.\n\n".format(
                        all_typedGoods.index(posted) + 1,
                        posted['title'],
                        posted['author'], posted['price'])

                elif good_type == 'stationery':
                    s = "{0}: Stationery of type '{1}', selling at price '{2}'.\n\n".format(
                        all_typedGoods.index(posted)+1,
                        posted['kind'],
                        posted['price'])

                elif good_type == 'others':
                    s = "{0}: It has the following description:\n{1}\nSelling at price {2}.\n\n".format(
                        all_typedGoods.index(posted) + 1,
                        posted['description'], posted['price'])

                elif good_type == 'furniture&home' or good_type == 'clothing&accessories' or good_type == 'gadgets':
                    s = "{0}: A '{1}', selling at price {2}.\n\n".format(all_typedGoods.index(posted)+1,
                                                                         posted['title'], posted['price'])

                answer += s

            time.sleep(0.5)
            self.sender.sendMessage(answer)  # sends the list of items to the buyer

            #  An inline keyboard with buttons corresponding to the index number of each item, as well as a button for cancellation, is defined.
            buttons = []

            for posted in all_typedGoods:  # generate the buttons corresponding to each item
                button0 = [InlineKeyboardButton(text=str(all_typedGoods.index(posted) + 1),
                                                callback_data=str(all_typedGoods.index(posted) + 1))]
                buttons.append(button0)

            buttons.append([InlineKeyboardButton(text='Cancel', callback_data="cancel")])  # add one button for cancellation
            keyboard_items = InlineKeyboardMarkup(inline_keyboard=buttons)

            self.sender.sendMessage(
                "Please select one item to view its details, or choose another type of goods to view.",
                reply_markup=keyboard_items)

    def buyer_selectItem(self, query_data):
        """
        Called when the user has selected the item s/he wants to view. Takes one parameter:
            query_data: a string which is the index of the item under its type. It should be the callback_data from keyboard_items.
        On success, details of the item is sent to the buyer, with an inline keyboard which enables him/her to go back to item selection.
        A keyword is returned for search on Carousell.
        """

        item_viewed = fetch_item_type(self.typeViewing)[int(query_data)-1]

        if self.typeViewing == 'computer':
            answer = "Brand: {0}\nModel: {1}\nPrice: {2}\nDescription: {3}\nPosted on {4}\nContact Details:{5}\n".format(
                item_viewed['brand'], item_viewed['model'], item_viewed['price'], item_viewed['description'],
                item_viewed['time'][0:10], item_viewed['contact'])

            keyword = item_viewed['brand']+" "+ item_viewed['model']

        elif self.typeViewing == 'book':
            answer = "Title: {0}\nAuthor: {1}\nPrice: {2}\nDescription: {3}\nPosted on {4}\nContact Details:{5}\n".format(
                item_viewed['title'], item_viewed['author'], item_viewed['price'], item_viewed['description'],
                item_viewed['time'][0:10], item_viewed['contact'])

            keyword = item_viewed['title']+" "+item_viewed['author']

        elif self.typeViewing == 'stationery':
            answer = "Type: {0}\nPrice: {1}\nDescription: {2}\nPosted on {3}\nContact Details:{4}\n".format(
                item_viewed['type'], item_viewed['price'], item_viewed['description'], item_viewed['time'][0:10],
                item_viewed['contact'])

            keyword = None

        elif self.typeViewing == 'others' or self.typeViewing == 'furniture&home' or self.typeViewing == 'clothing&accessories' or self.typeViewing == 'gadgets':
            answer = "Description: {0}\nPrice: {1}\nContact Details: {2}".format(item_viewed['description'], item_viewed['price'], item_viewed['contact'])

            keyword = None

        self.sender.sendMessage(answer)

        if 'photo' in item_viewed:
            self.sender.sendPhoto(item_viewed['photo'])

        keyboard_viewAnother = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='View Another', callback_data=self.typeViewing)],
                             ])
        self.sender.sendMessage(
            "If you are interested, please contact the seller through the details provided above. Else, click the button below to check out another item.",
            reply_markup=keyboard_viewAnother)

        return keyword

    def save_photo(self):
        """
        Called when the seller has sent a photo of the item. On success, the file_id of the photo is appended to good.
        """
        photo_info = bot.getUpdates()
        file_id = photo_info[0]['message']['photo'][0]['file_id']
        good['photo'] = file_id

        self.sender.sendMessage(
            'We have saved the photo for you! Now please provide your contact details and preferred location for meet-up.', reply_markup=keyboard_cancel_input)

    def on_chat_message(self, msg):
        # called when a message is sent to the bot
        # since a buyer does not need to enter message, this method is primarily for the seller
        global chat_id
        content_type, chat_type, chat_id = telepot.glance(msg)

        #  Firstly the bot checks whether the message is of the type 'text' or 'photo'.
        if content_type == 'text':
            if self.stage == '00':  # the text is a greeting send by the user to start a conversation
                # chat_id and current time are recorded for each item posted by the user
                good['chat_id'] = chat_id
                good['time'] = str(datetime.now())

                self.sender.sendMessage('Yo welcome! Are you a seller or a buyer?\nWarning: Conversation will reset after 180 seconds of inactivity.',
                                        reply_markup=keyboard_0)

            elif self.stage == '14' or self.stage == '24' or self.stage == '33' or self.stage == '53':  # The seller sent a text while a photo of the item is required at this stage.
                self.sender.sendMessage('A picture speaks a thousand words. Please send a photo.', reply_markup=keyboard_cancel_input)

            else:  # the text is send after the greeting. The seller has at least chosen the type of the item to be posted
                if good['type'] == 'computer':  # different types have different areas of information, thus the need to decide the type first
                    if self.stage == '02':
                        # this block is executed after the seller has sent the brand of the computer to the bot.
                        self.stage = '11'  # i.e. brand is sent
                        good['brand'] = msg['text']
                        self.sender.sendMessage(
                            'Brand recorded! Now what is the model? Simply put "idk" if you are not sure!', reply_markup=keyboard_cancel_input)
                        # The seller then sends the model of the computer to the bot,
                        # upon which the programme goes to the next elif block below

                    elif self.stage == '11':
                        self.stage = '12'
                        good['model'] = msg['text']
                        self.sender.sendMessage('Model recorded! How much do you want to sell it for?\nSuggested price from Carousell: ${0}'.format(carousell_price(good['brand']+" "+good['model'])),
                                                reply_markup=keyboard_cancel_input)

                    elif self.stage == '12':
                        self.stage = '13'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Price recorded! Now just tell us more details about the computer.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '13':
                        self.stage = '14'
                        good['description'] = msg['text']
                        self.sender.sendMessage('We\'ve noted that down! Now please send us a photo of the computer.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '15':
                        self.stage = '16'
                        good['contact'] = msg['text']
                        self.sender.sendMessage(
                            'We\'ve recorded that down. Now just wait patiently for anyone interested to contact you...', reply_markup=keyboard_cancel_input2)
                        # The good variable is saved to GoodsData.json, buyer process ends.
                        save_to_json(good)

                    elif self.stage == '16':  # The user is impatient and spamming messages to the bot
                        self.sender.sendMessage('Wait patiently lah pls.', reply_markup=keyboard_cancel_input2)

                elif good['type'] == 'book':
                    if self.stage == '02':
                        self.stage = '21'
                        good['title'] = msg['text']
                        self.sender.sendMessage('Title recorded, please tell us the author now.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '21':
                        self.stage = '22'
                        good['author'] = msg['text']
                        self.sender.sendMessage('Author recorded. Now how much do you wanna sell it for?\nSuggested price from Carousell: ${0}'.format(carousell_price(good['title']+" "+good['author'])),
                                                reply_markup=keyboard_cancel_input)

                    elif self.stage == '22':
                        self.stage = '23'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Price recorded. Tell us more about the book now.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '23':
                        self.stage = '24'
                        good['description'] = msg['text']
                        self.sender.sendMessage('Okay. Now please send us a photo of the book.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '25':
                        self.stage = '26'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('All set. Now please just wait patiently for a buyer to contact you...', reply_markup=keyboard_cancel_input2)
                        save_to_json(good)

                    elif self.stage == '26':
                        self.sender.sendMessage('Patience, friend, patience.', reply_markup=keyboard_cancel_input2)

                elif good['type'] == 'stationery':
                    if self.stage == '02':
                        self.stage = '31'
                        good['kind'] = msg['text']
                        self.sender.sendMessage('Okay, how much do you wanna sell it for?', reply_markup=keyboard_cancel_input)

                    elif self.stage == '31':
                        self.stage = '32'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Fine. Now please describe it a bit more.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '32':
                        self.stage = '33'
                        good['description'] = msg['text']
                        self.sender.sendMessage('Okay, now please send us a photo of it.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '34':
                        self.stage = '35'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('Great. Now just wait for a buyer to contact you.', reply_markup=keyboard_cancel_input2)
                        save_to_json(good)

                    elif self.stage == '35':
                        self.sender.sendMessage('Patience lah pls', reply_markup=keyboard_cancel_input2)

                elif good['type'] == 'others':
                    if self.stage == '02':
                        self.stage = '41'
                        good['description'] = msg['text']
                        self.sender.sendMessage('Okay, how much do you wanna sell it for?', reply_markup=keyboard_cancel_input)

                    elif self.stage == '41':
                        self.stage = '42'
                        good['price'] = msg['text']
                        self.sender.sendMessage(
                            'The price has been recorded. Now please send a photo of the good, or if a photo is not available, please tell us.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '42':
                        self.stage = '43'
                        self.sender.sendMessage(
                            'Alright, no photos for now. Just provide your contact details and preferred location for meet-up, and we\'ll be done.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '43':
                        self.stage = '44'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('We have recorded that down. Now just wait patiently for a buyer...', reply_markup=keyboard_cancel_input2)
                        save_to_json(good)

                    elif self.stage == '44':
                        self.sender.sendMessage('Patience lah bro, it will sell.', reply_markup=keyboard_cancel_input2)

                elif good['type'] == 'furniture&home' or good['type'] == 'clothing&accessories' or good['type'] == 'gadgets':
                    if self.stage == '02':
                        self.stage = '51'
                        good['title'] = msg['text']
                        self.sender.sendMessage('That\'s nice. Now please provide a more detailed description of the item.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '51':
                        self.stage = '52'
                        good['description'] = msg['text']
                        self.sender.sendMessage('We have recorded that down. Now please tell us how much you wanna sell the item for.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '52':
                        self.stage = '53'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Price recorded. Now please send a photo of the item.', reply_markup=keyboard_cancel_input)

                    elif self.stage == '54':
                        self.stage = '55'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('The information has been recorded. Now just wait patiently for a buyer.', reply_markup=keyboard_cancel_input2)
                        save_to_json(good)

                    elif self.stage == '55':
                        self.sender.sendMessage('Patience, my friend.', reply_markup=keyboard_cancel_input2)

        elif content_type == 'photo':
            if self.stage == '14':
                self.stage = '15'
                MainBody.save_photo(self)

            elif self.stage == '24':
                self.stage = '25'
                MainBody.save_photo(self)

            elif self.stage == '33':
                self.stage = '34'
                MainBody.save_photo(self)

            elif self.stage == '42':
                self.stage = '43'
                MainBody.save_photo(self)

            elif self.stage == '53':
                self.stage = '54'
                MainBody.save_photo(self)

            else:  # the seller sent a photo where a text is expected
                self.sender.sendMessage(
                    'A photo? Not really what we expected here... Maybe you should have talked instead?', reply_markup=keyboard_cancel_input)

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if query_data == 'seller_cancel':
            # this block is executed whenever the user clicks 'cancel' in an inline keyboard
            self.stage = '00'
            good['chat_id'] = from_id
            good['time'] = str(datetime.now())
            self.sender.sendMessage('Yo welcome! Are you a seller or a buyer?\nWarning: Conversation will reset after 180 seconds of inactivity.',
                                        reply_markup=keyboard_0)

        if self.stage == '00':  # user has pressed keyboard_0 to indicate seller/buyer identity
            if query_data == 'sell':
                self.stage = 'Seller_PorR'  # Update self.stage as the seller is going to choose whether to post or to remove
                self.BuyOrSell = 'Sell'  # Update the identity of the user
                self.sender.sendMessage(
                    'You are a seller! Are you gonna post a new item or remove an item you have posted? Please remember to remove your item once it\'s sold!',
                    reply_markup=keyboard_PostOrRemove)

            elif query_data == 'buy':
                self.stage = '01'
                self.BuyOrSell = 'Buy'
                self.sender.sendMessage('You are a buyer! What type of good do you wanna buy?',
                                        reply_markup=keyboard_type)

        elif self.stage == '01':  # seller/buyer has chosen the type of item to post/view
            self.stage = '02'  # Update stage to 'has chosen type'
            if self.BuyOrSell == 'Sell':
                good['type'] = query_data
                # response generated according to type of item
                if query_data == 'computer':
                    self.sender.sendMessage('A computer! What brand is it?', reply_markup=keyboard_cancel_input)

                elif query_data == 'book':
                    self.sender.sendMessage('A book! What is the title?', reply_markup=keyboard_cancel_input)

                elif query_data == 'stationery':
                    self.sender.sendMessage('What kind of stationery is it?', reply_markup=keyboard_cancel_input)

                elif query_data == 'others':
                    self.sender.sendMessage('Hmm okay, why not tell us more about it?', reply_markup=keyboard_cancel_input)

                elif query_data == 'furniture&home' or query_data == 'clothing&accessories' or query_data == 'gadgets':
                    self.sender.sendMessage('Okay, what is it? Give us a short title that will attract buyers!', reply_markup=keyboard_cancel_input)

                # After this block the buyer sends a text, which brings us back to on_chat_message() block

            elif self.BuyOrSell == 'Buy':
                # If a buyer has chosen type of item to view, call buyer_func()
                MainBody.buyer_func(self, query_data)

        elif self.stage == 'Seller_PorR':
            # This block is executed when the seller has chosen to post or to remove an item.
            if query_data == 'post':
                self.stage = '01'
                self.sender.sendMessage('A new item! What type of item is it?',
                                        reply_markup=keyboard_type)

            elif query_data == 'remove':
                l = retrieve_items(chat_id)  # load all items posted by the same chat_id to a list
                if l == []:  # no item under the current chat_id
                    self.stage = '01'
                    self.sender.sendMessage(
                        'You have no item posted. To post a new item, start by choosing a category from below.',
                        reply_markup=keyboard_type)

                else:
                    self.sender.sendMessage(
                        'You currently have {0} item(s) posted. We are fetching the details for you...'.format(len(l)))
                    answer = ""

                    for item in l:
                        # generate a string that lists all posted items
                        if item['type'] == 'book':
                            s = "{0}: {1}, titled '{2}', posted on {3}.\n \n".format(l.index(item) + 1, item['type'],
                                                                                     item['title'], item['time'][0:16])
                        elif item['type'] == 'stationery':
                            s = "{0}: {1}, of type '{2}', posted on {3}.\n \n".format(l.index(item) + 1, item['type'],
                                                                                      item['kind'], item['time'][0:16])
                        elif item['type'] == 'computer':
                            s = "{0}: {1}, of brand '{2}' model '{3}', posted on {4}.\n \n".format(l.index(item) + 1,
                                                                                                   item['type'],
                                                                                                   item['brand'],
                                                                                                   item['model'],
                                                                                                   item['time'][0:16])
                        elif item['type'] == 'others':
                            s = "{0}: An item of unidentified type, with description as follow: \n{1}\n Posted on {2}.\n \n".format(
                                l.index(item) + 1, item['description'], item['time'][0:16])

                        elif item['type'] == 'furniture&home' or item['type'] == 'clothing&accessories' or item['type'] == 'gadgets':
                            s = "{0}: A {1}, posted on {2}.\n \n".format(l.index(item)+1, item['title'], item['time'][0:16])

                        answer += s

                    time.sleep(0.5)
                    self.sender.sendMessage(answer)

                    # generates a keyboard for selecting which item to remove
                    buttons = []
                    for item in l:
                        button0 = [InlineKeyboardButton(text=str(l.index(item) + 1), callback_data=str(l.index(item) + 1))]
                        buttons.append(button0)

                    buttons.append([InlineKeyboardButton(text='Cancel', callback_data='cancel')])
                    keyboard_postedItemsIndex = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.sender.sendMessage('Which one are you gonna remove?', reply_markup=keyboard_postedItemsIndex)
                    self.stage = "Seller_R"

        elif self.stage == 'Seller_R':

            if not query_data == 'cancel':
                item_index = int(query_data) - 1
                l = retrieve_items(chat_id)
                item_removed = l[item_index]  # stores the item to be removed
                # load all items in database
                with open('GoodsData.json') as open_file:
                    all_items = json.load(open_file)

                # if an item in the database is the identical with the item to be removed, delete this item
                for each_item in all_items['goods']:
                    if each_item == item_removed:
                        all_items['goods'].remove(each_item)

                # save the edited data to the json file
                with open('GoodsData.json', 'w') as save_file:
                    json.dump(all_items, save_file, indent=4)

                self.stage = 'Seller_PorR'
                self.sender.sendMessage('Item {0} removed successfully!'.format(item_index+1),
                                        reply_markup=InlineKeyboardMarkup(
                                            inline_keyboard=[[InlineKeyboardButton(text="Post a new item",
                                                                                   callback_data='post')]]))
                bot.answerCallbackQuery(query_id)

            else:  # buyer chose 'Cancel' when selecting which item to remove
                self.stage = "Seller_PorR"
                self.sender.sendMessage(
                    "Alright. Press the button if you want to post a new item. Otherwise, just chill.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Post",
                                                                                             callback_data='post')]]))

        elif self.stage == 'Buyer_SelectItem':
            self.stage = '01'  # reset self.stage to get ready for viewing another item
            if query_data != 'cancel':
                keyword = MainBody.buyer_selectItem(self, query_data)

                if keyword is not None:
                    carousell_url = search_carousell(keyword)
                    self.sender.sendMessage('A Carousell page of similar search results has been fetched for your reference:\n' + carousell_url)

            else:  # query_data == 'cancel', buyer wants to choose another type of goods
                self.sender.sendMessage('Okay! Which type of good do you wanna check out this time?',
                                        reply_markup=keyboard_type)

        bot.answerCallbackQuery(query_id)


bot = telepot.DelegatorBot('396242409:AAFPS04xPoPAxRx9YlAopslwP6HJojLQR4c',
                           [pave_event_space()(per_chat_id(), create_open, MainBody, timeout=180)])  # Conversation is terminated after 180s of inactivity

MessageLoop(bot).run_as_thread()

while 1:
    time.sleep(10)
