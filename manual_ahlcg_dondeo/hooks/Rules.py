from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value, get_option_value
from BaseClasses import CollectionState

import re

def TwoUnlockedInvestigatorsCanPlayTogether(world: World, state: CollectionState, player: int, investigatorsName: tuple[str, str]):
    decks = {}
    decks[investigatorsName[0]] = list(GetCardsInvestigatorCanPlay(world, state, player, investigatorsName[0]))
    decks[investigatorsName[1]] = list(GetCardsInvestigatorCanPlay(world, state, player, investigatorsName[1]))
    if len(decks[investigatorsName[0]]) < 15 or len(decks[investigatorsName[1]]) < 15:
        return False
    
    common_adder = 2 * int(get_option_value(world.multiworld, player, "revised_core_set_expansion")) + int(get_option_value(world.multiworld, player, "core_set_expansion")) - 2
    
    # Quick Check before trying to count cards between investigators
    # TODO: Check for Exceptional and 3-cards
    if (common_adder >= 2):
        return True
    
    firstDeck = decks[investigatorsName[0]]
    secondDeck = decks[investigatorsName[1]]
    common = set(decks[investigatorsName[0]]).intersection(decks[investigatorsName[1]]) 
    for commonCard in common:
        if commonCard in firstDeck:
            firstDeck.remove(commonCard)
        if commonCard in secondDeck:
            secondDeck.remove(commonCard)
    return len(firstDeck) * 2 + len(secondDeck) * 2 + len(common) * common_adder >= 60


def TwoUnlockedInvestigatorsWithActions(world: World, state: CollectionState, player: int, actions1: str, actions2: str):
    investigatorsActions = [actions1, actions2]
    investigatorsName = world.item_name_groups["Investigators"]
    investigatorsUnlocked = []
    for name in investigatorsName:
        if state.has(name, player):
            investigatorsUnlocked.append(name)
    nbUnlocked = len(investigatorsUnlocked)
    if nbUnlocked <= 2:
        return False    
    # Get Investigators with actions
    # If multiple actions for one investigator - Split (Character: +)
    investigatorsPerActions = {}
    for actions in investigatorsActions:
        investigatorsPerActions[actions] = GetUnlockedInvestigatorsWithActions(world, state, player, actions)
        if len(investigatorsPerActions[actions]) == 0:
            return False
    couple: list[tuple[str, str]] = []
    for investigator1 in investigatorsPerActions[investigatorsActions[0]]:
        for investigator2 in investigatorsPerActions[investigatorsActions[1]]:
            if investigator1 == investigator2 or (investigator1, investigator2) in couple or (investigator2, investigator1) in couple:
                continue
            couple.append((investigator1, investigator2))
            res = TwoUnlockedInvestigatorsCanPlayTogether(world, state, player, (investigator1, investigator2))
            if res:
                return True
    return False


def GetCardsInvestigatorCanPlay(world: World, state: CollectionState, player: int, investigatorName: str, deckSize: int = 0):
    investigator = world.item_name_to_item[investigatorName]
    investigatorsName = world.item_name_groups["Investigators"]

    categories: list[str] = list(investigator["category"])
    categories.remove("Investigators")

    # Get unique item name
    checkedItems = list(state.prog_items[player])
    checkedItems = set(map(lambda x: x.split("-")[0].rstrip(), checkedItems))
    for investigatorName in investigatorsName:
        checkedItems = list(filter(lambda x: x not in investigatorName, checkedItems))

    cards = []
    for category in categories:
        categoryItems = world.item_name_groups[category]
        for categoryItem in categoryItems:
            if categoryItem in checkedItems:
                cards.append(categoryItem)
                if deckSize > 0 and len(cards) >= deckSize:
                    return cards
    return cards


def GetUnlockedInvestigatorsWithActions(world: World, state: CollectionState, player: int, actionStr: str, nbInvestigator = 0):
    result = []
    investigators = world.item_name_groups.get("Investigators")
    actions = actionStr.split("+")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        if not HasInvestigatorActions(world, state, player, investigator, actions):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            result.append(investigator)
            if nbInvestigator != 0 and len(result) >= nbInvestigator:
                return result
    return result

