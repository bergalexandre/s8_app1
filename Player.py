import pygame
import random
from Constants import *


class Player:
    x = 0
    y = 0

    def __init__(self):
        self.speed = 1
        self.size_x = 0
        self.size_y = 0
        self.attributes = [random.randrange(1, MAX_ATTRIBUTE) for i in range(NUM_ATTRIBUTES)]

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_attributes(self):
        return self.attributes

    def set_attributes(self, new_attributes):
        self.attributes = new_attributes

    def set_size(self, sizex, sizey):
        self.size_x = sizex
        self.size_y = sizey

    def get_size(self):
        return self.size_x, self.size_y

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size_x, self.size_y)

    def moveRight(self):
        self.x = self.x + self.speed

    def moveLeft(self):
        self.x = self.x - self.speed

    def moveUp(self):
        self.y = self.y - self.speed

    def moveDown(self):
        self.y = self.y + self.speed

