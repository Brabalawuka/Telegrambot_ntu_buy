#  First written on 26/09/17, based on body 0.2.2
#  Buyer-side codes are now almost complete.
#  To be added in 0.2.3: integrate ZZSearch

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from telepot.delegate import pave_event_space, create_open, per_chat_id
from Goods import save_to_json, save_to_xlsx, retrieve_items, fetch_item_type
from ZZsearch import search_amazon, search_carousell, split_keywords
import time
from datetime import datetime
import json
from pprint import pprint

"""
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

"""

keyboard_0 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Sell', callback_data='Sell')],
                                                   [InlineKeyboardButton(text='Buy', callback_data='Buy')], ])

keyboard_PostOrRemove = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Post', callback_data='Post')],
                                                              [InlineKeyboardButton(text='Remove',
                                                                                    callback_data='Remove')], ])

keyboard_type = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Computer', callback_data='Computer')],
                                                      [InlineKeyboardButton(text='Book', callback_data='Book')],
                                                      [InlineKeyboardButton(text='Stationery',
                                                                            callback_data='Stationery')],
                                                      [InlineKeyboardButton(text='Others', callback_data='Others')]
                                                      ])

chat_id = ""

good = {}
# the 'good' variable is a dictionary used to hold all data about the good.
# Each time the user inputs sth abt the good, the info is appended into this variable.
# In the end, save_to_json() is called to save the variable into a json file, while
# save_to_xlsx() is called to save to a xlsx file.

