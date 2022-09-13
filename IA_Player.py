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

    def findPathProlog(self, walls: list[pygame.Rect], player: Player):
        possible_direction = ["north", "south", "east", "west"]
        for wall in walls:
            wall_query = [*wall.topleft, wall.width, wall.height]
            player_query = [*player.get_position()]

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

        print(possible_direction)


    def isWallNorth(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_position()]
        return self.prolog_thread.query(f"is_wall_north({wall_query}, {player_query})")
    
    def isWallSouth(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_position()]
        return self.prolog_thread.query(f"is_wall_south({wall_query}, {player_query})")
    
    def isWallEast(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_position()]
        return self.prolog_thread.query(f"is_wall_east({wall_query}, {player_query})")

    def isWallWest(self, wall, player):
        wall_query = [*wall.topleft, wall.width, wall.height]
        player_query = [*player.get_position()]
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


    def getClosestPerception(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player):
        east_walls = list(filter(lambda wall: self.isWallEast(wall, player), walls))
        west_walls = list(filter(lambda wall: self.isWallWest(wall, player), walls))
        north_walls = list(filter(lambda wall: self.isWallNorth(wall, player), walls))
        south_walls = list(filter(lambda wall: self.isWallSouth(wall, player), walls))

        distance_wall_x = [PERCEPTION_RADIUS*self.maze_tile_size]
        distance_wall_y = [PERCEPTION_RADIUS*self.maze_tile_size]

        if len(east_walls) > 0:
            distance_wall_x.append(np.array([(wall.centerx + wall.width )for wall in east_walls]) - player.x)
        
        if len(west_walls) > 0:
            distance_wall_x.append(player.x - np.array([(wall.centerx)for wall in east_walls]))
        
        if len(north_walls) > 0:
            distance_wall_y.append(np.array([(wall.centery + wall.height )for wall in north_walls]) - player.y)
        
        if len(south_walls) > 0:
            distance_wall_y.append(player.y - np.array([(wall.centery)for wall in south_walls]))

        distance_wall_x = min(distance_wall_x, key=abs)
        distance_wall_y = min(distance_wall_y, key=abs)

        if(len(obstacles) > 0):
            distance_obstacle_x = min(np.array([obstacle.centerx for obstacle in obstacles]) - player.x, key=abs)
            distance_obstacle_y = min(np.array([obstacle.centery for obstacle in obstacles]) - player.y, key=abs)
        else:
            distance_obstacle_x = PERCEPTION_RADIUS*self.maze_tile_size
            distance_obstacle_y = PERCEPTION_RADIUS*self.maze_tile_size
        
        return (distance_wall_x, distance_wall_y), (distance_obstacle_x, distance_obstacle_y)


    def getNextInstruction(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player):
        self.findPathProlog(walls, player)

        #rotation_matrice = self.getRotationMatriceFromDirection()
        
        distance_wall, distance_obstacle = self.getClosestPerception(walls, obstacles, items, monsters, player)

        #distance_wall = rotation_matrice @ np.array([distance_wall_x, distance_wall_y])
        #distance_obstacle = rotation_matrice @ np.array([distance_wall_x, distance_wall_y])
         

        force_x = self.fuzzy_controller.get_direction(distance_wall[0], distance_obstacle[0], -distance_obstacle[1])
        force_y = self.fuzzy_controller.get_direction(-distance_wall[1], -distance_obstacle[1], distance_obstacle[0])

        #matrice de rotation

        #self.direction_courante = "south"
        commandes = []

        if force_x > 0.2:
            commandes.append("RIGHT")
        elif force_x < -0.2:
            commandes.append("LEFT")
        #else:
        #    if(self.direction_courante == "east"):
        #        commandes.append("LEFT")
        #    elif(self.direction_courante == "west"):
        #        commandes.append("RIGHT")
        if force_y > 0.2:
            commandes.append("UP")
        elif force_y < -0.2:
            commandes.append("DOWN")
        #else:
        #    if(self.direction_courante == "north"):
        #        commandes.append("UP")
        #    elif(self.direction_courante == "south"):
        #        commandes.append("DOWN")

        return commandes
