"""
Mission 1: The Bleeding of the Kyber Crystal
Vader's first mission - obtaining his red lightsaber by hunting Jedi Master Kirak Infil'a.
Based on the canonical story from Darth Vader (2017) comic series.
"""

from typing import Dict
from .story_system import (
    Scene, DialogueLine, Choice, ChoiceType,
    create_dialogue, create_choice
)


# ============================================================
# CALLBACKS FOR MISSION EVENTS
# ============================================================

def on_mission_start(vader, suit, state):
    """Called when mission begins"""
    state.set_flag("kyber_mission_started")
    state.current_mission = "bleeding_kyber"
    print("\n" + "═" * 60)
    print("MISSION: THE BLEEDING OF THE KYBER CRYSTAL")
    print("Objective: Hunt a Jedi and claim their lightsaber")
    print("═" * 60)


def on_witness_burning(vader, suit, state):
    """Witnessing the lightsaber burning ceremony"""
    vader.modify_suppression(5)
    state.set_flag("witnessed_lightsaber_burning")


def on_yoda_saber_destroyed(vader, suit, state):
    """Seeing Yoda's lightsaber destroyed"""
    vader.modify_darkness(5)
    vader.psychological_state.rage += 10


def on_pirates_eliminated(vader, suit, state):
    """After killing the pirates"""
    state.set_flag("pirates_eliminated")
    vader.modify_darkness(3)


def on_brighthome_massacre(vader, suit, state):
    """If Vader kills the clone troopers"""
    state.set_flag("brighthome_massacre")
    vader.modify_darkness(10)
    vader.modify_control(-5)
    state.imperials_killed += 4


def on_brighthome_peaceful(vader, suit, state):
    """If Vader uses security codes"""
    state.set_flag("brighthome_peaceful")
    vader.modify_control(5)


def on_find_infila(vader, suit, state):
    """When Infil'a is located"""
    state.set_flag("infila_located")
    state.named_characters_met.append("Kirak Infil'a")


def on_first_duel_loss(vader, suit, state):
    """After losing the first duel"""
    state.set_flag("first_duel_lost")
    vader.psychological_state.rage += 20
    vader.modify_darkness(5)
    
    # Suit damage from fall
    suit.take_suit_damage(15)


def on_self_repair(vader, suit, state):
    """After Vader repairs himself"""
    state.set_flag("self_repaired_suit")
    vader.modify_control(10)
    vader.modify_suppression(5)
    
    # Partial repair
    suit.repair_suit(10)


def on_water_tank_destroyed(vader, suit, state):
    """If Vader destroys the water tank (kills civilians)"""
    state.set_flag("ambalaar_massacre")
    state.civilians_killed += 1000  # Approximation
    vader.modify_darkness(20)
    vader.modify_control(-10)


def on_fought_honorably(vader, suit, state):
    """If Vader fights without destroying the tank"""
    state.set_flag("ambalaar_spared")
    state.civilians_spared += 1000
    vader.modify_darkness(5)
    vader.modify_control(10)


def on_infila_killed(vader, suit, state):
    """After killing Infil'a"""
    state.set_flag("infila_dead")
    state.jedi_killed += 1
    state.named_characters_killed.append("Kirak Infil'a")
    vader.modify_darkness(10)
    
    # Get kyber crystal
    suit.materials["kyber_fragments"] += 1


def on_vision_love(vader, suit, state):
    """If Vader sees the Padmé vision"""
    state.set_flag("mustafar_vision_love")
    vader.modify_suppression(20)
    vader.modify_darkness(15)


def on_vision_brotherhood(vader, suit, state):
    """If Vader sees the Obi-Wan vision"""
    state.set_flag("mustafar_vision_brotherhood")
    vader.modify_suppression(10)
    vader.modify_darkness(15)
    vader.psychological_state.rage += 5


def on_crystal_bled(vader, suit, state):
    """After successfully bleeding the kyber crystal"""
    state.set_flag("crystal_bled")
    state.set_flag("red_lightsaber_obtained")
    vader.modify_darkness(25)
    vader.modify_suppression(30)
    
    # Mark mission complete
    state.missions_completed.append("bleeding_kyber")
    state.current_mission = None


def on_mission_complete(vader, suit, state):
    """After showing the red lightsaber to Palpatine"""
    state.set_flag("kyber_mission_complete")
    vader.relationships["palpatine"] += 10


# ============================================================
# ACT 1: THE LESSON
# ============================================================

def create_act1_scenes() -> Dict[str, Scene]:
    """Act 1: The Balcony - Palpatine teaches about bleeding kyber crystals"""
    scenes = {}
    
    scenes["kyber_balcony"] = Scene(
        id="kyber_balcony",
        title="The Temple Balcony",
        description="You stand on a balcony overlooking the Jedi Temple. Below, a ceremony is underway.",
        location="Imperial Palace, Coruscant - Overlooking the Jedi Temple",
        scene_type="dialogue",
        on_enter=on_mission_start,
        dialogue=[
            create_dialogue(
                "Narrator",
                "Immediately after your surgery, the Emperor brings you here. To watch.",
                emotion="ominous"
            ),
            create_dialogue(
                "Palpatine",
                "Come, Lord Vader. There is something you must see.",
                emotion="satisfied"
            ),
            create_dialogue(
                "Narrator",
                "Below, clone troopers gather in formation. Mas Amedda stands before a great furnace.",
                emotion="somber"
            ),
            create_dialogue(
                "Mas Amedda",
                "Citizens of the Empire! Today we burn away the weapons of traitors! The Jedi are no more!",
                emotion="ceremonial",
                thought="They're burning the lightsabers. All of them."
            ),
            create_dialogue(
                "Palpatine",
                "Tell me, my apprentice... do you know why a Sith's lightsaber blade is red?",
                emotion="teaching"
            ),
            create_dialogue(
                "Vader",
                "The Temple's information on the subject was... incomplete.",
                emotion="measured",
                thought="I studied the archives. But they hid the truth about the Sith."
            ),
            create_dialogue(
                "Palpatine",
                "*laughs* The Jedi were uncomfortable with such knowledge. They buried it. As they buried so much else.",
                emotion="contemptuous"
            ),
            create_dialogue(
                "Palpatine",
                "Kyber crystals are alive, Lord Vader. They feel pain. They can be made to... bleed.",
                emotion="dark satisfaction"
            ),
            create_dialogue(
                "Palpatine",
                "You pour your rage into them. Your pain. Your hatred. Until they crack. Until they scream. Until they turn red.",
                emotion="teaching darkness"
            )
        ],
        choices=[
            create_choice(
                "understand_lesson",
                "I understand, Master.",
                ChoiceType.DIALOGUE,
                next_scene="kyber_yoda_saber",
                response=create_dialogue(
                    "Vader",
                    "I understand, Master.",
                    emotion="cold obedience"
                )
            ),
            create_choice(
                "question_method",
                "Could you not give me one of these burning sabers to corrupt?",
                ChoiceType.DIALOGUE,
                next_scene="kyber_yoda_saber",
                response=create_dialogue(
                    "Vader",
                    "You could give me any of these lightsabers to corrupt. Even Yoda's.",
                    emotion="calculating",
                    thought="But he won't. There's a lesson here."
                )
            )
        ]
    )
    
    scenes["kyber_yoda_saber"] = Scene(
        id="kyber_yoda_saber",
        title="The Burning",
        description="The clone troopers pour baskets of lightsabers into the flames.",
        location="Temple Balcony",
        scene_type="cutscene",
        on_enter=on_witness_burning,
        dialogue=[
            create_dialogue(
                "Palpatine",
                "But I will not. A Sith's kyber crystal must be won. Taken from a Jedi... by force.",
                emotion="commanding"
            ),
            create_dialogue(
                "Narrator",
                "Below, a clone trooper lifts a small, ancient lightsaber. Its hilt is worn from centuries of use.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Mas Amedda",
                "The weapon of the traitor Yoda!",
                emotion="triumphant"
            ),
            create_dialogue(
                "Narrator",
                "The lightsaber tumbles into the flames. For a moment, nothing happens. Then—",
                emotion="tense"
            ),
            create_dialogue(
                "Narrator",
                "BOOM! A massive explosion of Force energy erupts from the furnace. The kyber crystals scream as they die.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing intensifies*",
                emotion="affected",
                thought="I trained with Yoda. He was a fool. But he was... powerful."
            ),
            create_dialogue(
                "Palpatine",
                "Come. I have arranged your first mission, Lord Vader. We travel to Gattering.",
                emotion="satisfied"
            )
        ],
        choices=[
            create_choice(
                "accept_mission",
                "As you wish, Master.",
                ChoiceType.DIALOGUE,
                callback=on_yoda_saber_destroyed,
                next_scene="kyber_gattering_arrival",
                response=create_dialogue(
                    "Vader",
                    "As you wish.",
                    emotion="obedient"
                )
            )
        ]
    )
    
    return scenes


