"""
Opening Scene: The Operating Table
Vader's first moments in the suit - the iconic scene from Episode III.
This is where the player's journey begins.

FIXED: Properly transitions to Kyber Crystal mission instead of mentioning wrong Jedi.
"""

from typing import Dict
from .story_system import (
    Scene, DialogueLine, Choice, ChoiceType,
    create_dialogue, create_choice
)


def on_awakening_enter(vader, suit, state):
    """Called when entering the awakening scene"""
    # Set initial flags
    state.set_flag("awakened")
    
    # Log the moment
    print("\n" + "═" * 60)
    print("EPISODE III - AFTERMATH")
    print("Location: Emperor's Medical Facility, Coruscant")
    print("═" * 60)


def on_learn_truth(vader, suit, state):
    """Called when Vader learns Padmé's fate"""
    # Major psychological impact
    vader.psychological_state.rage = 100
    vader.modify_darkness(15)
    vader.modify_suppression(20)
    state.set_flag("learned_padme_death")


def on_nooo_rage(vader, suit, state):
    """Called when Vader unleashes the iconic 'NOOO' """
    # Maximum rage, full dark side commitment
    vader.psychological_state.rage = 100
    vader.modify_darkness(20)
    vader.modify_suppression(30)
    state.set_flag("iconic_nooo")
    
    # Damage from Force rage
    suit.take_suit_damage(5)


def on_silent_grief(vader, suit, state):
    """Called when Vader silently accepts the truth"""
    # Internal collapse, but controlled
    vader.modify_control(10)
    vader.modify_suppression(25)
    vader.psychological_state.rage = 80
    state.set_flag("silent_grief")


def on_blame_palpatine(vader, suit, state):
    """Called when Vader blames Palpatine"""
    # Seeds of betrayal planted early
    vader.relationships["palpatine"] -= 15
    vader.modify_control(5)
    vader.modify_suppression(15)
    state.set_flag("early_resentment")


