import scrython
import random

SPELL_TYPES = ["Creature", "Artifact", "Instant", "Sorcery", "Enchantment", "OTHER"]
UNCOLOR_TYPES = ["Land", "OTHER"]

BALANCING_MAP = {
    180: {"COLOR": 24, "LANDS": 15},
    235: {"COLOR": 30, "LANDS": 20},
    270: {"COLOR": 37, "LANDS": 25},
    315: {"COLOR": 44, "LANDS": 30},
    360: {"COLOR": 50, "LANDS": 35}
    }

def parse_type(type_in: str):
    spell_type_list = SPELL_TYPES
    for typepiece in spell_type_list:
        if typepiece in type_in:
            return typepiece
    return "OTHER"

def typed_pull_ratios(ratio_little: dict, color: str, this_color_list: list, cardlist: list):
    # now we have all our ratios for the card types
    #  type current can be something crazy, in which its just OTHER
    for type_current in ratio_little.keys():
        print("color: {}, type: {}".format(color, type_current))
        # populate type liat\
        this_typed_list = []
        for card in this_color_list:
            if parse_type(card["Type"]) == type_current:
                this_typed_list.append(card)
        cardlist = typed_rare_pull(this_typed_list, cardlist, ratio_little[type_current])
    return cardlist

def establish_ratios(spell_type_list: list, this_color_list: list, COLOR_180: int) -> dict:
    etablish_ratio = {}
    ratio_diff = {}
    for spell_type in spell_type_list:
        etablish_ratio[spell_type] = 0

    ratio_little = etablish_ratio.copy()

    # calculate ration to maintain it
    for card in this_color_list:
        type_current = parse_type(card["Type"])
        if type_current in etablish_ratio.keys():
            etablish_ratio[type_current] += 1
        else:
            etablish_ratio["OTHER"] += 1

    ratio_little_tmp = sorted(ratio_little.items())
    ratio_little = dict(ratio_little_tmp)
    ratio_little_tmp = list(ratio_little.keys())

    # get the rounded stuff for each type, we are solving for ratio_out, and
    # saving it in ratio_little
    #    number_of_this_type              ratio_out
    # ------------------------- = ---------------------------
    #    total of this color       23 (180 color draft size)
    for type_current in etablish_ratio.keys():
        ratio_float = etablish_ratio[type_current] / len(this_color_list)
        ratio_out = int(ratio_float * COLOR_180)
        if (ratio_out == 0) and (etablish_ratio[type_current] != 0):
            ratio_out = 1
        ratio_little[type_current] = ratio_out

    # verify that you have the color_180
    count = 0
    for type_current in ratio_little.keys():
        count += ratio_little[type_current]

    #  if we are less than 180, i want to add to the most favored
    # count is what we have, color_180 is the goal
    # if this is the case, we need to just return thie stuff, since
    # we just don't have enough cards. Ideally, we will be pulling from
    # the maybe pile
    while count < COLOR_180:
        # print("{} < {}".format(count, COLOR_180))
        # calculate all ratios
        # ratio_little is the goal, establish_ratio is what we have
        ratio_temp = {}
        for type_current in etablish_ratio.keys():
            ratio_float = etablish_ratio[type_current] / len(this_color_list)
            ratio_out_float = ratio_float * COLOR_180
            ratio_out_delta = ratio_out_float - (int(ratio_out_float) * 1.0)
            ratio_temp[type_current] = ratio_out_delta
                    
        ratio_temp_max = sorted(ratio_temp.items())
        ratio_temp_max.reverse()
        for ratio_iter in ratio_temp_max:
            if ratio_little[ratio_iter[0]] == etablish_ratio[ratio_iter[0]]:
                continue
            ratio_little[ratio_iter[0]] += 1
            count += 1
            if count == COLOR_180:
                break
        if len(this_color_list) < COLOR_180:
            for type_current in etablish_ratio.keys():
                ratio_diff[type_current] = ratio_little[type_current] - etablish_ratio[type_current]
        
    # if we are greater than our ratio, i want to remove from the least favored
    ratio_little_tmp.reverse()
    while count > COLOR_180:
        for key in ratio_little_tmp:
            ratio_little[key] -= 1
            count -= 1
            if count == COLOR_180:
                break
    
    print(etablish_ratio)
    return ratio_little, ratio_diff

def index_of_card_in_list(card_in: dict, cardlist: list):
    for card_index in range(0, len(cardlist)):
        card = cardlist[card_index]
        if card_in['name'] == card['name']:
            return card_index
    return None

