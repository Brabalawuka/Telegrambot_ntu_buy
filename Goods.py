"""

Two methods are defined to output the data stored in the object:
    1) save_to_json(data_dict):
        Takes a dictionary of field: value pairs as parameter, writes the data in json format into a txt file.
    2) save_to_xlsx(data_list, good_type=None):
        Takes a list of values of all fields as parameter, writes the data into a xlsx file, in which different
        sheets are named after the type of good they store.
"""

import json
import openpyxl



def save_to_json(data_dict):  # takes a dict as parameter
    with open('GoodsData.txt') as json_file:
        data = json.load(json_file)

    data['goods'].append(data_dict)

    with open('GoodsData.txt', 'w') as outfile:
        json.dump(data, outfile, sort_keys=False, indent=4)


def retrieve_items(chat_id):
    chat_id = chat_id

    with open('GoodsData.txt') as json_file:
        data = json.load(json_file)
        answer = []
        for good in data['goods']:
            if good['chat_id'] == chat_id:
                answer.append(good)
        return answer

def save_to_xlsx(data_dict, good_type=None):  # takes a dict
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
    with open('GoodsData.txt') as open_file:
        all_goods = json.load(open_file)
        answer = []
        for good in all_goods['goods']:
            if good['type'] == type:
                answer.append(good)
        return answer