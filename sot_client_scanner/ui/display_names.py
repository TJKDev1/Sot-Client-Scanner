"""Friendly display-name mappings for ships, AI, entities, and ship systems.

Centralises all the name-lookup dicts that were previously scattered across
individual update handlers in MainWindow.
"""

SHIP_DISPLAY_NAMES = {
    "Small": "Sloop",
    "Medium": "Brigantine",
    "Large": "Galleon",
}

SHIP_LIST_NAMES = {
    "Ship_Small": "Sloop",
    "Ship_Medium": "Brigantine",
    "Ship_Large": "Galleon",
}

AI_DISPLAY_NAMES = {
    "AI_Skeleton": "Skeleton",
    "AI_Phantom": "Phantom",
    "AI_Shark": "Shark",
    "AI_Megalodon": "Megalodon",
    "AI_Megalodon_Ancient": "Ancient Meg",
    "AI_Megalodon_OnDemand": "Summoned Meg",
    "AI_Kraken": "Kraken",
    "AI_Kraken_Tiny": "Baby Kraken",
    "AI_SwimmingCreature": "Sea Creature",
    "AI_GhostShip_Captain": "Ghost Captain",
    "AI_GhostShip_MiniBoss": "Ghost MiniBoss",
    "AI_GhostShip_Grunt": "Ghost Ship",
    "AI_OceanCrawler_Crab": "Crab",
    "AI_OceanCrawler_Eel": "Eel",
    "AI_OceanCrawler_Hermit": "Hermit",
    "AI_Siren": "Siren",
    "AI_Fauna": "Fauna",
    "AI_Pets": "Pet",
    "AI_Pets_Wielded": "Pet (held)",
    "FishingFish": "Fish",
}

ENTITY_DISPLAY_NAMES = {
    "Player": "Player",
    "NPC": "NPC",
    "GoalDrivenCharacter": "Character",
    "Mercenary": "Mercenary",
    "MercenarySpawner": "Merc Spawner",
    "ReapersChestMercenary": "Reaper Merc",
    "Booty": "Treasure",
    "Booty_AshenWindsSkull": "Ashen Skull",
    "Booty_CaptainsLog": "Captain's Log",
    "Booty_ReapersChest": "Reaper's Chest",
    "Booty_RuinedCaptainsLog": "Ruined Log",
    "Consumable": "Consumable",
    "GoldCoin": "Gold",
    "Pouch_Ammo": "Ammo",
    "Pouch_Doubloons": "Doubloons",
    "Pouch_Gold": "Gold Pouch",
    "HuntingSpear": "Spear",
    "BlowpipeDart": "Dart",
    "StorageContainer": "Storage",
    "StorageContainerBuoyant": "Floating Storage",
    "Mechanism": "Mechanism",
    "Mechanism_OneShot": "Trap Mechanism",
    "Trap": "Trap",
    "StatueThreat": "Coral Statue",
    "FireworkExplosion": "Firework",
    "FireworkProjectile": "Firework",
}

SYSTEM_DISPLAY_NAMES = {
    "Sails": "Sails",
    "Cannons": "Cannons",
    "Wheel": "Wheel",
    "Capstan": "Anchor",
    "Rudder": "Rudder",
    "Harpoon": "Harpoon",
}