def compensate_maybeboard_typed(cardlist_maybe: list, ratio_diff: dict, color: str) -> list:
    for typed_key in ratio_diff.keys():
        typed_cardlist = []
        if ratio_diff[typed_key] > 0:
            for card in cardlist_maybe:
                if (typed_key == "Land") and ("Land" in card["Type"].split(" ")):
                    typed_cardlist.append(card)
                elif (parse_type(card["Type"]) == typed_key) and (card['Color'] == color):
                    typed_cardlist.append(card)
                elif (color == None) and (len(card['Color']) != 1) and ("Land" not in card["Type"].split(" ")):
                    typed_cardlist.append(card)
            if len(typed_cardlist) < ratio_diff[typed_key]:
                print("ERROR: {}:{} maybe_typed {} < {}".format(color, typed_key, len(typed_cardlist), ratio_diff[typed_key]))
                return -1
            print("--M-- color: {}, type: {}; have:{} need:{}".format(color, typed_key, len(typed_cardlist), ratio_diff[typed_key]))
            cardlist_maybe = typed_rare_pull(typed_cardlist, cardlist_maybe, ratio_diff[typed_key])
    return cardlist_maybe


def typed_rare_pull(this_typed_color_list: list, cardlist: list, ratio_type_cap: int):
    rare_count = 0
    # print(this_typed_color_list)
    for card in this_typed_color_list:
        if (card['Rarity'] == 'rare') or (card['Rarity'] == 'mythic'):
            rare_count += 1
    print("\trare_count is {} of ratio {}".format(rare_count, ratio_type_cap))
    # if we have less rares than the ratio dictates, commit all rares
    if rare_count <= ratio_type_cap:
        card_index = 0
        while card_index < len(this_typed_color_list):
            card = this_typed_color_list[card_index]
            if (card['Rarity'] == 'rare') or (card['Rarity'] == 'mythic'):
                card_index_net = index_of_card_in_list(card, cardlist)
                cardlist[card_index_net]['maybeboard'] = False
                this_typed_color_list.pop(card_index)
                ratio_type_cap -= 1
                continue
            card_index += 1
        # the remainder of cards will be selected at random
        if ratio_type_cap > 0:
            # for each uncommon, make the chances of them being picked 3 times that of an common
            # then for non rares, ratio in the new cards
            counter = 0
            len_at_start = len(this_typed_color_list)
            while counter < len_at_start:
                if this_typed_color_list[counter]['Rarity'] == 'uncommon':
                    # for each of these appends, multiply the new odds
                    UNCOMMON_ODDS_FACTOR = 4
                    odds_counter = 0
                    while odds_counter < UNCOMMON_ODDS_FACTOR:
                        this_typed_color_list.append(this_typed_color_list[counter])
                        odds_counter += 1
                counter += 1
            print("\trandomizing {}(real {}) of {}".format(len(this_typed_color_list), len_at_start, ratio_type_cap))
            # unique_random_integers = random.sample(range(0, len(this_typed_color_list)), ratio_type_cap)
            counter = 0
            while counter < ratio_type_cap:
                if len(this_typed_color_list) == 1:
                    rand_card_index = 0
                else:
                    # print(ratio_type_cap, len(this_typed_color_list))
                    rand_card_index = random.randint(0, len(this_typed_color_list) - 1)
                card_index_net = index_of_card_in_list(this_typed_color_list[rand_card_index], cardlist)
                cardlist[card_index_net]['maybeboard'] = False
                # we need to remove all instances of this card
                rand_card = this_typed_color_list[rand_card_index]
                while index_of_card_in_list(rand_card, this_typed_color_list) != None:
                    this_typed_color_list.pop(index_of_card_in_list(rand_card, this_typed_color_list))
                counter += 1
            # for rand_card in unique_random_integers:
            #     cardlist[index_of_card_in_list(this_typed_color_list[rand_card], cardlist)]['maybeboard'] = False
                # color_dict.pop(temp_typelist[rand_card])
    # otherwise, we need to select our rares at random. This means we will only have rares
    else:
        temp_typelist = []
        for card in this_typed_color_list:
            if (card['Rarity'] == 'rare') or (card['Rarity'] == 'mythic'):
                temp_typelist.append(card)
        print("\trare: randomizing {} of {}".format(len(temp_typelist), ratio_type_cap))
        unique_random_integers = random.sample(range(0, len(temp_typelist)), ratio_type_cap)
        for rand_card in unique_random_integers:
            # print("random stuff")
            rare_card_index = index_of_card_in_list(temp_typelist[rand_card], cardlist)
            cardlist[rare_card_index]['maybeboard'] = False
            # print(cardlist[rare_card_index])
            # color_dict.pop(temp_typelist[rand_card])
    return cardlist