class MainBody(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(include_callback_query=True, *args, **kwargs)
        self.stage = '00'
        self.BuyOrSell = ''
        self.typeViewing = ""

    def on_chat_message(self, msg):
        global chat_id
        content_type, chat_type, chat_id = telepot.glance(msg)
        # 1 text or photo. Assume text:
        # 2 initialisation stage? assume not, good type must have been specified!
        if content_type == 'text':
            if self.stage == '00':  # if this is the greeting
                good['chat_id'] = chat_id
                good['time'] = str(datetime.now())
                self.sender.sendMessage('Yo welcome! Are you a seller or a buyer?',
                                        reply_markup=keyboard_0)

            elif self.stage == '14' or self.stage == '24' or self.stage == '33':
                self.sender.sendMessage('A picture speaks a thousand words. Please send a photo.')

            else:  # self.stage >= 02, meaning that type has been defined.
                if good['type'] == 'computer':
                    if self.stage == '02':  # if self.stage == '02': user sent a message of X1 after having chosen type.
                        self.stage = '11'
                        good['brand'] = msg['text']
                        self.sender.sendMessage(
                            'Brand recorded! Now what is the model? Simply put "idk" if you are not sure!')

                    elif self.stage == '11':
                        self.stage = '12'
                        good['model'] = msg['text']
                        self.sender.sendMessage('Model recorded! How much do you want to sell it for?')

                    elif self.stage == '12':
                        self.stage = '13'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Price recorded! Now just tell us more details about the computer.')

                    elif self.stage == '13':
                        self.stage = '14'
                        good['description'] = msg['text']
                        self.sender.sendMessage('We\'ve noted that down! Now please send us a photo of the computer.')

                    elif self.stage == '15':
                        self.stage = '16'
                        good['contact'] = msg['text']
                        self.sender.sendMessage(
                            'We\'ve recorded that down. Now just wait patiently for anyone interested to contact you...')
                        # the following two lines save the 'good' object to the .txt and .xlsx files respectively
                        save_to_json(good)
                        save_to_xlsx(good, good_type='computer')  # END

                    elif self.stage == '16':
                        self.sender.sendMessage('Wait patiently lah pls.')

                elif good['type'] == 'book':
                    if self.stage == '02':
                        self.stage = '21'
                        good['title'] = msg['text']
                        self.sender.sendMessage('Title recorded, please tell us the author now.')

                    elif self.stage == '21':
                        self.stage = '22'
                        good['author'] = msg['text']
                        self.sender.sendMessage('Author recorded. Now how much do you wanna sell it for?')

                    elif self.stage == '22':
                        self.stage = '23'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Price recorded. Tell us more about the book now.')

                    elif self.stage == '23':
                        self.stage = '24'
                        good['description'] = msg['text']
                        self.sender.sendMessage('Okay. Now please send us a photo of the book.')

                    elif self.stage == '25':
                        self.stage = '26'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('All set. Now please just wait patiently for a buyer to contact you...')
                        save_to_json(good)
                        save_to_xlsx(good, good_type='book')  # END

                    elif self.stage == '26':
                        self.sender.sendMessage('Patience, friend, patience.')

                elif good['type'] == 'stationery':
                    if self.stage == '02':
                        self.stage = '31'
                        good['kind'] = msg['text']
                        self.sender.sendMessage('Okay, how much do you wanna sell it for?')

                    elif self.stage == '31':
                        self.stage = '32'
                        good['price'] = msg['text']
                        self.sender.sendMessage('Fine. Now please describe it a bit more.')

                    elif self.stage == '32':
                        self.stage = '33'
                        good['description'] = msg['text']
                        self.sender.sendMessage('Okay, now please send us a photo of it.')

                    elif self.stage == '34':
                        self.stage = '35'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('Great. Now just wait for a buyer to contact you.')
                        save_to_json(good)
                        save_to_xlsx(good, good_type='stationery')  # END

                    elif self.stage == '35':
                        self.sender.sendMessage('Patience lah pls')

                elif good['type'] == 'others':
                    if self.stage == '02':
                        self.stage = '41'
                        good['description'] = msg['text']
                        self.sender.sendMessage('Okay, how much do you wanna sell it for?')

                    elif self.stage == '41':
                        self.stage = '42'
                        good['price'] = msg['text']
                        self.sender.sendMessage(
                            'The price has been recorded. Now please send a photo of the good, or if a photo is not available, please tell us.')

                    elif self.stage == '42':
                        self.stage = '43'
                        self.sender.sendMessage(
                            'Alright, no photos for now. Just provide your contact details and we\'ll be done.')

                    elif self.stage == '43':
                        self.stage = '44'
                        good['contact'] = msg['text']
                        self.sender.sendMessage('We have recorded that down. Now just wait patiently for a buyer...')
                        save_to_json(good)
                        save_to_xlsx(good, good_type='others')  # END

                    elif self.stage == '44':
                        self.sender.sendMessage('Patience lah bro, it will sell.')

        elif content_type == 'photo':
            if self.stage == '14':
                self.stage = '15'
                photo_info = bot.getUpdates()
                file_id = photo_info[0]['message']['photo'][0]['file_id']
                good['photo'] = file_id
                self.sender.sendMessage('We have saved the photo for you! Now please provide your contact details.')

            elif self.stage == '24':
                self.stage = '25'
                photo_info = bot.getUpdates()
                file_id = photo_info[0]['message']['photo'][0]['file_id']
                good['photo'] = file_id
                self.sender.sendMessage('We have saved the photo, now please provide your contact details.')

            elif self.stage == '33':
                self.stage = '34'
                photo_info = bot.getUpdates()
                file_id = photo_info[0]['message']['photo'][0]['file_id']
                good['photo'] = file_id
                self.sender.sendMessage('We have saved the photo, now please provide your contact details.')

            elif self.stage == '42':
                self.stage = '43'
                photo_info = bot.getUpdates()
                file_id = photo_info[0]['message']['photo'][0]['file_id']
                good['photo'] = file_id
                self.sender.sendMessage('We have saved the photo, now please provide your contact details.')

            else:
                self.sender.sendMessage(
                    'A photo? Not really what we expected here... Maybe you should have talked instead?')

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if self.stage == '00':  # if user has pressed keyboard_0
            if query_data == 'Sell':
                self.stage = 'Seller_PorR'  # Update self.stage to 'now choosing post or edit'
                self.BuyOrSell = 'Sell'
                self.sender.sendMessage(
                    'You are a seller! Are you gonna post a new item or remove an item you have posted?',
                    reply_markup=keyboard_PostOrRemove)

            elif query_data == 'Buy':
                self.stage = '01'
                self.BuyOrSell = 'Buy'
                self.sender.sendMessage('You are a buyer! What type of good do you wanna buy?',
                                        reply_markup=keyboard_type)

        elif self.stage == '01':  # if user has chosen sell/buy
            self.stage = '02'  # Update stage to 'has chosen type'
            if self.BuyOrSell == 'Sell':
                if query_data == 'Computer':
                    good['type'] = 'computer'
                    self.sender.sendMessage('A computer! What brand is it?')

                elif query_data == 'Book':
                    good['type'] = 'book'
                    self.sender.sendMessage('A book! What is the title?')

                elif query_data == 'Stationery':
                    good['type'] = 'stationery'
                    self.sender.sendMessage('What kind of stationery is it?')

                elif query_data == 'Others':
                    good['type'] = 'others'
                    self.sender.sendMessage('Hmm okay, why not tell us more about it?')

                # After this block the buyer sends a text, which brings us back to on_chat_message

            elif self.BuyOrSell == 'Buy':
                if query_data == 'Computer':  # user selected 'Buy' and then "Computer"
                    all_computers = fetch_item_type('computer')
                    if all_computers == []:
                        self.stage = '01'
                        self.sender.sendMessage("There are currently no computers for sale. Maybe you'd like to look at something else?",
                                                reply_markup=keyboard_type)
                    else:
                        self.stage = 'Buyer_SelectItem'
                        self.typeViewing = 'computer'
                        self.sender.sendMessage("There are {0} computers currently for sale. We are getting you the list...".format(len(all_computers)))
                        answer = ""
                        for posted in all_computers:
                            s = "{0}: Brand '{1}', model '{2}', selling at price '{3}'.\n \n".format(all_computers.index(posted)+1, posted['brand'],
                                                                                                 posted['model'], posted['price'])
                            answer += s

                        time.sleep(0.5)
                        self.sender.sendMessage(answer)

                        buttons = []
                        for posted in all_computers:
                            button0 = [InlineKeyboardButton(text=str(all_computers.index(posted)+1),
                                                            callback_data=str(all_computers.index(posted)+1))]
                            buttons.append(button0)
                        buttons.append([InlineKeyboardButton(text='Cancel', callback_data="cancel")])
                        keyboard_computers = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.sender.sendMessage("Please select one item to view its details, or choose another type of goods to view.",
                                                reply_markup=keyboard_computers)

                elif query_data == 'Book':
                    all_books = fetch_item_type('book')
                    if all_books == []:
                        self.stage ='01'
                        self.sender.sendMessage("There are currently no books for sale. Maybe you'd like to look at something else?",
                                                reply_markup=keyboard_type)
                    else:
                        self.stage = 'Buyer_SelectItem'
                        self.typeViewing = 'book'
                        self.sender.sendMessage("There are {0} books currently for sale. We are getting you the list...".format(len(all_books)))
                        answer = ""
                        for posted in all_books:
                            s = "{0}: '{1}', written by '{2}', selling at price '{3}'.\n\n".format(all_books.index(posted)+1, posted['title'],
                                                                                                   posted['author'], posted['price'])
                            answer += s

                        time.sleep(0.5)
                        self.sender.sendMessage(answer)

                        buttons = []
                        for posted in all_books:
                            button0 = [InlineKeyboardButton(text=str(all_books.index(posted)+1),
                                                            callback_data=str(all_books.index(posted)+1))]
                            buttons.append(button0)
                        buttons.append([InlineKeyboardButton(text='Cancel', callback_data="cancel")])
                        keyboard_books = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.sender.sendMessage("Please select one item to view its details, or choose another type of goods to view.",
                                                reply_markup=keyboard_books)

                elif query_data == 'Stationery':
                    all_stationery = fetch_item_type('stationery')
                    if all_stationery == []:
                        self.stage = '01'
                        self.sender.sendMessage("There are currently no stationery for sale. Maybe you'd like to look at something else?",
                                                reply_markup=keyboard_type)
                    else:
                        self.stage = 'Buyer_SelectItem'
                        self.typeViewing = 'stationery'
                        self.sender.sendMessage("There are {0} pieces of stationery currently for sale. We are getting you the list...".format(len(all_stationery)))
                        answer = ""
                        for posted in all_stationery:
                            s = "{0}: Stationery of type '{1}', selling at price '{2}'.\n\n".format(all_stationery.index(posted)+1, posted['kind'],
                                                                                                   posted['price'])
                            answer += s

                        time.sleep(0.5)
                        self.sender.sendMessage(answer)

                        buttons = []
                        for posted in all_stationery:
                            button0 = [InlineKeyboardButton(text=str(all_stationery.index(posted)+1),
                                                            callback_data=str(all_stationery.index(posted)+1))]
                            buttons.append(button0)
                        buttons.append([InlineKeyboardButton(text='Cancel', callback_data="cancel")])
                        keyboard_stationery = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.sender.sendMessage("Please select one item to view its details, or choose another type of goods to view.",
                                                reply_markup=keyboard_stationery)

                elif query_data == "Others":
                    all_others = fetch_item_type('others')
                    if all_others == []:
                        self.stage = '01'
                        self.sender.sendMessage("There are currently no goods under this category. Do you wanna browse under another type?",
                                                reply_markup=keyboard_type)

                    else:
                        self.stage = 'Buyer_SelectItem'
                        self.typeViewing = 'others'
                        self.sender.sendMessage("There are currently {0} goods under this category. We are getting you the list...".format(len(all_others)))
                        answer = ""
                        for posted in all_others:
                            s = "{0}: It has the following description:\n{1}\nSelling at price {2}.\n\n".format(all_others.index(posted)+1,
                                                                                                                posted['description'], posted['price'])
                            answer += s

                        time.sleep(0.5)
                        self.sender.sendMessage(answer)

                        buttons = []
                        for posted in all_others:
                            button0 = [InlineKeyboardButton(text=str(all_others.index(posted)+1), callback_data=str(all_others.index(posted)+1))]
                            buttons.append(button0)
                        buttons.append([InlineKeyboardButton(text='Cancel', callback_data='cancel')])
                        keyboard_other = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.sender.sendMessage("If you are interested in an item, you can select its index number to view the seller's contact details and its photo, if the user has uploaded one.",
                                                reply_markup=keyboard_other)

        elif self.stage == 'Seller_PorR':
            if query_data == 'Post':
                self.stage = '01'
                self.sender.sendMessage('A new item! What type of item is it?',
                                        reply_markup=keyboard_type)

            elif query_data == 'Remove':
                l = retrieve_items(chat_id)
                if l == []:
                    self.sender.sendMessage(
                        'You have no item posted. To post a new item, start by choosing a category from below.',
                        reply_markup=keyboard_type)

                else:
                    self.sender.sendMessage(
                        'You currently have {0} item(s) posted. We are fetching the details for you...'.format(len(l)))
                    answer = ""
                    for item in l:
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
                                l.index(item) + 1, item['description'],
                                item['time'][0:16])
                        answer += s

                    time.sleep(0.5)
                    self.sender.sendMessage(answer)

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
                item_removed = l[item_index]
                with open('GoodsData.txt') as open_file:
                    all_items = json.load(open_file)

                for each_item in all_items['goods']:
                    if each_item == item_removed:
                        all_items['goods'].remove(each_item)

                with open('GoodsData.txt', 'w') as save_file:
                    json.dump(all_items, save_file, indent=4)

                self.stage = 'Seller_PorR'
                self.sender.sendMessage('Item {0} removed successfully!'.format(item_index),
                                        reply_markup=InlineKeyboardMarkup(
                                            inline_keyboard=[[InlineKeyboardButton(text="Post a new item",
                                                                                   callback_data='Post')]]))
                bot.answerCallbackQuery(query_id)

            else:
                self.stage = "Seller_PorR"
                self.sender.sendMessage(
                    "Alright. Press the button if you want to post a new item. Otherwise, just chill.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Post",
                                                                                             callback_data='Post')]]))

        elif self.stage == 'Buyer_SelectItem':
            if query_data != 'cancel':
                self.stage = '01'  # get ready to be sent back to choosing another item of the same type
                if self.typeViewing == 'computer':
                    item_viewed = fetch_item_type('computer')[int(query_data)-1]
                    answer = "Brand: {0}\nModel: {1}\nPrice: {2}\nDescription: {3}\nPosted on {4}\nContact Details:{5}\n".format(item_viewed['brand'], item_viewed['model'], item_viewed['price'], item_viewed['description'], item_viewed['time'][0:10], item_viewed['contact'])
                    self.sender.sendMessage(answer)
                    self.sender.sendPhoto(item_viewed['photo'])
                    keyboard_viewAnother=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='View Another', callback_data='Computer')]])
                    self.sender.sendMessage("If you are interested, please contact the seller through the details provided above. Else, click the button below to check out another computer.",
                                            reply_markup=keyboard_viewAnother)

                elif self.typeViewing == 'book':
                    item_viewed = fetch_item_type('book')[int(query_data)-1]
                    answer = "Title: {0}\nAuthor: {1}\nPrice: {2}\nDescription: {3}\nPosted on {4}\nContact Details:{5}\n".format(item_viewed['title'], item_viewed['author'], item_viewed['price'], item_viewed['description'], item_viewed['time'][0:10], item_viewed['contact'])
                    self.sender.sendMessage(answer)
                    self.sender.sendPhoto(item_viewed['photo'])
                    keyboard_viewAnother=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='View Another', callback_data='Book')]])
                    self.sender.sendMessage("If you are interested, please contact the seller through the details provided above. Else, click the button below to check out another book.",
                                            reply_markup=keyboard_viewAnother)

                elif self.typeViewing == 'stationery':
                    item_viewed = fetch_item_type('stationery')[int(query_data)-1]
                    answer = "Type: {0}\nPrice: {1}\nDescription: {2}\nPosted on {3}\nContact Details:{4}\n".format(item_viewed['type'], item_viewed['price'], item_viewed['description'], item_viewed['time'][0:10], item_viewed['contact'])
                    self.sender.sendMessage(answer)
                    self.sender.sendPhoto(item_viewed['photo'])
                    keyboard_viewAnother=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='View Another', callback_data='Stationery')]])
                    self.sender.sendMessage("If you are interested, please contact the seller through the details provided above. Else, click the button below to check out another one.",
                                            reply_markup=keyboard_viewAnother)

                elif self.typeViewing == 'others':
                    item_viewed = fetch_item_type('others')[int(query_data)-1]
                    answer = "Contact Details: {0}".format(item_viewed['contact'])
                    self.sender.sendMessage(answer)
                    if 'photo' in item_viewed:
                        self.sender.sendPhoto(item_viewed['photo'])
                    keyboard_viewAnother=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='View Another', callback_data='Others')]])
                    self.sender.sendMessage("If you are interested, please contact the seller through the details provided above. Else, click the button below to check out another one.",
                                            reply_markup=keyboard_viewAnother)

            else: # query_data == 'cancel', buyer wants to choose another type of goods
                self.stage = '01'
                self.sender.sendMessage('Okay! Which type of good do you wanna check out this time?',
                                        reply_markup=keyboard_type)

        bot.answerCallbackQuery(query_id)


bot = telepot.DelegatorBot("314595812:AAG4i3an7TD3fLdpwHvP_L8pGZejpltAabc",
                           [pave_event_space()(per_chat_id(), create_open, MainBody, timeout=60)])

MessageLoop(bot).run_as_thread()

while 1:
    time.sleep(10)
