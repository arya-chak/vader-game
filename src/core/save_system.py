"""
Save/load system — 3 JSON slots, fully stateless.
"""

import json
import os
from datetime import datetime
from typing import Optional

from src.character.vader import DarthVader
from src.character.suit_system import SuitSystem, SuitComponent
from src.story.story_system import StorySystem
from src.story.opening_scenes import create_opening_scenes
from src.story.mission_kyber import create_kyber_mission_scenes
from src.core.game_session import GameSession

_SAVES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "saves")
)
SAVE_VERSION = "1.0"
MAX_SLOTS = 3


def _slot_path(slot: int) -> str:
    return os.path.join(_SAVES_DIR, f"slot_{slot}.json")


class SaveSystem:

    @staticmethod
    def save(session: GameSession) -> bool:
        os.makedirs(_SAVES_DIR, exist_ok=True)
        vader = session.vader
        suit = session.suit
        story = session.story_system

        scene = story.scenes.get(story.state.current_scene_id)
        metadata = {
            "scene_id": story.state.current_scene_id,
            "scene_title": scene.title if scene else "",
            "darkness": vader.psychological_state.darkness,
            "story_arc": story.state.story_arc,
            "mission": story.state.current_mission,
        }

        vader_data = {
            "level": vader.level,
            "experience": vader.experience,
            "current_health": vader.current_health,
            "max_health": vader.max_health,
            "current_force_points": vader.current_force_points,
            "max_force_points": vader.max_force_points,
            "suit_integrity": vader.suit_integrity,
            "pain_level": vader.pain_level,
            "psychological_state": {
                "darkness": vader.psychological_state.darkness,
                "control": vader.psychological_state.control,
                "suppression": vader.psychological_state.suppression,
                "rage": vader.psychological_state.rage,
                "pain_tolerance": vader.psychological_state.pain_tolerance,
            },
            "relationships": vader.relationships,
            "choices_made": vader.choices_made,
            "missions_completed": vader.missions_completed,
            "jedi_killed": vader.jedi_killed,
            "learned_powers": [],
        }

        suit_data = {
            "integrity": suit.integrity,
            "component_integrity": {
                comp.name: val for comp, val in suit.component_integrity.items()
            },
            "base_pain_level": suit.base_pain_level,
            "current_pain_level": suit.current_pain_level,
            "installed_upgrades": list(suit.installed_upgrades.keys()),
            "total_suspicion": suit.total_suspicion,
            "suspicion_since_last_meeting": suit.suspicion_since_last_meeting,
            "missions_since_palpatine_meeting": suit.missions_since_palpatine_meeting,
            "palpatine_knows_upgrades": suit.palpatine_knows_upgrades,
            "loyalty_test_triggered": suit.loyalty_test_triggered,
            "loyalty_test_failed": suit.loyalty_test_failed,
            "credits": suit.credits,
            "materials": suit.materials,
        }

        story_data = {
            "current_scene_id": story.state.current_scene_id,
            "previous_scene_id": story.state.previous_scene_id,
            "flags": story.state.flags,
            "choices_made": story.state.choices_made,
            "current_mission": story.state.current_mission,
            "missions_completed": story.state.missions_completed,
            "missions_failed": story.state.missions_failed,
            "jedi_killed": story.state.jedi_killed,
            "civilians_spared": story.state.civilians_spared,
            "civilians_killed": story.state.civilians_killed,
            "imperials_killed": story.state.imperials_killed,
            "named_characters_met": story.state.named_characters_met,
            "named_characters_killed": story.state.named_characters_killed,
            "story_arc": story.state.story_arc,
            "arc_progress": story.state.arc_progress,
        }

        data = {
            "version": SAVE_VERSION,
            "slot": session.slot,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "playtime_seconds": session.playtime_seconds,
            "metadata": metadata,
            "vader": vader_data,
            "suit": suit_data,
            "story": story_data,
        }

        try:
            with open(_slot_path(session.slot), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except IOError:
            return False

    @staticmethod
    def load(slot: int) -> Optional[GameSession]:
        path = _slot_path(slot)
        if not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError):
            return None

        # --- Restore vader ---
        vd = data["vader"]
        vader = DarthVader()
        vader.level = vd["level"]
        vader.experience = vd["experience"]
        vader.current_health = vd["current_health"]
        vader.max_health = vd["max_health"]
        vader.current_force_points = vd["current_force_points"]
        vader.max_force_points = vd["max_force_points"]
        vader.suit_integrity = vd["suit_integrity"]
        vader.pain_level = vd["pain_level"]
        ps = vd["psychological_state"]
        vader.psychological_state.darkness = ps["darkness"]
        vader.psychological_state.control = ps["control"]
        vader.psychological_state.suppression = ps["suppression"]
        vader.psychological_state.rage = ps["rage"]
        vader.psychological_state.pain_tolerance = ps["pain_tolerance"]
        vader.relationships = vd["relationships"]
        vader.choices_made = vd["choices_made"]
        vader.missions_completed = vd["missions_completed"]
        vader.jedi_killed = vd["jedi_killed"]

        # --- Restore suit ---
        sd = data["suit"]
        suit = SuitSystem()
        suit.integrity = sd["integrity"]
        for name, val in sd["component_integrity"].items():
            try:
                suit.component_integrity[SuitComponent[name]] = val
            except KeyError:
                pass
        suit.base_pain_level = sd["base_pain_level"]
        suit.current_pain_level = sd["current_pain_level"]
        for upgrade_id in sd["installed_upgrades"]:
            if upgrade_id in suit.available_upgrades:
                upgrade = suit.available_upgrades[upgrade_id]
                upgrade.installed = True
                suit.installed_upgrades[upgrade_id] = upgrade
        suit.total_suspicion = sd["total_suspicion"]
        suit.suspicion_since_last_meeting = sd["suspicion_since_last_meeting"]
        suit.missions_since_palpatine_meeting = sd["missions_since_palpatine_meeting"]
        suit.palpatine_knows_upgrades = sd["palpatine_knows_upgrades"]
        suit.loyalty_test_triggered = sd["loyalty_test_triggered"]
        suit.loyalty_test_failed = sd["loyalty_test_failed"]
        suit.credits = sd["credits"]
        suit.materials = sd["materials"]

        # --- Restore story ---
        story = StorySystem(vader, suit)
        for scene in create_opening_scenes().values():
            story.register_scene(scene)
        for scene in create_kyber_mission_scenes().values():
            story.register_scene(scene)

        st = data["story"]
        story.state.current_scene_id = st["current_scene_id"]
        story.state.previous_scene_id = st.get("previous_scene_id")
        story.state.flags = st.get("flags", {})
        story.state.choices_made = st.get("choices_made", {})
        story.state.current_mission = st.get("current_mission")
        story.state.missions_completed = st.get("missions_completed", [])
        story.state.missions_failed = st.get("missions_failed", [])
        story.state.jedi_killed = st.get("jedi_killed", 0)
        story.state.civilians_spared = st.get("civilians_spared", 0)
        story.state.civilians_killed = st.get("civilians_killed", 0)
        story.state.imperials_killed = st.get("imperials_killed", 0)
        story.state.named_characters_met = st.get("named_characters_met", [])
        story.state.named_characters_killed = st.get("named_characters_killed", [])
        story.state.story_arc = st.get("story_arc", "dark_lord")
        story.state.arc_progress = st.get("arc_progress", 0)

        session = GameSession(slot)
        session.vader = vader
        session.suit = suit
        session.story_system = story
        session.playtime_seconds = data.get("playtime_seconds", 0.0)
        return session

    @staticmethod
    def get_slot_metadata(slot: int) -> Optional[dict]:
        path = _slot_path(slot)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                "slot": data.get("slot", slot),
                "timestamp": data.get("timestamp", ""),
                "playtime_seconds": data.get("playtime_seconds", 0.0),
                "metadata": data.get("metadata", {}),
            }
        except (IOError, json.JSONDecodeError):
            return None

    @staticmethod
    def get_all_slots() -> list:
        return [SaveSystem.get_slot_metadata(s) for s in range(1, MAX_SLOTS + 1)]

    @staticmethod
    def get_most_recent_slot() -> Optional[int]:
        best_slot = None
        best_ts = ""
        for slot in range(1, MAX_SLOTS + 1):
            meta = SaveSystem.get_slot_metadata(slot)
            if meta and meta["timestamp"] > best_ts:
                best_ts = meta["timestamp"]
                best_slot = slot
        return best_slot

    @staticmethod
    def slot_exists(slot: int) -> bool:
        return os.path.exists(_slot_path(slot))

    @staticmethod
    def delete(slot: int) -> bool:
        path = _slot_path(slot)
        if not os.path.exists(path):
            return False
        try:
            os.remove(path)
            return True
        except IOError:
            return False