# ============================================================
# ACT 2: GATTERING - THE PIRATES
# ============================================================

def create_act2_scenes() -> Dict[str, Scene]:
    """Act 2: Gattering - Vader must reclaim his stolen ship from pirates"""
    scenes = {}
    
    scenes["kyber_gattering_arrival"] = Scene(
        id="kyber_gattering_arrival",
        title="Gattering",
        description="A barren world in the Mid Rim. Your ship should be waiting.",
        location="Gattering, Mid Rim",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your black Eta-2 Actis-class interceptor awaits at the coordinates. Once yellow—Anakin Skywalker's personal fighter. Now dark as the Empire itself.",
                emotion="descriptive"
            ),
            create_dialogue(
                "Palpatine",
                "I have arranged for a vessel to be delivered here. It will serve your purposes.",
                emotion="matter-of-fact"
            ),
            create_dialogue(
                "Narrator",
                "But when you arrive at the landing site, the ship is gone. Scorch marks. Boot prints. Signs of a struggle.",
                emotion="tense"
            ),
            create_dialogue(
                "Vader",
                "The ship has been stolen.",
                emotion="cold anger",
                thought="Pirates. Or scavengers. They will regret this."
            ),
            create_dialogue(
                "Palpatine",
                "Then you will reclaim it. Alone. The nearest settlement is 5 kilometers north.",
                emotion="dismissive"
            ),
            create_dialogue(
                "Palpatine",
                "Do not disappoint me, Lord Vader.",
                emotion="warning"
            ),
            create_dialogue(
                "Narrator",
                "The Emperor's shuttle departs, leaving you alone on the barren plain.",
                emotion="ominous"
            )
        ],
        choices=[
            create_choice(
                "head_to_settlement",
                "Walk to the settlement.",
                ChoiceType.TACTICAL,
                next_scene="kyber_pirate_settlement",
                response=create_dialogue(
                    "Vader",
                    "*begins walking*",
                    emotion="determined",
                    thought="5 kilometers. In this suit. This is a test."
                )
            )
        ]
    )
    
    scenes["kyber_pirate_settlement"] = Scene(
        id="kyber_pirate_settlement",
        title="The Pirate Den",
        description="A ramshackle settlement. Your ship sits in the center, surrounded by armed thugs.",
        location="Pirate Settlement, Gattering",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "You arrive at the settlement. Your black interceptor is surrounded by a dozen armed pirates, celebrating their prize.",
                emotion="tense"
            ),
            create_dialogue(
                "Pirate Leader",
                "What have we here? Imperial scum? Come to beg for your ship back?",
                emotion="mocking"
            ),
            create_dialogue(
                "Vader",
                "*ignites lightsaber - green blade from Brighthome*",
                emotion="cold menace",
                thought="They don't know what I am. They will learn."
            ),
            create_dialogue(
                "Pirate Leader",
                "A Jedi? HA! Boys, kill this fool!",
                emotion="aggressive"
            ),
            create_dialogue(
                "Narrator",
                "[COMBAT: Eliminate the pirates - Tutorial fight]",
                emotion="action"
            )
        ],
        trigger_combat={
            "enemy_types": ["pirate_thug", "pirate_thug", "pirate_thug", "pirate_leader"],
            "difficulty": "easy",
            "tutorial": True
        },
        auto_next="kyber_pirates_defeated"
    )
    
    scenes["kyber_pirates_defeated"] = Scene(
        id="kyber_pirates_defeated",
        title="Reclaimed",
        description="The pirates lie dead. Your ship is yours once more.",
        location="Pirate Settlement, Gattering",
        scene_type="cutscene",
        on_enter=on_pirates_eliminated,
        dialogue=[
            create_dialogue(
                "Narrator",
                "The pirates fall before you like wheat before a scythe. Your lightsaber skills remain, even in this mechanical body.",
                emotion="satisfied"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing*",
                emotion="calm",
                thought="The suit is clumsy. But the Force is still mine."
            ),
            create_dialogue(
                "Narrator",
                "You board your interceptor. The droid co-pilot activates, its systems coming online.",
                emotion="technical"
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Lord Vader. Master's instructions loaded. Plotting course to... Brighthome Station.",
                emotion="mechanical"
            ),
            create_dialogue(
                "Vader",
                "Brighthome?",
                emotion="questioning",
                thought="A Jedi outpost. The Emperor wants me to find someone there."
            )
        ],
        choices=[
            create_choice(
                "depart_for_brighthome",
                "Set course for Brighthome.",
                ChoiceType.DIALOGUE,
                next_scene="kyber_brighthome_approach",
                response=create_dialogue(
                    "Vader",
                    "Proceed.",
                    emotion="commanding"
                )
            )
        ]
    )
    
    return scenes


# ============================================================
# ACT 3: BRIGHTHOME - THE CHOICE & THE RESEARCH
# ============================================================

