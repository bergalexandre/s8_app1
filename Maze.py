import random
import pygame
import csv
from Monster import *
from Constants import *


class Maze:
    def __init__(self, mazefile):
        self.tile_size_x = 0
        self.tile_size_y = 0
        self.maze = []
        with open(mazefile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self.maze.append(row)
        self.N = len(self.maze)
        self.M = len(self.maze[0])
        self.wallList = []
        self.coinList = []
        self.treasureList = []
        self.obstacleList = []
        self.monsterList = []
        self.exit = []
        self.start = []
        self.tile_size_x = WIDTH/self.M
        self.tile_size_y = HEIGHT / self.N
        self._coin_surf = pygame.image.load("assets/coin.png")
        self._coin_surf = pygame.transform.scale(self._coin_surf, (ITEM_SIZE*self.tile_size_x, ITEM_SIZE*self.tile_size_y))
        self._treasure_surf = pygame.image.load("assets/treasure.png")
        self._treasure_surf = pygame.transform.scale(self._treasure_surf,
                                                 (2*ITEM_SIZE * self.tile_size_x, 2*ITEM_SIZE * self.tile_size_y))
        self._monster_surf = pygame.image.load("assets/monster1.png")
        self._monster_surf = pygame.transform.scale(self._monster_surf, (self.tile_size_x, self.tile_size_y))

    def random_position(self, i, j):
        x = (j + random.uniform(0, 1 - ITEM_SIZE)) * self.tile_size_x
        y = (i + random.uniform(0, 1 - ITEM_SIZE)) * self.tile_size_y
        return x, y

    def make_maze_wall_list(self):
        # Start tile wall
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == '1':
                    cell = pygame.Rect((j * self.tile_size_x, i * self.tile_size_y), (self.tile_size_x, self.tile_size_y))
                    self.wallList.append(cell)
                elif self.maze[i][j] == 'S':
                    print([i,j])
                    # Add conditions for starts not at top.
                    self.start = [(j + 0.2) * self.tile_size_x, (i + 0.2) * self.tile_size_y]
                    cell = pygame.Rect((j * self.tile_size_x, i * self.tile_size_y),
                                       (self.tile_size_x, 0.1 * self.tile_size_y))
                    self.wallList.append(cell)

    def make_maze_item_lists(self):
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == COIN:
                    new_coin = pygame.Rect((self.random_position(i, j)),
                                           (ITEM_SIZE*self.tile_size_x, ITEM_SIZE*self.tile_size_y))
                    self.coinList.append(new_coin)
                elif self.maze[i][j] == TREASURE:
                    new_treasure = pygame.Rect((self.random_position(i, j)), (ITEM_SIZE*self.tile_size_x, ITEM_SIZE*self.tile_size_y))
                    self.treasureList.append(new_treasure)
                elif self.maze[i][j] == OBSTACLE:
                    new_obstacle = pygame.Rect((self.random_position(i, j)), (ITEM_SIZE*self.tile_size_x, ITEM_SIZE*self.tile_size_y))
                    self.obstacleList.append(new_obstacle)
                elif self.maze[i][j] == MONSTER:
                    new_monster = pygame.Rect((j * self.tile_size_x, i * self.tile_size_y), (self.tile_size_x, self.tile_size_y))
                    self.monsterList.append(Monster(new_monster))
                elif self.maze[i][j] == EXIT:
                    self.exit = pygame.Rect((j * self.tile_size_x, i * self.tile_size_y), (self.tile_size_x, self.tile_size_y))

    def draw(self, display_surf, image_surf):
        image_surf = pygame.transform.scale(image_surf, (self.tile_size_x, self.tile_size_y))
        thinwall_surf = pygame.transform.scale(image_surf, (self.tile_size_x, 0.1 * self.tile_size_y))
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                if self.maze[i][j] == '1':
                    display_surf.blit(image_surf, (j * self.tile_size_x, i * self.tile_size_y))
                elif self.maze[i][j] == 'S':
                    pygame.draw.rect(display_surf, BLUE,
                                     (j * self.tile_size_x, i * self.tile_size_y, self.tile_size_x, self.tile_size_y))
                    display_surf.blit(thinwall_surf, (j * self.tile_size_x, i * self.tile_size_y))
                elif self.maze[i][j] == 'E':
                    pygame.draw.rect(display_surf, GREEN,
                                     (j * self.tile_size_x, i * self.tile_size_y, self.tile_size_x, self.tile_size_y))
                    display_surf.blit(thinwall_surf, (j * self.tile_size_x, (i+0.9) * self.tile_size_y))

        for item in self.coinList:
            display_surf.blit(self._coin_surf, item.topleft)

        for item in self.treasureList:
            display_surf.blit(self._treasure_surf, item.topleft)

        for item in self.obstacleList:
            pygame.draw.rect(display_surf, RED, item)

        for item in self.monsterList:
            display_surf.blit(self._monster_surf, item.rect.topleft)

    def make_perception_list(self, player_current, display_surf):
        perception_distance = PERCEPTION_RADIUS * max(self.tile_size_x, self.tile_size_y)
        perception_left = player_current.x + 0.5 * (player_current.size_x - perception_distance)
        perception_top = player_current.y + 0.5 * (player_current.size_y - perception_distance)
        perception_rect = pygame.Rect(perception_left, perception_top, perception_distance, perception_distance)
        wall_list = []
        obstacle_list = []
        item_list = []
        monster_list = []
        for i in perception_rect.collidelistall(self.wallList):
            wall_list.append(self.wallList[i])
        for i in perception_rect.collidelistall(self.obstacleList):
            obstacle_list.append(self.obstacleList[i])
        for i in perception_rect.collidelistall(self.coinList):
            item_list.append(self.coinList[i])
        for i in perception_rect.collidelistall(self.treasureList):
            item_list.append(self.treasureList[i])

        # POUR DEBUG - tenir la touche "p" pour voir la zone de perception
        #pygame.draw.rect(display_surf, GREEN, perception_rect)
        pygame.display.flip()
        print([wall_list, obstacle_list, item_list, monster_list])
        return [wall_list, obstacle_list, item_list, monster_list]
