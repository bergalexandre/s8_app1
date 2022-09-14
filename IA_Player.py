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
        self.fuzzy_controller = IA_FuzzyController(maze_tile_size)
        self.maze_tile_size = maze_tile_size
        
        self.maze = maze.maze
        self.node_matrix = None
        start_x, start_y, end_x, end_y = self.nodify_maze()
        self.path = self.build_tree(start_x, start_y, end_x, end_y)
        print("")
        

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
                
        direction =self.getDirection(player) # Algo A star
        
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
    
    def getDirection(self, player):
        current_position = [*player.get_position()]
        active_coord = (int(np.floor(current_position[1]/50)), int(np.floor(current_position[0]/50)))
        next_coord = self.path[active_coord]
        delta=np.asarray(next_coord) - np.asarray(active_coord)
        if (delta ==[1.0, 0.0]).all():
                direction= "DOWN"
        elif (delta ==[-1.0, 0.0]).all():
                direction= "up"
        elif (delta ==[0.0, 1.0]).all():
                direction= "LEFT"
        elif (delta ==[0.0, -1.0]).all():
                direction= "RIGHT"
                      
        return direction
        
    
    def nodify_maze(self):
        self.node_matrix = dd(dict)
        m = np.array(self.maze)
        start = np.where(m=='S')
        end = np.where(m=='E')
        
        all_coordinates = np.dstack(np.where(m.T))
        all_coordinates = all_coordinates[0, :, :]
        
        # Coordinates of start and end in a numpy array
        self.start = np.concatenate((start[0], start[1]), axis=0)
        #self.start = np.hstack(start)
        self.end = np.concatenate((end[1], end[0]), axis=0)
        #self.end = np.hstack(end)
        
        # Wall matrix and heuristic matrix
        heuristic_matrix = np.linalg.norm(all_coordinates - self.end, axis=1)
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
        
        start_x , start_y = self.start
        end_y , end_x = self.end
        
        return start_x , start_y, end_x, end_y
        
    def h(self, c1, c2):
        x1,y1=c1
        x2,y2=c2
        
        return np.sqrt(abs(x1-x2)**2 + abs(y1-y2)**2)
        
    def build_tree(self, x, y, _x, _y):
        LONGUEUR = len(self.node_matrix)
        HAUTEUR = len(self.node_matrix[0])
        
        open_nodes = []
        closed_nodes = []
        start = (x,y)
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
