#!/usr/bin/env python3

import asyncio
import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
from engine.myEngine import MurderEngine
from grammar.extractor import ClueExtractor

engine = MurderEngine()
extractor = ClueExtractor()

# Define markers associated with clue sentences
guests_markers = [
    CustomObjectTypes.CustomType00,
    CustomObjectTypes.CustomType01,
    CustomObjectTypes.CustomType02,
    CustomObjectTypes.CustomType03
]

# Define clue sentence
guests = [
    "Colonel Mustard",
    "Mrs. White",
    "Mr. Green",
    "Miss Scarlet"
]

weapons_markers = [
    CustomObjectTypes.CustomType04,
    CustomObjectTypes.CustomType05,
    CustomObjectTypes.CustomType06,
    CustomObjectTypes.CustomType07
]

weapons = [
    "Couteau",
    "Revolver",
    "Corde",
    "Livre"
]

rooms_markers = [
    CustomObjectTypes.CustomType08,
    CustomObjectTypes.CustomType09,
    CustomObjectTypes.CustomType10,
    CustomObjectTypes.CustomType11,
    CustomObjectTypes.CustomType12,
    CustomObjectTypes.CustomType13
]

rooms = [
    "Library",
    "Study",
    "Cellar",
    "Kitchen",
    "Manoir",
    "Prison"
]


def wait_for_marker(robot: cozmo.robot.Robot, markers_list, text_list):
    try:
        # Try to observe an object
        event = robot.world.wait_for(cozmo.objects.EvtObjectObserved, timeout=8)

        # If object is a CustomObject
        if isinstance(event.obj, CustomObject):
            print(event.obj.object_type)
            text = text_list[markers_list.index(event.obj.object_type)]
            return text
    except asyncio.TimeoutError:
        print("No marker found")


# Cozmo waits up to 2 seconds for a cube, if a cube appears he flips it, else he execute one of the sequential actions
def murder_info(robot: cozmo.robot.Robot):

    try:
        # robot.set_head_angle(degrees(-5.0)).wait_for_completed()
        robot.say_text("Effectivement, la victime est morte.").wait_for_completed()
        keyboard_input("Qui est la victime")

        robot.say_text("Où sommes nous?").wait_for_completed()
        room = wait_for_marker(robot, rooms_markers, rooms)
        engine.assert_murder_room(room)
        robot.say_text("Nous sommes dans le {}".format(room)).wait_for_completed()

        robot.say_text("Miss Scarlet, vous êtes coroner, quand croyez que le crime a été commit?").wait_for_completed()
        keyboard_input("Temps du décès")

    except asyncio.TimeoutError:
        print("Flip cube timeout")


def flip_victim(robot: cozmo.robot.Robot):
    print("Cozmo is waiting until he sees a cube")
    try:
        cube = robot.world.wait_for_observed_light_cube(timeout=5)

        print("Cozmo found a cube, and will now attempt to pop a wheelie on it")

        robot.pickup_object(cube, num_retries=2).wait_for_completed()
        robot.set_lift_height(0).wait_for_completed()
        robot.drive_straight(distance_mm(-10), speed_mmps(75)).wait_for_completed()
    except TimeoutError:
        print("No cube found")


def ask_to_see_weapon(robot: cozmo.robot.Robot):
    print("Cozmo wants to see the murder weapon")
    robot.say_text("Je désire voir l'arme du crime.").wait_for_completed()
    weapon = engine.get_murder_weapon()
    marker_weapon = wait_for_marker(robot, weapons_markers, weapons)

    if weapon == marker_weapon:
        robot.say_text("Merci, c'est bien l'arme du crime.").wait_for_completed()
    else:
        robot.say_text("Non, ceci est un {}".format(marker_weapon)).wait_for_completed()
        ask_to_see_weapon(robot)


def greet_guests(robot: cozmo.robot.Robot):
    victim = engine.get_victim()
    robot.say_text("{} vient tout juste d'être froidement assasiné, je demande à voir tous les invités".format(victim)).wait_for_completed()
    for i in range(len(guests)):
        guest = wait_for_marker(robot, guests_markers, guests)
        robot.say_text("Bonjour {}, je vous ai à l'oeil".format(guest)).wait_for_completed()


def arrest_murderer(robot: cozmo.robot.Robot):
    engine.assert_murderer()
    murderer = engine.get_murderer()
    victim = engine.get_victim()

    # murderer = "BOB"
    # victim = "Robert"
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

    # try to find a block
    cube = None

    try:
        cube = robot.world.wait_for_observed_light_cube(timeout=30)
        print("Found cube", cube)

    except asyncio.TimeoutError:
        print("Didn't find a cube :-(")

    finally:
        # whether we find it or not, we want to stop the behavior
        look_around.stop()

    robot.pickup_object(cube, num_retries=2).wait_for_completed()

    robot.say_text(
        "{}, vous êtes en état d'arrestation pour le meurtre de {}".format(murderer, victim)).wait_for_completed()

    robot.set_lift_height(0.1).wait_for_completed()
    robot.set_lift_height(0.5).wait_for_completed()
    robot.set_lift_height(0.1).wait_for_completed()
    robot.set_lift_height(0.5).wait_for_completed()
    robot.set_lift_height(0.1).wait_for_completed()
    robot.set_lift_height(1.0).wait_for_completed()

    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    room = wait_for_marker(robot, rooms_markers, rooms)
    while room is not "Prison":
        room = wait_for_marker(robot, rooms_markers, rooms)

    look_around.stop()
    robot.say_text("Voilà la prison.").wait_for_completed()
    robot.drive_straight(distance_mm(200), speed_mmps(75)).wait_for_completed()

    robot.set_lift_height(0).wait_for_completed()
    robot.drive_straight(distance_mm(-10), speed_mmps(75)).wait_for_completed()
    robot.say_text("Prends ça, racaille!").wait_for_completed()


