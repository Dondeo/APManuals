# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, Visibility
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################

# Logic options

class PlayingCampaignCoreSet(Toggle):
    default = 0

class PlayingCampaignDunwichLegacy(Toggle):
    default = 0

# File options

class CoreSetExpansion(Range):
    """
    Number of Core Set boxes you have. This will determine how many number of cards you can afford to make a deck for an investigator.
    Warning: you need at least 2 Core Set boxes or 1 Revised Core Set Box to make it work.
    """
    range_start = 0
    range_end = 4
    default = 2

class RevisedCoreSetExpansion(Range):
    """
    Number of Revised Core Set boxes you have. This will determine how many number of cards you can afford to make a deck for an investigator.
    This option will also add revised core set specific cards to logic. (#TODO)
    Warning: you need at least 2 Core Set boxes or 1 Revised Core Set Box to make it work.
    """
    range_start = 0
    range_end = 2
    default = 0

class DunwichLegacyExpansion(Range):
    """
    Definition for all Expansion Packs:
    Number of said Expansion Pack you have. You must fulfill one of these two criterias to set to '1':
    - Having the Campaign Expansion + Investigator Expansion
    - Having the older expansion pack + all mythos packs
    You can set the option to '2' if you have the requirement above and one of these two criterias:
    - Another Investigator Expansion
    - Another older expansion pack + all mythos packs

    These options allow you to set options based on the related expansion.

    ---
    Number of Dunwich Legacy Expansion Pack you have.
    """
    range_start = 0
    range_end = 2
    default = 0

class CoreSetInvestigators(Toggle):
    """
    When Enabled: Add all investigators from Core Set to the pool.
    If all investigators options are disabled, this option will be enabled by default.
    """
    default = 1

class DunwichLegacyInvestigators(Toggle):
    """
    Dunwich Legacy Expansion Required.
    When Enabled: Add all investigators from Dunwich Legacy Expansion Pack to the pool.
    """
    default = 0

class DunwichLegacyCards(Toggle):
    """
    Dunwich Legacy Expansion Required.
    When Enabled: Add all deckbuilding cards from Dunwich Legacy Expansion Pack to the pool.
    """
    default = 0

class CampaignChoice(Choice):
    """
    Choose a campaign you want to play.

    noz: Night of the Zealot
    dl: Dunwich Legacy (Dunwich Legacy Expansion Required)
    """
    display_name = "Campaign choice"
    option_noz = 0
    option_dl = 1
    default = 0

class DunwichLegacyStarterScenario(Choice):
    """
    Only with Dunwich Legacy Campaign.
    Choose which first scenario you begin.
    """
    display_name = "Starter Scenario (Dunwich Legacy)"
    option_1A = 0
    option_1B = 1

class LocationLogic(Choice):
    """
    Some locations are classified as "hard" to obtain.
    This option give you the possibility to remove or keep these locations to logic.

    Standard: Remove Hard Locations to logic
    Hard: Keep all Locations to logic (Good Luck)
    """
    display_name = "Location Logic"
    option_standard = 0
    option_hard = 1
    default = 0

class NumberOfStarterInvestigators(Range):
    """
    Set the number of investigators available at start. Useful if you wish to play with friends.
    Also impact card randomization at start, making sure all available investigators can build a deck.
    """
    display_name = "Number of investigators unlocked at start"
    range_start = 1
    range_end = 4
    default = 1

class StarterCardsMaxLevel(Range):
    """
    Set the maximum level af cards that can be available at start.
    """
    display_name = "Maximum Level of cards that can be picked for starter deck"
    range_start = 0
    range_end = 5
    default = 0

class StarterChoice(Choice):
    option_zero = 0
    option_one_starter = 1
    option_one_any = 2
    option_all_starter = 3
    option_all_any = 4
    option_random_starter = 5
    option_random_any = 6    

class StarterActionMove(StarterChoice):
    """
    Definition for all StarterAction and StarterSlot:
    Define the number of investigators that can make an action or has access to a slot at start.

    zero: None
    one_starter: Any starter investigator has access to it
    one_any: Any investigator (locked or unlocked) has access to it
    all_starter: All starters investigators have access to it
    all_any: All investigators have access to it
    random_starter: A random number of starter investigators have access to it - can be 0
    random_any: A random number of investigators (locked or unlocked) have access to it - can be 0

    ---
    Number of investigators that can move (as Basic Action and card-related action) at start.
    """
    display_name = "Number of investigators that can move at start"
    default = 1

