import argparse
import os
import json
from txt_to_cc import FIELDNAME_RAW, txt_to_cc
from setprim import write_cardlistcsv
from dup_sets import populate_database

def main(args):
    cardlist_out = []
    scryfall_cardlist = populate_database(args.scryfall_list)
    scryfall_carddict = populate_database(args.scryfall_dict)
    for card in scryfall_cardlist:
        if card['set'] == args.setcode:
            cardname = card["name"]
            if cardname not in cardlist_out:
                cardlist_out.append(cardname)
    if args.outfile == None:
        for card in cardlist_out:
            print(card)
    else:
        cardlist_out_cc = txt_to_cc(scryfall_carddict, cardlist_out, args.setcode)
        write_cardlistcsv(cardlist_out_cc, args.outfile, FIELDNAME_RAW.split(','))
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("cards_in_set")
    argparser.add_argument("scryfall_list", help="scryfall list to search")
    argparser.add_argument("scryfall_dict", help="scryfall dict to search")
    argparser.add_argument("setcode", help="setcode to find")
    argparser.add_argument("--outfile", help="outfile to write")
    args = argparser.parse_args()
    main(args)