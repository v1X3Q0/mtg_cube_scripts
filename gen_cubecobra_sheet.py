import argparse
from cardrand import cardlistcsv
from dup_sets import populate_database, get_real_cardname

file_head = "<!DOCTYPE html>"
html_head = "<html>"
head_head = "<head>"
style_head = "<style>"
body_head = "<body>"
div_head = "<div>"

BACKGROUND_TYPE = """
body {
    background: #111;
    font-family: sans-serif;
}
"""

CONTAINER_TYPE = """
.container {{
    position: relative;
    width: {}px;
    height: {}px;
    background: #111;
}}
"""

# position: relative;

CARD_TYPE = """
/* rectangle */
.card {{
    position: absolute;
    background: #464545;
    width: {}px;
    height: {}px;
    border-radius: 10px;
    cursor: pointer;
}}
"""

CARD_IMAGE_TYPE = """
/* preview image */
.card img {
    position: absolute;
    width: 250px;
    left: 160px;
    top: 0;
    opacity: 0;
    pointer-events: none;
    transform: scale(.9);
    transition: .15s;
    z-index: 10;
}
"""

CARD_HOVER_TYPE = """
/* hover effect */
.card:hover img {
    opacity: 1;
    transform: scale(1);
}
"""

LABEL_TEXT_TYPE = """
.label {
    color: black;
    padding: 8px;
    font-size: small;
}
"""
# transform: translate({},{})
# CARD_INSTANCE = """
# <div class="card" style="left:{}px; top:{}px; background: {};">
#     <div class="label">{}
#     </div>
#     <img src="{}">
# </div>
# """

CARD_INSTANCE = """
<div class="card" style="transform: translate({}px,{}px); background: {};">
    <div class="label">{}
    </div>
    <img src="{}">
</div>
"""

RED_CARD=0xef5c5c
BLUE_CARD=0x4947e4
GREEN_CARD=0x18d043
BLACK_CARD=0x4d4d4d
WHITE_CARD = 0xf5f2c5
MULTICOLOR_CARD = 0xcbc243
COLORLESS_CARD = 0xc3c3c3

CARD_WIDTH = 120
CARD_HEIGHT = 25

def add_body_arg(div_type: str, div_arg: str):
    div_result = div_type.replace('>', " {}{}".format(div_arg, ">"))
    return div_result

def close_head(div_type: str):
    return div_type.replace('<', "</")

def get_image_uris_card(card: dict, card_in: dict):
    if 'image_uris' in card.keys():
        return card
    else:
        if ('mtgo_id' in card.keys()) and (int(card_in['MTGO ID']) != -1) and (int(card['mtgo_id']) == int(card_in['MTGO ID'])):
            if "card_faces" in card.keys() and len(card["card_faces"]) > 1:
                card_out = card["card_faces"][0]
            else:
                card_out = card
            return card_out
        # print(card_in['Set'], card['set'], card['collector_number'], card_in['Collector Number'])
        if (card_in['Set'] == card['set']) and (card['collector_number'] == card_in['Collector Number']):
            if "card_faces" in card.keys() and len(card["card_faces"]) > 1:
                card_out = card["card_faces"][0]
            else:
                card_out = card
            return card_out
    return None

def get_scryfall_card(carddb: dict, card_in: dict, preferred_lang='en'):
    name_local = get_real_cardname(carddb, card_in['name'])
    for card in carddb[name_local]:
        if card['lang'] == preferred_lang:
            card_uri = get_image_uris_card(card, card_in)
            if card_uri != None:
                return card_uri
    return None

def main(args):
    carddb = populate_database(args.scryfall_list)
    fieldnames, cardlist_target, _ = cardlistcsv(args.cardlist_csv)
    web_card_instance = []
    color_base = {'W': [CARD_WIDTH * 0, 0],
                  'B': [CARD_WIDTH * 1, 0],
                  'U': [CARD_WIDTH * 2, 0],
                  'R': [CARD_WIDTH * 3, 0],
                  'G': [CARD_WIDTH * 4, 0],
                  'M': [CARD_WIDTH * 5, 0],
                  'L': [CARD_WIDTH * 6, 0]}
    for card in cardlist_target:
        name_local = get_real_cardname(carddb, card['name'])
        # print(name_local)
        scryfall_card = get_scryfall_card(carddb, card)
        image_url = scryfall_card['image_uris']['normal']
        if len(card['Color']) > 1:
            color_local = MULTICOLOR_CARD
            color_index = 'M'
        elif len(card['Color']) < 1:
            color_local = COLORLESS_CARD
            color_index = 'L'
        else:
            color_index = card['Color']
            if card['Color'] == 'U':
                color_local = BLUE_CARD
            elif card['Color'] == 'R':
                color_local = RED_CARD
            elif card['Color'] == 'W':
                color_local = WHITE_CARD
            elif card['Color'] == 'B':
                color_local = BLACK_CARD
            elif card['Color'] == 'G':
                color_local = GREEN_CARD
        this_card_instance = CARD_INSTANCE.format(color_base[color_index][0],
            color_base[color_index][1], '#' + hex(color_local)[2:], card['name'], image_url)
        web_card_instance.append(this_card_instance)
        color_base[color_index][1] += CARD_HEIGHT
    max_cards = 0
    for color_key in color_base.keys():
        if color_base[color_key][1] > max_cards:
            max_cards = color_base[color_key][1]
    card_type = CARD_TYPE.format(CARD_WIDTH, CARD_HEIGHT)
    container_width = CARD_WIDTH * len(color_base.items())
    container_height = CARD_HEIGHT * max_cards
    container_type = CONTAINER_TYPE.format(container_width, container_height)

    webpage_str = ""
    webpage_str += file_head + '\n'
    webpage_str += html_head + '\n'
    webpage_str += head_head + '\n'
    webpage_str += style_head + '\n'
    webpage_str += BACKGROUND_TYPE
    webpage_str += container_type
    webpage_str += card_type
    webpage_str += CARD_IMAGE_TYPE
    webpage_str += CARD_HOVER_TYPE
    webpage_str += LABEL_TEXT_TYPE
    webpage_str += close_head(style_head) + '\n'
    webpage_str += close_head(head_head) + '\n'
    webpage_str += body_head + '\n'
    webpage_str += add_body_arg(div_head, "class=\"container\"")
    for webcard in web_card_instance:
        webpage_str += webcard
    webpage_str += close_head(div_head) + '\n'
    webpage_str += close_head(body_head) + '\n'
    webpage_str += close_head(html_head) + '\n'

    if args.webpage != None:
        with open(args.webpage, "w") as webpage_raw:
            webpage_raw.write(webpage_str)
    return

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("gen_cubecobra_sheet")
    argparser.add_argument("cardlist_csv", help="cardlist to use")
    argparser.add_argument("scryfall_list", help="scryfall list of cards")
    argparser.add_argument("--webpage", help="webpage to host")
    args = argparser.parse_args()
    main(args)
