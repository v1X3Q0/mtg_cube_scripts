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

CARD_HOVER_TYPE = """
#preview{
    position: fixed;
    pointer-events:none;
    z-index: 999999;
    opacity:0;
    transition: opacity .12s ease;
}
"""

CARD_IMAGE_TYPE = """
#preview img{
    width:260px;
    border-radius:12px;
    box-shadow:0 20px 40px rgba(0,0,0,.6);
}
"""

LABEL_TEXT_TYPE = """
.label {
    color: black;
    padding: 8px;
    font-size: small;
}
"""

GLOBAL_PREVIEW = """
<!-- GLOBAL preview -->
<div id="preview">
    <img id="preview-img">
</div>
"""

CARD_INSTANCE = """
<div class="card" data-img="{}"
        style="transform: translate({}px,{}px); background:{};">
    <div class="label">{}</div>
</div>
"""

SAMPLE_PREVIEW_JS = """
<script>

const preview = document.getElementById("preview");
const img = document.getElementById("preview-img");

document.querySelectorAll(".card").forEach(card => {

    card.addEventListener("mouseenter", e=>{
        img.src = card.dataset.img;
        preview.style.opacity = 1;
    });

    card.addEventListener("mouseleave", ()=>{
        preview.style.opacity = 0;
    });

    card.addEventListener("mousemove", e=>{

        const pad = 20;
        let x = e.clientX + pad;
        let y = e.clientY - 140;

        // prevent offscreen right
        if(x + 260 > window.innerWidth){
            x = e.clientX - 280;
        }

        // prevent offscreen bottom
        if(y + 360 > window.innerHeight){
            y = window.innerHeight - 380;
        }

        preview.style.left = x + "px";
        preview.style.top = y + "px";
    });

});

</script>
"""

RED_CARD=0xef5c5c
BLUE_CARD=0x4947e4
GREEN_CARD=0x18d043
BLACK_CARD=0x4d4d4d
WHITE_CARD = 0xf5f2c5
PURPLE_CARD = 0xa912ea
YELLOW_CARD = 0xebf306
MULTICOLOR_CARD = 0xcbc243
COLORLESS_CARD = 0xc3c3c3

CARD_WIDTH = 120
CARD_HEIGHT = 25

def add_body_arg(div_type: str, div_arg: str):
    div_result = div_type.replace('>', " {}{}".format(div_arg, ">"))
    return div_result

def close_head(div_type: str):
    return div_type.replace('<', "</")

class trading_card_game_t:
    def __init__(self, carddb: dict):
        self.carddb = carddb
    def initialize_colorbase(self):
        pass
    def get_real_cardname(name: str):
        pass
    def color_retrieve(card: dict):
        pass
    def getimage_uri(card: dict):
        pass

    def create_webpage(self, cardlist_target: dict):
        web_card_instance = []
        color_base = {}

        color_glob_index = 0
        for color_glob in self.initialize_colorbase():
            color_base[color_glob] = [CARD_WIDTH * color_glob_index, 0]
            color_glob_index += 1

        for card in cardlist_target:
            name_local = self.get_real_cardname(card['name'])
            # print(name_local)
            color_local, color_index = self.color_retrieve(card)
            image_uri = self.getimage_uri(card)
            this_card_instance = CARD_INSTANCE.format(image_uri, color_base[color_index][0],
                color_base[color_index][1], '#' + hex(color_local)[2:], name_local)
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
        webpage_str += GLOBAL_PREVIEW
        webpage_str += SAMPLE_PREVIEW_JS
        webpage_str += close_head(div_head) + '\n'
        webpage_str += close_head(body_head) + '\n'
        webpage_str += close_head(html_head) + '\n'

        if args.webpage != None:
            with open(args.webpage, "w") as webpage_raw:
                webpage_raw.write(webpage_str)
        return


