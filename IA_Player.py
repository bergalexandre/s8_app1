import pygame
import time
from swiplserver import PrologMQI
from IA_FuzzyController import *
import math
from Player import Player

class IA_Player:
    prolog_thread = None
    mqi = PrologMQI(output_file_name="output.txt")
    maze_tile_size = 1

    def __init__(self, maze_tile_size):
        self.prolog_thread = self.mqi.create_thread()
        self.prolog_thread.query("[prolog/pathfinder]")
        self.fuzzy_controller = IA_FuzzyController(maze_tile_size)
        self.maze_tile_size = maze_tile_size

    def __del__(self):
        self.mqi.stop()

    def findPathProlog(self, walls: list[pygame.Rect], player: Player, show_possible_direction):
        possible_direction = ["north", "south", "east", "west"]
        for wall in walls:
            wall_query = [*wall.topleft, wall.width, wall.height]
            player_query = [*player.get_center()]

            if(self.prolog_thread.query(f"is_wall_north({wall_query}, {player_query})")):
                if("north" in possible_direction):
                    possible_direction.remove("north")
            
            if(self.prolog_thread.query(f"is_wall_south({wall_query}, {player_query})")):
                if("south" in possible_direction):
                    possible_direction.remove("south")

            if(self.prolog_thread.query(f"is_wall_east({wall_query}, {player_query})")):
                if("east" in possible_direction):
                    possible_direction.remove("east")

            if(self.prolog_thread.query(f"is_wall_west({wall_query}, {player_query})")):
                if("west" in possible_direction):
                    possible_direction.remove("west")
        
        if(show_possible_direction):
            print(possible_direction)


    def isWallNorth(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_center()]
        return self.prolog_thread.query(f"is_wall_north({wall_query}, {player_query})")
    
    def isWallSouth(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_center()]
        return self.prolog_thread.query(f"is_wall_south({wall_query}, {player_query})")
    
    def isWallEast(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_center()]
        return self.prolog_thread.query(f"is_wall_east({wall_query}, {player_query})")

    def isWallWest(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_center()]
        return self.prolog_thread.query(f"is_wall_west({wall_query}, {player_query})")


    def getRotationMatriceFromDirection(self):

        match self.direction_courante:
            case "north":
                theta = 0
            case "west":
                theta = np.radians(90)
            case "south":
                theta = np.radians(180)
            case "east":
                theta = np.radians(270)
            case _:
                raise("Direction not configured for rotation matrice")
            
        c, s = np.cos(theta), np.sin(theta)
        return np.array(((c, -s), (s, c)))


    def getClosestPerception(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player: Player):
        east_walls = list(filter(lambda wall: self.isWallEast(wall, player), walls))
        west_walls = list(filter(lambda wall: self.isWallWest(wall, player), walls))
        north_walls = list(filter(lambda wall: self.isWallNorth(wall, player), walls))
        south_walls = list(filter(lambda wall: self.isWallSouth(wall, player), walls))

        distance_wall_x = [PERCEPTION_RADIUS*self.maze_tile_size]
        distance_wall_y = [PERCEPTION_RADIUS*self.maze_tile_size]

        player_x, player_y = player.get_center()

        distance_wall_x += ([(wall.topleft[0] + wall.width - player_x)for wall in east_walls])
        distance_wall_x += ([(wall.topleft[0] - player_x)for wall in west_walls])
        distance_wall_y += ([(wall.topleft[1] + wall.height - player_x)for wall in north_walls])
        distance_wall_y += ([(wall.topleft[1] - player_y)for wall in south_walls])

        distance_wall_x = min(distance_wall_x, key=abs)
        distance_wall_y = min(distance_wall_y, key=abs)


        distance_obstacle_x = [PERCEPTION_RADIUS*self.maze_tile_size]
        distance_obstacle_y = [PERCEPTION_RADIUS*self.maze_tile_size]
        distance_obstacle_x += ([(obstacle.centerx - player_x)for obstacle in obstacles])
        distance_obstacle_y += ([(obstacle.centery - player_y)for obstacle in obstacles])

        distance_obstacle_x = min(distance_obstacle_x, key=abs)
        distance_obstacle_y = min(distance_obstacle_y, key=abs)

        return (distance_wall_x, distance_wall_y), (distance_obstacle_x, distance_obstacle_y)


    def getNextInstruction(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player, direction, show_debug_info):
        self.findPathProlog(walls, player, show_debug_info)

        distance_wall, distance_obstacle = self.getClosestPerception(walls, obstacles, items, monsters, player)         

        match direction:
            case "UP":
                distance_obstacle = (distance_obstacle[0], PERCEPTION_RADIUS*self.maze_tile_size)
            case "DOWN":
                distance_obstacle = (distance_obstacle[0], PERCEPTION_RADIUS*self.maze_tile_size)
            case "LEFT":
                distance_obstacle = (PERCEPTION_RADIUS*self.maze_tile_size, distance_obstacle[1])
            case "RIGHT":
                distance_obstacle = (PERCEPTION_RADIUS*self.maze_tile_size, distance_obstacle[1])

        force_x = self.fuzzy_controller.get_direction(distance_wall[0], distance_obstacle[0])
        force_y = self.fuzzy_controller.get_direction(distance_wall[1], distance_obstacle[1])

        if(show_debug_info):
            print(f"distance_wall={distance_wall}\ndistance_obstacle({distance_obstacle})\nforces({force_x}, {force_y})\n")

        #self.direction_courante = "south"
        commandes = []

        if force_x > 0.005:
            commandes.append("RIGHT")
        elif force_x < -0.005:
            commandes.append("LEFT")
        else:
            if(direction == "LEFT"  or direction == "RIGHT"):
                commandes.append(direction)
        #else:
        #    if(self.direction_courante == "east"):
        #        commandes.append("LEFT")
        #    elif(self.direction_courante == "west"):
        #        commandes.append("RIGHT")
        if force_y < -0.05:
            commandes.append("UP")
        elif force_y > 0.05:
            commandes.append("DOWN")
        else:
            if(direction == "DOWN"  or direction == "UP"):
                commandes.append(direction)
        #else:
        #    if(self.direction_courante == "north"):
        #        commandes.append("UP")
        #    elif(self.direction_courante == "south"):
        #        commandes.append("DOWN")

        return commandes
