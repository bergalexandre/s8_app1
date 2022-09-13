import gym
import time
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import numpy as np
from Constants import PERCEPTION_RADIUS

class IA_FuzzyController_left_right:
    def __init__(self, maze_tile_size):
        #Le linspace contient des distances
        perception_distance = PERCEPTION_RADIUS*maze_tile_size

        wall_antecedent_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall_x')
        wall_antecedent_y = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall_y')

        obstacle_antecedent_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle_x')
        obstacle_antecedent_y = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle_y')

        greedy_antecedent_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'greedy_x')
        greedy_antecedent_y = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'greedy_y')

        movement_x_consequence = ctrl.Consequent(np.linspace(-1, 1, 1000), 'movement', defuzzify_method='centroid')
        movement_y_consequence = ctrl.Consequent(np.linspace(-1, 1, 1000), 'movement', defuzzify_method='centroid')

        #membership
        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.3, -perception_distance*0.15]
        proche_gauche = [-perception_distance*0.3, -perception_distance*0.15, 0, 0]
        wall_antecedent_x["loin_gauche"] = fuzz.trapmf(wall_antecedent_x.universe, loin_gauche)
        wall_antecedent_x["proche_gauche"] = fuzz.trapmf(wall_antecedent_x.universe, proche_gauche)
        wall_antecedent_x["proche_droite"] = fuzz.trapmf(wall_antecedent_x.universe, np.flip(np.abs(proche_gauche)))
        wall_antecedent_x["loin_droite"] = fuzz.trapmf(wall_antecedent_x.universe, np.flip(np.abs(loin_gauche)))

        obstacle_antecedent_x["loin_gauche"] = fuzz.trapmf(obstacle_antecedent_x.universe, loin_gauche)
        obstacle_antecedent_x["proche_gauche"] = fuzz.trapmf(obstacle_antecedent_x.universe, proche_gauche)
        obstacle_antecedent_x["proche_droite"] = fuzz.trapmf(obstacle_antecedent_x.universe, np.flip(np.abs(proche_gauche)))
        obstacle_antecedent_x["loin_droite"] = fuzz.trapmf(obstacle_antecedent_x.universe, np.flip(np.abs(loin_gauche)))

        wall_antecedent_y["loin_bas"] = fuzz.trapmf(wall_antecedent_y.universe, loin_gauche)
        wall_antecedent_y["proche_bas"] = fuzz.trapmf(wall_antecedent_y.universe, proche_gauche)
        wall_antecedent_y["proche_haut"] = fuzz.trapmf(wall_antecedent_y.universe, np.flip(np.abs(proche_gauche)))
        wall_antecedent_y["loin_haut"] = fuzz.trapmf(wall_antecedent_y.universe, np.flip(np.abs(loin_gauche)))

        obstacle_antecedent_y["loin_bas"] = fuzz.trapmf(obstacle_antecedent_y.universe, loin_gauche)
        obstacle_antecedent_y["proche_bas"] = fuzz.trapmf(obstacle_antecedent_y.universe, proche_gauche)
        obstacle_antecedent_y["proche_haut"] = fuzz.trapmf(obstacle_antecedent_y.universe, np.flip(np.abs(proche_gauche)))
        obstacle_antecedent_y["loin_haut"] = fuzz.trapmf(obstacle_antecedent_y.universe, np.flip(np.abs(loin_gauche)))

        movement_x_consequence['gauche'] = fuzz.trapmf(movement_x_consequence.universe, [-1, -1, -0.5 , -0.0])
        movement_x_consequence['milieu'] = fuzz.trimf(movement_x_consequence.universe, [-0.3,0,0.3])
        movement_x_consequence['droite'] = fuzz.trapmf(movement_x_consequence.universe, [0.0, 0.5, 1, 1])

        movement_y_consequence['bas'] = fuzz.trapmf(movement_y_consequence.universe, [-1, -1, -0.3 , 0])
        movement_y_consequence['milieu'] = fuzz.trimf(movement_y_consequence.universe, [-0.3,0,0.3])
        movement_y_consequence['haut'] = fuzz.trapmf(movement_y_consequence.universe, [0, 0.3, 1, 1])

        #rules
        rules = []
        rules.append(ctrl.Rule(antecedent=wall_antecedent_x['loin_gauche'], consequent=movement_x_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent_x['proche_gauche'], consequent=movement_x_consequence['droite']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent_x['proche_droite'], consequent=movement_x_consequence['gauche']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent_x['loin_droite'], consequent=movement_x_consequence['milieu']))

        rules.append(ctrl.Rule(antecedent=wall_antecedent_y['loin_bas'], consequent=movement_y_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent_y['proche_bas'], consequent=movement_y_consequence['droite']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent_y['proche_haut'], consequent=movement_y_consequence['gauche']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent_y['loin_haut'], consequent=movement_y_consequence['milieu']))

        rules.append(ctrl.Rule(antecedent=obstacle_antecedent_x['loin_gauche'], consequent=movement_x_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_gauche'], obstacle_antecedent_y['proche_bas']), consequent=movement_x_consequence['droite']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_gauche'], obstacle_antecedent_y['proche_haut']), consequent=movement_x_consequence['droite']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_gauche'], obstacle_antecedent_y['loin_bas']), consequent=movement_x_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_gauche'], obstacle_antecedent_y['loin_haut']), consequent=movement_x_consequence['milieu']))
        
        rules.append(ctrl.Rule(antecedent=obstacle_antecedent_x['loin_droite'], consequent=movement_x_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_droite'], obstacle_antecedent_y['proche_bas']), consequent=movement_x_consequence['gauche']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_droite'], obstacle_antecedent_y['proche_haut']), consequent=movement_x_consequence['gauche']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_droite'], obstacle_antecedent_y['loin_bas']), consequent=movement_x_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(obstacle_antecedent_x['proche_droite'], obstacle_antecedent_y['loin_haut']), consequent=movement_x_consequence['milieu']))

        rules.append(ctrl.Rule(antecedent=obstacle_antecedent_y['loin_bas'], consequent=movement_y_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=obstacle_antecedent_y['proche_bas'], consequent=movement_y_consequence['droite']))
        rules.append(ctrl.Rule(antecedent=obstacle_antecedent_y['proche_haut'], consequent=movement_y_consequence['gauche']))
        rules.append(ctrl.Rule(antecedent=obstacle_antecedent_y['loin_haut'], consequent=movement_y_consequence['milieu']))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(system)

        #self.show_fuzzy_controls()

    def show_fuzzy_controls(self):
        # Display fuzzy variables
        for var in self.sim.ctrl.fuzzy_variables:
            var.view()
        plt.show()

    def get_direction(self, wall, obstacle):
        self.sim.input['wall'] = wall
        self.sim.input['obstacle'] = obstacle

        self.sim.compute()

        return self.sim.output['movement']

