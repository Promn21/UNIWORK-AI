#!/usr/bin/env python3
# Python 3.6

import math
import hlt
from hlt import constants
from hlt.positionals import Direction, Position
import random
import logging
from hlt.entity import Ship

# Define the maximum number of ships that can be spawned
MAX_SHIPS = 5

global canSpawned

""" <<<Game Begin>>> """
canSpawned = False
game = hlt.Game()
game.ready("Decepticon")

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

stages = {'go_to_collect', 'collecting', 'back_home'}
ship_stage = {}
ship_canBack = {}  


def is_position_occupied(pos):
    for other_ship in game.me.get_ships():
        if other_ship.position == pos:
            return True
    return False

def check_move_conflicts(command_queue):
    move_targets = set()
    new_command_queue = []

    for command in command_queue:
        if isinstance(command, str) and command.startswith("MOVE"):
            parts = command.split()
            if len(parts) > 2:
                target_pos = parts[2]
                if target_pos in move_targets:
                    continue
                move_targets.add(target_pos)
        new_command_queue.append(command)

    return new_command_queue

while True:
    game.update_frame()
    me = game.me
    game_map = game.game_map

    command_queue = []

    for ship in me.get_ships():
        if ship.id not in ship_stage:
            ship_stage[ship.id] = 'go_to_collect'
            ship_canBack[ship.id] = True  

        if ship_stage[ship.id] == 'go_to_collect':
            shipSpawnedAfterDrop()
            halite_values = {}
            direction_values = {}
            for direction in [Direction.North, Direction.South, Direction.East, Direction.West]:
                pos = ship.position.directional_offset(direction)
                halite_values[pos] = game_map[pos].halite_amount
                direction_values[pos] = direction

            if len(halite_values) > 0:
                highest_halite_pos = max(halite_values, key=halite_values.get)  
                direction = direction_values[highest_halite_pos]  
                
                target_pos = ship.position.directional_offset(direction)
                if is_position_occupied(target_pos):
                    logging.info(f"Ship {ship.id} found collision at {target_pos}. Choosing another direction.")
                    available_directions = [Direction.North, Direction.South, Direction.East, Direction.West]
                    random.shuffle(available_directions) 
                    for alt_direction in available_directions: 
                        alt_target_pos = ship.position.directional_offset(alt_direction)
                        if not is_position_occupied(alt_target_pos):
                            direction = alt_direction
                            break

                command_queue.append(ship.move(direction))
                ship_stage[ship.id] = 'collecting'
                logging.info(f"Ship {ship.id} moved to collect halite and is now in 'collecting' state")
            
            else:
                command_queue.append(ship.stay_still())

        elif ship_stage[ship.id] == 'collecting':
            command_queue.append(ship.stay_still()) 

            if ship.halite_amount >= constants.MAX_HALITE and ship_canBack[ship.id] == True:
                ship_stage[ship.id] = 'back_home'
                ship_canBack[ship.id] = False  
                logging.info(f"Ship {ship.id} changed to back_home state")
            
            elif game_map[ship.position].halite_amount <= 10:
                ship_stage[ship.id] = 'go_to_collect'
                logging.info(f"Ship {ship.id} changed to go_to_collect state")

        elif ship_stage[ship.id] == 'back_home':
            d = Position(0, 0)
            d.x = me.shipyard.position.x - ship.position.x
            d.y = me.shipyard.position.y - ship.position.y

            cmd = Direction.Still
            if d.x > 0:
                cmd = Direction.East
            elif d.x < 0:
                cmd = Direction.West
            if d.y > 0:
                cmd = Direction.South
            elif d.y < 0:
                cmd = Direction.North

            target_pos = ship.position.directional_offset(cmd)
            if is_position_occupied(target_pos):
                available_directions = [Direction.North, Direction.South, Direction.East, Direction.West]
                random.shuffle(available_directions)  
                for alt_direction in available_directions:
                    alt_target_pos = ship.position.directional_offset(alt_direction)
                    if not is_position_occupied(alt_target_pos):
                        cmd = alt_direction
                        break

            command_queue.append(ship.move(cmd))

            if ship.position == me.shipyard.position:
                canSpawned = True
                ship_canBack[ship.id] = True 
                ship_stage[ship.id] = 'go_to_collect'
                logging.info(f"Ship {ship.id} reached the shipyard and changed to go_to_collect state")

    if game.turn_number <= 1 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        if len(me.get_ships()) < MAX_SHIPS:
            command_queue.append(me.shipyard.spawn())

    def shipSpawnedAfterDrop():
        global canSpawned
        if game.turn_number >= 2 and me.halite_amount >= constants.SHIP_COST and canSpawned == True and not game_map[me.shipyard].is_occupied:
            if len(me.get_ships()) < MAX_SHIPS:
                command_queue.append(me.shipyard.spawn())
                canSpawned = False

    command_queue = check_move_conflicts(command_queue)

    game.end_turn(command_queue)
