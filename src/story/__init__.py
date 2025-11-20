"""
Story Module
Manages narrative progression, dialogue, choices, and story state.
"""

from .story_system import (
    StorySystem,
    StoryState,
    Scene,
    DialogueLine,
    Choice,
    ChoiceType,
    StoryFlag,
    create_dialogue,
    create_choice
)

__all__ = [
    'StorySystem',
    'StoryState',
    'Scene',
    'DialogueLine',
    'Choice',
    'ChoiceType',
    'StoryFlag',
    'create_dialogue',
    'create_choice'
]