import scrython
import argparse
import tqdm
import json
import os
from cardrand import cardlistcsv, write_cardlistcsv
from balancing import index_of_card_in_list

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
            print(cardname)
            exit()
    return

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


def main(args):
    # all_sets = scrython.sets.All()
    # get_card_sets(all_sets, "Lightning Bolt")
    # for card in cardlist_raw:
    database = populate_database(args.database)
    fieldnames, drl, drll = cardlistcsv(args.cardlist)
    card_set_list = []
    card_set_list_old = []
    drl_range = range(0, len(drl))
    setcodelist_in = args.setcode
    prevsetlist = None
    card_set_list_old_len = 0

    if (args.append == True) and (os.path.exists(args.outfile)):
        _, prevsetlist, card_set_list_old_len = cardlistcsv(args.outfile)
        print("going to append to our file {} with {} cards".format(args.outfile, card_set_list_old_len))

    # check older first
    for card_index in tqdm.tqdm(drl_range):
        card = drl[card_index]
        if prevsetlist != None:
            previndex = index_of_card_in_list(card, prevsetlist)
            # if it is not none, we can still get a positive! we just need to add it to the maybeboard
            # and then that will be that.
            if previndex != None:
                continue
        # if we found a card, and its in our setlist but we are appending, we can assume that it can
        # be put onto the maybeboard
        if card['Set'] in setcodelist_in:
            card_set_list.append(card)
            card_set_list_old.append(card)
            continue
        if args.dictified == True:
            cardname_temp = get_real_cardname(database, card['name'])
            if search_dictified_database(database, cardname_temp, setcodelist_in) != None:
                card_set_list.append(card)
        else:
            if search_database(database, card['name'], setcodelist_in) != None:
                card_set_list.append(card)
        # cardlist_local, setlist_local = search_database_all_hits(database, card['name'])
        # if args.setcode in setlist_local:
        #     card_set_list.append(card)
    if card_set_list_old_len == 0:
        card_set_list_old_len = len(card_set_list_old)
        card_set_list_len = len(card_set_list)
    else:
        card_set_list_len = len(card_set_list) + len(prevsetlist)
    print("had {}, now have {}".format(card_set_list_old_len, card_set_list_len))
    if args.outfile != None:
        filename = "inorganic.{}".format(os.path.basename(args.outfile))
        filename = os.path.join(os.path.dirname(args.outfile), filename)
        if prevsetlist != None:
            for card in card_set_list:
                if args.force_main == True:
                    card['maybeboard'] = False
                else:
                    card['maybeboard'] = True
            card_set_list = prevsetlist + card_set_list
        write_cardlistcsv(filename, card_set_list, fieldnames)
        print("wrote to file {}".format(filename))
    else:
        for card in card_set_list:
            print(card['name'])
        print("Once again, had {}, now have {}".format(card_set_list_old_len, card_set_list_len))
    return

if __name__ == "__main__":
    # help="tool to find all cards in a cardlist that belong to a setcode"
    argparser = argparse.ArgumentParser("dup_sets")
    argparser.add_argument("cardlist", help="cardlist to find dups for")
    argparser.add_argument("database", help="database in to use")
    argparser.add_argument("--dictified", action="store_true", help="database has been dictified")
    argparser.add_argument("--force_main", action="store_true", help="force cards to main board")
    argparser.add_argument("--outfile", help="where the output should go")
    argparser.add_argument("--append", action="store_true", help="append to outfile")
    argparser.add_argument("setcode", nargs="+", help="codes to use for a set to find")
    args = argparser.parse_args()
    main(args)