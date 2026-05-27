"""
Converts story system Scene/Choice objects into the dict format
StoryDialogueScreen.set_scene() expects.
"""

import re
from typing import List, Dict
from src.story.story_system import Scene, Choice

_VADER_SPEAKERS = {"vader", "darth vader"}
_TAG_PREFIX = re.compile(r"^\[[A-Z ]+\] ?")
_NARRATOR_SPEAKERS = {"narrator", "inner voice"}


def _portraits_for_line(speaker: str):
    lower = speaker.lower()
    if lower in _NARRATOR_SPEAKERS:
        return None, None
    if lower in _VADER_SPEAKERS:
        return "vader_mask", None
    return "vader_mask", lower.replace(" ", "_")


def scene_to_gui(scene: Scene, available_choices: List[Choice]) -> Dict:
    """Convert a Scene + available Choice list to the set_scene() dict format."""
    lines = []
    for line in scene.dialogue:
        left, right = _portraits_for_line(line.speaker)
        entry = {
            "speaker": line.speaker,
            "text": line.text,
            "left_portrait": left,
            "right_portrait": right,
        }
        if line.internal_thought:
            entry["internal_thought"] = line.internal_thought
        lines.append(entry)

    choices = []
    if available_choices:
        for choice in available_choices:
            choices.append({
                "id": choice.id,
                "text": _TAG_PREFIX.sub("", choice.text),
                "tags": [],
            })
    elif scene.auto_next:
        # No choices — synthesise a continue action so the player can advance
        choices.append({
            "id": "__continue__",
            "text": "Continue...",
            "tags": [],
        })

    return {
        "id": scene.id,
        "title": scene.title,
        "background_image": None,
        "lines": lines,
        "choices": choices,
    }
