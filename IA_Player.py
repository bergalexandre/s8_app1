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
        self.maze_tile_size_x, self.maze_tile_size_y = maze_tile_size
        self.fuzzy_controller = IA_FuzzyController(self.maze_tile_size_x)
        
        self.maze = maze.maze
        self.node_matrix = None
        start, end = self.nodify_maze()
        self.path = self.build_tree(start, end)
        
        # Pour trésor
        self.FIND_TREASURE = False
        m = np.array(self.maze)
        all_treasure = np.argwhere(m=='T')
        end = np.argwhere(m=='E')
        self.all_goals = np.vstack((all_treasure,end))
        

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

        distance_wall_x = [PERCEPTION_RADIUS*self.maze_tile_size_x]
        distance_wall_y = [PERCEPTION_RADIUS*self.maze_tile_size_y]

        player_x, player_y = player.get_center()
        player_w = player.get_size()[0]/2

        distance_wall_x += ([(wall.topleft[0] + wall.width - player_x)for wall in east_walls])
        distance_wall_x += ([(wall.topleft[0] - player_x)for wall in west_walls])
        distance_wall_y += ([(wall.topleft[1] + wall.height - player_y)for wall in north_walls])
        distance_wall_y += ([(wall.topleft[1] - player_y)for wall in south_walls])

        distance_wall_x = min(distance_wall_x, key=abs)
        distance_wall_y = min(distance_wall_y, key=abs)

        distance_obstacle_x = [PERCEPTION_RADIUS*self.maze_tile_size_x]
        distance_obstacle_y = [PERCEPTION_RADIUS*self.maze_tile_size_y]
        distance_obstacle_x += ([(obstacle.centerx - player_x)for obstacle in obstacles])
        distance_obstacle_y += ([(obstacle.centery - player_y)for obstacle in obstacles])

        distance_obstacle_x = min(distance_obstacle_x, key=abs)
        distance_obstacle_y = min(distance_obstacle_y, key=abs)

        wall_obstacle_x = [PERCEPTION_RADIUS*self.maze_tile_size_x]
        wall_obstacle_y = [PERCEPTION_RADIUS*self.maze_tile_size_y]

        if(direction == "UP"):
            wall_obstacle_x += ([(wall.centerx - (wall.width/2) - (player_x+player_w)) for wall in north_walls])
        
        if(direction == "DOWN"):
            wall_obstacle_x += ([(wall.centerx + (wall.width/2) - (player_x-player_w)) for wall in south_walls])

        if(direction == "LEFT"):
            wall_obstacle_y += ([(wall.centery - (wall.height/2) - (player_y+player_w)) for wall in east_walls])

        if(direction == "RIGHT"):
            wall_obstacle_y += ([(wall.centery + (wall.height/2) - (player_y-player_w)) for wall in west_walls])

        wall_obstacle_x = min(wall_obstacle_x, key=abs)
        wall_obstacle_y = min(wall_obstacle_y, key=abs)

        return (distance_wall_x, distance_wall_y), (distance_obstacle_x, distance_obstacle_y), (wall_obstacle_x, wall_obstacle_y)


    def getNextInstruction(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters, player, direction, show_debug_info):
        self.is_direction_free(walls, player, show_possible_direction=show_debug_info)

        distance_wall, distance_obstacle, wall_obstacle = self.getClosestPerception(walls, obstacles, items, monsters, player, direction) 

        match direction:
            case "UP":
                distance_obstacle = (distance_obstacle[0], PERCEPTION_RADIUS*self.maze_tile_size_x)
                wall_obstacle = (wall_obstacle[0], PERCEPTION_RADIUS*self.maze_tile_size_x)
            case "DOWN":
                distance_obstacle = (distance_obstacle[0], PERCEPTION_RADIUS*self.maze_tile_size_x)
                wall_obstacle = (wall_obstacle[0], PERCEPTION_RADIUS*self.maze_tile_size_x)
            case "LEFT":
                distance_obstacle = (PERCEPTION_RADIUS*self.maze_tile_size_x, distance_obstacle[1])
                wall_obstacle = (PERCEPTION_RADIUS*self.maze_tile_size_x, wall_obstacle[1])
            case "RIGHT":
                distance_obstacle = (PERCEPTION_RADIUS*self.maze_tile_size_x, distance_obstacle[1])
                wall_obstacle = (PERCEPTION_RADIUS*self.maze_tile_size_x, wall_obstacle[1])

        if(direction == "LEFT"  or direction == "RIGHT"):
            force_x = 0
        else:
            force_x = self.fuzzy_controller.get_direction(distance_wall[0], distance_obstacle[0], wall_obstacle[0])

        if(direction == "DOWN"  or direction == "UP"):
            force_y = 0
        else:
            force_y = self.fuzzy_controller.get_direction(distance_wall[1], distance_obstacle[1], wall_obstacle[1])

        if(show_debug_info):
            print(f"distance_wall={distance_wall}\ndistance_obstacle({distance_obstacle})\nforces({force_x}, {force_y})\n")

        #self.direction_courante = "south"
        commandes = []

        if force_x > 0.1:
            commandes.append("RIGHT")
        elif force_x < -0.1:
            commandes.append("LEFT")
        else:
            if(direction == "LEFT"  or direction == "RIGHT"):
                commandes.append(direction)
        #else:
        #    if(self.direction_courante == "east"):
        #        commandes.append("LEFT")
        #    elif(self.direction_courante == "west"):
        #        commandes.append("RIGHT")
        if force_y < -0.1:
            commandes.append("UP")
        elif force_y > 0.1:
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