def HasInvestigatorActions(world: World, state: CollectionState, player: int, investigator: str, actions: list[str]):
    for action in actions:
        if not state.has(f"{investigator} can {action}", player):
            return False
    return True

# For 1 investigator only. If multiple actions required: - Split (Character: +)
def AnyUnlockedInvestigatorWithActions(world: World, state: CollectionState, player: int, actionStr: str):
    """has the player unlocked an investigator that can do specific actions?"""
    return len(GetUnlockedInvestigatorsWithActions(world, state, player, actionStr, 1)) == 1


def AnyUnlockedInvestigatorCanPlayLita(world: World, state: CollectionState, player: int):
    """Has the player unlocked what it takes to play Lita Chantler?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        conditions = {
            "Lita Chantler",
            f"{investigator} Ally Slot",
        }
        if not state.has_all(conditions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def EligibleUnlockedInvestigatorCanPlay(world: World, state: CollectionState, player: int, cardName: str, actions: str = None):
    """Has the player unlocked an investigator that can play specific card?"""
    if not state.has(cardName, player):
        return False
    currentItem = world.item_name_to_item[cardName]
    investigatorsNames = world.item_name_groups.get("Investigators")

    for investigatorName in investigatorsNames:
        res = True
        if not state.has(investigatorName, player):
            continue
        investigator = world.item_name_to_item[investigatorName]
        #Check actions
        if actions is not None and not HasInvestigatorActions(world, state, player, investigatorName, actions.split("+")):
            continue
        if not UnlockedInvestigatorCanPlay(world, state, player, investigatorName):
            continue

        # Remove Unnecessary Categories
        categoryFilter = ["Card", "Asset", "Event", "Skill", "Hand Slot", "2 Hand Slots", "Ally Slot", "Body Slot",
                          "Arcane Slot", "2 Arcane Slots", "Accessory Slot"]
        currentItemCategories = list(filter(lambda x: x not in categoryFilter, currentItem["category"]))
        for category in currentItemCategories:
            res = res and (category in investigator["category"] or " Level " not in category)
            if not res:
                break
        if res:
            return True
    return False

# Need testing
firearms = {"Roland Banks": 1, ".45 Automatic": 1, ".41 Derringer": 1, "Shotgun": 2}
def EligibleUnlockedInvestigatorCanPlaceFirearm(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can place a firearm?"""

    investigatorsNames = world.item_name_groups.get("Investigators")

    for firearm in firearms:
        currentItem = world.item_name_to_item[firearm]
        if not state.has(f"{firearm}", player):
            continue

        # Investigator: Check for his signature card
        if ("Investigators" in currentItem["category"]):
            if not state.has(f"{firearm} Hand Slot", player, firearms[firearm]):
                continue
            if UnlockedInvestigatorCanPlay(world, state, player, firearm):
                return True
        # Card: Generic check
        else:
            for investigator in investigatorsNames:
                if not state.has(f"{investigator}", player):
                    continue
                if not state.has(f"{investigator} Hand Slot", player, firearms[firearm]):
                    continue
                if EligibleUnlockedInvestigatorCanPlay(world, state, player, firearm):
                    return True
    return False


onlyStrengthCommits = ["Beat Cop", "Machete", "Guard Dog", "Vicious Blow", "Shotgun", "Medical Texts", ".41 Derringer",
                       "Sneak Attack", "Shriveling", "Leather Coat", "Baseball Bat", "Knife", "Overpower"]
onlyKnowledgeCommits = ["Evidence!", "Extra Ammunition", "Magnifying Glass", "Dr. Milan Christopher", "Working a Hunch",
                        "Magnifying Glass - Level 1", "Deduction", "Burglary", "Leo De Luca", "Sneak Attack",
                        "Leo De Luca - Level 1", "Forbidden Knowledge", "Scrying", "Scavenging", "Look What I Found!",
                        "Flashlight", "Perception"]