def create_opening_scenes() -> Dict[str, Scene]:
    """
    Create the complete opening sequence.
    Returns dict of scene_id: Scene
    """
    scenes = {}
    
    # ================================================================
    # SCENE 1: THE VOID
    # Brief moment of consciousness before awakening
    # ================================================================
    
    scenes["the_void"] = Scene(
        id="the_void",
        title="The Void",
        description="Darkness. Pain. Silence.",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Inner Voice",
                "...",
                thought="Where am I? I can't... feel anything. Everything is... wrong."
            ),
            create_dialogue(
                "Inner Voice",
                "...",
                thought="Padmé... I saved her. I must have saved her. The dark side gave me the power."
            ),
            create_dialogue(
                "Inner Voice",
                "...",
                thought="But why can't I feel her? Where is she?"
            )
        ],
        auto_next="awakening"
    )
    
    # ================================================================
    # SCENE 2: AWAKENING
    # First moments of consciousness in the suit
    # ================================================================
    
    scenes["awakening"] = Scene(
        id="awakening",
        title="The Awakening",
        description="You awaken to the sound of mechanical breathing. Your breathing.",
        location="Surgical Suite, Emperor's Medical Facility, Coruscant",
        scene_type="dialogue",
        on_enter=on_awakening_enter,
        dialogue=[
            create_dialogue(
                "Medical Droid",
                "Subject is stabilizing. Neural interface responding. Lord Vader, can you hear me?",
                emotion="clinical"
            ),
            create_dialogue(
                "Vader",
                "*attempts to move*",
                emotion="confused",
                thought="My body... it won't respond. What have they done to me?"
            ),
            create_dialogue(
                "Medical Droid",
                "Please remain still. Your cybernetic systems are still calibrating. The Emperor will be pleased you survived the procedure.",
                emotion="matter-of-fact"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing intensifies*",
                emotion="rising panic",
                thought="This mask... this breathing apparatus... I'm trapped in this thing."
            ),
            create_dialogue(
                "Vader",
                "Where... is... Padmé?",
                emotion="desperate",
                thought="She has to be safe. Everything I did... it was for her."
            )
        ],
        choices=[
            create_choice(
                "demand_padme",
                "[RAGE] DEMAND to know where Padmé is",
                ChoiceType.MORAL,
                darkness=5,
                rage_change=15,
                next_scene="demand_answer",
                tooltip="Give in to desperation and fury",
                response=create_dialogue(
                    "Vader",
                    "TELL ME NOW!",
                    emotion="furious"
                )
            ),
            create_choice(
                "ask_padme",
                "[CONTROL] Ask about her condition calmly",
                ChoiceType.MORAL,
                control=5,
                rage_change=5,
                next_scene="ask_calmly",
                tooltip="Try to maintain composure despite the pain",
                response=create_dialogue(
                    "Vader",
                    "Her condition... is she safe?",
                    emotion="controlled desperation"
                )
            ),
            create_choice(
                "focus_on_self",
                "[SUPPRESS] Focus on understanding what happened to you",
                ChoiceType.MORAL,
                suppression_change=5,
                control=3,
                next_scene="assess_situation",
                tooltip="Push aside emotion, assess the situation like a tactician",
                response=create_dialogue(
                    "Vader",
                    "What... what have you done to me?",
                    emotion="cold"
                )
            )
        ]
    )
    
    # ================================================================
    # SCENE 3A: DEMAND ANSWER (Rage path)
    # ================================================================
    
    scenes["demand_answer"] = Scene(
        id="demand_answer",
        title="Fury Unleashed",
        description="Your rage builds. The machines around you begin to shake.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Medical Droid",
                "Lord Vader, please! Your rage is destabilizing the equipment. I must—",
                emotion="alarmed"
            ),
            create_dialogue(
                "Vader",
                "*Force grip tightens*",
                emotion="rage",
                thought="This machine will tell me. NOW."
            ),
            create_dialogue(
                "Medical Droid",
                "*struggling* I... I don't have that information! Only the Emperor—",
                emotion="panicked"
            ),
            create_dialogue(
                "Palpatine",
                "Release him, Lord Vader.",
                emotion="cold command"
            )
        ],
        choices=[
            create_choice(
                "crush_droid",
                "[DARK SIDE] Crush the useless droid",
                ChoiceType.MORAL,
                darkness=10,
                control=-5,
                rage_change=5,
                next_scene="palpatine_arrives_rage",
                relationship_changes={"palpatine": -5},
                tooltip="Give in completely to rage - show Palpatine you're unstable",
                response=create_dialogue(
                    "Vader",
                    "*crushing sounds* Useless.",
                    emotion="cold fury"
                )
            ),
            create_choice(
                "release_droid",
                "[CONTROL] Release the droid, face Palpatine",
                ChoiceType.MORAL,
                control=5,
                rage_change=-5,
                next_scene="palpatine_arrives_controlled",
                tooltip="Regain control, show discipline to your master",
                response=create_dialogue(
                    "Vader",
                    "*releases droid* Yes... my Master.",
                    emotion="controlled"
                )
            )
        ]
    )
    
    # ================================================================
    # SCENE 3B: ASK CALMLY (Control path)
    # ================================================================
    
    scenes["ask_calmly"] = Scene(
        id="ask_calmly",
        title="Desperate Control",
        description="You fight to maintain composure as pain radiates through your body.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Medical Droid",
                "I... I am not authorized to discuss patient information, Lord Vader.",
                emotion="uncertain"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing intensifies*",
                emotion="barely controlled",
                thought="Stay calm. Control. But I NEED to know she's safe."
            ),
            create_dialogue(
                "Medical Droid",
                "The Emperor will be here momentarily. He can answer your questions.",
                emotion="nervous"
            ),
            create_dialogue(
                "Palpatine",
                "I am here, Lord Vader.",
                emotion="satisfied"
            )
        ],
        auto_next="palpatine_arrives_controlled"
    )
    
    # ================================================================
    # SCENE 3C: ASSESS SITUATION (Suppression path)
    # ================================================================
    
    scenes["assess_situation"] = Scene(
        id="assess_situation",
        title="Cold Assessment",
        description="You push aside emotion and examine your new form.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Medical Droid",
                "You suffered catastrophic injuries on Mustafar. We saved what we could. Your life support system is now—",
                emotion="clinical"
            ),
            create_dialogue(
                "Vader",
                "I am... trapped in this machine.",
                emotion="cold realization",
                thought="This suit. This mask. This is my prison now."
            ),
            create_dialogue(
                "Medical Droid",
                "The suit is necessary for your survival. Over time, you will adapt. The Emperor has spared no expense—",
                emotion="matter-of-fact"
            ),
            create_dialogue(
                "Vader",
                "Padmé. Where is she?",
                emotion="cold demand",
                thought="Focus. Mission first. She must be safe. Then I can deal with this... condition."
            ),
            create_dialogue(
                "Medical Droid",
                "I... I cannot—",
                emotion="nervous"
            ),
            create_dialogue(
                "Palpatine",
                "I will answer that question, Lord Vader.",
                emotion="ominous"
            )
        ],
        auto_next="palpatine_arrives_controlled"
    )
    
    # ================================================================
    # SCENE 4A: PALPATINE ARRIVES (After rage path)
    # ================================================================
    
    scenes["palpatine_arrives_rage"] = Scene(
        id="palpatine_arrives_rage",
        title="The Master's Displeasure",
        description="Emperor Palpatine enters, his presence filling the room with dark energy.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Palpatine",
                "Your lack of control disappoints me, Lord Vader.",
                emotion="cold disapproval"
            ),
            create_dialogue(
                "Vader",
                "Master... I must know. Where is Padmé?",
                emotion="desperate rage",
                thought="He knows. He always knows. Tell me she's safe."
            ),
            create_dialogue(
                "Palpatine",
                "Ah yes... your wife. It seems in your anger... you killed her.",
                emotion="false sympathy"
            )
        ],
        choices=[
            create_choice(
                "nooo_rage",
                "[RAGE] NOOOOOO!",
                ChoiceType.COMMITMENT,
                darkness=20,
                control=-10,
                rage_change=0,  # Already maxed
                next_scene="aftermath_rage",
                callback=on_nooo_rage,
                tooltip="The iconic moment - unleash Force devastation",
                response=create_dialogue(
                    "Vader",
                    "NOOOOOOOO!",
                    emotion="anguished fury"
                )
            ),
            create_choice(
                "silent_devastation",
                "[SUPPRESS] Fall silent, crush the grief",
                ChoiceType.COMMITMENT,
                suppression_change=20,
                control=10,
                darkness=15,
                next_scene="aftermath_silent",
                callback=on_silent_grief,
                tooltip="Bury Anakin forever - become the mask",
                response=create_dialogue(
                    "Vader",
                    "...",
                    emotion="dead inside",
                    thought="She's gone. I killed her. There is no Anakin anymore. Only Vader."
                )
            ),
            create_choice(
                "blame_palpatine",
                "[RESENTMENT] 'You told me I could save her!'",
                ChoiceType.COMMITMENT,
                darkness=10,
                control=5,
                suppression_change=10,
                next_scene="aftermath_resentment",
                relationship_changes={"palpatine": -15},
                callback=on_blame_palpatine,
                set_flags=["early_resentment"],
                tooltip="Plant seeds of betrayal - blame your master",
                response=create_dialogue(
                    "Vader",
                    "You told me the dark side could save her! You LIED!",
                    emotion="betrayed fury"
                )
            )
        ]
    )
    
    # ================================================================
    # SCENE 4B: PALPATINE ARRIVES (After control path)
    # ================================================================
    
    scenes["palpatine_arrives_controlled"] = Scene(
        id="palpatine_arrives_controlled",
        title="The Master Arrives",
        description="Emperor Palpatine enters, observing you with interest.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Palpatine",
                "Good, Lord Vader. You have regained control. That is wise.",
                emotion="approving"
            ),
            create_dialogue(
                "Vader",
                "Master. My wife... Padmé. Is she safe?",
                emotion="controlled urgency",
                thought="Please. Let her be alive."
            ),
            create_dialogue(
                "Palpatine",
                "*long pause* I am afraid... in your anger... you killed her.",
                emotion="false regret"
            )
        ],
        choices=[
            create_choice(
                "nooo_controlled",
                "[BREAK] NOOOOOO!",
                ChoiceType.COMMITMENT,
                darkness=15,
                control=-15,
                rage_change=20,
                next_scene="aftermath_rage",
                callback=on_nooo_rage,
                tooltip="Control shatters - the pain is too much",
                response=create_dialogue(
                    "Vader",
                    "NOOOOOOOO!",
                    emotion="breaking"
                )
            ),
            create_choice(
                "accept_fate",
                "[SUPPRESS] Accept it. Become Vader.",
                ChoiceType.COMMITMENT,
                suppression_change=25,
                control=15,
                darkness=18,
                next_scene="aftermath_silent",
                callback=on_silent_grief,
                tooltip="Perfect control - kill Anakin completely",
                response=create_dialogue(
                    "Vader",
                    "I... understand, Master.",
                    emotion="hollowed out",
                    thought="Anakin Skywalker is dead. I killed him along with her."
                )
            ),
            create_choice(
                "question_truth",
                "[DOUBT] 'How can you be certain?'",
                ChoiceType.TACTICAL,
                control=8,
                suppression_change=5,
                darkness=5,
                next_scene="palpatine_explains",
                set_flags=["questions_padme_death"],
                tooltip="Seeds of doubt - Palpatine might be lying",
                response=create_dialogue(
                    "Vader",
                    "You were not there. How can you be certain of this?",
                    emotion="suspicious grief"
                )
            )
        ]
    )
    
    # ================================================================
    # SCENE 5A: AFTERMATH - RAGE PATH
    # The Force devastation scene
    # ================================================================
    
    scenes["aftermath_rage"] = Scene(
        id="aftermath_rage",
        title="Unleashed",
        description="Your anguish unleashes a Force shockwave. Equipment explodes. Walls crack.",
        location="Surgical Suite",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The Dark Lord's pain erupts as raw Force energy. Medical equipment shatters. Droids are crushed. Even Palpatine staggers back.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing ragged*",
                emotion="exhausted rage",
                thought="She's dead. I killed her. Everything I did... for nothing."
            ),
            create_dialogue(
                "Palpatine",
                "Good. GOOD! Your rage makes you powerful. Channel it. Use it. This pain will fuel your strength.",
                emotion="satisfied"
            ),
            create_dialogue(
                "Vader",
                "*rises from table*",
                emotion="cold fury",
                thought="Yes. The pain. The rage. It's all I have now. I will use it."
            ),
            create_dialogue(
                "Palpatine",
                "Come, my apprentice. The Jedi will pay for what has been done to you.",
                emotion="commanding"
            )
        ],
        auto_next="first_lesson"
    )
    
    # ================================================================
    # SCENE 5B: AFTERMATH - SILENT PATH
    # Vader becomes the mask
    # ================================================================
    
    scenes["aftermath_silent"] = Scene(
        id="aftermath_silent",
        title="The Death of Anakin Skywalker",
        description="You stand. The pain is still there. But you will not show it. Never again.",
        location="Surgical Suite",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Lord Vader rises from the operating table. His movements are mechanical. Precise. No emotion shows through the mask.",
                emotion="somber"
            ),
            create_dialogue(
                "Vader",
                "...",
                emotion="empty",
                thought="Anakin would have screamed. Would have wept. But Anakin is dead."
            ),
            create_dialogue(
                "Palpatine",
                "Excellent, Lord Vader. You have accepted your fate. You are stronger for it. That weakness - that love - it nearly destroyed you.",
                emotion="pleased"
            ),
            create_dialogue(
                "Vader",
                "What is thy bidding, my Master?",
                emotion="cold obedience",
                thought="I am nothing but a tool now. His tool. And I will be the perfect weapon."
            ),
            create_dialogue(
                "Palpatine",
                "Come. There is much you must learn about the ways of the Sith.",
                emotion="commanding"
            )
        ],
        auto_next="first_lesson"
    )
    
    # ================================================================
    # SCENE 5C: AFTERMATH - RESENTMENT PATH
    # Early betrayal path
    # ================================================================
    
    scenes["aftermath_resentment"] = Scene(
        id="aftermath_resentment",
        title="Seeds of Betrayal",
        description="You have accused the Emperor. This will not be forgotten.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Palpatine",
                "*Force Lightning crackles* You DARE accuse me? I saved your life! I gave you power!",
                emotion="furious"
            ),
            create_dialogue(
                "Vader",
                "*writhes in pain*",
                emotion="agony",
                thought="He's going to kill me. But... I don't care anymore."
            ),
            create_dialogue(
                "Palpatine",
                "*stops* No. You are too valuable. But remember this pain, Lord Vader. Remember who holds your leash.",
                emotion="cold warning"
            ),
            create_dialogue(
                "Vader",
                "*gasping*",
                emotion="humiliated rage",
                thought="One day. One day I will be free of him. One day..."
            ),
            create_dialogue(
                "Palpatine",
                "Now... rise. You have much to learn if you are to serve me.",
                emotion="dismissive"
            )
        ],
        auto_next="first_lesson"
    )
    
    # ================================================================
    # SCENE 5D: PALPATINE EXPLAINS (Doubt path)
    # ================================================================
    
    scenes["palpatine_explains"] = Scene(
        id="palpatine_explains",
        title="The Emperor's Truth",
        description="Palpatine explains what happened on Mustafar.",
        location="Surgical Suite",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Palpatine",
                "I recovered you from Mustafar. Your body was burning. You were calling her name.",
                emotion="matter-of-fact"
            ),
            create_dialogue(
                "Palpatine",
                "By the time I brought you here... she had died. The medical facility on Polis Massa could not save her.",
                emotion="false sympathy"
            ),
            create_dialogue(
                "Vader",
                "...",
                emotion="processing",
                thought="Polis Massa. The Jedi could have saved her. But they didn't. They let her die."
            ),
            create_dialogue(
                "Palpatine",
                "The Jedi abandoned her, Lord Vader. As they abandoned you. They took everything from you.",
                emotion="poisonous suggestion"
            )
        ],
        choices=[
            create_choice(
                "believe_palpatine",
                "The Jedi killed her.",
                ChoiceType.COMMITMENT,
                darkness=20,
                suppression_change=20,
                next_scene="aftermath_silent",
                set_flags=["blames_jedi"],
                tooltip="Accept Palpatine's version - fuel your hatred",
                response=create_dialogue(
                    "Vader",
                    "The Jedi will pay. All of them.",
                    emotion="cold fury"
                )
            ),
            create_choice(
                "doubt_remains",
                "Say nothing. Remember this conversation.",
                ChoiceType.TACTICAL,
                control=10,
                suppression_change=15,
                darkness=10,
                next_scene="aftermath_silent",
                set_flags=["suspects_truth", "remembers_polis_massa"],
                tooltip="File it away - someday you'll learn the truth",
                response=create_dialogue(
                    "Vader",
                    "I understand, Master.",
                    emotion="controlled",
                    thought="Something isn't right. But for now... I will serve."
                )
            )
        ]
    )
    
    # ================================================================
    # SCENE 6: FIRST LESSON - TRANSITION TO KYBER MISSION
    # Instead of specific mission briefing, Palpatine hints at training
    # ================================================================
    
    scenes["first_lesson"] = Scene(
        id="first_lesson",
        title="The First Lesson",
        description="Palpatine leads you from the medical facility. Your training begins.",
        location="Imperial Palace, Coruscant",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The Emperor leads you through the corridors of the Imperial Palace. Your mechanical steps echo in the silence.",
                emotion="ominous"
            ),
            create_dialogue(
                "Palpatine",
                "You have taken your first steps into a larger world, Lord Vader. But you are not yet complete.",
                emotion="teaching"
            ),
            create_dialogue(
                "Vader",
                "Master?",
                emotion="questioning",
                thought="What more does he want from me? I have given him everything."
            ),
            create_dialogue(
                "Palpatine",
                "A Sith is not truly a Sith until they have claimed their weapon. You carry a Jedi's lightsaber still.",
                emotion="pointed"
            ),
            create_dialogue(
                "Vader",
                "*looks at the green blade at his belt*",
                emotion="understanding",
                thought="A Jedi's weapon. I took it from the temple. But it's not... mine."
            ),
            create_dialogue(
                "Palpatine",
                "Come. There is something you must see. A lesson about what it means to be Sith.",
                emotion="commanding"
            )
        ],
        choices=[
            create_choice(
                "follow_palpatine",
                "Follow the Emperor",
                ChoiceType.DIALOGUE,
                next_scene="tutorial_complete",
                set_flags=["first_lesson_begun"],
                response=create_dialogue(
                    "Vader",
                    "Lead on, my Master.",
                    emotion="obedient"
                )
            )
        ]
    )
    
    # ================================================================
    # SCENE 7: TUTORIAL COMPLETE
    # Transition to gameplay - now properly sets up Kyber mission
    # ================================================================
    
    scenes["tutorial_complete"] = Scene(
        id="tutorial_complete",
        title="The Path Forward",
        description="Your journey as Darth Vader begins. But first, you must learn what it means to be Sith.",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The opening is complete. You are Darth Vader now - Dark Lord of the Sith.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Narrator",
                "But your transformation is not finished. The Emperor has lessons to teach you.",
                emotion="ominous"
            ),
            create_dialogue(
                "Narrator",
                "About power. About sacrifice. About what it truly means to serve the dark side.",
                emotion="foreboding"
            )
        ],
        auto_next="kyber_balcony"  # End of opening, transition to Kyber mission
    )
    
    return scenes


# Test function
if __name__ == "__main__":
    scenes = create_opening_scenes()
    print(f"✓ Created {len(scenes)} opening scenes:")
    for scene_id, scene in scenes.items():
        print(f"  - {scene_id}: {scene.title}")