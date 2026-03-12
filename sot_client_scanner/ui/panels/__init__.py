"""Panel widgets for the dashboard UI."""

from sot_client_scanner.ui.panels.position import PositionPanel
from sot_client_scanner.ui.panels.network import NetworkPanel
from sot_client_scanner.ui.panels.ship import ShipInfoPanel
from sot_client_scanner.ui.panels.session import SessionPanel
from sot_client_scanner.ui.panels.status import StatusPanel
from sot_client_scanner.ui.panels.world_events import WorldEventsPanel
from sot_client_scanner.ui.panels.ships import ShipsPanel
from sot_client_scanner.ui.panels.ai import AIPanel
from sot_client_scanner.ui.panels.entities import EntitiesPanel

__all__ = [
    "PositionPanel",
    "NetworkPanel",
    "ShipInfoPanel",
    "SessionPanel",
    "StatusPanel",
    "WorldEventsPanel",
    "ShipsPanel",
    "AIPanel",
    "EntitiesPanel",
]
