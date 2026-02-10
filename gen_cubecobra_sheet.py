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

# border-radius: 8px;
# padding: 6px;
RECTANGLE_TYPE = """
.rect {{
    position: absolute;
    background: #2a2a2a;
    color: white;
    width: {}px;
    height: {}px;
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
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
"""

GLOBAL_PREVIEW = """
<!-- GLOBAL preview -->
<div id="preview">
    <img id="preview-img">
</div>
"""

SEARCH_BAR_INSTANCE="""
<input id="search"
       type="text"
       placeholder="Search cards..."
       autocomplete="off">
"""

CARD_INSTANCE = """
<div class="card" data-name="{}" data-img="{}" data-color="{}" data-text="{}" data-type="{}" data-set="{}" data-rarity="{}"
        style="transform: translate({}px,{}px); background:{};">
    <div class="label">{}</div>
</div>
"""

FILLER_INSTANCE = """
<div class="rect"
        style="transform: translate({}px,{}px);">
    <div class="label" style="color: white">{}</div>
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

const search = document.getElementById("search");
const cards = document.querySelectorAll(".card");

search.addEventListener("input", () => {

    const term = search.value.toLowerCase();
    let hastext = term.substring(0, 2);
    let termfix = term.substring(2);

    cards.forEach(card => {

        let tagterm = "";
        if(hastext === "t:"){
            tagterm = card.dataset.type.toLowerCase();
        }
        else if(hastext === "c:"){
            tagterm = card.dataset.color.toLowerCase();
        }
        else if(hastext === "o:"){
            tagterm = card.dataset.text.toLowerCase();
        }
        else if(hastext === "s:"){
            tagterm = card.dataset.set.toLowerCase();
        }
        else if(hastext === "r:"){
            tagterm = card.dataset.rarity.toLowerCase();
        }
        else {
            tagterm = card.dataset.name.toLowerCase();
            termfix = term;
        }

        if(tagterm.includes(termfix)){
            card.style.display = "block";
        }
        else{
            card.style.display = "none";
        }

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
    def get_real_cardname(self, name: str):
        pass
    def color_retrieve(self, card: dict):
        pass
    def getimage_uri(self, card: dict):
        pass
    def get_card_cost(self, card: dict):
        pass
    def get_card_type(self, card: dict):
        pass
    def get_card_type_whole(self, card: dict):
        pass
    def get_card_text(self, card: dict):
        pass
    def rarity_variants(self):
        pass
    def rarity_retrieve(self, card: dict):
        pass
    def get_set(self, card: dict):
        pass
    def sort_by_cmc(self, cardlist_in: list):
        cardlist = cardlist_in.copy()
        new_cardlist = []
        while len(cardlist) != 0:
            first_card_index = 0
            first_card = cardlist[first_card_index]
            for card_index in range(0, len(cardlist)):
                card = cardlist[card_index]
                if self.get_card_cost(card) < self.get_card_cost(first_card):
                    first_card = card
                    first_card_index = card_index
            new_cardlist.append(first_card)
            cardlist.pop(first_card_index)
        return new_cardlist

    def create_webpage(self, cardlist_target: dict, prim_sort_grade: str):
        web_card_instance = []

        if prim_sort_grade == "color":
            column_keys = self.initialize_colorbase()
        elif prim_sort_grade == "rarity":
            column_keys = self.rarity_variants()
        
        # subtype sort by type
        # Then you have the card_types_dict
        # {
        #     L: {
        #         Artifact: [
        #             Sol Ring
        #             Nyx Lotus
        #             ]
        #         Creature: [
        #             Abundant Maw
        #             ]
        #     }
        #     R: {
        #         Sorcery: [
        #             Comet Storm
        #             ]
        #     }
        # }
        card_types_dict = {}
        for column_key in column_keys:
            card_types_dict[column_key] = {}
        for card in cardlist_target:
            card_type = self.get_card_type(card)
            if prim_sort_grade == "color":
                _, column_key = self.color_retrieve(card)
            elif prim_sort_grade == "rarity":
                column_key = self.rarity_retrieve(card)
            if card_type not in card_types_dict[column_key].keys():
                card_types_dict[column_key][card_type] = []
            card_types_dict[column_key][card_type].append(card)

        # sub sub sort by cmc
        for column_key in card_types_dict.keys():
            card_types_dict[column_key] = dict(sorted(card_types_dict[column_key].items()))
            for card_type in card_types_dict[column_key].keys():
                card_types_dict[column_key][card_type] = self.sort_by_cmc(card_types_dict[column_key][card_type])

        max_height = 0
        column_glob_base = 0
        card_count = 0
        for column_glob in card_types_dict.keys():
            row_glob_base = 0
            this_filler_instance = FILLER_INSTANCE.format(column_glob_base,
                row_glob_base, "{}".format(column_glob))
            row_glob_base += CARD_HEIGHT
            web_card_instance.append(this_filler_instance)
            for card_type in card_types_dict[column_glob].keys():
                this_filler_instance = FILLER_INSTANCE.format(column_glob_base,
                    row_glob_base, "{} ({})".format(str(card_type).lower(), len(card_types_dict[column_glob][card_type])))
                row_glob_base += CARD_HEIGHT
                web_card_instance.append(this_filler_instance)
                for card in card_types_dict[column_glob][card_type]:
                    name_local = self.get_real_cardname(card['name'])
                    color_local, color_index = self.color_retrieve(card)
                    image_uri = self.getimage_uri(card)
                    index_x = column_glob_base
                    index_y = row_glob_base
                    this_card_instance = CARD_INSTANCE.format(name_local, image_uri, color_index,
                        self.get_card_text(card), self.get_card_type_whole(card), self.get_set(card), self.rarity_retrieve(card), index_x, index_y, '#' + hex(color_local)[2:], name_local)
                    web_card_instance.append(this_card_instance)
                    row_glob_base += CARD_HEIGHT
                    if row_glob_base > max_height:
                        max_height = row_glob_base
                    card_count += 1
            column_glob_base += CARD_WIDTH

        rectange_type = RECTANGLE_TYPE.format(CARD_WIDTH, CARD_HEIGHT)
        card_type = CARD_TYPE.format(CARD_WIDTH, CARD_HEIGHT)
        container_width = CARD_WIDTH * len(column_keys)
        container_height = max_height
        container_type = CONTAINER_TYPE.format(container_width, container_height)

        webpage_str = ""
        webpage_str += file_head + '\n'
        webpage_str += html_head + '\n'
        webpage_str += head_head + '\n'
        webpage_str += style_head + '\n'
        webpage_str += BACKGROUND_TYPE
        webpage_str += container_type
        webpage_str += card_type
        webpage_str += rectange_type
        webpage_str += CARD_IMAGE_TYPE
        webpage_str += CARD_HOVER_TYPE
        webpage_str += LABEL_TEXT_TYPE
        webpage_str += close_head(style_head) + '\n'
        webpage_str += close_head(head_head) + '\n'
        webpage_str += body_head + '\n'
        webpage_str += SEARCH_BAR_INSTANCE
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
    def get_card_cost(self, card):
        return int(card['CMC'])
    def get_card_type(self, card: dict):
        local_type = card['Type']
        local_type = local_type.replace('Legendary ', '')
        return local_type.split(' ')[0]
    def get_card_type_whole(self, card):
        return card['Type']
    def rarity_variants(self):
        MTG_RARITY_VARIANTS = ['common', 'uncommon', 'rare', 'mythic']
        return MTG_RARITY_VARIANTS
    def rarity_retrieve(self, card: str):
        return card['Rarity']
    def get_card_text(self, card):
        scryfall_card = self.get_scryfall_card(card)
        return self.get_block_card(scryfall_card, card, "oracle_text")
    def get_set(self, card):
        return card['Set']
    def get_real_cardname(self, cardname: str):
        database = self.carddb
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
    def get_block_card(self, card: dict, card_in: dict, block='image_uris'):
        """
        Docstring for get_block_card
        
        :param self: Description
        :param card: scryfall card in
        :type card: dict
        :param card_in: cube cobra card in
        :type card_in: dict
        :param block: which key we want from the primary face
        """
        if block in card.keys():
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
    def get_image_uris_card(self, card: dict, card_in: dict):
        return self.get_block_card(card, card_in, "image_uris")
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
    def get_card_cost(self, card: dict):
        if card['cost'] == '-':
            return 0
        return int(card['cost'])
    def get_card_text(self, card):
        return card['effect']
    def get_card_type(self, card: dict):
        return card['type']
    def get_card_type_whole(self, card):
        return card['card_type']
    def rarity_variants(self):
        OP_RARITY_VARIANTS = ['C', 'UC', 'R', 'SR', 'L', 'SEC']
        return OP_RARITY_VARIANTS
    def rarity_retrieve(self, card: dict):
        return card['rarity']
    def get_set(self, card):
        return card["id"].split('-')[0]
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
        mtg_tcg.create_webpage(cardlist_target, args.sortby)
    elif args.tcg == 'op':
        fieldnames_db, carddb, _ = cardlistcsv(args.scryfall_list)
        fieldnames, cardlist_target, _ = cardlistcsv(args.cardlist_csv)
        op_tcg = op_tcg_t(carddb)
        op_tcg.create_webpage(cardlist_target, args.sortby)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser("gen_cubecobra_sheet")
    argparser.add_argument("cardlist_csv", help="cardlist to use")
    argparser.add_argument("scryfall_list", help="scryfall list of cards")
    argparser.add_argument('tcg', type=str, choices=['mtg', 'op'], help="choose a tcg, mtg or op.")
    argparser.add_argument("--webpage", help="webpage to host")
    argparser.add_argument("--sortby", default="color", help="what to sort by, color or rarity")
    args = argparser.parse_args()
    main(args)