def create_act3_scenes() -> Dict[str, Scene]:
    """Act 3: Brighthome Jedi Outpost - Clone trooper garrison and research"""
    scenes = {}
    
    scenes["kyber_brighthome_approach"] = Scene(
        id="kyber_brighthome_approach",
        title="Brighthome Station",
        description="A small Jedi outpost, now garrisoned by clone troopers. They hail your approach.",
        location="Brighthome Station, Outer Rim",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your interceptor approaches the station. Clone trooper markings cover its hull. They survived Order 66, now serving as guards.",
                emotion="tense"
            ),
            create_dialogue(
                "Clone Trooper (Comms)",
                "Unidentified craft, transmit security codes immediately or be fired upon.",
                emotion="professional"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing*",
                emotion="considering",
                thought="I have the codes. I could enter peacefully. Or..."
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Lord Vader, I can transmit authorization codes. The clones will grant us entry.",
                emotion="helpful"
            ),
            create_dialogue(
                "Narrator",
                "You sense four clone troopers inside. Armed. Alert. They don't know what you are.",
                emotion="tense"
            )
        ],
        choices=[
            create_choice(
                "use_codes",
                "[CONTROL] Transmit security codes",
                ChoiceType.TACTICAL,
                control=5,
                next_scene="kyber_brighthome_peaceful",
                callback=on_brighthome_peaceful,
                response=create_dialogue(
                    "Vader",
                    "Transmit the codes.",
                    emotion="controlled",
                    thought="Efficiency. No need for unnecessary violence."
                )
            ),
            create_choice(
                "kill_clones",
                "[DARK SIDE] Dock and eliminate them",
                ChoiceType.MORAL,
                darkness=10,
                control=-5,
                next_scene="kyber_brighthome_massacre",
                callback=on_brighthome_massacre,
                response=create_dialogue(
                    "Vader",
                    "No.",
                    emotion="cold",
                    thought="I need no one's permission. They are in my way."
                )
            )
        ]
    )
    
    scenes["kyber_brighthome_peaceful"] = Scene(
        id="kyber_brighthome_peaceful",
        title="Authorized Entry",
        description="The clones stand aside as you enter the station.",
        location="Brighthome Station - Interior",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Clone Trooper Leader",
                "Codes accepted. Welcome to Brighthome, sir. How can we assist the Empire?",
                emotion="professional"
            ),
            create_dialogue(
                "Vader",
                "I require access to your archives. Leave me.",
                emotion="commanding"
            ),
            create_dialogue(
                "Clone Trooper Leader",
                "Sir, yes sir!",
                emotion="obedient"
            ),
            create_dialogue(
                "Narrator",
                "The clones depart to their posts. You are alone with the archives.",
                emotion="calm"
            )
        ],
        auto_next="kyber_archive_search"
    )
    
    scenes["kyber_brighthome_massacre"] = Scene(
        id="kyber_brighthome_massacre",
        title="No Witnesses",
        description="You dock forcefully and storm the station.",
        location="Brighthome Station - Interior",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your ship docks with a violent clang. The airlock hisses open. The clones raise their weapons.",
                emotion="tense"
            ),
            create_dialogue(
                "Clone Trooper 'Ding'",
                "Unauthorized breach! Open fire!",
                emotion="alarmed"
            ),
            create_dialogue(
                "Narrator",
                "With a gesture, you summon a lightsaber from the wall—a fallen Jedi's weapon. Green blade ignites.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Vader",
                "*uses the Jedi's own weapon to kill the clones*",
                emotion="efficient brutality",
                thought="Their weapons are useless. I am beyond them now."
            ),
            create_dialogue(
                "Clone Trooper 'Kicker'",
                "*throws thermal detonator* Die, Jedi scum!",
                emotion="desperate"
            ),
            create_dialogue(
                "Narrator",
                "You freeze the explosion in mid-air with the Force. The clones believe you're helpless, concentrating on containment.",
                emotion="tense"
            ),
            create_dialogue(
                "Clone Trooper 'Ding'",
                "Now! While he's distracted! Restrain him!",
                emotion="hopeful"
            ),
            create_dialogue(
                "Vader",
                "*Force chokes both clones simultaneously while maintaining the frozen explosion*",
                emotion="effortless menace",
                thought="Fools. I am Darth Vader."
            ),
            create_dialogue(
                "Narrator",
                "*SNAP* Their necks break. You release the explosion safely and walk deeper into the station. Two more clones fall to your blade.",
                emotion="dark"
            )
        ],
        auto_next="kyber_archive_search"
    )
    
    scenes["kyber_archive_search"] = Scene(
        id="kyber_archive_search",
        title="The Archives",
        description="You search the Jedi archives for a target.",
        location="Brighthome Archives",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Vader",
                "Droid. Access the archives. Search for Jedi who took the Barash Vow before Order 66.",
                emotion="commanding",
                thought="Jedi who swore off all Jedi affairs. They would have ignored Order 66. Survived by isolation."
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Searching... searching... match found. Jedi Master Kirak Infil'a.",
                emotion="mechanical"
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Last known location: Al'doleem. The river moon. Master Infil'a was a combat specialist. Dedicated to perfecting lightsaber technique.",
                emotion="informative"
            ),
            create_dialogue(
                "Vader",
                "A warrior. Good.",
                emotion="satisfied",
                thought="His kyber crystal will be powerful. Worthy of a Sith."
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Plotting course to Al'doleem, Lord Vader.",
                emotion="mechanical"
            )
        ],
        choices=[
            create_choice(
                "depart_for_aldoleem",
                "Go. The hunt begins.",
                ChoiceType.DIALOGUE,
                callback=on_find_infila,
                next_scene="kyber_aldoleem_arrival",
                response=create_dialogue(
                    "Vader",
                    "Set course.",
                    emotion="cold determination"
                )
            )
        ]
    )
    
    return scenes


# ============================================================
# ACT 4: AL'DOLEEM - THE FIRST DUEL (DEFEAT)
# ============================================================

