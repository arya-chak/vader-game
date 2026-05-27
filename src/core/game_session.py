"""
Active game session — holds all live game objects for one playthrough.
"""

from __future__ import annotations
from typing import Optional

from src.character.vader import DarthVader
from src.character.suit_system import SuitSystem
from src.story.story_system import StorySystem, Scene
from src.story.opening_scenes import create_opening_scenes
from src.story.mission_kyber import create_kyber_mission_scenes


class GameSession:
    """Holds the live vader, suit, and story objects for an active playthrough."""

    def __init__(self, slot: int):
        self.slot = slot
        self.vader: Optional[DarthVader] = None
        self.suit: Optional[SuitSystem] = None
        self.story_system: Optional[StorySystem] = None
        self.playtime_seconds: float = 0.0

    @classmethod
    def new_game(cls, slot: int) -> "GameSession":
        session = cls(slot)
        session.vader = DarthVader()
        session.suit = SuitSystem()
        session.story_system = StorySystem(session.vader, session.suit)

        for scene in create_opening_scenes().values():
            session.story_system.register_scene(scene)
        for scene in create_kyber_mission_scenes().values():
            session.story_system.register_scene(scene)

        # Set starting scene ID directly — on_enter fires when player first advances
        session.story_system.state.current_scene_id = "the_void"
        return session

    def get_current_scene(self) -> Optional[Scene]:
        scene_id = self.story_system.state.current_scene_id
        return self.story_system.scenes.get(scene_id) if scene_id else None

    def advance_to_scene(self, scene_id: str) -> Optional[Scene]:
        """Start a scene (fires on_enter) and return it. Returns None on failure."""
        success, _msg, scene = self.story_system.start_scene(scene_id)
        return scene if success else None

    def make_choice(self, choice_id: str) -> dict:
        """Delegate to story_system.make_choice and return the consequences dict."""
        scene_id = self.story_system.state.current_scene_id
        _success, _msg, consequences = self.story_system.make_choice(scene_id, choice_id)
        return consequences

    def tick(self, dt: float) -> None:
        self.playtime_seconds += dt