def balancing_main(capacity: int, cardlist: list, cardlist_maybe: list):
    cardlist_scrython=[]
    color_dict = {'W':[], 'B':[], 'U':[], 'G':[], 'R':[]}
    uncolor_list = []
    land_list = []
    CAPACITY_180=capacity
    COLOR_180=BALANCING_MAP[capacity]["COLOR"]
    LAND_CAPACITY=BALANCING_MAP[capacity]["LANDS"]

    for card in cardlist:
        type_spacesplit = card['Type'].split(' ')
        # pull monochromatic cards
        if (len(card['Color']) == 1) and (card['Type'] != 'Land'):
            color_dict[card['Color']].append(card)
        # pull multicolors and colorless
        elif 'Land' not in type_spacesplit:
            uncolor_list.append(card)
        elif 'Land' in type_spacesplit:
            land_list.append(card)

    for color in color_dict.keys():
        # print(color)
        # if color != 'B':
        #     continue
        this_color_list = color_dict[color]

        ratio_little, ratio_diff = establish_ratios(SPELL_TYPES, this_color_list, COLOR_180)
        print(ratio_little)

        if len(this_color_list) > COLOR_180:
            # now we have all our ratios for the card types
            #  type current can be something crazy, in which its just OTHER
            cardlist = typed_pull_ratios(ratio_little, color, this_color_list, cardlist)
        elif len(this_color_list) < COLOR_180:
            print("ERROR: you need more primary color cards to keep up with ratio {} < {}".format(len(this_color_list), COLOR_180))
            read_in = input("Continue? [y]")
            if (read_in != '') and (read_in != None) and (read_in.lower() != 'y'):
                return -1, -1
            cardlist_maybe_tmp = compensate_maybeboard_typed(cardlist_maybe, ratio_diff, color)
            if cardlist_maybe_tmp == -1:
                print("ERROR: not enough maybeboard cards for the cube")
            else:
                cardlist_maybe = cardlist_maybe_tmp
        if len(this_color_list) <= COLOR_180:
            for card in this_color_list:
                colored_card_index = index_of_card_in_list(card, cardlist)
                cardlist[colored_card_index]['maybeboard'] = False

    # return
    # get lands
    land_size_real = len(land_list)
    print("retrieving {} lands".format(land_size_real))
    if len(land_list) > LAND_CAPACITY:
        cardlist = typed_rare_pull(land_list, cardlist, LAND_CAPACITY)
    # less than, we gotta get some lands from teh maybe board
    elif len(land_list) < LAND_CAPACITY:
        print("ERROR: you do not have enough lands for this draft, adjust land numbers {} < {}".format(
            len(land_list), LAND_CAPACITY
        ))
        read_in = input("Continue? [y]")
        if (read_in != '') and (read_in != None) and (read_in.lower() != 'y'):
            return -1, -1
        cardlist_maybe_tmp = compensate_maybeboard_typed(cardlist_maybe, {"Land": LAND_CAPACITY - land_size_real}, -1)
        if cardlist_maybe_tmp == -1:
            print("ERROR: few lands short")
        else:
            cardlist_maybe = cardlist_maybe_tmp
    # force in the rest of the lands
    if land_size_real <= LAND_CAPACITY:
        for card in land_list:
            colored_card_index = index_of_card_in_list(card, cardlist)
            cardlist[colored_card_index]['maybeboard'] = False
    # we are gonna set this to be the capacity, if its less we can comment it out
    # or overwrite, or just add in more lands ourselves to take the burden off the
    # uncolor
    land_size_real = LAND_CAPACITY

    # get multicolors and colorless cards
    print("retrieving multicolor and colorless")
    UNCOLOR_180 = CAPACITY_180 - (COLOR_180 * 5) - land_size_real
    if len(uncolor_list) > UNCOLOR_180:
        cardlist = typed_rare_pull(uncolor_list, cardlist, UNCOLOR_180)
    elif len(uncolor_list) < UNCOLOR_180:
        print("ERROR: you do not have enough colorless for this draft, adjust primary color numbers {} < {}".format(
            len(uncolor_list), UNCOLOR_180
        ))
        read_in = input("Continue? [y]")
        if (read_in != '') and (read_in != None) and (read_in.lower() != 'y'):
            return -1, -1
        # if force, then we don't have enough and just take all cards of this category
        cardlist_maybe_tmp = compensate_maybeboard_typed(cardlist_maybe, {"": UNCOLOR_180 - len(uncolor_list)}, None)
        if cardlist_maybe_tmp == -1:
            print("ERROR: few uncolor short")
        else:
            cardlist_maybe = cardlist_maybe_tmp
    if len(uncolor_list) <= UNCOLOR_180:
        for card in uncolor_list:
            colored_card_index = index_of_card_in_list(card, cardlist)
            cardlist[colored_card_index]['maybeboard'] = False

    return cardlist, cardlist_maybe