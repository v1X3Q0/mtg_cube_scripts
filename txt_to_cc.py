import argparse
from dup_sets import populate_database, get_real_cardname, get_block_card
from setprim import write_cardlistcsv

# name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID,Custom

FIELDNAME_RAW = "name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID,Custom"

def txt_to_cc(cardlist_dict: dict, cardlist_in: list, set_suggestion=None):
    cardlist_out = []
    for cardname in cardlist_in:
        # print(cardname)

        cardname_real = get_real_cardname(cardlist_dict, cardname)

        if set_suggestion != None:
            scrycard_base = None
            for scrycard in cardlist_dict[cardname_real]:
                if scrycard['set'] == set_suggestion:
                    if scrycard_base == None:
                        scrycard_base = scrycard
                    elif int(scrycard["collector_number"]) < int(scrycard_base["collector_number"]):
                        scrycard_base = scrycard
            if scrycard_base == None:
                print("card {} not in set {}".format(cardname_real, set_suggestion))
        else:
            scrycard_base = cardlist_dict[cardname_real][0]

        # for i in scrycard.keys():
        #     print(i)
        carddict_local = {}
        carddict_local['name'] = cardname_real
        carddict_local['CMC'] = int(scrycard_base['cmc'])
        carddict_local['Type'] = scrycard_base['type_line']
        carddict_local['Color'] = ''.join(scrycard_base['color_identity'])
        carddict_local['Set'] = ''.join(scrycard_base['set'])
        carddict_local['Collector Number'] = "{}".format(scrycard_base['collector_number'])
        carddict_local['Rarity'] = scrycard_base['rarity']
        carddict_local['Color Category'] = 'null'
        carddict_local['status'] = 'Not Owned'
        if scrycard_base['nonfoil'] == True:
            carddict_local['Finish'] = "Non-foil"
        else:
            carddict_local['Finish'] = "Foil"
        carddict_local['maybeboard'] = False
        carddict_local['image URL'] = ""
        carddict_local['image Back URL'] = ""
        carddict_local['tags'] = ""
        carddict_local['Notes'] = ""
        if 'mtgo_id' in scrycard_base.keys():
            carddict_local['MTGO ID'] = scrycard_base['mtgo_id']
        else:
            carddict_local['MTGO ID'] = "-1"
        carddict_local['Custom'] = False
        # print(scrycard)
        # print(scrycard['multiverse_ids'])
        # print(carddict_local)
        # print(scrycard)
        cardlist_out.append(carddict_local)
    return cardlist_out

def main(args):
    cardlist_in = []
    cardlist_out = []
    with open(args.txt, "r") as txtfile:
        txtlines = txtfile.readlines()
        for line in txtlines:
            cardname = line.replace("\n", '')
            if cardname != '':
                cardlist_in.append(cardname)
    if cardlist_in == []:
        return
    cardlist_dict = populate_database(args.dictlist)
    cardlist_out = txt_to_cc(cardlist_dict, cardlist_in)
    write_cardlistcsv(cardlist_out, "{}.csv".format(args.txt), FIELDNAME_RAW.split(','))
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("txt_to_cc")
    argparser.add_argument("txt", help="txt to convert to csv")
    argparser.add_argument("dictlist", help="dict list to user for card specs")
    args = argparser.parse_args()
    main(args)