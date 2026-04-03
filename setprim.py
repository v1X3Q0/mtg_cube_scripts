import argparse
import csv
from pathlib import Path
import os
import re
from util_cardlist import cardlistcsv, set_main, set_maybe, write_cardlistcsv

SETNAME_REGEX=r'([a-zA-Z0-9]+)?-(base|preb)\.csv'
PURCHASEDNAME_REGEX=r'([a-zA-Z0-9]{3})([0-9]{4})?-purchased\.csv'

def update_cardnamelist(cardlist_in: list, cardnamelist: list, cardlistnet: list):
    for card in cardlist_in:
        if card["name"] not in cardnamelist:
            cardnamelist.append(card["name"])
            cardlistnet.append(card)
    return cardnamelist, cardlistnet

def adjust_board(cardlistnet: list) -> list:
    for card in cardlistnet:
        if (card['maybeboard'] == True) or (card['maybeboard'] == "TRUE"):
            card["board"] = "maybeboard"
        else:
            card["board"] = "mainboard"
    return cardlistnet

def adjust_voucher(cardlistnet: list) -> list:
    for card in cardlistnet:
        card['Voucher'] = False
    return cardlistnet

def set_newcardlist(file_path: str, main_setname: str, setlist: list, fieldnames, cardnamelist: list, cardlistnet: list, setmFlag: bool, purchasedFlag: bool):
    purchased_set = False
    # Check if the entry is actually a file (and not a subdirectory)
    if file_path.is_file():
        fname = os.path.basename(file_path)
        # # this is our main set
        # if (args.setm != None) and (os.path.basename(args.setm) == fname):
        #     return None, None, None, None
        # test if we are a purchased or not purchased set
        fsetpre = re.match(PURCHASEDNAME_REGEX, fname)
        if (purchasedFlag == True) and (fsetpre != None):
            purchased_set = True
            cursetname = fsetpre.groups()[0] + 'p'
        else:
            fsetpre = re.match(SETNAME_REGEX, fname)
            # not a set
            if fsetpre == None:
                return None, None, None, None
            cursetname = fsetpre.groups()[0]
            if fsetpre.groups()[1] == 'preb':
                cursetname += 'd'
        # test for cursetname
        if (cursetname not in setlist) or (cursetname == main_setname):
            setlist.append(cursetname)
        # we have already hit this one
        else:
            return None, None, None, None
        fieldnames_tmp, setmaybe, setmaybe_sz = cardlistcsv(file_path)
        if fieldnames == None:
            fieldnames = fieldnames_tmp
        if purchasedFlag == True:
            if purchased_set == True:
                setmaybe = set_maybe(setmaybe)
            else:
                setmaybe = set_main(setmaybe)
        else:
            if setmFlag == True:
                setmaybe = set_maybe(setmaybe)
            else:
                setmaybe = set_main(setmaybe)
        cardnamelist, cardlistnet = update_cardnamelist(setmaybe, cardnamelist, cardlistnet)
        return setlist, fieldnames, cardnamelist, cardlistnet
    return None, None, None, None


def main(args):
    cardnamelist = []
    cardlistnet = []
    setlist = []
    main_setname=None
    fieldnames=None

    if args.setm != None:
        fieldnames, setm, setm_sz = cardlistcsv(args.setm)
        setm = set_main(setm)

        main_setname = re.match(SETNAME_REGEX, os.path.basename(args.setm))
        if main_setname != None:
            main_setname = main_setname.groups()[0]
        cardnamelist, cardlistnet = update_cardnamelist(setm, cardnamelist, cardlistnet)

    for maybedir in args.maybe:
        res_path = Path(maybedir)
        if os.path.isdir(res_path):
            for file_path in res_path.iterdir():
                setlist_tmp, fieldnames_tmp, cardnamelist_tmp, cardlistnet_tmp = set_newcardlist(file_path, main_setname, setlist, fieldnames, cardnamelist, cardlistnet, args.setm != None, args.purchased)
                if setlist_tmp == None:
                    continue
                setlist = setlist_tmp
                fieldnames = fieldnames_tmp
                cardnamelist = cardnamelist_tmp
                cardlistnet = cardlistnet_tmp
        else:
            setlist_tmp, fieldnames_tmp, cardnamelist_tmp, cardlistnet_tmp = set_newcardlist(res_path, main_setname, setlist, fieldnames, cardnamelist, cardlistnet, args.setm != None, args.purchased)
            if setlist_tmp == None:
                print("parsing error on file: {}".format(res_path))
                return
            setlist = setlist_tmp
            fieldnames = fieldnames_tmp
            cardnamelist = cardnamelist_tmp
            cardlistnet = cardlistnet_tmp

    
    if args.typelist != None:
        typelist = str(args.typelist.replace('\"', '')).split(',')
        for mtgtype in typelist:
            mtgtype = mtgtype.lower()
            for card in cardlistnet:
                type_local = str(card['Type']).lower()
                typelist_local = type_local.split(' ')
                if mtgtype in typelist_local:
                    card['maybeboard'] = False

    setlist.sort()
    print("maineboard \"{}\": have sets {} on the maybeboard".format(main_setname, setlist))
    if args.adjust_board == True:
        cardlistnet = adjust_board(cardlistnet)
        if "board" not in fieldnames:
            fieldnames.append("board")
    if args.adjust_voucher == True:
        cardlistnet = adjust_voucher(cardlistnet)
        if "Voucher" not in fieldnames:
            fieldnames.append("Voucher")
    if args.outfile != None:
        write_cardlistcsv(args.outfile, cardlistnet, fieldnames)
    else:
        print("have {} cards".format(len(cardlistnet)))
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("cardrand")
    argparser.add_argument("--outfile", help="file to write the set to")
    argparser.add_argument("--typelist", help="comma separated list of types to unmaybe, comma separated like \"vampire,dwarf\"")
    argparser.add_argument("--setm", help="just take a bunch of csv, and make this your main set")
    argparser.add_argument("--purchased", action="store_true", help="will look for purchased cards," \
    " those will go on the maybe and unpurchased will go on main")
    argparser.add_argument("maybe", nargs='*', type=str, help="make these your maybeboard")
    argparser.add_argument("--adjust_board", action="store_true", help="force board into the csv")
    argparser.add_argument("--adjust_voucher", action="store_true", help="force voucher into the csv")
    args = argparser.parse_args()
    main(args)