def create_act4_scenes() -> Dict[str, Scene]:
    """Act 4: Al'doleem - First encounter with Infil'a, ending in Vader's defeat"""
    scenes = {}
    
    scenes["kyber_aldoleem_arrival"] = Scene(
        id="kyber_aldoleem_arrival",
        title="Al'doleem - The River Moon",
        description="A verdant moon, covered in rivers and waterfalls. You sense him immediately.",
        location="Al'doleem, Outer Rim",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your ship descends through misty clouds. Below, a massive mountain rises from a river valley. At its peak—a temple.",
                emotion="atmospheric"
            ),
            create_dialogue(
                "Vader",
                "*disembarks*",
                emotion="focused",
                thought="He knows I'm here. He's waiting for me."
            ),
            create_dialogue(
                "Kirak Infil'a",
                "*appears from the mist, igniting blue lightsaber* So. The Empire sends a servant.",
                emotion="calm warrior"
            ),
            create_dialogue(
                "Vader",
                "*Force choke*",
                emotion="immediate aggression",
                thought="No words. Only action."
            ),
            create_dialogue(
                "Infil'a",
                "*Force blast—breaks the choke* You are powerful. But untested in that suit.",
                emotion="analytical"
            ),
            create_dialogue(
                "Infil'a",
                "My Barash Vow is complete. If you want my lightsaber... climb.",
                emotion="challenging"
            ),
            create_dialogue(
                "Narrator",
                "The Jedi Master leaps up the mountain path. Behind him, a training droid—Arex—opens a sluice gate.",
                emotion="tense"
            ),
            create_dialogue(
                "Narrator",
                "A RIVER crashes down upon you with tremendous force.",
                emotion="dramatic"
            )
        ],
        auto_next="kyber_river_challenge"
    )
    
    scenes["kyber_river_challenge"] = Scene(
        id="kyber_river_challenge",
        title="The River",
        description="Water crushes you, threatening to sweep you away.",
        location="Al'doleem Mountain Path",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The torrent slams into your armor with the force of a speeder. Your suit groans under the pressure.",
                emotion="intense"
            ),
            create_dialogue(
                "Vader",
                "*extends hand*",
                emotion="straining",
                thought="The Force. Part the water. Like the ancient Sith."
            ),
            create_dialogue(
                "Narrator",
                "The river SPLITS before you. Water flows around an invisible barrier. You walk through the riverbed.",
                emotion="powerful"
            ),
            create_dialogue(
                "Narrator",
                "But as you reach the shore, massive shapes descend from the sky—carnivorous birds, drawn by the commotion.",
                emotion="tense"
            ),
            create_dialogue(
                "Vader",
                "*one lands on your back, its talons piercing hydraulics*",
                emotion="pained",
                thought="My leg... damage to the servos..."
            ),
            create_dialogue(
                "Narrator",
                "You crush them one by one with the Force. But the damage is done. Your left leg stutters with each step.",
                emotion="ominous"
            )
        ],
        auto_next="kyber_first_duel"
    )
    
    scenes["kyber_first_duel"] = Scene(
        id="kyber_first_duel",
        title="The Peak",
        description="You reach the mountain peak. Infil'a awaits with his training droid.",
        location="Al'doleem Mountain Peak",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Infil'a",
                "You survived. Impressive. But you are damaged, servant of darkness.",
                emotion="cautious"
            ),
            create_dialogue(
                "Arex",
                "*training droid ignites practice blade* Master, shall I—",
                emotion="mechanical"
            ),
            create_dialogue(
                "Vader",
                "*Force pushes Infil'a, crushes Arex, takes its training saber*",
                emotion="ruthless efficiency",
                thought="Unarmed no longer. Now we fight."
            ),
            create_dialogue(
                "Narrator",
                "*throws the droid's broken body off the mountain*",
                emotion="brutal"
            ),
            create_dialogue(
                "Infil'a",
                "You want my lightsaber. You will not have it!",
                emotion="determined"
            ),
            create_dialogue(
                "Narrator",
                "[COMBAT: First Duel with Kirak Infil'a]",
                emotion="epic"
            )
        ],
        trigger_combat={
            "enemy_type": "infila_first_duel",
            "scripted_loss": True,
            "loss_trigger": "leg_breaks"
        },
        auto_next="kyber_first_defeat"
    )
    
    scenes["kyber_first_defeat"] = Scene(
        id="kyber_first_defeat",
        title="Defeat",
        description="Your leg gives out. You fall.",
        location="Al'doleem Mountain Peak",
        scene_type="cutscene",
        on_enter=on_first_duel_loss,
        dialogue=[
            create_dialogue(
                "Narrator",
                "*CRACK* Your damaged leg breaks apart at the knee. You collapse.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Vader",
                "*struggles to rise*",
                emotion="furious",
                thought="NO! I cannot lose! Not again!"
            ),
            create_dialogue(
                "Infil'a",
                "The Emperor made you weak with that suit. You are more machine than man now.",
                emotion="pitying"
            ),
            create_dialogue(
                "Infil'a",
                "I will find your master. I will end this tyranny before it begins.",
                emotion="resolved"
            ),
            create_dialogue(
                "Narrator",
                "Infil'a raises his hand. A massive Force push sends you flying off the mountain.",
                emotion="devastating"
            ),
            create_dialogue(
                "Vader",
                "*falling*",
                emotion="rage and pain",
                thought="I... will... KILL... HIM..."
            ),
            create_dialogue(
                "Narrator",
                "You crash into the valley below. Everything goes dark.",
                emotion="ominous"
            )
        ],
        auto_next="kyber_rebuild_awakening"
    )
    
    return scenes


# ============================================================
# ACT 5: THE REBUILD
# ============================================================

def create_act5_scenes() -> Dict[str, Scene]:
    """Act 5: Vader repairs himself using the broken training droid"""
    scenes = {}
    
    scenes["kyber_rebuild_awakening"] = Scene(
        id="kyber_rebuild_awakening",
        title="The Valley",
        description="You awaken in the valley. Broken. But not defeated.",
        location="Al'doleem Valley Floor",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Pain. That's what brings you back to consciousness. Your suit's emergency systems beeping critical warnings.",
                emotion="harsh"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing labored*",
                emotion="struggling",
                thought="My leg... destroyed. I cannot walk. Cannot pursue him."
            ),
            create_dialogue(
                "Narrator",
                "Next to you, partially buried in mud—the broken remains of Arex, the training droid. Its leg servos intact.",
                emotion="descriptive"
            ),
            create_dialogue(
                "Vader",
                "*reaches out with the Force*",
                emotion="determined",
                thought="I need no one. I will repair myself."
            )
        ],
        choices=[
            create_choice(
                "rebuild_self",
                "Cannibalize the droid. Repair your leg.",
                ChoiceType.TACTICAL,
                control=10,
                callback=on_self_repair,
                next_scene="kyber_rebuild_complete",
                response=create_dialogue(
                    "Vader",
                    "*begins dismantling Arex with the Force*",
                    emotion="cold focus",
                    thought="Piece by piece. Servo by servo. I will make myself whole."
                )
            )
        ]
    )
    
    scenes["kyber_rebuild_complete"] = Scene(
        id="kyber_rebuild_complete",
        title="Rebuilt",
        description="Your leg functions again. You stand.",
        location="Al'doleem Valley",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Hours pass. Your hands work with mechanical precision, guided by the Force. Arex's parts fuse with your own.",
                emotion="methodical"
            ),
            create_dialogue(
                "Vader",
                "*stands, tests the new leg*",
                emotion="satisfied",
                thought="Crude. But functional. I am stronger than this body."
            ),
            create_dialogue(
                "Vader",
                "Droid. Track Infil'a's ship.",
                emotion="commanding"
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Scanning... Jedi vessel detected. Course set for... Am'balaar City, Al'doleem.",
                emotion="mechanical"
            ),
            create_dialogue(
                "Vader",
                "He seeks allies. He will find only death.",
                emotion="cold promise",
                thought="He defeated me once. It will not happen again."
            )
        ],
        auto_next="kyber_ambalaar_pursuit"
    )
    
    return scenes


# ============================================================
# ACT 6: AM'BALAAR CITY - THE WATER TANK CHOICE
# ============================================================