def EligibleUnlockedInvestigatorCanCommit(world: World, state: CollectionState, player: int, itemName: str):
    """Has the player unlocked an investigator that can commit specific card?"""

    # Check if card unlocked
    if not state.has(itemName, player):
        return False
    currentItem = world.item_name_to_item[itemName]
    investigatorsNames = world.item_name_groups.get("Investigators")

    for investigatorName in investigatorsNames:
        res = True
        # Check if investigator unlocked
        if not state.has(investigatorName, player):
            continue
        investigator = world.item_name_to_item[investigatorName]

        # Check if investigator can play (enough cards to create deck)
        if not UnlockedInvestigatorCanPlay(world, state, player, investigatorName):
            continue

        # Remove Unnecessary Categories
        categoryFilter = ["Card", "Asset", "Event", "Skill", "Hand Slot", "2 Hand Slots", "Ally Slot", "Body Slot",
                          "Arcane Slot", "2 Arcane Slots", "Accessory Slot", "Exceptional"]
        currentItemCategories = list(filter(lambda x: x not in categoryFilter, currentItem["category"]))

        # Check if Investigator has requirements to have card into his deck
        for category in currentItemCategories:
            res = res and category in investigator["category"]
            if not res:
                break
        if res:
            # Core Set Specification: Check if commit for strength and knowledge possible
            actionsCommit = []
            if currentItem["name"] in onlyStrengthCommits:
                actionsCommit.append("attack")
            if currentItem["name"] in onlyKnowledgeCommits:
                actionsCommit.append("investigate")

            # If not actions to commit: Valid
            if len(actionsCommit) == 0:
                return True

            # Check if any playable investigator has necessary action to make commit card possible
            for action in actionsCommit:
                hasActionCommit = AnyUnlockedInvestigatorWithActions(world, state, player, action)
                if hasActionCommit:
                    return True
    return False


def UnlockedInvestigatorCanPlay(world: World, state: CollectionState, player: int, investigatorName: str):
    """Has the player unlocked enough cards to play as specific investigator?"""
    if not state.has(investigatorName, player):
        return False
    return len(GetCardsInvestigatorCanPlay(world, state, player, investigatorName, 15)) >= 15


def AnyUnlockedInvestigatorIsPrepared(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator's full potential?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can investigate",
            f"{investigator} can move",
            f"{investigator} can attack",
            f"{investigator} can evade",
            f"{investigator} can parley",
            # f"{investigator} can play an Asset",
            # f"{investigator} can play an Event",
            # f"{investigator} can commit a card",
            f"{investigator} Hand Slot",
            f"{investigator} Arcane Slot",
            f"{investigator} Ally Slot",
            f"{investigator} Body Slot",
            f"{investigator} Accessory Slot"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False

firstScenario1A = {
    "Extracurricular Activity - Beginning": "0",
    "Extracurricular Activity - After Act 1": "1",
    "Extracurricular Activity - After Act 2": "2",
    "The House Always Wins - Beginning": "3",
    "The House Always Wins - After Act 1": "4",
    "The House Always Wins - After Act 2": "5",
}
firstScenario1B = {
    "Extracurricular Activity - Beginning": "3",
    "Extracurricular Activity - After Act 1": "4",
    "Extracurricular Activity - After Act 2": "5",
    "The House Always Wins - Beginning": "0",
    "The House Always Wins - After Act 1": "1",
    "The House Always Wins - After Act 2": "2",
}
def requirementDLScenario1(world: World, state: CollectionState, player: int, regionName: str):
    optionValue = world.options.dunwich_legacy_starter_scenario.value
    requirementScenario = {}
    if optionValue == 0: # Scenario 1A
        requirementScenario = firstScenario1A
    else: # Scenario 1B
        requirementScenario = firstScenario1B
    return f"|Progressive History Unlock:{requirementScenario[regionName]}|"
