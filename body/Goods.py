"""
This module provides the following functions:
    1) save_to_json(data_dict)
    2) retrieve_items(chat_id)
    3) save_to_xlsx(data_list, good_type=None):
    4) fetch_item(type)

Note that save_to_xlsx is not called in the main body. This is a feature initially introduced, but then removed in a
later version. However I decided not to delete the code and kept it.
"""

import json
import openpyxl


def save_to_json(data_dict):
    """
    data_dict is a python dictionary representing an item to be posted.
    On success, the data is written in json format to GoodsData.json
    """
    with open('GoodsData.json') as json_file:
        data = json.load(json_file)

    data['goods'].append(data_dict)

    with open('GoodsData.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=False, indent=4)


def retrieve_items(chat_id):
    """
    Takes one parameter:
        chat_id: a string which is the chat_id of the current conversation
    On success, returns a list of dictionaries.
    """
    chat_id = chat_id

    with open('GoodsData.json') as json_file:
        data = json.load(json_file)
        answer = []
        for good in data['goods']:
            if good['chat_id'] == chat_id:
                answer.append(good)
        return answer


def save_to_xlsx(data_dict, good_type=None):
    # NOTE: This function is not called in the main body, but I decided to keep it anyway.
    # If you want to test it, create a xlsx file and name it output.xlsx under the bot's directory.
    data_book = openpyxl.load_workbook('output.xlsx')
    if good_type == 'computer':
        sheet = data_book['Computer']
        sheet.append(tuple(data_dict.values()))
        data_book.save('output.xlsx')

    elif good_type == 'book':
        sheet = data_book['Book']
        sheet.append(tuple(data_dict.values()))
        data_book.save('output.xlsx')

    elif good_type == 'stationery':
        sheet = data_book['Stationery']
        sheet.append(tuple(data_dict.values()))
        data_book.save('output.xlsx')

    else:
        sheet = data_book['Others']
        sheet.append(tuple(data_dict.values()))
        data_book.save('output.xlsx')

def fetch_item_type(type):
    """
    Loads all item of a given type.
    param type: a string representing a type of items
    return: a list of dictionaries representing the items
    """
    with open('GoodsData.json') as open_file:
        all_goods = json.load(open_file)
        answer = []
        for good in all_goods['goods']:
            if good['type'] == type:
                answer.append(good)
        return answer