def create_act6_scenes() -> Dict[str, Scene]:
    """Act 6: The final duel with Infil'a and the moral choice"""
    scenes = {}
    
    scenes["kyber_ambalaar_pursuit"] = Scene(
        id="kyber_ambalaar_pursuit",
        title="Am'balaar City",
        description="A sprawling city built around a massive dam. You sense him here.",
        location="Am'balaar City, Al'doleem",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your interceptor descends into the city. Thousands of civilians go about their lives, unaware of the predator in their midst.",
                emotion="ominous"
            ),
            create_dialogue(
                "Vader",
                "*senses through the Force*",
                emotion="focused",
                thought="There. On the dam. He knows I've come for him."
            ),
            create_dialogue(
                "Narrator",
                "You land near the city's central dam—a massive structure holding back millions of gallons of water.",
                emotion="tense"
            ),
            create_dialogue(
                "Infil'a",
                "*waiting atop the dam* You... survived. I should have made certain.",
                emotion="surprised"
            ),
            create_dialogue(
                "Vader",
                "Your mistake.",
                emotion="cold menace"
            ),
            create_dialogue(
                "Infil'a",
                "*ignites lightsaber* Then let us finish this. And this time, no one else will be involved!",
                emotion="determined"
            )
        ],
        auto_next="kyber_final_duel_start"
    )
    
    scenes["kyber_final_duel_start"] = Scene(
        id="kyber_final_duel_start",
        title="The Dam",
        description="You face Infil'a atop the dam. Water rushes below.",
        location="Am'balaar Dam",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Blades clash. Blue against green. Infil'a fights with perfect Form III technique—defensive, patient, seeking your openings.",
                emotion="intense"
            ),
            create_dialogue(
                "Vader",
                "*presses the attack*",
                emotion="aggressive",
                thought="He's skilled. But I've fought Dooku. I've dueled Obi-Wan. He is nothing."
            ),
            create_dialogue(
                "Narrator",
                "[COMBAT: Second Duel with Kirak Infil'a - Phase 1]",
                emotion="epic"
            )
        ],
        trigger_combat={
            "enemy_type": "infila_final_duel",
            "phase": 1,
            "hp_threshold_for_choice": 60
        },
        auto_next="kyber_water_tank_choice"
    )
    
    scenes["kyber_water_tank_choice"] = Scene(
        id="kyber_water_tank_choice",
        title="The Choice",
        description="The duel is even. Below, a massive water storage tank looms over the city.",
        location="Am'balaar Dam",
        scene_type="decision",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The fight continues. He parries every strike. You cannot break his defense.",
                emotion="frustrated"
            ),
            create_dialogue(
                "Vader",
                "*senses the massive water tank below with the Force*",
                emotion="calculating",
                thought="Thousands of civilians below. The tank is the size of a building. If it breaks..."
            ),
            create_dialogue(
                "Infil'a",
                "You fight well for a machine. But you lack the discipline of a true warrior!",
                emotion="taunting"
            ),
            create_dialogue(
                "Narrator",
                "Below, the tank is a tempting target. If you destroy it, Infil'a will be distracted trying to save the civilians. You would have your opening.",
                emotion="tempting"
            ),
            create_dialogue(
                "Narrator",
                "But thousands will die. The city will flood.",
                emotion="warning"
            )
        ],
        choices=[
            create_choice(
                "destroy_tank",
                "[DARK SIDE] Destroy the water tank",
                ChoiceType.COMMITMENT,
                darkness=20,
                control=-10,
                next_scene="kyber_massacre_path",
                callback=on_water_tank_destroyed,
                response=create_dialogue(
                    "Vader",
                    "*reaches out with the Force toward the tank below*",
                    emotion="cold ruthlessness",
                    thought="Victory matters. Nothing else. They are acceptable losses."
                )
            ),
            create_choice(
                "fight_honorably",
                "[CONTROL] Continue the duel without collateral damage",
                ChoiceType.COMMITMENT,
                darkness=5,
                control=10,
                next_scene="kyber_honor_path",
                callback=on_fought_honorably,
                response=create_dialogue(
                    "Vader",
                    "*focuses entirely on Infil'a*",
                    emotion="controlled aggression",
                    thought="I don't need tricks. I am the superior warrior. I will prove it."
                )
            )
        ]
    )
    
    # Path A: Destroy the tank
    scenes["kyber_massacre_path"] = Scene(
        id="kyber_massacre_path",
        title="Acceptable Losses",
        description="You rip apart the water tank. The city begins to flood.",
        location="Am'balaar Dam",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "You tear the storage tank apart with the Force. Metal screams. Rivets snap like gunfire.",
                emotion="violent"
            ),
            create_dialogue(
                "Civilian (below)",
                "THE TANK! IT'S—",
                emotion="terrified"
            ),
            create_dialogue(
                "Narrator",
                "WHOOOOSH! A tsunami of water crashes through the city streets. Buildings collapse. Screams rise and are cut short.",
                emotion="catastrophic"
            ),
            create_dialogue(
                "Infil'a",
                "NO! *reaches out with the Force to stop the destruction*",
                emotion="horrified"
            ),
            create_dialogue(
                "Vader",
                "*uses Force Pull to rip Infil'a's lightsaber from his belt*",
                emotion="ruthless",
                thought="Distracted. As I knew he would be. Weakness."
            ),
            create_dialogue(
                "Narrator",
                "You catch his lightsaber. Blue blade in your hand. Your prize.",
                emotion="triumphant"
            ),
            create_dialogue(
                "Infil'a",
                "*still trying to save civilians below* Please! Stop this! They're innocent!",
                emotion="desperate"
            ),
            create_dialogue(
                "Vader",
                "*Force chokes Infil'a, lifting him from the dam*",
                emotion="cold",
                thought="Innocent. There are no innocents. Not anymore."
            ),
            create_dialogue(
                "Infil'a",
                "*choking* You... monster...",
                emotion="dying"
            ),
            create_dialogue(
                "Vader",
                "*crushes his throat*",
                emotion="emotionless"
            ),
            create_dialogue(
                "Narrator",
                "Infil'a's body falls into the flooded wreckage below. The city is silent except for the rushing water.",
                emotion="grim"
            )
        ],
        auto_next="kyber_aftermath_victory"
    )
    
    # Path B: Fight honorably
    scenes["kyber_honor_path"] = Scene(
        id="kyber_honor_path",
        title="The Warrior's Way",
        description="You reject the easy path. This fight will be won through skill alone.",
        location="Am'balaar Dam",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Vader",
                "*attacks with renewed intensity*",
                emotion="focused fury",
                thought="I don't need tricks. I was trained by the best. I am the best."
            ),
            create_dialogue(
                "Infil'a",
                "You... choose to spare them? Perhaps there is still—",
                emotion="hopeful"
            ),
            create_dialogue(
                "Vader",
                "I choose to defeat you myself.",
                emotion="cold pride"
            ),
            create_dialogue(
                "Narrator",
                "[COMBAT: Second Duel with Kirak Infil'a - Phase 2, Harder difficulty]",
                emotion="epic"
            )
        ],
        trigger_combat={
            "enemy_type": "infila_final_duel",
            "phase": 2,
            "difficulty": "hard"
        },
        auto_next="kyber_honor_victory"
    )
    
    scenes["kyber_honor_victory"] = Scene(
        id="kyber_honor_victory",
        title="Earned Victory",
        description="Infil'a falls to your blade. The civilians below live.",
        location="Am'balaar Dam",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your relentless assault finally breaks through his defense. Your blade finds its mark.",
                emotion="intense"
            ),
            create_dialogue(
                "Infil'a",
                "*wounded, dropping his lightsaber* You... are stronger than I thought...",
                emotion="defeated"
            ),
            create_dialogue(
                "Vader",
                "*picks up his lightsaber*",
                emotion="satisfied",
                thought="Earned. Through skill. Not through massacre."
            ),
            create_dialogue(
                "Infil'a",
                "Will you... spare the city?",
                emotion="pleading"
            ),
            create_dialogue(
                "Vader",
                "*ignites Infil'a's lightsaber* The city was never my target.",
                emotion="cold"
            ),
            create_dialogue(
                "Narrator",
                "You end him quickly. No words. No theatrics. A warrior's death.",
                emotion="grim"
            ),
            create_dialogue(
                "Narrator",
                "Below, security guards have witnessed the entire duel. They will speak of this day. Of the dark warrior who could have destroyed the city, but didn't.",
                emotion="ominous"
            )
        ],
        auto_next="kyber_aftermath_victory"
    )
    
    scenes["kyber_aftermath_victory"] = Scene(
        id="kyber_aftermath_victory",
        title="The Lightsaber",
        description="You hold Kirak Infil'a's lightsaber. Your prize.",
        location="Am'balaar Dam",
        scene_type="cutscene",
        on_enter=on_infila_killed,
        dialogue=[
            create_dialogue(
                "Vader",
                "*mechanical breathing, looking at the blue blade*",
                emotion="satisfied",
                thought="A Jedi's weapon. Soon to become a Sith's."
            ),
            create_dialogue(
                "Narrator",
                "You deactivate the lightsaber and attach it to your belt. The crystal within awaits its corruption.",
                emotion="ominous"
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "*ship descends to pick you up* Lord Vader, receiving automated navigation instructions from the Emperor.",
                emotion="mechanical"
            ),
            create_dialogue(
                "Vader",
                "Destination?",
                emotion="questioning"
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Mustafar.",
                emotion="mechanical"
            ),
            create_dialogue(
                "Vader",
                "*pause*",
                emotion="affected",
                thought="Mustafar. Where I died. Where Anakin burned."
            )
        ],
        choices=[
            create_choice(
                "journey_to_mustafar",
                "Set course.",
                ChoiceType.DIALOGUE,
                next_scene="kyber_mustafar_arrival",
                response=create_dialogue(
                    "Vader",
                    "...Proceed.",
                    emotion="controlled emotion"
                )
            )
        ]
    )
    
    return scenes