def ask_question(robot: cozmo.robot.Robot, question, affirmation):

    robot.say_text(question).wait_for_completed()
    tap_count = 0

    cube = None
    try:
        cube = robot.world.wait_for_observed_light_cube(timeout=2)
        for i in range(3):
            try:
                print("Waiting for tap")
                cube.wait_for_tap(timeout=2)
                print("Tap recorded")
                tap_count = tap_count + 1
            except asyncio.TimeoutError:
                print("No tap")
    except asyncio.TimeoutError:
        print("No cube found")

    if tap_count == 1:
        engine.eval_sentence(affirmation)
    elif tap_count == 2:
        print("Detective cozmo says no")
    elif tap_count == 3:
        print("Detective cozmo says maybe")


def keyboard_input(prompt):
    sentence = input("{} : ".format(prompt))
    print("Keyboard input : {}".format(sentence))
    engine.eval_sentence(sentence)


# Defines the markers in cozmo's world
def define_markers(robot: cozmo.robot.Robot):
    robot.world.define_custom_cube(CustomObjectTypes.CustomType00,
                                   CustomObjectMarkers.Triangles2,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType01,
                                   CustomObjectMarkers.Triangles3,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType02,
                                   CustomObjectMarkers.Triangles4,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType03,
                                   CustomObjectMarkers.Triangles5,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType04,
                                   CustomObjectMarkers.Circles2,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType05,
                                   CustomObjectMarkers.Circles3,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType06,
                                   CustomObjectMarkers.Circles4,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType07,
                                   CustomObjectMarkers.Circles5,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType08,
                                   CustomObjectMarkers.Diamonds2,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType09,
                                   CustomObjectMarkers.Diamonds3,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType10,
                                   CustomObjectMarkers.Diamonds4,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType11,
                                   CustomObjectMarkers.Diamonds5,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType12,
                                   CustomObjectMarkers.Hexagons2,
                                   44,
                                   30, 30, True)

    robot.world.define_custom_cube(CustomObjectTypes.CustomType13,
                                   CustomObjectMarkers.Hexagons3,
                                   44,
                                   30, 30, True)


def interogate_guests(robot: cozmo.robot.Robot):
    w_room = engine.get_weapon_room()
    w_time = engine.get_weapon_time()
    m_room = engine.get_murder_room()
    m_time = engine.get_murder_time()

    for guest in guests:
        # Access to murder room
        question = "{}, étiez-vous dans {} entre {} et {}".format(guest, m_room, m_time[0].lower(), m_time[1].lower())
        affirmation = "{} was_in the {} between {} and {}".format(guest, m_room, m_time[0].lower(), m_time[1].lower())
        ask_question(robot, question, affirmation)

        # Access to weapon room
        question = "{}, étiez-vous dans {} entre {} et {}".format(guest, w_room, w_time[0].lower(), w_time[1].lower())
        affirmation = "{} was_in the {} between {} and {}".format(guest, w_room, w_time[0].lower(), w_time[1].lower())
        ask_question(robot, question, affirmation)


def party_arrival(robot: cozmo.robot.Robot):
    robot.set_lift_height(0).wait_for_completed()
    robot.drive_straight(distance_mm(100), speed_mmps(75)).wait_for_completed()
    robot.say_text("Où est le manoir?").wait_for_completed()

    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

    # try to find a block
    cube = None
    event = None
    room = None
    try:
        event = robot.world.wait_for(cozmo.objects.EvtObjectObserved, timeout=8)
        # If object is a CustomObject
        if isinstance(event.obj, CustomObject):
            print(event.obj.object_type)
            room = rooms[rooms_markers.index(event.obj.object_type)]
        print("Found cube", cube)

    except asyncio.TimeoutError:
        print("Didn't find a cube :-(")

    finally:
        # whether we find it or not, we want to stop the behavior
        look_around.stop()

    if room is not "Manoir":
        robot.say_text("Ce n'est pas le manoir.").wait_for_completed()
        party_arrival(robot)
        return
    else:
        robot.drive_straight(distance_mm(100), speed_mmps(75)).wait_for_completed()

    robot.say_text("Enfin arrivé!").wait_for_completed()
    person = wait_for_marker(robot, guests_markers, guests)
    robot.say_text("Bonjour {}, où se trouve la victime? Je vous suis.".format(person)).wait_for_completed()


# Scenario method ran by the cozmo SDK
def cozmo_scenario(robot: cozmo.robot.Robot):

    define_markers(robot)

    party_arrival(robot)

    flip_victim(robot)

    murder_info(robot)

    robot.say_text("Quand est-ce que l'arme a été obtenue?").wait_for_completed()
    keyboard_input("Période pour l'arme")

    greet_guests(robot)

    ask_to_see_weapon(robot)

    interogate_guests(robot)

    arrest_murderer(robot)


cozmo.run_program(cozmo_scenario, use_viewer=True)