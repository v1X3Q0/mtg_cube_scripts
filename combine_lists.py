import argparse
from util_cardlist import cardlistcsv, write_cardlistcsv

def main(args):
    cardlists_net = []
    cardlist_first = None
    for cardlist in args.card_lists:
        if cardlist_first == None:
            cardlist_first = cardlist
        fieldnames, cardlist_local, _ = cardlistcsv(cardlist)
        cardlists_net += cardlist_local
    if args.outfile != None:
        cardlist_first = args.outfile
    write_cardlistcsv(cardlist_first, cardlists_net, fieldnames)
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("combine_lists.py")
    argparser.add_argument("card_lists", nargs="+", help="lists of sets to append")
    argparser.add_argument("--outfile", help="file to output")
    args = argparser.parse_args()
    main(args)