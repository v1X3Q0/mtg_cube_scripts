import argparse
import re
import json
import time
def pull_dict(cardlist: list):
    carddict = {}
    curtime = time.time()
    firsttime = curtime
    prevlength = len(cardlist)
    firstlength = prevlength
    second_interval = 10
    print("begun dictifying {} cards! Will update you every {} seconds".format(prevlength, second_interval))
    while len(cardlist) > 0:
        thiscardlist = []
        card = cardlist.pop(0)
        thiscardlist.append(card)
        card_index = 0
        while card_index < len(cardlist):
            card_compare = cardlist[card_index]
            if card['name'] == card_compare['name']:
                thiscardlist.append(cardlist.pop(card_index))
            else:
                card_index += 1
        carddict[card['name']] = thiscardlist
        nexttime = time.time()
        if nexttime > (curtime + second_interval):
            curtime = nexttime
            print("current cardlist size {}/{} decrease by {}, {} cards processed, {}'s elapsed".format(
                len(cardlist), firstlength, prevlength - len(cardlist), firstlength - len(cardlist), curtime - firsttime))
            prevlength = len(cardlist)
    print("time elapsed: ~{}".format(curtime - firsttime))
    return carddict

def main(args):
    with open(args.cardlist, "r") as cardlist_file:
        cardlist = json.load(cardlist_file)
    carddict = pull_dict(cardlist)
    with open(args.carddict, "w") as carddict_file:
        json.dump(carddict, carddict_file)
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("cardlist_to_hash")
    argparser.add_argument("cardlist", help="json card list from scrython")
    argparser.add_argument("carddict", help="output card dict")
    args = argparser.parse_args()
    main(args)