# ============================================================
# ACT 7: MUSTAFAR - THE BLEEDING & THE VISION
# ============================================================

def create_act7_scenes() -> Dict[str, Scene]:
    """Act 7: Return to Mustafar, the vision, and bleeding the crystal"""
    scenes = {}
    
    scenes["kyber_mustafar_arrival"] = Scene(
        id="kyber_mustafar_arrival",
        title="Mustafar",
        description="The volcanic world where Anakin Skywalker died. Where Darth Vader was born.",
        location="Mustafar",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The ship breaks through ash clouds. Lava flows carve glowing rivers through black stone. The air itself burns.",
                emotion="hellish"
            ),
            create_dialogue(
                "Droid Co-Pilot",
                "Emperor's instructions: Land at coordinates 2-7-7-9. A dark side locus awaits.",
                emotion="mechanical"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing intensifies*",
                emotion="affected",
                thought="I know this place. I burned here. I lost everything here."
            ),
            create_dialogue(
                "Narrator",
                "The ship lands near a shallow cavern. Inside, you sense it—a wound in the Force. A place of darkness.",
                emotion="ominous"
            ),
            create_dialogue(
                "Vader",
                "*disembarks and enters the cavern*",
                emotion="determined",
                thought="An ancient Sith shrine. The Emperor prepared this. Always manipulating."
            ),
            create_dialogue(
                "Narrator",
                "The cavern walls are carved with Sith runes. In the center, a flat stone formation—an altar of sorts.",
                emotion="dark"
            )
        ],
        auto_next="kyber_disassemble_saber"
    )
    
    scenes["kyber_disassemble_saber"] = Scene(
        id="kyber_disassemble_saber",
        title="The Ritual Begins",
        description="You disassemble Infil'a's lightsaber and extract the kyber crystal.",
        location="Sith Shrine, Mustafar",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "You place the lightsaber on the stone. Your mechanical hands work with precision, removing each component.",
                emotion="methodical"
            ),
            create_dialogue(
                "Vader",
                "*removes the kyber crystal*",
                emotion="focused",
                thought="Blue. Pure. Connected to the light. It will resist me."
            ),
            create_dialogue(
                "Narrator",
                "The crystal glows softly in your palm. You can feel its essence—Infil'a's dedication, his discipline, his hope.",
                emotion="spiritual"
            ),
            create_dialogue(
                "Vader",
                "*begins to pour rage and pain into the crystal*",
                emotion="straining",
                thought="Bleed. BLEED. Become what I am. Become red."
            ),
            create_dialogue(
                "Narrator",
                "The crystal RESISTS. It pushes back against your hatred with the Force.",
                emotion="intense"
            ),
            create_dialogue(
                "Narrator",
                "You are thrown against the cavern wall with tremendous force!",
                emotion="violent"
            ),
            create_dialogue(
                "Vader",
                "*struggles to stand*",
                emotion="surprised",
                thought="What... the crystal fights me?"
            )
        ],
        auto_next="kyber_vision_choice"
    )
    
    scenes["kyber_vision_choice"] = Scene(
        id="kyber_vision_choice",
        title="The Crystal's Vision",
        description="The kyber crystal shows you what could have been. A choice you didn't make.",
        location="Sith Shrine, Mustafar",
        scene_type="decision",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The crystal invades your mind. It shows you a vision—a path not taken.",
                emotion="mystical"
            ),
            create_dialogue(
                "Narrator",
                "You see yourself in the Emperor's office. But in this vision, you are different. Not broken. Not mechanical.",
                emotion="hopeful"
            ),
            create_dialogue(
                "Narrator",
                "In this vision, you reject the dark side. You kill Palpatine.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Narrator",
                "But the vision diverges. The crystal shows you two possible paths it saw in your heart...",
                emotion="choosing"
            ),
            create_dialogue(
                "Narrator",
                "What haunts you most? What did you truly lose?",
                emotion="questioning"
            )
        ],
        choices=[
            create_choice(
                "vision_love",
                "[LOVE] The life you could have had with Padmé",
                ChoiceType.COMMITMENT,
                darkness=15,
                suppression_change=20,
                callback=on_vision_love,
                next_scene="kyber_vision_padme",
                response=create_dialogue(
                    "Vader",
                    "*the vision shifts to Padmé*",
                    emotion="anguished",
                    thought="Padmé... no. Don't show me this."
                )
            ),
            create_choice(
                "vision_brotherhood",
                "[BROTHERHOOD] The bond you destroyed with Obi-Wan",
                ChoiceType.COMMITMENT,
                darkness=15,
                suppression_change=10,
                rage_change=5,
                callback=on_vision_brotherhood,
                next_scene="kyber_vision_obiwan",
                response=create_dialogue(
                    "Vader",
                    "*the vision shifts to Obi-Wan*",
                    emotion="conflicted rage",
                    thought="Obi-Wan. My master. My brother. My enemy."
                )
            )
        ]
    )
    
    # Vision Path A: Padmé (Love)
    scenes["kyber_vision_padme"] = Scene(
        id="kyber_vision_padme",
        title="What Love Could Have Been",
        description="The crystal shows you Padmé alive. Children. Peace.",
        location="Vision - Naboo",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The vision solidifies. You stand in a meadow on Naboo. The sun is warm. No suit. No mask. You can breathe.",
                emotion="peaceful"
            ),
            create_dialogue(
                "Padmé",
                "*appears, smiling* Anakin. You came back to me. You chose love over power.",
                emotion="joyful"
            ),
            create_dialogue(
                "Narrator",
                "Behind her, two small children run through the grass. A boy and a girl. Your children. Luke and Leia.",
                emotion="tender"
            ),
            create_dialogue(
                "Padmé",
                "We're safe here. The Empire never rose. The Jedi are rebuilding. And we have our family.",
                emotion="loving"
            ),
            create_dialogue(
                "Vision Anakin",
                "I chose you. Over everything. Over Palpatine. Over power.",
                emotion="content"
            ),
            create_dialogue(
                "Padmé",
                "*touches your face* You were always strong enough. You just needed to believe it.",
                emotion="tender"
            ),
            create_dialogue(
                "Narrator",
                "She leans in. Her lips almost touch yours. You can almost feel her warmth—",
                emotion="yearning"
            ),
            create_dialogue(
                "Vader",
                "NO!",
                emotion="shattering the vision",
                thought="This is a lie! She's dead! I killed her! This future is IMPOSSIBLE!"
            )
        ],
        auto_next="kyber_reject_vision"
    )
    
    # Vision Path B: Obi-Wan (Brotherhood)
    scenes["kyber_vision_obiwan"] = Scene(
        id="kyber_vision_obiwan",
        title="What Brotherhood Could Have Been",
        description="The crystal shows you Obi-Wan forgiving you. Redemption.",
        location="Vision - Tatooine",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The vision takes shape. A desert world. Twin suns. A simple dwelling in the sand.",
                emotion="stark"
            ),
            create_dialogue(
                "Obi-Wan",
                "*steps out of the dwelling* Anakin? Is that... you came to me.",
                emotion="shocked"
            ),
            create_dialogue(
                "Vision Anakin",
                "*kneeling* Master. I've come to beg your forgiveness. For everything I've done.",
                emotion="broken"
            ),
            create_dialogue(
                "Obi-Wan",
                "*tears in his eyes* Anakin... my brother. I never stopped believing you could come back.",
                emotion="emotional"
            ),
            create_dialogue(
                "Narrator",
                "Obi-Wan kneels beside you. He places a hand on your shoulder.",
                emotion="tender"
            ),
            create_dialogue(
                "Obi-Wan",
                "The Jedi Code says there is no death, only the Force. But I say—there is no fall so far that redemption cannot reach.",
                emotion="wise"
            ),
            create_dialogue(
                "Obi-Wan",
                "I forgive you, Anakin. I forgive you.",
                emotion="loving"
            ),
            create_dialogue(
                "Vision Anakin",
                "I don't deserve—",
                emotion="anguished"
            ),
            create_dialogue(
                "Obi-Wan",
                "None of us do. That's what makes it forgiveness.",
                emotion="gentle"
            ),
            create_dialogue(
                "Vader",
                "STOP!",
                emotion="furious rejection",
                thought="Anakin is dead! I killed him! This weakness... I will not feel it!"
            )
        ],
        auto_next="kyber_reject_vision"
    )
    
    # Rejection and Bleeding
    scenes["kyber_reject_vision"] = Scene(
        id="kyber_reject_vision",
        title="Rejection",
        description="You shatter the vision and pour your hatred into the crystal.",
        location="Sith Shrine, Mustafar",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Vader",
                "*back in the cavern, the crystal glowing in your hand*",
                emotion="furious",
                thought="That future is dead. Those people are dead. I am all that remains!"
            ),
            create_dialogue(
                "Vader",
                "Anakin Skywalker is dead! I killed him!",
                emotion="roaring"
            ),
            create_dialogue(
                "Narrator",
                "You pour EVERYTHING into the crystal. Your rage at Padmé's death. Your hatred of Obi-Wan's betrayal.",
                emotion="intense"
            ),
            create_dialogue(
                "Narrator",
                "Your pain from the burning on Mustafar. The agony of your suit. The loss of your children you never knew.",
                emotion="overwhelming"
            ),
            create_dialogue(
                "Narrator",
                "The crystal SCREAMS. A psychic wail that shakes the cavern. Outside, Mustafar itself responds—eruptions intensify.",
                emotion="apocalyptic"
            ),
            create_dialogue(
                "Vader",
                "BLEED!",
                emotion="commanding",
                thought="You will be mine. You will serve the dark side. You will serve ME!"
            ),
            create_dialogue(
                "Narrator",
                "The blue glow flickers... cracks appear in the crystal... red light seeps through...",
                emotion="transforming"
            ),
            create_dialogue(
                "Narrator",
                "The crystal BLEEDS. The blue fades completely. It glows crimson—the color of hate, of pain, of the Sith.",
                emotion="triumphant"
            ),
            create_dialogue(
                "Vader",
                "*mechanical breathing, holding the red crystal*",
                emotion="satisfied",
                thought="Mine. A Sith's weapon. The transformation is complete."
            )
        ],
        choices=[
            create_choice(
                "reassemble_saber",
                "Reassemble the lightsaber.",
                ChoiceType.DIALOGUE,
                callback=on_crystal_bled,
                next_scene="kyber_red_saber_complete",
                response=create_dialogue(
                    "Vader",
                    "*methodically rebuilds the lightsaber around the red crystal*",
                    emotion="focused"
                )
            )
        ]
    )
    
    scenes["kyber_red_saber_complete"] = Scene(
        id="kyber_red_saber_complete",
        title="The Red Blade",
        description="You ignite your lightsaber. The blade burns red.",
        location="Sith Shrine, Mustafar",
        scene_type="cutscene",
        dialogue=[
            create_dialogue(
                "Narrator",
                "The lightsaber is whole. You press the activation stud.",
                emotion="anticipation"
            ),
            create_dialogue(
                "Narrator",
                "*SNAP-HISS* A crimson blade ignites. The light bathes the cavern in blood-red.",
                emotion="dramatic"
            ),
            create_dialogue(
                "Vader",
                "*swings the blade, testing its weight*",
                emotion="satisfied",
                thought="Perfect. The weapon of a Sith Lord. My weapon."
            ),
            create_dialogue(
                "Narrator",
                "Outside the cavern, Mustafar's storm rages. But you are calm. The transformation is complete.",
                emotion="ominous"
            ),
            create_dialogue(
                "Vader",
                "It is time to show the Emperor what I have become.",
                emotion="cold confidence"
            )
        ],
        auto_next="kyber_return_coruscant"
    )
    
    return scenes


