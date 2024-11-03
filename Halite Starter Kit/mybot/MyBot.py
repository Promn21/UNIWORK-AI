#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Decepticons")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        
        
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            command_queue.append(
                ship.move(
                    random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])))
        else:
            command_queue.append(ship.stay_still())

        if game_map[ship.position].ship.is_full: 
            
            #Flag everyship I spawned with Decepticon_bots
            

            #Bot 1: minerShips
            #try to create: state 1: if ship is not full go in one random direction for 5 tile while moving checking for high halite location 
            #try to create: state 2: if found high hallite then go to this state to stay still if not go back to state 1
            #try to create: state 3: while stay still or moving if near another ship by 2 cell radius move away in random position for 3 tiles then go back to state 1
            #try to create: state 4: if ship is full move to shipyard(x,y) if reached shipyard dropoff hallite

            #Bot 2: attackShip spwan if there are no attackShip role is limit to 1 ship (only supportShip can spawn the attackShip)
            #try to create: state 1: #Seek enemyShip(not mine)(move to the direction of their base) once found enemy move my ship to collide
            #try to create: state 2: #Once collide store the last position of the cell
            #try to create: state 3: #Assign position for supportShip to retieve the halite, and immediately go back home to dropoff
            #try to create: state 4: once drop off spawn a new attackship immediately

            #Bot 3: supportShip - always spawn if there are no supportShip - role is limit to 1(stay close to an attack ship to get halite once the enemy is killed by the attackship)
            #try to create: state 1: stay close to an attack ship by 1 cell radius while avoid the enemy ship by 2 cell
            #try to create: state 2: runaway if enemyShip is within 2 cell radius
            #try to create: state 3: Once attackship is colide move to the halite and stay still(retieve it)
            #try to create: state 4: Once retieved go back to base to drop off halite and spawn new attackship

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

