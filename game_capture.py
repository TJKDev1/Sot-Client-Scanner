"""
Sea of Thieves Telemetry Capture Script for mitmproxy
This file is loaded by mitmdump to intercept and parse game telemetry.
"""
from mitmproxy import http
import atexit
import json
import os
from datetime import datetime
import re


class GameCapture:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)
        self._log_file = None
        self._ws_log_file = None
        self.url_pattern = r"https://.*-fd\.prod\.athena\.msrareservices\.com/ares/cyclone/api/ingestion/tenant/athenaprodga/route/game/.*"
        print("[FILTER] Capturing ALL Sea of Thieves events - NO FILTERING!")
        print("[WEBSOCKET] Logging to websocket_capture.txt")

        # Safety net: close file handles even if done() is never called
        atexit.register(self._close_files)

        self.skip_events = []  # no skipping; UI/screen + status events are useful

        # ALL tracked actor keys from the game - COMPLETE LIST
        self.all_world_event_keys = [
            "SkullCloud", "AshenLordCloud", "ShipCloud", "Ghostship_Flameheart_Cloud",
            "Storm", "FogBank", "Volcano", "Earthquake", "Geyser", "SuperHeatedWater",
            "Haunted_Fort", "Spire", "SkeletonThrone",
            "Shipwreck", "Shipwreck_Graveyard", "Shipwreck_Smuggler",
            "BarrelsOfPlenty", "Jettisoned_Supplies", "MessageInABottle",
            "WreckDebris_Land", "WreckDebris_Sea",
            "Mermaid",
        ]

        self.all_ship_keys = [
            "Ship_Small", "Ship_Medium", "Ship_Large",
            "AI_Ship_Aggressive_Large", "AI_Ship_Aggressive_Small",
            "AI_Ship_Battle_Large", "AI_Ship_Battle_Small",
            "AI_Ship_Passive_Large", "AI_Ship_Passive_Small",
            "AI_Ship_ReapersTribute",
            "Rowboat", "Rowboat_Cannon", "Rowboat_Harpoon",
        ]

        self.all_ai_keys = [
            "AI_Skeleton", "AI_Phantom",
            "AI_Shark", "AI_Megalodon", "AI_Megalodon_Ancient", "AI_Megalodon_OnDemand",
            "AI_Kraken", "AI_Kraken_Tiny", "AI_SwimmingCreature",
            "AI_GhostShip_Captain", "AI_GhostShip_MiniBoss", "AI_GhostShip_Grunt",
            "AI_OceanCrawler_Crab", "AI_OceanCrawler_Eel", "AI_OceanCrawler_Hermit",
            "AI_Siren",
            "AI_Fauna", "AI_Pets", "AI_Pets_Wielded",
            "FishingFish",
        ]

        self.all_entity_keys = [
            "Player", "NPC", "GoalDrivenCharacter",
            "Mercenary", "MercenarySpawner", "ReapersChestMercenary",
            "Booty", "Booty_AshenWindsSkull", "Booty_CaptainsLog",
            "Booty_ReapersChest", "Booty_RuinedCaptainsLog",
            "Consumable", "GoldCoin", "Pouch_Ammo", "Pouch_Doubloons", "Pouch_Gold",
            "HuntingSpear", "BlowpipeDart",
            "Deployable_Cannon", "Deployable_Cannon_Item",
            "Mechanism", "Mechanism_Continuous", "Mechanism_OneShot", "MechanismElementProxy",
            "StorageContainer", "StorageContainerBuoyant",
            "BuoyantActor", "StatueThreat", "Trap", "ShortRangeMarker",
            "FireworkExplosion", "FireworkProjectile",
            "Unknown",
        ]

    @property
    def log_file(self):
        """Lazily open the main log file."""
        if self._log_file is None or self._log_file.closed:
            self._log_file = open("logs/sea_of_thieves_capture.txt", "a", encoding="utf-8")
        return self._log_file

    @property
    def ws_log_file(self):
        """Lazily open the WebSocket log file."""
        if self._ws_log_file is None or self._ws_log_file.closed:
            self._ws_log_file = open("logs/websocket_capture.txt", "a", encoding="utf-8")
        return self._ws_log_file

    def _safe_write(self, file_prop, content):
        """Write to a log file, swallowing I/O errors so the addon stays alive."""
        try:
            f = file_prop
            f.write(content)
            f.flush()
        except Exception as e:
            print(f"[LOG_ERROR] Failed to write: {e}")

    def _close_files(self):
        """Flush and close both log files (safe to call multiple times)."""
        for f in (self._log_file, self._ws_log_file):
            if f is not None and not f.closed:
                try:
                    f.flush()
                    f.close()
                except Exception:
                    pass

    def done(self):
        """Called by mitmproxy when the addon is unloaded."""
        self._close_files()

    def websocket_message(self, flow):
        """Called for each WebSocket message - FULL LOGGING"""
        message = flow.websocket.messages[-1]
        direction = "CLIENT->" if message.from_client else "SERVER->"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        url = flow.request.pretty_url

        content = message.content
        content_type = "BINARY"
        decoded_content = ""

        try:
            decoded_content = content.decode('utf-8')
            content_type = "TEXT"
            try:
                json_data = json.loads(decoded_content)
                decoded_content = json.dumps(json_data, indent=2)
                content_type = "JSON"
            except json.JSONDecodeError:
                pass
        except UnicodeDecodeError:
            decoded_content = self.hex_dump(content)
            content_type = "BINARY"

        preview = decoded_content[:100].replace('\n', ' ') if len(decoded_content) > 100 else decoded_content.replace('\n', ' ')
        print(f"[WEBSOCKET] {direction} {len(content)} bytes ({content_type}): {preview}...")

        log_entry = f"\n{'='*80}\n"
        log_entry += f"[{timestamp}] WEBSOCKET MESSAGE\n"
        log_entry += f"Direction: {direction}\n"
        log_entry += f"URL: {url}\n"
        log_entry += f"Size: {len(content)} bytes\n"
        log_entry += f"Type: {content_type}\n"
        log_entry += f"Content:\n{decoded_content}\n"

        self._safe_write(self.ws_log_file, log_entry)

    def websocket_start(self, flow):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = flow.request.pretty_url
        headers = dict(flow.request.headers)
        print(f"[WEBSOCKET_START] {url}")

        log_entry = f"\n{'#'*80}\n"
        log_entry += f"[{timestamp}] WEBSOCKET CONNECTION OPENED\n"
        log_entry += f"URL: {url}\n"
        log_entry += f"Headers:\n{json.dumps(headers, indent=2)}\n"

        self._safe_write(self.ws_log_file, log_entry)

    def websocket_end(self, flow):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = flow.request.pretty_url
        msg_count = len(flow.websocket.messages) if flow.websocket else 0
        print(f"[WEBSOCKET_END] {url} ({msg_count} messages)")

        log_entry = f"\n{'#'*80}\n"
        log_entry += f"[{timestamp}] WEBSOCKET CONNECTION CLOSED\n"
        log_entry += f"URL: {url}\n"
        log_entry += f"Total Messages: {msg_count}\n"

        self._safe_write(self.ws_log_file, log_entry)

    def hex_dump(self, data, bytes_per_line=16):
        lines = []
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:08x}  {hex_part:<{bytes_per_line*3}}  |{ascii_part}|")
        return '\n'.join(lines)

    def process_event_body(self, event_body, event_name=""):
        """Extract data from any event body - ALL FRAGMENTS"""

        # Player Position
        if "PlayerPositionTelemetryFragment" in event_body:
            pos_data = event_body["PlayerPositionTelemetryFragment"]
            pos = pos_data.get("position", {})
            location = pos_data.get("worldLocationName", "Unknown")
            x = pos.get("x", 0)
            y = pos.get("y", 0)
            z = pos.get("z", 0)
            print(f"[POSITION] X:{x} Y:{y} Z:{z} Location:{location}")

        # Network Data
        if "NetworkDataTelemetryFragment" in event_body:
            net = event_body["NetworkDataTelemetryFragment"]
            rtt = net.get("avgRttMilliseconds", -1)
            rtt_var = net.get("avgRttVariationMilliseconds", -1)
            out_bps = net.get("avgOutBytesPerSecond", 0)
            in_bps = net.get("avgInBytesPerSecond", 0)
            out_loss = net.get("avgOutPacketLossRatio", 0)
            in_loss = net.get("avgInPacketLossRatio", 0)
            print(f"[NETWORK] RTT:{rtt}ms Var:{rtt_var}ms Out:{out_bps}B/s In:{in_bps}B/s OutLoss:{out_loss} InLoss:{in_loss}")

        # FPS / Frame Duration Data
        if "FrameDurationDataTelemetryFragment" in event_body:
            fd = event_body["FrameDurationDataTelemetryFragment"]
            avg_frame = fd.get("average", 0)
            min_frame = fd.get("min", 0)
            max_frame = fd.get("max", 0)
            target = fd.get("averageTargetFrameTime", 0)
            histogram = fd.get("frameTimeHistogram", [])
            # histogram buckets represent frame time distribution
            print(f"[FPS] AvgFrame:{avg_frame:.2f}ms MinFrame:{min_frame:.2f}ms MaxFrame:{max_frame:.2f}ms Target:{target:.2f}ms Histogram:{','.join(str(h) for h in histogram)}")

        # Action State Changes
        if "ActionStateChangeAcceptedTelemetryEvent" in event_body:
            action = event_body["ActionStateChangeAcceptedTelemetryEvent"]
            prev_state = action.get("previousState", "")
            new_state_server = action.get("newStateServer", "")
            new_state_client = action.get("newStateClient", "")
            time_in_prev = action.get("timeInPreviousState", 0)

            # Prefer client state when server is "Invalid" (client-predicted actions)
            new_state = new_state_client if new_state_server == "Invalid" else new_state_server
            print(f"[ACTION_STATE] From:{prev_state} To:{new_state} TimeInPrev:{time_in_prev:.1f}s")

        # Crew Info
        if "CrewBaseTelemetryFragment" in event_body:
            crew = event_body["CrewBaseTelemetryFragment"]
            crew_count = crew.get("currentCrewCount", 0)
            session_type = crew.get("sessionType", "")
            crew_type = crew.get("crewType", "")
            alliance_id = crew.get("allianceId", "00000000-0000-0000-0000-000000000000")
            is_captained = crew.get("isCaptainedCrew", False)
            guild_id = crew.get("guildId", "00000000-0000-0000-0000-000000000000")
            has_alliance = alliance_id != "00000000-0000-0000-0000-000000000000"
            has_guild = guild_id != "00000000-0000-0000-0000-000000000000"
            print(f"[CREW] Count:{crew_count} Session:{session_type} Type:{crew_type} Captained:{is_captained} Alliance:{has_alliance} Guild:{has_guild}")

        # Player Current Ship
        if "PlayerCurrentShipTelemetryFragment" in event_body:
            ship = event_body["PlayerCurrentShipTelemetryFragment"]
            ship_size = ship.get("currentShipSize", "")
            is_crew_ship = ship.get("isCrewShip", False)
            ship_loc = ship.get("currentShipLocation", {})
            sx = ship_loc.get("x", 0)
            sy = ship_loc.get("y", 0)
            sz = ship_loc.get("z", 0)
            print(f"[PLAYER_SHIP] Size:{ship_size} IsCrewShip:{is_crew_ship} ShipPos:({sx},{sy},{sz})")

        # Company Progress (from PlayerPirateSetsSails)
        if "PlayerPirateSetsSailsTelemetryEvent" in event_body:
            sails = event_body["PlayerPirateSetsSailsTelemetryEvent"]
            companies = sails.get("companyProgress", [])
            company_parts = []
            for c in companies:
                cid = c.get("companyId", "")
                level = c.get("level", 0)
                xp = c.get("xp", 0)
                xp_next = c.get("xpRequiredToAttainNextRank", 0)
                company_parts.append(f"{cid}:{level}:{xp}:{xp_next}")
            if company_parts:
                print(f"[COMPANIES] {';'.join(company_parts)}")

            # Season info
            seasons = sails.get("seasons", [])
            if seasons:
                s = seasons[0]
                title = s.get("localizedTitle", "")
                theme = s.get("themeId", "")
                active_until = s.get("activeUntil", "")
                print(f"[SEASON] Title:{title} Theme:{theme} Until:{active_until}")

        # Fire Status
        if "FireTelemetryFragment" in event_body:
            fire = event_body["FireTelemetryFragment"]
            ships_with_fire = fire.get("numOfShipWithActiveCells", 0)
            active_cells = fire.get("numOfActiveCells", 0)
            if ships_with_fire > 0 or active_cells > 0:
                print(f"[FIRE] ShipsOnFire:{ships_with_fire} ActiveCells:{active_cells}")

        # Game Mode + Client Info (from ClientTelemetryFragment)
        if "ClientTelemetryFragment" in event_body:
            client = event_body["ClientTelemetryFragment"]
            play_mode = client.get("clientPlayMode", "")
            play_state = client.get("playModeState", "")
            build_id = client.get("buildId", "")
            platform_id = client.get("platformId", "")
            spec = client.get("deviceSpecScore", "")
            rhi = client.get("rHIType", "")
            fg = client.get("appInForeground", "")
            device_id = client.get("deviceId", "")
            player_game_id = client.get("playerGameId", "")
            title_session = client.get("titleSession", "")

            if play_mode:
                print(f"[GAMEMODE] Mode:{play_mode} State:{play_state}")

            # Emit richer client metadata (GUI can de-dup updates)
            if build_id or title_session or device_id:
                print(
                    f"[CLIENT] Build:{build_id} Platform:{platform_id} Spec:{spec} RHI:{rhi} "
                    f"Foreground:{fg} Device:{device_id} PlayerGameId:{player_game_id} Session:{title_session} "
                    f"PlayMode:{play_mode} State:{play_state}"
                )

        # Services Connection Result
        if "ServicesConnectionResultTelemetryEvent" in event_body:
            s = event_body["ServicesConnectionResultTelemetryEvent"]
            result = s.get("result", "")
            t = s.get("timeInSeconds", 0)
            refresh = s.get("refreshDiscoveryTime", 0)
            token = s.get("retrieveLogonTokenTime", 0)
            reconnect = s.get("reconnectToBridgeTime", 0)
            reason = s.get("reason", "")
            req_stamp = s.get("requestedStampId", "")
            disc_stamp = s.get("discoveryStampId", "")
            logon_stamp = s.get("logonRedirectStampId", "")
            contest_stamp = s.get("contestStampId", "")
            print(
                f"[SERVICES] Result:{result} Total:{t:.3f}s Refresh:{refresh:.3f}s Token:{token:.3f}s "
                f"Reconnect:{reconnect:.3f}s Reason:{reason} Requested:{req_stamp} Discovery:{disc_stamp} "
                f"Logon:{logon_stamp} Contest:{contest_stamp}"
            )

        # Boot / Login errors (Cyanbeard etc.)
        if "ClientBootFlowErrorOccurredTelemetryEvent" in event_body:
            e = event_body["ClientBootFlowErrorOccurredTelemetryEvent"]
            msg = e.get("errorMessage", "")
            if msg:
                print(f"[BOOT_ERROR] {msg}")

        # UI screen transitions (Engage / ServiceConnection / Error / Blank)
        if "UIScreenTransitionTelemetryEvent" in event_body:
            u = event_body["UIScreenTransitionTelemetryEvent"]
            cur = u.get("currentScreen", "")
            prev = u.get("previousScreen", "")
            print(f"[UI_SCREEN] Current:{cur} Previous:{prev}")

        # Window focus / fullscreen state
        if "WindowStatusChangedTelemetryEvent" in event_body:
            w = event_body["WindowStatusChangedTelemetryEvent"]
            status = w.get("statusName", "")
            focused = w.get("isFocused", False)
            minimized = w.get("isMinimized", False)
            fullscreen = w.get("isFullScreen", False)
            print(f"[WINDOW] Status:{status} Focused:{focused} Minimized:{minimized} FullScreen:{fullscreen}")

        # Movement base (what you're standing on)
        if "CharacterMovementBaseChangedTelemetryEvent" in event_body:
            mb = event_body["CharacterMovementBaseChangedTelemetryEvent"]
            prev = mb.get("previousBaseActorName", "")
            new = mb.get("newBaseActorName", "")
            print(f"[MOVEMENT_BASE] From:{prev} To:{new}")

        # Player Prompts (location discoveries, NPC interactions)
        if "PlayerPromptTelemetryEvent" in event_body:
            prompt = event_body["PlayerPromptTelemetryEvent"]
            message = prompt.get("message", "")
            key = prompt.get("key", "")
            if message:
                print(f"[PROMPT] Message:{message} Key:{key}")

        # Tracked Actors
        if "TrackedActorTelemetryFragment" in event_body:
            tracked_data = event_body["TrackedActorTelemetryFragment"].get("json", {})

            world_events = []
            for key in self.all_world_event_keys:
                if key in tracked_data and tracked_data[key].get("Count", 0) > 0:
                    count = tracked_data[key]["Count"]
                    world_events.append(f"{key}:{count}")
            if world_events:
                print(f"[WORLD_EVENTS] {','.join(world_events)}")

            ship_data = []
            for key in self.all_ship_keys:
                if key in tracked_data and tracked_data[key].get("Count", 0) > 0:
                    count = tracked_data[key]["Count"]
                    ship_data.append(f"{key}:{count}")
            if ship_data:
                print(f"[SHIPS] {','.join(ship_data)}")

            ai_data = []
            for key in self.all_ai_keys:
                if key in tracked_data and tracked_data[key].get("Count", 0) > 0:
                    count = tracked_data[key]["Count"]
                    ai_data.append(f"{key}:{count}")
            if ai_data:
                print(f"[AI_ENTITIES] {','.join(ai_data)}")

            entity_data = []
            for key in self.all_entity_keys:
                if key in tracked_data and tracked_data[key].get("Count", 0) > 0:
                    count = tracked_data[key]["Count"]
                    entity_data.append(f"{key}:{count}")
            if entity_data:
                print(f"[ENTITIES] {','.join(entity_data)}")

        # Ship Systems Status
        if "ShippingStatsTelemetryFragment" in event_body:
            ship_stats = event_body["ShippingStatsTelemetryFragment"].get("json", {})
            ship_systems = []

            sail_avg = ship_stats.get("Aggregate_SailTick", {}).get("Avg", 0)
            cannon_avg = ship_stats.get("Aggregate_CannonTick", {}).get("Avg", 0)
            wheel_avg = ship_stats.get("AggregateWheelTick", {}).get("Avg", 0)
            capstan_avg = ship_stats.get("Aggregate_CapstanTick", {}).get("Avg", 0)
            rudder_avg = ship_stats.get("Aggregate_RudderTick", {}).get("Avg", 0)
            hull_avg = ship_stats.get("HullDamageAggregateTick", {}).get("Avg", 0)
            water_avg = ship_stats.get("ShipInternalWaterAggregateTick", {}).get("Avg", 0)
            sinking_avg = ship_stats.get("SinkingComponent_AggregateTick", {}).get("Avg", 0)
            mast_avg = ship_stats.get("Aggregate_MastTick", {}).get("Avg", 0)
            harpoon_avg = ship_stats.get("Aggregate_HarpoonLauncherTick", {}).get("Avg", 0)

            if sail_avg > 0: ship_systems.append("Sails")
            if cannon_avg > 0: ship_systems.append("Cannons")
            if wheel_avg > 0: ship_systems.append("Wheel")
            if capstan_avg > 0: ship_systems.append("Capstan")
            if rudder_avg > 0: ship_systems.append("Rudder")
            if mast_avg > 0: ship_systems.append("Mast")
            if harpoon_avg > 0: ship_systems.append("Harpoon")
            if hull_avg > 0: ship_systems.append(f"HullDamage:{hull_avg:.4f}")
            if water_avg > 0: ship_systems.append(f"Water:{water_avg:.4f}")
            if sinking_avg > 0: ship_systems.append("SINKING")

            if ship_systems:
                print(f"[SHIP_SYSTEMS] {','.join(ship_systems)}")

    def request(self, flow: http.HTTPFlow):
        if flow.request.method != "POST":
            return

        if not re.match(self.url_pattern, flow.request.url):
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if not flow.request.content:
                return

            body = json.loads(flow.request.content)

            log_entry = f"\n{'='*80}\n"
            log_entry += f"[{timestamp}] CAPTURED POST REQUEST\n"
            log_entry += f"Body (JSON):\n{json.dumps(body, indent=2)}\n"
            self._safe_write(self.log_file, log_entry)

            if "events" in body:
                for event in body["events"]:
                    event_name = event.get("name", "Unknown")

                    if event_name in self.skip_events:
                        continue

                    print(f"[EVENT] {event_name}")

                    event_body = event.get("body", {})
                    self.process_event_body(event_body, event_name)

        except json.JSONDecodeError:
            print("[ERROR] Failed to parse JSON")
        except Exception as e:
            print(f"[ERROR] {str(e)}")


addons = [GameCapture()]