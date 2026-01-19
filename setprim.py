import argparse
import csv
from pathlib import Path
import os
import re
from balancing import parse_type

SETNAME_REGEX=r'([a-zA-Z0-9]{3})([0-9]{4})?-base\.csv'
PURCHASEDNAME_REGEX=r'([a-zA-Z0-9]{3})([0-9]{4})?-purchased\.csv'

def set_maybe(cardlist: list):
    for card_index in range(0, len(cardlist)):
        cardlist[card_index]['maybeboard'] = True
    return cardlist

def set_main(cardlist: list):
    for card_index in range(0, len(cardlist)):
        cardlist[card_index]['maybeboard'] = False
    return cardlist

def cardlistcsv(cardlist_csv: str):
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

def write_cardlistcsv(useddict: list, filename: str, fieldnames: list):
    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        writer.writerows(useddict)

def update_cardnamelist(cardlist_in: list, cardnamelist: list, cardlistnet: list):
    for card in cardlist_in:
        if card["name"] not in cardnamelist:
            cardnamelist.append(card["name"])
            cardlistnet.append(card)
    return cardnamelist, cardlistnet

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

    write_cardlistcsv(cardlistnet, args.outfile, fieldnames)
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("cardrand")
    argparser.add_argument("outfile", help="file to write the set to")
    argparser.add_argument("--typelist", help="comma separated list of types to unmaybe")
    argparser.add_argument("--setm", help="just take a bunch of csv, and make this your main set")
    argparser.add_argument("--purchased", action="store_true", help="will look for purchased cards," \
    " those will go on the maybe and unpurchased will go on main")
    argparser.add_argument("maybe", nargs='*', type=str, help="make these your maybeboard")
    args = argparser.parse_args()
    main(args)