class mtg_tcg_t(trading_card_game_t):
    def initialize_colorbase(self):
        MTG_COLOR_BASE = ['W', 'B', 'U', 'R', 'G', 'M', 'L']
        return MTG_COLOR_BASE
    def get_real_cardname(self, cardname: str):
        database = self.db
        if cardname in database.keys():
            return cardname
        else:
            for cardkey in database.keys():
                if ("{} // ".format(cardname) in cardkey) and (cardkey != "{} // {}".format(cardname, cardname)):
                    return cardkey
            # we haven't returned yet
            for cardname_iter in database.keys():
                for eachcard in database[cardname_iter]:
                    if ("flavor_name" in eachcard.keys()) and (eachcard["flavor_name"] == cardname):
                        return cardname_iter
                    elif ("printed_name" in eachcard.keys()) and (eachcard["printed_name"] == cardname):
                        return cardname_iter
            else:
                print(cardname)
                exit()
        return
    def color_retrieve(self, card: dict):
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
        return color_local, color_index
    def get_image_uris_card(self, card: dict, card_in: dict):
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
    def get_scryfall_card(self, card_in: dict, preferred_lang='en'):
        carddb = self.carddb
        name_local = get_real_cardname(carddb, card_in['name'])
        for card in carddb[name_local]:
            if card['lang'] == preferred_lang:
                card_uri = self.get_image_uris_card(card, card_in)
                if card_uri != None:
                    return card_uri
        return None
    def mtg_getimage_uri(self, scryfall_card: dict):
        return scryfall_card['image_uris']['normal']

    def getimage_uri(self, card: dict):
        scryfall_card = self.get_scryfall_card(card)
        image_url = self.mtg_getimage_uri(scryfall_card)
        return image_url

class op_tcg_t(trading_card_game_t):
    def initialize_colorbase(self):
        OP_COLOR_BASE = ['Y', 'G', 'U', 'B', 'R', 'P', 'M']
        return OP_COLOR_BASE
    def color_retrieve(self, card):
        color_array = card['color']
        if len(color_array.split('/')) > 1:
            color_local = MULTICOLOR_CARD
            color_index = 'M'
        else:
            if card['color'] == 'Green':
                color_local = GREEN_CARD
                color_index = 'G'
            elif card['color'] == 'Yellow':
                color_local = YELLOW_CARD
                color_index = 'Y'
            elif card['color'] == 'Purple':
                color_local = PURPLE_CARD
                color_index = 'P'
            elif card['color'] == 'Blue':
                color_local = BLUE_CARD
                color_index = 'U'
            elif card['color'] == 'Black':
                color_local = BLACK_CARD
                color_index = 'B'
            elif card['color'] == 'Red':
                color_local = RED_CARD
                color_index = 'R'
        return color_local, color_index
    def get_real_cardname(self, name):
        return name
    def getimage_uri(elf, card):
        return card["image_url"]

def main(args):
    if args.tcg == 'mtg':
        carddb = populate_database(args.scryfall_list)
        fieldnames, cardlist_target, _ = cardlistcsv(args.cardlist_csv)
        mtg_tcg = mtg_tcg_t(carddb)
        mtg_tcg.create_webpage(cardlist_target)
    elif args.tcg == 'op':
        fieldnames_db, carddb, _ = cardlistcsv(args.scryfall_list)
        fieldnames, cardlist_target, _ = cardlistcsv(args.cardlist_csv)
        op_tcg = op_tcg_t(carddb)
        op_tcg.create_webpage(cardlist_target)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("gen_cubecobra_sheet")
    argparser.add_argument("cardlist_csv", help="cardlist to use")
    argparser.add_argument("scryfall_list", help="scryfall list of cards")
    argparser.add_argument('tcg', type=str, choices=['mtg', 'op'], help="choose a tcg, mtg or op.")
    argparser.add_argument("--webpage", help="webpage to host")
    args = argparser.parse_args()
    main(args)
