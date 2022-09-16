from operator import truediv
import pygame
import time
from swiplserver import PrologMQI
from collections import defaultdict as dd
from queue import PriorityQueue
from IA_FuzzyController import *
import math
from Player import Player
class Case:
    def __init__(self, x, y, h, parent=None, start=False, end=False, wall=False):
        self.x = x
        self.y = y
        self.position = (x,y)
        self.g= float('inf')
        self.h = h
        self.f = float('inf')
        self.parent = parent
        self.start = start
        self.end = end
        self.wall = wall

class IA_Player:
    prolog_thread = None
    mqi = PrologMQI(output_file_name="output.txt")
    maze_tile_size = 1
    

    def __init__(self, maze_tile_size, maze):
        self.prolog_thread = self.mqi.create_thread()
        self.prolog_thread.query("[prolog/pathfinder]")
        self.fuzzy_controller = {}
        
        #self.fuzzy_controller["LEFT"] = IA_FuzzyController2(maze_tile_size[0])
        self.fuzzy_controller["RIGHT"] = IA_FuzzyController2(maze_tile_size[0])
        #self.fuzzy_controller["UP"] = IA_FuzzyController2(maze_tile_size[1])
        self.fuzzy_controller["DOWN"] = IA_FuzzyController2(maze_tile_size[1])

        self.maze_tile_size = maze_tile_size
        self.maze_tile_size_x, self.maze_tile_size_y = maze_tile_size
        
        self.maze = maze.maze
        self.node_matrix = None
        start, self.end = self.nodify_maze()
        self.path = self.build_tree(start, self.end)
        
        # Pour trésor
        self.FIND_TREASURE = False
        m = np.array(self.maze)
        all_treasure = np.argwhere(m=='T')
        end = np.argwhere(m=='E')
        self.all_goals = np.vstack((all_treasure,end))
        

    def find_closest_of_axis(self, objs, axis, condition):
        smallest_pair = [PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]]
        for obj in objs:
            if(abs(obj[axis]) < smallest_pair[axis] and condition(obj[axis])):
                smallest_pair = obj
        return smallest_pair

    def __del__(self):
        self.mqi.stop()

    def is_direction_free(self, walls: list[pygame.Rect], player: Player, possible_direction = ("DOWN", "UP", "LEFT", "RIGHT"), show_possible_direction = False):
        free_direction = list(possible_direction)
        for wall in walls:
            wall_query = [*wall.topleft, wall.width, wall.height]
            player_query = [*player.get_center()]

            if(self.prolog_thread.query(f"is_wall_north({wall_query}, {player_query})")):
                if("UP" in free_direction):
                    free_direction.remove("UP")
            
            if(self.prolog_thread.query(f"is_wall_south({wall_query}, {player_query})")):
                if("DOWN" in free_direction):
                    free_direction.remove("DOWN")

            if(self.prolog_thread.query(f"is_wall_east({wall_query}, {player_query})")):
                if("LEFT" in free_direction):
                    free_direction.remove("LEFT")

            if(self.prolog_thread.query(f"is_wall_west({wall_query}, {player_query})")):
                if("RIGHT" in free_direction):
                    free_direction.remove("RIGHT")
        
        if(show_possible_direction):
            print(free_direction)
        
        return free_direction == list(possible_direction)


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


    def getClosestPerception(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player: Player, direction):
        east_walls = list(filter(lambda wall: self.isWallEast(wall, player), walls))
        west_walls = list(filter(lambda wall: self.isWallWest(wall, player), walls))
        north_walls = list(filter(lambda wall: self.isWallNorth(wall, player), walls))
        south_walls = list(filter(lambda wall: self.isWallSouth(wall, player), walls))

        distance_wall = {}
        distance_wall["UP"] = [[PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[0]]]
        distance_wall["DOWN"] = [[PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[0]]]
        distance_wall["LEFT"] = [[PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[0]]]
        distance_wall["RIGHT"] = [[PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[0]]]

        player_x, player_y = player.get_center()
        player_size = np.array(player.get_size())/2

        distance_wall["LEFT"]   += ([np.abs((np.array(wall.center) + (wall.width/2, 0) - player.get_center())).tolist() for wall in east_walls])
        distance_wall["RIGHT"]  += ([(np.array(wall.center) - (wall.width/2, 0) - player.get_center()).tolist() for wall in west_walls])
        distance_wall["UP"]     += ([np.abs((np.array(wall.center) + (0, wall.height/2) - player.get_center())).tolist() for wall in north_walls])
        distance_wall["DOWN"]   += ([(np.array(wall.center) - (0, wall.height/2) - player.get_center()).tolist() for wall in south_walls])
        
        distance_wall["LEFT"] = self.find_closest_of_axis(distance_wall["LEFT"], 0, lambda _: True)
        distance_wall["RIGHT"] = self.find_closest_of_axis(distance_wall["RIGHT"], 0, lambda _: True)
        distance_wall["DOWN"] = self.find_closest_of_axis(distance_wall["DOWN"], 1, lambda _: True)
        distance_wall["UP"] = self.find_closest_of_axis(distance_wall["UP"], 1, lambda _: True)

        distance_obstacle = [[PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]]]
        distance_obstacle += [(np.array(obstacle.center) - [player_x, player_y]).tolist() for obstacle in obstacles]

        obstacle = {}
        obstacle["LEFT"] = self.find_closest_of_axis(distance_obstacle, 0, lambda x: True)
        obstacle["RIGHT"] = self.find_closest_of_axis(distance_obstacle, 0, lambda x: True)
        obstacle["UP"] = self.find_closest_of_axis(distance_obstacle, 1, lambda y: True)
        obstacle["DOWN"] = self.find_closest_of_axis(distance_obstacle, 1, lambda y: True)

        dist_item = [[PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]]]
        dist_item += [(np.array(item.center) - [player_x, player_y]).tolist() for item in items]

        item = {}
        item["LEFT"] = self.find_closest_of_axis(dist_item, 0, lambda x: True)
        item["RIGHT"] = self.find_closest_of_axis(dist_item, 0, lambda x: True)
        item["UP"] = self.find_closest_of_axis(dist_item, 1, lambda y: True)
        item["DOWN"] = self.find_closest_of_axis(dist_item, 1, lambda y: True)

        bloqueur_consigne = {
            "LEFT": [PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]], 
            "RIGHT": [PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]], 
            "UP": [PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]], 
            "DOWN": [PERCEPTION_RADIUS*self.maze_tile_size[0], PERCEPTION_RADIUS*self.maze_tile_size[1]]
            }
        
        if(direction == "LEFT" or direction == "RIGHT"):
            bloqueur_consigne["UP"] = obstacle[direction]
            bloqueur_consigne["DOWN"] = obstacle[direction]
        else:
            bloqueur_consigne["LEFT"] = obstacle[direction]
            bloqueur_consigne["RIGHT"] = obstacle[direction]

        return distance_wall, obstacle, bloqueur_consigne, item


    def getNextInstruction(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player, direction, show_debug_info):
        self.is_direction_free(walls, player, show_possible_direction=show_debug_info)

        wall, obstacle, bloqueur_consigne, item = self.getClosestPerception(walls, obstacles, items, monsters, player, direction) 
        
        consigne = { "UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0 }

        match direction:
            case "UP":
                consigne["DOWN"] = -1        
            case "DOWN":
                consigne["DOWN"] = 1
            case "LEFT":
                consigne["RIGHT"] = -1
            case "RIGHT":
                consigne["RIGHT"] = 1
            
        
        
        forces = {}
        forces["RIGHT"] = self.fuzzy_controller["RIGHT"].get_direction(
            wall["RIGHT"][0], 
            wall["RIGHT"][1],
            wall["LEFT"][0], 
            wall["LEFT"][1],
            obstacle["RIGHT"][0], 
            obstacle["RIGHT"][1], 
            bloqueur_consigne["RIGHT"][1],
            bloqueur_consigne["RIGHT"][0],
            item["RIGHT"][0],
            consigne["RIGHT"]
        )
        forces["DOWN"] = self.fuzzy_controller["DOWN"].get_direction(
            wall["DOWN"][1], 
            wall["DOWN"][0],
            wall["UP"][1], 
            wall["UP"][0],
            obstacle["DOWN"][1], 
            obstacle["DOWN"][0], 
            bloqueur_consigne["DOWN"][1],
            bloqueur_consigne["DOWN"][0],
            item["DOWN"][1],
            consigne["DOWN"]
        )
        
        #if(show_debug_info):
        #    print(f"distance_wall={wall}\ndistance_obstacle({distance_obstacle})\nforces({force_x}, {force_y})\n")

        #self.direction_courante = "south"
        commandes = []

        if(forces["RIGHT"] > 0.2):
            commandes.append("RIGHT")
        elif (forces["RIGHT"] < -0.2):
            commandes.append("LEFT")
        if(forces["DOWN"] > 0.2):
            commandes.append("DOWN")
        elif (forces["DOWN"] < -0.2):
            commandes.append("UP")
        
        return commandes
    
    def getDirection(self, player: Player, walls: list[pygame.Rect]):
        current_position = [*player.get_center()]
        active_coord = (int(np.floor(current_position[1]/self.maze_tile_size_x)), int(np.floor(current_position[0]/self.maze_tile_size_y))) 
        next_coord = self.getPath(active_coord)
        if next_coord:
            delta=np.asarray(next_coord) - np.asarray(active_coord)
        else:
            delta=np.array([0.0, 0.0])

        direction = None

        if (delta ==[1.0, 0.0]).all():
            if(self.is_direction_free(walls, player, ("DOWN",))): #one value tuple
                direction= "DOWN"
        elif (delta ==[-1.0, 0.0]).all():
            if(self.is_direction_free(walls, player, ("UP",))): #one value tuple
                direction= "UP"
        elif (delta ==[0.0, 1.0]).all():
            if(self.is_direction_free(walls, player, ("RIGHT",))): #one value tuple
                direction= "RIGHT"
        elif (delta ==[0.0, -1.0]).all():
            if(self.is_direction_free(walls, player, ("LEFT",))): #one value tuple
                direction= "LEFT"
        else:
            direction=None
                      
        return direction
    
    def getPath(self, active_coord):
        
        if(len(self.all_goals) == 0):
            self.all_goals = np.array([self.end])
        closest_goal = np.argmin([(active_coord[0]-i[0])**2+(active_coord[1]-i[1])**2 for i in self.all_goals])

        if self.FIND_TREASURE == False:
            start, end = self.nodify_maze(Custom_start=active_coord, Tresor=self.all_goals[closest_goal])
            self.path = self.build_tree(start, end)
            self.all_goals = np.delete(self.all_goals, closest_goal,0)
            self.FIND_TREASURE = True
        
        if active_coord not in self.path:
            start, end = self.nodify_maze(Custom_start=active_coord, Tresor=self.all_goals[closest_goal])
            self.path = self.build_tree(start, end)
            return 
                
        if active_coord in self.path:
            return self.path[active_coord]
        
        if active_coord not in self.path:
            start, end = self.nodify_maze(Custom_start=active_coord)
            self.path = self.build_tree(start, end)
            return self.path[active_coord]
        
    
    def nodify_maze(self, Custom_start=None, Tresor=None):
        self.node_matrix = dd(dict)
        m = np.array(self.maze)
        start = np.argwhere(m=='S')
        end = np.argwhere(m=='E')
        
        
        if Custom_start is not None:
            start = np.asarray(Custom_start)
            
        if Tresor is not None:
            end = np.asarray(Tresor)
            
        
        all_coordinates = np.dstack(np.where(m.T))
        all_coordinates = all_coordinates[0, :, :]
        

        
        # Wall matrix and heuristic matrix
        heuristic_matrix = np.linalg.norm(all_coordinates - end, axis=1)
        LONGUEUR = len(m)
        HAUTEUR = len(m[0])
        heuristic_matrix = np.reshape(heuristic_matrix, (HAUTEUR, LONGUEUR)).T      
        
        for i in range(len(m)):
            for j in range(len(m[0])):
                if m[i][j] == '1':
                    self.node_matrix[i][j] = Case(i, j, heuristic_matrix[i][j], wall=True)
                elif m[i][j] =='S':
                    self.node_matrix[i][j] = Case(i, j, heuristic_matrix[i][j],start=True)
                elif m[i][j] =='E':
                    self.node_matrix[i][j] = Case(i, j, heuristic_matrix[i][j],end=True)
                else:
                    self.node_matrix[i][j] = Case(i, j, heuristic_matrix[i][j],)
        
        
        return  np.squeeze(start), np.squeeze(end)
        
    def h(self, c1, c2):
        x1,y1=c1
        x2,y2=c2
        
        return np.sqrt(abs(x1-x2)**2 + abs(y1-y2)**2)
        
    def build_tree(self, S, E):
        LONGUEUR = len(self.node_matrix)
        HAUTEUR = len(self.node_matrix[0])
        
        open_nodes = []
        closed_nodes = []
        
        x, y = S[0],S[1]
        _x, _y = E[0],E[1]
        
        start = (x, y)
        end = (_x, _y)
        self.node_matrix[x][y].g = 0
        self.node_matrix[x][y].f = self.h(start,end)
        
        open_nodes = PriorityQueue()
        open_nodes.put((self.h(start,end),self.h(start,end),start))
        path={}
        
        while not open_nodes.empty():
            current_coord = open_nodes.get()[2]
            if current_coord==end:
                break
            for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                coord_x = current_coord[0]+d[0]
                coord_y = current_coord[1]+d[1]
                if coord_x in range(LONGUEUR) and coord_y in range(HAUTEUR):
                    current_node = self.node_matrix[current_coord[0]][current_coord[1]]
                    temp_node = self.node_matrix[coord_x][coord_y]
                    if temp_node.wall ==False:
                        if d==(0, 1):
                            child=(current_coord[0],current_coord[1]+1)
                        if d==(0, -1):
                            child=(current_coord[0],current_coord[1]-1)
                        if d==(-1, 0):
                            child=(current_coord[0]-1,current_coord[1])
                        if d==(1, 0):
                            child=(current_coord[0]+1,current_coord[1])

                        g_score=current_node.g+1
                        f_score=g_score+self.h(temp_node.position,end)

                        if f_score < temp_node.f:
                            temp_node.g= g_score
                            temp_node.f= f_score
                            open_nodes.put((f_score,self.h(child,end),child))
                            path[child]=current_coord
        finale_path={}
        cell=end
        while cell!=start:
            finale_path[path[cell]]=cell
            cell=path[cell]
        return finale_path
