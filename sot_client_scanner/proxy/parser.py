"""Parse stdout lines from mitmdump into structured (signal_name, data) tuples."""

import re


def parse_line(line):
    """Parse a single output line from the mitmproxy addon.

    Returns a list of (signal_name, data) tuples. Most lines produce zero or
    one result, but every recognised line may also produce an ("output", line)
    entry for the console log.
    """
    if not line:
        return []

    results = []

    if "[POSITION]" in line:
        match = re.search(r"X:([\d.-]+) Y:([\d.-]+) Z:([\d.-]+) Location:(\S+)", line)
        if match:
            results.append(("position_update", {
                "x": float(match.group(1)),
                "y": float(match.group(2)),
                "z": float(match.group(3)),
                "location": match.group(4),
            }))

    elif "[NETWORK]" in line:
        match = re.search(
            r"RTT:(-?[\d]+)ms Var:(-?[\d]+)ms Out:(\d+)B/s In:(\d+)B/s OutLoss:([\d.]+) InLoss:([\d.]+)",
            line,
        )
        if match:
            results.append(("network_update", {
                "rtt": int(match.group(1)),
                "rtt_var": int(match.group(2)),
                "out_bps": int(match.group(3)),
                "in_bps": int(match.group(4)),
                "out_loss": float(match.group(5)),
                "in_loss": float(match.group(6)),
            }))

    elif "[FPS]" in line:
        match = re.search(
            r"AvgFrame:([\d.]+)ms MinFrame:([\d.]+)ms MaxFrame:([\d.]+)ms Target:([\d.]+)ms Histogram:(.*)",
            line,
        )
        if match:
            results.append(("fps_update", {
                "avg_frame": float(match.group(1)),
                "min_frame": float(match.group(2)),
                "max_frame": float(match.group(3)),
                "target": float(match.group(4)),
                "histogram": match.group(5),
            }))

    elif "[ACTION_STATE]" in line:
        match = re.search(r"From:(\S+) To:(\S+) TimeInPrev:([\d.]+)s", line)
        if match:
            results.append(("action_state_update", {
                "from": match.group(1),
                "to": match.group(2),
                "time_in_prev": float(match.group(3)),
            }))

    elif "[CREW]" in line:
        match = re.search(
            r"Count:(\d+) Session:(\S*) Type:(\S*) Captained:(\S+) Alliance:(\S+) Guild:(\S+)",
            line,
        )
        if match:
            results.append(("crew_update", {
                "count": int(match.group(1)),
                "session": match.group(2),
                "type": match.group(3),
                "captained": match.group(4) == "True",
                "alliance": match.group(5) == "True",
                "guild": match.group(6) == "True",
            }))

    elif "[PLAYER_SHIP]" in line:
        match = re.search(r"Size:(\S*) IsCrewShip:(\S+) ShipPos:\(([\d.-]+),([\d.-]+),([\d.-]+)\)", line)
        if match:
            results.append(("player_ship_update", {
                "size": match.group(1),
                "is_crew": match.group(2) == "True",
                "x": float(match.group(3)),
                "y": float(match.group(4)),
                "z": float(match.group(5)),
            }))

    elif "[COMPANIES]" in line:
        data = line.split("[COMPANIES]")[1].strip()
        companies = []
        for entry in data.split(';'):
            parts = entry.split(':')
            if len(parts) == 4:
                companies.append({
                    "id": parts[0],
                    "level": int(parts[1]),
                    "xp": int(parts[2]),
                    "xp_next": int(parts[3]),
                })
        if companies:
            results.append(("company_update", companies))

    elif "[SEASON]" in line:
        match = re.search(r"Title:(.+?) Theme:(\S+) Until:(\S+)", line)
        if match:
            results.append(("season_update", {
                "title": match.group(1),
                "theme": match.group(2),
                "until": match.group(3),
            }))

    elif "[FIRE]" in line:
        match = re.search(r"ShipsOnFire:(\d+) ActiveCells:(\d+)", line)
        if match:
            results.append(("fire_update", {
                "ships": int(match.group(1)),
                "cells": int(match.group(2)),
            }))

    elif "[GAMEMODE]" in line:
        match = re.search(r"Mode:(\S+) State:(\S*)", line)
        if match:
            results.append(("gamemode_update", {
                "mode": match.group(1),
                "state": match.group(2),
            }))

    elif "[PROMPT]" in line:
        match = re.search(r"Message:(.+?) Key:(.+)$", line)
        if match:
            results.append(("prompt_update", {
                "message": match.group(1),
                "key": match.group(2),
            }))

    elif "[WORLD_EVENTS]" in line:
        events = line.split("[WORLD_EVENTS]")[1].strip().split(',')
        results.append(("world_events_update", events))

    elif "[SHIPS]" in line:
        ships = line.split("[SHIPS]")[1].strip().split(',')
        results.append(("ships_update", ships))

    elif "[SHIP_SYSTEMS]" in line:
        systems = line.split("[SHIP_SYSTEMS]")[1].strip().split(',')
        results.append(("ship_systems_update", systems))

    elif "[AI_ENTITIES]" in line:
        ai_list = line.split("[AI_ENTITIES]")[1].strip().split(',')
        results.append(("ai_entities_update", ai_list))

    elif "[ENTITIES]" in line:
        entities = line.split("[ENTITIES]")[1].strip().split(',')
        results.append(("entities_update", entities))

    elif "[EVENT]" in line:
        event_name = line.split("[EVENT]")[1].strip()
        results.append(("event_captured", event_name))

    elif "[SERVICES]" in line:
        match = re.search(
            r"Result:(\S*) Total:([\d.-]+)s Refresh:([\d.-]+)s Token:([\d.-]+)s Reconnect:([\d.-]+)s "
            r"Reason:(.*?) Requested:(\S*) Discovery:(\S*) Logon:(\S*) Contest:(\S*)",
            line,
        )
        if match:
            results.append(("services_update", {
                "result": match.group(1),
                "total": float(match.group(2)),
                "refresh": float(match.group(3)),
                "token": float(match.group(4)),
                "reconnect": float(match.group(5)),
                "reason": match.group(6).strip(),
                "requested": match.group(7),
                "discovery": match.group(8),
                "logon": match.group(9),
                "contest": match.group(10),
            }))

    elif "[BOOT_ERROR]" in line:
        msg = line.split("[BOOT_ERROR]", 1)[-1].strip()
        if msg:
            results.append(("boot_error_update", {"message": msg}))

    elif "[UI_SCREEN]" in line:
        match = re.search(r"Current:(\S*) Previous:(\S*)", line)
        if match:
            results.append(("ui_screen_update", {"current": match.group(1), "previous": match.group(2)}))

    elif "[WINDOW]" in line:
        match = re.search(r"Status:(\S*) Focused:(\S+) Minimized:(\S+) FullScreen:(\S+)", line)
        if match:
            def _to_bool(v: str) -> bool:
                return v.lower() in ("true", "1", "yes")
            results.append(("window_update", {
                "status": match.group(1),
                "focused": _to_bool(match.group(2)),
                "minimized": _to_bool(match.group(3)),
                "fullscreen": _to_bool(match.group(4)),
            }))

    elif "[CLIENT]" in line:
        match = re.search(
            r"Build:(\S*) Platform:(\S*) Spec:(\S*) RHI:(\S*) Foreground:(\S*) "
            r"Device:(\S*) PlayerGameId:(\S*) Session:(\S*) PlayMode:(\S*) State:(\S*)",
            line,
        )
        if match:
            results.append(("client_update", {
                "build": match.group(1),
                "platform": match.group(2),
                "spec": match.group(3),
                "rhi": match.group(4),
                "foreground": match.group(5),
                "device": match.group(6),
                "player_game_id": match.group(7),
                "session": match.group(8),
                "play_mode": match.group(9),
                "state": match.group(10),
            }))

    elif "[MOVEMENT_BASE]" in line:
        match = re.search(r"From:(\S*) To:(\S*)", line)
        if match:
            results.append(("movement_base_update", {"from": match.group(1), "to": match.group(2)}))

    # Log relevant lines (always runs independently of the elif chain above)
    _LOG_KEYWORDS = (
        "[CAPTURED]", "[POSITION]", "[EVENT]", "[FILTER]", "[ERROR]",
        "[WORLD_EVENTS]", "[SHIPS]", "[SHIP_SYSTEMS]", "[AI_ENTITIES]",
        "[ENTITIES]", "[WEBSOCKET]", "[NETWORK]", "[FPS]", "[ACTION_STATE]",
        "[CREW]", "[COMPANIES]", "[SEASON]", "[FIRE]", "[GAMEMODE]",
        "[PROMPT]", "[PLAYER_SHIP]", "[SERVICES]", "[BOOT_ERROR]",
        "[UI_SCREEN]", "[WINDOW]", "[CLIENT]", "[MOVEMENT_BASE]",
        "Error", "Exception",
    )
    if any(kw in line for kw in _LOG_KEYWORDS):
        results.append(("output", line))

    return results
