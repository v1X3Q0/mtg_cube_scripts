import argparse
import os
import json
from txt_to_cc import FIELDNAME_RAW, txt_to_cc
from util_cardlist import populate_database, write_cardlistcsv, cardlistcsv

def subcardlists(cardlist_big: dict, cardlist_small: dict):
    card_diff_list = []
    countnum = 0
    for card_b in cardlist_big:
        name = card_b['name']
        for card_s in cardlist_small:
            if card_s['name'] == name:
                countnum += 1
                # print("found {}'th match: {}".format(countnum, name))
                break
        else:
            card_diff_list.append(card_b)
    return card_diff_list

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
        if args.subfile != None:
            _, past_cardlist, _ = cardlistcsv(args.subfile)
            actual_cardlist_len = len(cardlist_out_cc)
            cardlist_out_cc = subcardlists(cardlist_out_cc, past_cardlist)
            print("the list length was {}, but you need {} cards".format(actual_cardlist_len, len(cardlist_out_cc)))
        write_cardlistcsv(args.outfile, cardlist_out_cc, FIELDNAME_RAW.split(','))
        print("wrote cardlist to {}".format(args.outfile))
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("cards_in_set")
    argparser.add_argument("scryfall_list", help="scryfall list to search")
    argparser.add_argument("scryfall_dict", help="scryfall dict to search")
    argparser.add_argument("setcode", help="setcode to find")
    argparser.add_argument("--outfile", help="outfile to write")
    argparser.add_argument("--subfile", help="cardlist to subtract from cards in set")
    args = argparser.parse_args()
    main(args)