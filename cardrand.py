import argparse
import random
import json
import os
import csv
from balancing import balancing_main

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

def cardlistcsv(cardlist_csv: str):
    """
    Returns:
    fieldnames, dictreader list, len(dictreader list)    
    """
    with open(cardlist_csv, mode='r', newline='', encoding='utf-8') as csvfile:
        # Create a DictReader object
        dict_reader = csv.DictReader(csvfile)
        fieldnames = dict_reader.fieldnames
        # Iterate through each row (as a dictionary) and print specific columns
        dict_reader_l = list(dict_reader)
        return fieldnames, dict_reader_l, len(dict_reader_l)

def main(args):
    if args.cardlist_counts != None:
        cardlist, totalcards = cardlistdict(args.cardlist_counts)
        useddict = {}
        for i in cardlist:
            useddict[i[0]] = []
    elif args.cardlist_csv != None:
        fieldnames, cardlist, totalcards = cardlistcsv(args.cardlist_csv)
        useddict = cardlist.copy()
    cube_count = args.cube_count
    if cube_count > totalcards:
        print("WARNING: not enough cards in this set! Have {} need {}".format(totalcards, cube_count))
    if args.bell == False:
        unique_random_integers = random.sample(range(0, totalcards), cube_count)
        if args.cardlist_counts != None:
            for random_card in unique_random_integers:
                cardpair = ret_card(cardlist, random_card)
                useddict[cardpair[0]].append(cardpair[1])
        if args.cardlist_csv != None:
            for card in range(0, totalcards):
                if card in unique_random_integers:
                    useddict[card]['maybeboard'] = False
                else:
                    useddict[card]['maybeboard'] = True
            # useddict.append(cardpair)
        # for i in range(0, cube_count):
        #     while True:
        #         random_card = random.randint(0, totalcards - 1)
        #         cardpair = ret_card(cardlist, random_card)
        #         if cardpair[0] not in useddict.keys():
        #             useddict[cardpair[0]] = cardpair[1]
        #             break
        print("used {} of {} cards".format(cube_count, totalcards))
        if args.cardlist_counts != None:
            for i in useddict.keys():
                useddict[i].sort()
            print(json.dumps(useddict, indent="\t"))
        elif args.cardlist_csv != None:
            filename = "{}sort.{}".format(cube_count, args.cardlist_csv)

            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write the header row
                writer.writeheader()

                # Write the data rows
                writer.writerows(useddict)
    elif args.bell == True:
        cardlist_real = []
        cardlist_unbell = []
        # take all maybeboard cards out
        for card_index in range(0, len(cardlist)):
            if str(cardlist[card_index]['maybeboard']).lower() == "false":
                cardlist_real.append(cardlist[card_index])
            else:
                cardlist_unbell.append(cardlist[card_index])
        # maybeboard all
        for card_index in range(0, len(cardlist_real)):
            cardlist_real[card_index]['maybeboard'] = True
        print("beginning with {} cards, will add {} later".format(len(cardlist_real), len(cardlist_unbell)))
        useddict, cardlist_unbell = balancing_main(cube_count, cardlist_real, cardlist_unbell, args.owcolor, args.owland)
        if useddict == -1:
            return useddict
        useddict = useddict + cardlist_unbell
        fnamebase = os.path.basename(args.cardlist_csv)
        filename = "{}sort.{}".format(cube_count, fnamebase)
        filename = os.path.join(os.path.dirname(args.cardlist_csv), filename)

        write_cardlistcsv(filename, useddict, fieldnames)
        print("wrote {}".format(filename))
    if args.rand_color_print:
        mainboardcards = []
        for card in useddict:
            if card['maybeboard'] == False:
                mainboardcards.append(card)
        colordict = {"W": 0, "U": 0, "G": 0, "R": 0, "B": 0}
        for card in mainboardcards:
            typesplit = card['Type'].split(' ')
            if (len(card['Color']) >= 1) and ('Land' not in typesplit):
                if (card['Rarity'] == 'mythic') or (card['Rarity'] == 'rare'):
                    for eachcolor in card['Color']:
                        colordict[eachcolor] += 1
        print("rarity color dict: {}".format(colordict))
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("cardrand")
    argparser.add_argument("--cardlist_counts", help="card list to parse and geenrate rand table for, in the format \"1:5,2:6\" etc.")
    argparser.add_argument("--cardlist_csv", help="csv cardlist, could be a cubetutor list")
    argparser.add_argument("--bell", action="store_true", help="try and get a good curve")
    argparser.add_argument("--cube_count", type=int, default=180, help="total cards to use for draft cube")
    argparser.add_argument("--owcolor", type=int, help="overwrite the color base count")
    argparser.add_argument("--owland", type=int, help="overwrite the land base count")
    argparser.add_argument("--rand_color_print", action='store_true', help='display the random color balance')
    args = argparser.parse_args()
    main(args)