# ============================================================
# ACT 8: THE RETURN - SHOWING PALPATINE
# ============================================================

def create_act8_scenes() -> Dict[str, Scene]:
    """Act 8: Return to Coruscant and present the red lightsaber to Palpatine"""
    scenes = {}
    
    scenes["kyber_return_coruscant"] = Scene(
        id="kyber_return_coruscant",
        title="Return to Coruscant",
        description="You return to the Imperial Palace. The Emperor is in a meeting.",
        location="Coruscant, Imperial Palace",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Narrator",
                "Your black interceptor lands in the Imperial hangar. You stride through the palace corridors, red lightsaber at your belt.",
                emotion="purposeful"
            ),
            create_dialogue(
                "Narrator",
                "Guards scramble out of your way. They don't know who—or what—you are. Only that you radiate menace.",
                emotion="intimidating"
            ),
            create_dialogue(
                "Narrator",
                "You reach the Emperor's office. Inside, you hear voices—Tarkin, Mas Amedda, and the Emperor discussing something called 'The Death Star.'",
                emotion="intriguing"
            ),
            create_dialogue(
                "Vader",
                "*Force-pushes the doors open without touching them*",
                emotion="dramatic entrance"
            )
        ],
        auto_next="kyber_throne_room_intrusion"
    )
    
    scenes["kyber_throne_room_intrusion"] = Scene(
        id="kyber_throne_room_intrusion",
        title="The Intrusion",
        description="You burst into the Emperor's office during a classified meeting.",
        location="Emperor's Office",
        scene_type="dialogue",
        dialogue=[
            create_dialogue(
                "Grand Moff Tarkin",
                "*turns* What is the meaning of this intrusion? Who are you?",
                emotion="indignant"
            ),
            create_dialogue(
                "Royal Guard",
                "*two guards move to intercept* Halt! This is a restricted—",
                emotion="alarmed"
            ),
            create_dialogue(
                "Vader",
                "*Force blasts both guards back into the window without looking at them*",
                emotion="effortless power"
            ),
            create_dialogue(
                "Tarkin",
                "*hand on blaster* My Lord, this... individual is dangerous. Shall I call for—",
                emotion="concerned"
            ),
            create_dialogue(
                "Palpatine",
                "*raises hand* No. Leave us. All of you.",
                emotion="knowing smile"
            ),
            create_dialogue(
                "Tarkin",
                "But Your Majesty, your safety—",
                emotion="protesting"
            ),
            create_dialogue(
                "Palpatine",
                "I said... leave.",
                emotion="commanding"
            ),
            create_dialogue(
                "Narrator",
                "Tarkin and Mas Amedda exchange glances, then bow and depart. The Royal Guards help each other up and follow.",
                emotion="tense"
            ),
            create_dialogue(
                "Narrator",
                "The door closes. You are alone with the Emperor.",
                emotion="dramatic"
            )
        ],
        auto_next="kyber_show_saber"
    )
    
    scenes["kyber_show_saber"] = Scene(
        id="kyber_show_saber",
        title="The Presentation",
        description="You present your red lightsaber to Emperor Palpatine.",
        location="Emperor's Office",
        scene_type="cutscene",
        on_enter=on_mission_complete,
        dialogue=[
            create_dialogue(
                "Palpatine",
                "Well, Lord Vader? Did you complete your task?",
                emotion="testing"
            ),
            create_dialogue(
                "Vader",
                "*draws the lightsaber but does not ignite it*",
                emotion="silent confidence"
            ),
            create_dialogue(
                "Palpatine",
                "Show me.",
                emotion="anticipation"
            ),
            create_dialogue(
                "Narrator",
                "You press the activation stud. *SNAP-HISS*",
                emotion="dramatic"
            ),
            create_dialogue(
                "Narrator",
                "A crimson blade erupts from the hilt. The red light reflects in Palpatine's eyes.",
                emotion="triumphant"
            ),
            create_dialogue(
                "Palpatine",
                "*smiles* Good. GOOD! You have taken a Jedi's weapon and made it a tool of the Sith.",
                emotion="satisfied"
            ),
            create_dialogue(
                "Palpatine",
                "You have proven yourself, my apprentice. You are truly Darth Vader.",
                emotion="approving"
            ),
            create_dialogue(
                "Vader",
                "*deactivates lightsaber and clips it to belt*",
                emotion="cold satisfaction",
                thought="I have proven nothing. I have simply become what I must be."
            ),
            create_dialogue(
                "Palpatine",
                "Now... there is much work to do. The Jedi are scattered across the galaxy. You will hunt them all.",
                emotion="commanding"
            ),
            create_dialogue(
                "Vader",
                "As you wish, my Master.",
                emotion="obedient"
            ),
            create_dialogue(
                "Narrator",
                "The transformation is complete. Anakin Skywalker is gone. Darth Vader, Sith Lord, stands in his place—clad in black, wielding a red blade.",
                emotion="ominous"
            ),
            create_dialogue(
                "Narrator",
                "The hunt... has only just begun.",
                emotion="foreboding"
            )
        ],
        choices=[
            create_choice(
                "mission_complete",
                "[Mission Complete]",
                ChoiceType.DIALOGUE,
                next_scene=None,  # End of mission
                response=create_dialogue(
                    "Vader",
                    "*turns and leaves the office*",
                    emotion="purposeful",
                    thought="The hunt continues. There are many Jedi left to kill."
                )
            )
        ]
    )
    
    return scenes


