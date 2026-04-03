import argparse
import random
import json
import os
import csv

def set_maybe(cardlist: list):
    for card_index in range(0, len(cardlist)):
        cardlist[card_index]['maybeboard'] = True
    return cardlist

def set_main(cardlist: list):
    for card_index in range(0, len(cardlist)):
        cardlist[card_index]['maybeboard'] = False
    return cardlist

def populate_database(database_filename: str):
    with open(database_filename, "r") as database_file:
        database = json.load(database_file)
        return database

def get_real_cardname(database: dict, cardname: str):
    if cardname in database.keys():
        return cardname
    else:
        for cardkey in database.keys():
            if ("{} // ".format(cardname) in cardkey) and (cardkey != "{} // {}".format(cardname, cardname)):
                return cardkey
        # we haven't returned yet
        for cardname_iter in database.keys():
            for eachcard in database[cardname_iter]:
                if ("flavor_name" in eachcard.keys()) and (eachcard["flavor_name"] == cardname):
                    return cardname_iter
                elif ("printed_name" in eachcard.keys()) and (eachcard["printed_name"] == cardname):
                    return cardname_iter
        else:
            print("Error, could not find card: {}".format(cardname))
            exit()
    return

def cardlistdict(cardliststr: str):
    thisdict = []
    eachquantsplit = cardliststr.split(',')
    totalcards = 0
    for eachkeypair in eachquantsplit:
        keyval = eachkeypair.split(':')
        localkey = keyval[0]
        localval = int(keyval[1])
        totalcards += localval
        thisdict.append((localkey, localval))
        # thisdict[localkey] = localval
    return thisdict, totalcards

def write_cardlistcsv(filename: str, useddict: list, fieldnames):
        # return
        with open(filename, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the header row
            writer.writeheader()

            # Write the data rows
            writer.writerows(useddict)


def ret_card(cardlist: list, cardno: int):
    counter = 0
    for costlist in cardlist:
        if cardno < (costlist[1] + counter):
            return costlist[0], (cardno - counter)
        counter += costlist[1]
    return None

def ret_card_csv(cardlist: list, cardno: int):
    return cardlist[cardno]

def cardlistcsv(cardlist_csv: str) -> tuple[list, list, int]:
    """
    Docstring for cardlistcsv
    
    :param cardlist_csv: Description
    :type cardlist_csv: str
    Returns
    fieldnames list, dictreader, num of cards
    """
    with open(cardlist_csv, mode='r', newline='', encoding='utf-8') as csvfile:
        # Create a DictReader object
        dict_reader = csv.DictReader(csvfile)
        fieldnames = dict_reader.fieldnames
        # Iterate through each row (as a dictionary) and print specific columns
        dict_reader_l = list(dict_reader)
        return fieldnames, dict_reader_l, len(dict_reader_l)

def get_block_card(card: dict, block='image_uris'):
    """
    Docstring for get_block_card
    
    :param self: Description
    :param card: scryfall card in
    :type card: dict
    :param card_in: cube cobra card in
    :type card_in: dict
    :param block: which key we want from the primary face
    """
    if block in card.keys():
        return card
    else:
        if ('mtgo_id' in card.keys()):
            if "card_faces" in card.keys() and len(card["card_faces"]) > 1:
                card_out = card["card_faces"][0]
            else:
                card_out = card
            return card_out
    return None


def search_database(database:list, cardname:str, setnamelist_in:list):
    for card in database:
        if ((card['name'] == cardname) or ("{} // ".format(cardname) in card['name'])) and (card['set'] in setnamelist_in):
            return card
    return None

def search_dictified_database(database: dict, cardname:str, setnamelist_in:list):
    carlist_local = database[cardname]
    for card in carlist_local:
        if (card['set'] in setnamelist_in):
            return card
    return None

def search_database_all_hits(database:list, cardname:str):
    cardlist = []
    setlist = []
    databaserange = range(0, len(database))
    for card_index in databaserange:
        card = database[card_index]
        if (card['name'] == cardname) and (card['set'] not in setlist):
            setlist.append(card['set'])
            cardlist.append(card)
    return cardlist, setlist


def get_card_sets(all_sets, cardname: str):
    card_set_list = []
    all_sets_list = range(0, len(all_sets.data))
    for set_obj_index in tqdm(all_sets_list):
        set_obj = all_sets.data[set_obj_index]
        search_str = 's:{} !"{}"'.format(set_obj.code, cardname)
        print(search_str)
        try:
            results_local = scrython.cards.Search(q=search_str)
            if len(results_local) > 0:
                card_set_list.append(results_local.data[0])
        except:
            print("set:{} has no such card".format(set_obj.code))
    return card_set_list

