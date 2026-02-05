import re
import os
import argparse
from pathlib import Path

from setprim import cardlistcsv, write_cardlistcsv

# 1 And That's When Somebody Makes Fun of Their Friend's Dream!!!! [EB-02] EB02-030
# 1 Emporio.Ivankov (065) [OP12] OP12-065

card_regex = r'[0-9]+ [a-zA-Z0-9\'\"!\.\(\)& -]+ \[[A-Z0-9- ]+\] ([A-Z0-9-]+)'

def tcgplayer_to_seitex_card(carddb: list, cardslot: str):
    # print(cardslot)
    cardre = re.match(card_regex, cardslot)
    card_id = cardre.groups()[0]
    # print(card_id)
    for card in carddb:
        if card["id"] == card_id:
            return card

def tcgplayer_to_seitex(carddb: list, cardlist_name: str):
    cardlist_out = []
    with open(cardlist_name, "r") as cardlistfile:
        cardlistraw = cardlistfile.readlines()
        for line in cardlistraw:
            line = line.replace('\n', '')
            # print(line)
            card = tcgplayer_to_seitex_card(carddb, line)
            cardlist_out.append(card)
    return cardlist_out


def main(args):
    cardlist_net = []
    fn, carddb, _ = cardlistcsv(args.db)

    for maybedir in args.cardlist:
        res_path = Path(maybedir)
        if os.path.isdir(res_path):
            for file_path in res_path.iterdir():
                cardlist_net += tcgplayer_to_seitex(carddb, file_path)
        else:
            cardlist_net += tcgplayer_to_seitex(carddb, file_path)

    cardlist_filt = []
    cardlist_filt_cards = []
    for card in cardlist_net:
        if card['id'] not in cardlist_filt:
            cardlist_filt.append(card['id'])
            cardlist_filt_cards.append(card)

    if args.outfile != None:
        write_cardlistcsv(cardlist_filt_cards, args.outfile, fn)
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("ttd")
    argparser.add_argument("db")
    argparser.add_argument("cardlist", nargs='+')
    argparser.add_argument("--outfile")
    args = argparser.parse_args()
    main(args)