# ============================================================
# MASTER FUNCTION - CREATE ALL SCENES
# ============================================================

def create_kyber_mission_scenes() -> Dict[str, Scene]:
    """
    Create all scenes for the Kyber Crystal mission.
    Returns dict of scene_id: Scene for all 8 acts.
    """
    all_scenes = {}
    
    # Combine all acts
    all_scenes.update(create_act1_scenes())
    all_scenes.update(create_act2_scenes())
    all_scenes.update(create_act3_scenes())
    all_scenes.update(create_act4_scenes())
    all_scenes.update(create_act5_scenes())
    all_scenes.update(create_act6_scenes())
    all_scenes.update(create_act7_scenes())
    all_scenes.update(create_act8_scenes())
    
    return all_scenes


# Test function
if __name__ == "__main__":
    scenes = create_kyber_mission_scenes()
    print(f"✓ Created {len(scenes)} scenes for Kyber Crystal mission")
    print("\nScene List by Act:")
    print("\n=== ACT 1: THE LESSON ===")
    print("  - kyber_balcony")
    print("  - kyber_yoda_saber")
    print("\n=== ACT 2: GATTERING ===")
    print("  - kyber_gattering_arrival")
    print("  - kyber_pirate_settlement")
    print("  - kyber_pirates_defeated")
    print("\n=== ACT 3: BRIGHTHOME ===")
    print("  - kyber_brighthome_approach")
    print("  - kyber_brighthome_peaceful / kyber_brighthome_massacre")
    print("  - kyber_archive_search")
    print("\n=== ACT 4: FIRST DUEL ===")
    print("  - kyber_aldoleem_arrival")
    print("  - kyber_river_challenge")
    print("  - kyber_first_duel")
    print("  - kyber_first_defeat")
    print("\n=== ACT 5: REBUILD ===")
    print("  - kyber_rebuild_awakening")
    print("  - kyber_rebuild_complete")
    print("\n=== ACT 6: FINAL DUEL ===")
    print("  - kyber_ambalaar_pursuit")
    print("  - kyber_final_duel_start")
    print("  - kyber_water_tank_choice")
    print("  - kyber_massacre_path / kyber_honor_path")
    print("  - kyber_aftermath_victory")
    print("\n=== ACT 7: MUSTAFAR ===")
    print("  - kyber_mustafar_arrival")
    print("  - kyber_disassemble_saber")
    print("  - kyber_vision_choice")
    print("  - kyber_vision_padme / kyber_vision_obiwan")
    print("  - kyber_reject_vision")
    print("  - kyber_red_saber_complete")
    print("\n=== ACT 8: RETURN ===")
    print("  - kyber_return_coruscant")
    print("  - kyber_throne_room_intrusion")
    print("  - kyber_show_saber")