class IA_FuzzyController_down_up:
    def __init__(self, maze_tile_size):
        #Le linspace contient des distances
        perception_distance = PERCEPTION_RADIUS * maze_tile_size

        wall_antecedent = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall')
        obstacle_antecedent = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle')
        greedy_antecedent = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'greedy')
        movement_consequence = ctrl.Consequent(np.linspace(-1, 1, 3), 'movement', defuzzify_method='centroid')

        #membership
        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.3, -perception_distance*0.15]
        proche_gauche = [-perception_distance*0.3, -perception_distance*0.15, 0, 0]
        

        #rules
        rules = []
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_bas'] & obstacle_antecedent['loin_bas']), consequent=movement_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_bas'] & obstacle_antecedent['loin_bas']), consequent=movement_consequence['haut']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_haut'] & obstacle_antecedent['loin_bas']), consequent=movement_consequence['bas']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_haut'] & obstacle_antecedent['loin_bas']), consequent=movement_consequence['milieu']))

        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_bas'] & obstacle_antecedent['proche_bas']), consequent=movement_consequence['haut']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_bas'] & obstacle_antecedent['proche_bas']), consequent=movement_consequence['haut']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_haut'] & obstacle_antecedent['proche_bas']), consequent=movement_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_haut'] & obstacle_antecedent['proche_bas']), consequent=movement_consequence['haut']))

        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_bas'] & obstacle_antecedent['proche_haut']), consequent=movement_consequence['bas']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_bas'] & obstacle_antecedent['proche_haut']), consequent=movement_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_haut'] & obstacle_antecedent['proche_haut']), consequent=movement_consequence['bas']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_haut'] & obstacle_antecedent['proche_haut']), consequent=movement_consequence['bas']))

        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_bas'] & obstacle_antecedent['loin_haut']), consequent=movement_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_bas'] & obstacle_antecedent['loin_haut']), consequent=movement_consequence['haut']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['proche_haut'] & obstacle_antecedent['loin_haut']), consequent=movement_consequence['bas']))
        rules.append(ctrl.Rule(antecedent=(wall_antecedent['loin_haut'] & obstacle_antecedent['loin_haut']), consequent=movement_consequence['milieu']))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(system)

        #self.show_fuzzy_controls()

    def show_fuzzy_controls(self):
        # Display fuzzy variables
        for var in self.sim.ctrl.fuzzy_variables:
            var.view()
        plt.show()
    
    def get_direction(self, wall, obstacle):
        self.sim.input['wall'] = wall
        self.sim.input['obstacle'] = obstacle

        self.sim.compute()

        return self.sim.output['movement']