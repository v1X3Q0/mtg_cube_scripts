import scrython
import argparse
import tqdm
import json
import os
from cardrand import cardlistcsv, write_cardlistcsv

def populate_database(database_filename: str):
    with open(database_filename, "r") as database_file:
        database = json.load(database_file)
        return database
    
def search_database(database:list, cardname:str, setnamelist_in:list):
    for card in database:
        if (card['name'] == cardname) and (card['set'] in setnamelist_in):
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

    # check older first
    for card_index in tqdm.tqdm(drl_range):
        card = drl[card_index]
        if card['Set'] in setcodelist_in:
            card_set_list.append(card)
            card_set_list_old.append(card)
            continue
        if search_database(database, card['name'], setcodelist_in) != None:
            card_set_list.append(card)
        # cardlist_local, setlist_local = search_database_all_hits(database, card['name'])
        # if args.setcode in setlist_local:
        #     card_set_list.append(card)
    print("had {}, now have {}".format(len(card_set_list_old), len(card_set_list)))
    filename = "inorganic.{}".format(os.path.basename(args.outfile))
    filename = os.path.join(os.path.dirname(args.outfile), filename)
    write_cardlistcsv(filename, card_set_list, fieldnames)
    print("wrote to file {}".format(filename))
    return

if __name__ == "__main__":
    # help="tool to find all cards in a cardlist that belong to a setcode"
    argparser = argparse.ArgumentParser("dup_sets")
    argparser.add_argument("cardlist", help="cardlist to find dups for")
    argparser.add_argument("database", help="database in to use")
    argparser.add_argument("outfile", help="where the output should go")
    argparser.add_argument("setcode", nargs="+", help="codes to use for a set to find")
    args = argparser.parse_args()
    main(args)