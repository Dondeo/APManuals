# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item
from Options import OptionError

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging


########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    if world.options.revised_core_set_expansion.value == 0 and world.options.core_set_expansion.value < 1:
        raise OptionError("One of the following options must have a value: Revised Core Set Expansion > 0; Core Set Expansion > 1")
    if world.options.dunwich_legacy_expansion.value == 0:
        world.options.dunwich_legacy_investigators.value = 0
        world.options.dunwich_legacy_cards.value = 0
    match world.options.campaign_choice.value:
        case 0: # Core Set Campaign
            world.options.playing_campaign_core_set.value = 1
        case 1: # Dunwich Legacy Campaign
            if world.options.dunwich_legacy_expansion.value <= 0:
                raise OptionError("Cannot play dunwich legacy campaign because you don't have the required expansion")
            else:
                world.options.playing_campaign_dunwich_legacy.value = 1
        case _:
            raise OptionError("Error when reading value for Camapgin Choice")
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):

    # Use this hook to remove locations from the world
    opt = int(get_option_value(multiworld, player, "location_logic"))
    locationNamesToRemove: list[str] = [] # List of location names
    if opt == 0: locationNamesToRemove = list(world.location_name_groups["Hard Logic"])

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Number of Starter Investigators Option
    opt = int(get_option_value(multiworld, player, "number_of_starter_investigators"))
    starters_investigators: list[Item] = []
    starters_str_investigators: list[str] = []
    all_str_investigators: list[str] = list(world.item_name_groups["Investigators"])

    temp_str_investigators = list(all_str_investigators)
    investigators_deck_cards_nb: dict[str, int] = {}
    for _ in range(opt):
       choice = world.random.choice(temp_str_investigators)
       starters_investigators.append(world.item_name_to_item[choice])
       starters_str_investigators.append(choice)
       investigators_deck_cards_nb[choice] = 0
       temp_str_investigators.remove(choice)
    
    starters_cards: list[Item] = []
    str_cards: list[str] = list(world.item_name_groups["Card"])

    # Level filter option
    opt = int(get_option_value(multiworld, player, "starter_cards_max_level"))
    level_filter = []
    for i in range(5 - opt):
        for investigator_class in ["Guardian", "Rogue", "Seeker", "Survivor", "Mystic", "Neutral"]:
            level_filter.append(f"{investigator_class} Level {5 - i}")

    # Randomize starter cards
    get_cards_finished = False
    while not get_cards_finished:
        # Get a new card
        choice = world.random.choice(str_cards)
        card_item = world.item_name_to_item[choice]
        str_cards.remove(choice)

        # Same name card already drawn (different level) -> discarded
        same_name = False
        for starter_card in starters_cards:
            str_starter_card = starter_card["name"].split('-')[0].rstrip()
            str_card_item = card_item["name"].split('-')[0].rstrip()
            if str_starter_card == str_card_item:
                same_name = True
                break
        if same_name:
            continue

        # Remove Unnecessary Categories
        category_filter = ["Card", "Asset", "Event", "Skill", "Hand Slot", "2 Hand Slots", "Ally Slot", "Body Slot", "Arcane Slot", "2 Arcane Slots", "Accessory Slot"]
        card_categories = list(filter(lambda x: x not in category_filter, card_item["category"]))

        # Level Filter
        card_filtered = False
        for category in card_categories:
            if category in level_filter:
                card_filtered = True
                break
        if card_filtered:
            continue
        
        # Check if card is compatible with starter investigators
        eligible_investigators: list[str] = []
        for starter_investigator in starters_investigators:
            name: str = starter_investigator["name"]
            if investigators_deck_cards_nb[name] >= 15:
                continue
            for category in card_categories:
                if category in starter_investigator["category"]:
                    eligible_investigators.append(name)
                    break

        # Count cards for unlock
        if len(eligible_investigators) > 0:
            starters_cards.append(card_item)
            for eligible_investigator in eligible_investigators:
                investigators_deck_cards_nb[eligible_investigator] += 1
            
        # check loop
        get_cards_finished = True
        for deck_nb in investigators_deck_cards_nb.values():
            if deck_nb < 15:
                get_cards_finished = False
                break

    # Actions and Slots
    starter_opts_str: dict[str, tuple[str, int]] = {
        "starter_action_move": ("can move", 1),
        "starter_action_investigate": ("can investigate", 1),
        "starter_action_attack": ("can attack", 1),
        "starter_action_evade": ("can evade", 1),
        "starter_action_parley": ("can parley", 1),
        "starter_slot_hand": ("Hand Slot", int(get_option_value(multiworld, player, "number_of_starter_slot_hand"))),
        "starter_slot_body": ("Body Slot", 1),
        "starter_slot_ally": ("Ally Slot", 1),
        "starter_slot_arcane": ("Arcane Slot", int(get_option_value(multiworld, player, "number_of_starter_slot_arcane"))),
        "starter_slot_accessory": ("Accessory Slot", 1)
    }
    starter_opts = []
    for opt_str in starter_opts_str:
        # Get number of unlock
        opt = int(get_option_value(multiworld, player, opt_str))
        nb_opt_unlock = 0
        if opt == 0: continue
        elif opt in [1, 2]: nb_opt_unlock = 1
        elif opt == 3: nb_opt_unlock = len(starters_str_investigators)
        elif opt == 4: nb_opt_unlock = len(all_str_investigators)
        elif opt == 5: nb_opt_unlock = world.random.randrange(len(starters_str_investigators))
        elif opt == 6: nb_opt_unlock = world.random.randrange(len(all_str_investigators))
        else: continue

        # Starter or Any Investigators
        eligible_investigators = []
        if (opt in [1, 3, 5]): eligible_investigators = list(starters_str_investigators)
        elif (opt in [2, 4, 6]): eligible_investigators = list(all_str_investigators)

        # Random choices or all choices
        chosen_investigators = []
        if nb_opt_unlock >= len(eligible_investigators):
            chosen_investigators = eligible_investigators
        else:
            for _ in range(nb_opt_unlock):
                choice = world.random.choice(eligible_investigators)
                chosen_investigators.append(choice)
                eligible_investigators.remove(choice)
        # Parse item name
        for investigator in chosen_investigators:
            for _ in range(starter_opts_str[opt_str][1]):
                starter_opts.append(f"{investigator} {starter_opts_str[opt_str][0]}")

    # manage item pool
    for item_remove in starters_investigators:
        item = next(i for i in item_pool if i.name == item_remove["name"])
        multiworld.push_precollected(item)
        item_pool.remove(item)
    for item_remove  in starters_cards:
        item = next(i for i in item_pool if i.name == item_remove["name"])
        multiworld.push_precollected(item)
        item_pool.remove(item)
    for item_remove  in starter_opts:
        item = next(i for i in item_pool if i.name == item_remove)
        multiworld.push_precollected(item)
        item_pool.remove(item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