class StarterActionInvestigate(StarterChoice):
    """
    Number of investigators that can investigate (as Basic Action and card-related action) at start.
    """
    display_name = "Number of investigators that can investigate at start"
    default = 1

class StarterActionAttack(StarterChoice):
    """
    Number of investigators that can attack (as Basic Action and card-related action) at start.
    """
    display_name = "Number of investigators that can attack at start"
    default = 1

class StarterActionEvade(StarterChoice):
    """
    Number of investigators that can evade (as Basic Action and card-related action) at start.
    """
    display_name = "Number of investigators that can evade at start"
    default = 1

class StarterActionParley(StarterChoice):
    """
    Number of investigators that can parley (as Basic Action and card-related action) at start.
    """
    display_name = "Number of investigators that can parley at start"
    default = 1

class StarterActionEngage(StarterChoice):
    display_name = "Number of investigators that can engage at start"
    default = 4

class StarterActionCommit(StarterChoice):
    display_name = "Number of investigators that can commit at start"
    default = 4

class StarterSlotHand(StarterChoice):
    """
    Number of investigators that has a Hand Slot at start.
    """
    display_name = "Number of investigators that has a hand slot at start"
    default = 0

class StarterSlotBody(StarterChoice):
    """
    Number of investigators that has a Body Slot at start.
    """
    display_name = "Number of investigators that has a body slot at start"
    default = 0

class StarterSlotAlly(StarterChoice):
    """
    Number of investigators that has an Ally Slot at start.
    """
    display_name = "Number of investigators that has an ally slot at start"
    default = 0

class StarterSlotArcane(StarterChoice):
    """
    Number of investigators that has an Arcane Slot at start.
    """
    display_name = "Number of investigators that has an arcane slot at start"
    default = 0

class StarterSlotAccessory(StarterChoice):
    """
    Number of investigators that has an Accessory Slot at start.
    """
    display_name = "Number of investigators that has an accessory slot at start"
    default = 0

class NumberOfStarterSlotHand(Range):
    """
    Set how many hand slots are available at start for an investigator.
    Useful if "StarterSlotHand" has other option than "zero".
    """
    display_name = "Number of hand slots unlocked at start"
    range_start = 1
    range_end = 2
    default = 1

class NumberOfStarterSlotArcane(Range):
    """
    Set how many arcane slots are available at start for an investigator.
    Useful if "StarterSlotArcane" has other option than "zero".
    """
    display_name = "Number of arcane slots unlocked at start"
    range_start = 1
    range_end = 2
    default = 1

# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["core_set_expansion"] = CoreSetExpansion
    options["revised_core_set_expansion"] = RevisedCoreSetExpansion
    options["dunwich_legacy_expansion"] = DunwichLegacyExpansion

    options["core_set_investigators"] = CoreSetInvestigators
    options["dunwich_legacy_investigators"] = DunwichLegacyInvestigators
    options["dunwich_legacy_cards"] = DunwichLegacyCards

    options["campaign_choice"] = CampaignChoice
    options["playing_campaign_core_set"] = PlayingCampaignCoreSet
    options["playing_campaign_dunwich_legacy"] = PlayingCampaignDunwichLegacy

    options["dunwich_legacy_starter_scenario"] = DunwichLegacyStarterScenario

    options["location_logic"] = LocationLogic

    options["number_of_starter_investigators"] = NumberOfStarterInvestigators
    options["starter_cards_max_level"] = StarterCardsMaxLevel

    options["starter_action_move"] = StarterActionMove
    options["starter_action_investigate"] = StarterActionInvestigate
    options["starter_action_attack"] = StarterActionAttack
    options["starter_action_evade"] = StarterActionEvade
    options["starter_action_parley"] = StarterActionParley
    # options["starter_action_engage"] = StarterActionEngage
    # options["starter_action_commit"] = StarterActionCommit
    options["starter_slot_hand"] = StarterSlotHand
    options["starter_slot_body"] = StarterSlotBody
    options["starter_slot_ally"] = StarterSlotAlly
    options["starter_slot_arcane"] = StarterSlotArcane
    options["starter_slot_accessory"] = StarterSlotAccessory
    options["number_of_starter_slot_hand"] = NumberOfStarterSlotHand
    options["number_of_starter_slot_arcane"] = NumberOfStarterSlotArcane
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    for option in options.type_hints.keys():
        if 'playing_campaign_' in option:
            options.type_hints[option].visibility = Visibility.none
    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
