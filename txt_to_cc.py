import argparse
from dup_sets import populate_database, get_real_cardname

# name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID,Custom

fieldname_raw = "name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID,Custom"

def main(args):
    cardlist_in = []
    with open(args.txt, "r") as txtfile:
        txtlines = txtfile.readlines()
        for line in txtlines:
            cardname = line.replace("\n", '')
            if cardname != '':
                cardlist_in.append(cardname)
    if cardlist_in == []:
        return
    cardlist_dict = populate_database(args.dictlist)
    for cardname in cardlist_in:
        cardname_real = get_real_cardname(cardlist_dict, cardname)
        # for i in cardlist_dict[cardname_real][0].keys():
        #     print(i)
        carddict_local = {}
        carddict_local['name'] = cardname_real
        carddict_local['CMC'] = int(cardlist_dict[cardname_real][0]['cmc'])
        carddict_local['Type'] = cardlist_dict[cardname_real][0]['type_line']
        carddict_local['Color'] = ''.join(cardlist_dict[cardname_real][0]['color_identity'])
        carddict_local['Set'] = ''.join(cardlist_dict[cardname_real][0]['set'])
        carddict_local['Collector Number'] = "{}".format(cardlist_dict[cardname_real][0]['collector_number'])
        carddict_local['Rarity'] = cardlist_dict[cardname_real][0]['rarity']
        carddict_local['Color Category'] = 'null'
        carddict_local['status'] = 'Not Owned'
        if cardlist_dict[cardname_real][0]['nonfoil'] == True:
            carddict_local['Finish'] = "Non-foil"
        else:
            carddict_local['Finish'] = "Foil"
        carddict_local['maybeboard'] = False
        carddict_local['image URL'] = ""
        carddict_local['image Back URL'] = ""
        carddict_local['tags'] = "\"\""
        carddict_local['Notes'] = "\"\""
        if 'mtgo_id' in cardlist_dict[cardname_real][0].keys():
            carddict_local['MTGO ID'] = carddict_local[0]['mtgo_id']
        else:
            carddict_local['MTGO ID'] = "-1"
        carddict_local['custom'] = False

        # print(cardlist_dict[cardname_real][0])
        # print(cardlist_dict[cardname_real][0]['multiverse_ids'])
        print(carddict_local)
        # print(cardlist_dict[cardname_real][0])
        break
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("txt_to_cc")
    argparser.add_argument("txt", help="txt to convert to csv")
    argparser.add_argument("dictlist", help="dict list to user for card specs")
    args = argparser.parse_args()
    main(args)