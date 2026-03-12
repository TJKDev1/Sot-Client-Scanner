"""Action states and session/ship type mappings."""

# Action state readable names
ACTION_STATES = {
    # Basic Movement
    "LocomotionActionStateId": "Walking",
    "SprintActionStateId": "Sprinting",
    "JumpActionStateId": "Jumping",
    "CrouchActionStateId": "Crouching",
    "SwimmingActionStateId": "Swimming",
    "SwimmingIdleActionStateId": "Treading Water",

    # Ladders & Climbing
    "ClimbingActionStateId": "Climbing Ladder",
    "UseLadderActionStateId": "Using Ladder",
    "OnBottomTransitionLadderActionStateId": "Mounting Ladder",
    "OffTopTransitionLadderActionStateId": "Dismounting Ladder",

    # Ship Controls
    "ControlWheelActionStateId": "Steering Ship",
    "ControlCapstanArmActionStateId": "Operating Anchor",
    "SailManipulationActionStateId": "Adjusting Sails",
    "ControlPulleyActionStateId": "Using Pulley",
    "HarpoonActionStateId": "Using Harpoon",

    # Combat & Actions
    "UseCannonActionStateId": "Using Cannon",
    "FiredFromCannonActionStateId": "Fired from Cannon",
    "LoadItemActionStateId": "Loading Item",
    "DigActionStateId": "Digging",
    "FishingActionStateId": "Fishing",
    "CookingActionStateId": "Cooking",
    "RepairActionStateId": "Repairing",
    "BailingActionStateId": "Bailing Water",

    # Interactions
    "UseMapTableActionStateId": "Viewing Map",
    "QuestTableActionStateId": "Quest Table",
    "InteractObjectActionStateId": "Interacting",
    "ItemInteractionActionStateId": "Interacting",
    "CompanyShopActionStateId": "Shopping",
    "TakeControlActionStateId": "Taking Control",

    # Social & Emotes
    "EmoteActionStateId": "Emoting",
    "WalkableEmoteActionStateId": "Emoting (Walking)",
    "SittingActionStateId": "Sitting",
    "SleepingActionStateId": "Sleeping",
    "PlayingInstrumentActionStateId": "Playing Instrument",
    "HideInObjectActionStateId": "Hiding",

    # Death & Respawn
    "DeadActionStateId": "Dead",
    "GhostActionStateId": "Ghost (Ferry)",
    "ReviveActionStateId": "Being Revived",
    "ReviveableActionStateId": "Reviveable",
    "RespawnActionStateId": "Respawning",
    "WaitingToSpawnActionStateId": "Waiting to Spawn",

    # Tunnels & Teleports
    "TeleportActionStateId": "Teleporting",
    "EnterTunnelOfTheDamnedActionStateId": "Entering Ferry",
    "SinkingTunnelOfTheDamnedActionStateId": "Ship Sinking (Ferry)",
    "ArrivalTunnelOfTheDamnedActionStateId": "Arriving at Ferry",
    "LeaveGhostShipActionStateId": "Leaving Ghost Ship",

    # Special States
    "ZiplineActionStateId": "Using Zipline",
    "RideTransitionActionStateId": "Mounting/Dismounting",
    "LoadPlayerActionStateId": "Loading",
    "MigrationActionStateId": "Server Migration",
    "RowingActionStateId": "Rowing",
    "NullActionStateId": "Idle",
    "Invalid": "Transitioning",
}

# Session type to ship name
SESSION_SHIP = {
    "SmallShipSessionTemplate": "Sloop",
    "MediumShipSessionTemplate": "Brigantine",
    "LargeShipSessionTemplate": "Galleon",
}
