from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState

import re


# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
# def overfishedAnywhere(world: World, state: CollectionState, player: int):
#    """Has the player collected all fish from any fishing log?"""
#    for cat, items in world.item_name_groups:
#        if cat.endswith("Fishing Log") and state.has_all(items, player):
#            return True
#    return False

# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
# def anyClassLevel(state: CollectionState, player: int, level: str):
#    """Has the player reached the given level in any class?"""
#    for item in ["Figher Level", "Black Belt Level", "Thief Level", "Red Mage Level", "White Mage Level", "Black Mage Level"]:
#        if state.count(item, player) >= int(level):
#            return True
#    return False

# You can also return a string from your function, and it will be evaluated as a requires string.

def UnlockedInvestigatorCanPlay(world: World, state: CollectionState, player: int, investigatorName: str):
    """Has the player unlocked enough cards to play as specific investigator?"""
    investigator = world.item_name_to_item[investigatorName]
    investigatorsName = world.item_name_groups["Investigators"]

    categories: list[str] = list(investigator["category"])
    categories.remove("Investigators")

    checkedItems = list(state.prog_items[player])
    for investigatorName in investigatorsName:
        checkedItems = list(filter(lambda x: x not in investigatorName, checkedItems))

    count = 0
    for category in categories:
        categoryItems = world.item_name_groups[category]
        for categoryItem in categoryItems:
            count = count + checkedItems.count(categoryItem)
        if count >= 15:
            return True
    return False

def AnyUnlockedInvestigatorCanInvestigate(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can investigate?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        action = f"{investigator} can investigate"
        if not state.has(action, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanMove(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can move?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        action = f"{investigator} can move"
        if not state.has(action, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanAttack(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can attack?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        action = f"{investigator} can attack"
        if not state.has(action, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanEvade(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can evade?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        action = f"{investigator} can evade"
        if not state.has(action, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanAttackOrEvade(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can attack or evade?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can attack",
            f"{investigator} can evade"
        }
        if not state.has_any(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanAttackAndEvade(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can attack or evade?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can attack",
            f"{investigator} can evade"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanMoveAndInvestigate(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can move and investigate?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can move",
            f"{investigator} can investigate"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanMoveAndAttack(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can move and attack?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can move",
            f"{investigator} can attack"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanMoveAndEvade(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that move and evade?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can move",
            f"{investigator} can evade"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanMoveAndParley(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can move and parley?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can move",
            f"{investigator} can parley"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


def AnyUnlockedInvestigatorCanInvestigateAndEvade(world: World, state: CollectionState, player: int):
    """Has the player unlocked an investigator that can investigate and evade?"""
    investigators = world.item_name_groups.get("Investigators")
    for investigator in investigators:
        if not state.has(investigator, player):
            continue
        actions = {
            f"{investigator} can investigate",
            f"{investigator} can evade"
        }
        if not state.has_all(actions, player):
            continue
        if UnlockedInvestigatorCanPlay(world, state, player, investigator):
            return True
    return False


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


def ProgressiveStoryUnlocked(val: int):
    return True


def EligibleUnlockedInvestigatorCanPlay(world: World, state: CollectionState, player: int, name: str):
    """Has the player unlocked an investigator that can play specific card?"""
    if not state.has(name, player):
        return False
    currentItem = world.item_name_to_item[name]
    investigatorsNames = world.item_name_groups.get("Investigators")

    for investigatorName in investigatorsNames:
        res = True
        if not state.has(investigatorName, player):
            continue
        investigator = world.item_name_to_item[investigatorName]

        if not UnlockedInvestigatorCanPlay(world, state, player, investigatorName):
            continue

        for category in currentItem["category"]:
            match category:
                case "Card":
                    continue
                case "Skill":
                    continue
                case "Asset":
                    continue  # res = res and state.has(f"{investigatorName} can play an Asset", player)
                case "Event":
                    continue  # res = res and state.has(f"{investigatorName} can play an Event", player)
                case "Hand Slot":
                    res = res and state.has(f"{investigatorName} Hand Slot", player)
                case "2 Hand Slots":
                    res = res and state.has(f"{investigatorName} Hand Slot", player, 2)
                case "Ally Slot":
                    res = res and state.has(f"{investigatorName} Ally Slot", player)
                case "Body Slot":
                    res = res and state.has(f"{investigatorName} Body Slot", player)
                case "Arcane Slot":
                    res = res and state.has(f"{investigatorName} Arcane Slot", player)
                case "2 Arcane Slots":
                    res = res and state.has(f"{investigatorName} Arcane Slot", player, 2)
                case "Accessory Slot":
                    res = res and state.has(f"{investigatorName} Accessory Slot", player)
                case _:
                    res = res and (category in investigator["category"] or " Level " not in category)
            if not res: break
        if res: return True
    return False


onlyStrengthCommits = ["Beat Cop", "Machete", "Guard Dog", "Vicious Blow", "Shotgun", "Medical Texts", ".41 Derringer",
                       "Sneak Attack", "Shrivelling", "Leather Coat", "Baseball Bat", "Knife", "Overpower"]
onlyKnowledgeCommits = ["Evidence!", "Extra Ammunition", "Magnifying Glass", "Dr. Milan Christopher", "Working a Hunch",
                        "Magnifying Glass - Level 1", "Deduction", "Burglary", "Leo De Luca", "Sneak Attack",
                        "Leo De Luca - Level 1", "Forbidden Knowledge", "Scrying", "Scavenging", "Look What I Found!",
                        "Flashlight", "Perception"]
def EligibleUnlockedInvestigatorCanCommit(world: World, state: CollectionState, player: int, itemName: str):
    """Has the player unlocked an investigator that can commit specific card?"""
    if not state.has(itemName, player):
        return False
    currentItem = world.item_name_to_item[itemName]
    investigatorsNames = world.item_name_groups.get("Investigators")

    for investigatorName in investigatorsNames:
        res = True
        if not state.has(investigatorName, player):
            continue
        investigator = world.item_name_to_item[investigatorName]

        # Core Set Specification: Check if commit for strength and knowledge possible
        if (
                (currentItem["name"] in onlyStrengthCommits and not state.has(f"{investigator["name"]} can attack", player))
                or
                (currentItem["name"] in onlyKnowledgeCommits and not state.has(f"{investigator["name"]} can investigate", player))
         ):
            continue


        # Remove Unnecessary Categories
        categoryFilter = ["Card", "Asset", "Event", "Skill", "Hand Slot", "2 Hand Slots", "Ally Slot", "Body Slot",
                          "Arcane Slot", "2 Arcane Slots", "Accessory Slot"]
        currentItemCategories = list(filter(lambda x: x not in categoryFilter, currentItem["category"]))

        for category in currentItemCategories:
            res = res and category in investigator["category"]
            if not res:
                break
        if res:
            return True
    return False
