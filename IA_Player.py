
import pygame

class IA_Player:
    def getNextInstruction(self, walls: list[pygame.Rect], obstacles: list[pygame.Rect], items: list[pygame.Rect], monsters: list[pygame.Rect]):
        if(len(obstacles) > 0):
            return "UP"
        return "DOWN"
