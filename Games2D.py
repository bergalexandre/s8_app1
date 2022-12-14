from pygame.locals import *
import pygame

from Player import *
from Maze import *
from Constants import *
from IA_Player import *
from genetic import Genetic, bin2ufloat

class App:
    windowWidth = WIDTH
    windowHeight = HEIGHT
    player = 0

    def __init__(self, mazefile):
        self._running = True
        self._win = False
        self._dead = False
        self._display_surf = None
        self._image_surf = None
        self._block_surf = None
        self._clock = None
        self.level = 0
        self.score = 0
        self.timer = 0.0
        self.player = Player()
        self.maze = Maze(mazefile)
        self.genetic = Genetic(NUM_ATTRIBUTES, 1000, 11)
        self.genetic.set_crossover_modulo(np.array([0,0,1,0,0,1,1,1,1,0,0]))
        self.genetic.set_sim_parameters(10, 0.11, 0.8, 0.1)

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._clock = pygame.time.Clock()
        pygame.display.set_caption("Dungeon Crawler")
        pygame.time.set_timer(pygame.USEREVENT, 10)
        self._running = True
        self.maze.make_maze_wall_list()
        self.maze.make_maze_item_lists()
        self._image_surf = pygame.image.load("assets/kickboxeuse.png")
        self.player.set_position(self.maze.start[0], self.maze.start[1])
        self.player.set_size(PLAYER_SIZE*self.maze.tile_size_x, PLAYER_SIZE*self.maze.tile_size_x)
        self._image_surf = pygame.transform.scale(self._image_surf, self.player.get_size())
        self._block_surf = pygame.image.load("assets/wall.png")
        self.ia_player = IA_Player((self.maze.tile_size_x, self.maze.tile_size_y), self.maze)

    def genetic_loop(self):
        for _ in range(self.genetic.num_generations):
            population_fitness = []
            population_win = []
            for individu in self.genetic.decode_individuals():
                number_of_wins = 0
                fitness = 0
                for monster in self.maze.monsterList:
                    self.player.set_attributes(individu)
                    fight = monster.mock_fight(self.player)[0]
                    number_of_wins += fight
                    fitness += 10**fight if fight > 0 else 0
                
                population_fitness.append(fitness)
                population_win.append(number_of_wins)

            self.genetic.fitness = np.array(population_fitness)
            self.genetic.eval_fit()

            print(f"generation {self.genetic.current_gen}:")
            print(f"\tbest fitness: {max(population_win)}")
            print(f"\tavg fitness: {np.sum(population_win)/1000}")

            self.genetic.new_gen()
        self.player.set_attributes(bin2ufloat(np.reshape(self.genetic.bestIndividual, (NUM_ATTRIBUTES, -1)), 11))

    def on_keyboard_input(self, keys):
        if keys[K_RIGHT] or keys[K_d]:
            self.move_player_right()

        if keys[K_LEFT] or keys[K_a]:
            self.move_player_left()

        if keys[K_UP] or keys[K_w]:
            self.move_player_up()

        if keys[K_DOWN] or keys[K_s]:
            self.move_player_down()

        # Utility functions for AI
        if keys[K_p]:
            self.maze.make_perception_list(self.player, self._display_surf)
            # returns a list of 4 lists of pygame.rect inside the perception radius
            # the 4 lists are [wall_list, obstacle_list, item_list, monster_list]
            # item_list includes coins and treasure

        if keys[K_m]:
            for monster in self.maze.monsterList:
                print(monster.mock_fight(self.player))
            # returns the number of rounds you win against the monster
            # you need to win all four rounds to beat it

        if (keys[K_ESCAPE]):
            self._running = False

    # FONCTION ?? Ajuster selon votre format d'instruction
    def on_AI_input(self, instruction):
        if 'RIGHT' in instruction:
            self.move_player_right()

        if 'LEFT' in instruction:
            self.move_player_left()

        if "UP" in instruction:
            self.move_player_up()

        if "DOWN" in instruction:
            self.move_player_down()

    def move_player_right(self):
        self.player.moveRight()
        if self.on_wall_collision() or self.on_obstacle_collision():
            self.player.moveLeft()

    def move_player_left(self):
        self.player.moveLeft()
        if self.on_wall_collision() or self.on_obstacle_collision():
            self.player.moveRight()

    def move_player_up(self):
        self.player.moveUp()
        if self.on_wall_collision() or self.on_obstacle_collision():
            self.player.moveDown()

    def move_player_down(self):
        self.player.moveDown()
        if self.on_wall_collision() or self.on_obstacle_collision():
            self.player.moveUp()

    def on_wall_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.wallList)
        if not collide_index == -1:
            # print("Collision Detected!")
            return True
        return False

    def on_obstacle_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.obstacleList)
        if not collide_index == -1:
            # print("Collision Detected!")
            return True
        return False

    def on_coin_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.coinList)
        if not collide_index == -1:
            self.maze.coinList.pop(collide_index)
            return True
        else:
            return False

    def on_treasure_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.treasureList)
        if not collide_index == -1:
            self.maze.treasureList.pop(collide_index)
            return True
        else:
            return False

    def on_monster_collision(self):
        for monster in self.maze.monsterList:
            if self.player.get_rect().colliderect(monster.rect):
                return monster
        return False

    def on_exit(self):
        return self.player.get_rect().colliderect(self.maze.exit)

    def maze_render(self):
        self._display_surf.fill((0, 0, 0))
        self.maze.draw(self._display_surf, self._block_surf)
        font = pygame.font.SysFont(None, 32)
        text = font.render("Coins: " + str(self.score), True, BLACK)
        self._display_surf.blit(text, (WIDTH - 120, 10))
        text = font.render("Time: " + format(self.timer, ".2f"), True, BLACK)
        self._display_surf.blit(text, (WIDTH - 300, 10))

    def on_render(self):
        self.maze_render()
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        pygame.display.flip()

    def on_win_render(self):
        self.maze_render()
        font = pygame.font.SysFont(None, 120)
        text = font.render("CONGRATULATIONS!", True, GREEN)
        self._display_surf.blit(text, (0.1 * self.windowWidth, 0.4 * self.windowHeight))
        pygame.display.flip()

    def on_death_render(self):
        self.maze_render()
        font = pygame.font.SysFont(None, 120)
        text = font.render("YOU DIED!", True, RED)
        self._display_surf.blit(text, (0.1 * self.windowWidth, 0.4 * self.windowHeight))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.on_init()
        self.genetic_loop()

        direction = None

        while self._running:
            self._clock.tick(GAME_CLOCK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.USEREVENT:
                    self.timer += 0.01
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if(keys[K_p]):
                print(self.player.get_position())

            perceptions = self.maze.make_perception_list(self.player, keys[K_p])
            direction = self.ia_player.getDirection(self.player, perceptions[0]) or direction
            instruction = self.ia_player.getNextInstruction(*perceptions, self.player, direction, keys[K_p])
            if(keys[K_q]):
                self.on_keyboard_input(keys)
            else:
                self.on_AI_input(instruction)
            
            if self.on_coin_collision():
                self.score += 1
            if self.on_treasure_collision():
                self.score += 10
                self.ia_player.FIND_TREASURE = False
            monster = self.on_monster_collision()
            if monster:
                if monster.fight(self.player):
                    self.maze.monsterList.remove(monster)
                else:
                    self._running = False
                    self._dead = True
            if self.on_exit():
                self._running = False
                self._win = True
            self.on_render()

        while self._win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._win = False
            self.on_win_render()

        while self._dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._dead = False
            self.on_death_render()

        self.on_cleanup()
