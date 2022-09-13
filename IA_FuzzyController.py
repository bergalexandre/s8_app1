import gym
import time
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import numpy as np
from Constants import PERCEPTION_RADIUS

class IA_FuzzyController:
    def __init__(self, maze_tile_size):
        #Le linspace contient des distances
        perception_distance = PERCEPTION_RADIUS*maze_tile_size

        wall_antecedent = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall')

        obstacle_antecedent = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle')
        obstacle_opp_antecedent = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle_opp')

        greedy_antecedent_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'greedy_x')

        movement_consequence = ctrl.Consequent(np.linspace(-1, 1, 1000), 'movement', defuzzify_method='centroid')

        #membership
        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.3, -perception_distance*0.15]
        proche_gauche = [-perception_distance*0.3, -perception_distance*0.15, 0, 0]
        wall_antecedent["loin_gauche"] = fuzz.trapmf(wall_antecedent.universe, loin_gauche)
        wall_antecedent["proche_gauche"] = fuzz.trapmf(wall_antecedent.universe, proche_gauche)
        wall_antecedent["proche_droite"] = fuzz.trapmf(wall_antecedent.universe, np.flip(np.abs(proche_gauche)))
        wall_antecedent["loin_droite"] = fuzz.trapmf(wall_antecedent.universe, np.flip(np.abs(loin_gauche)))

        #obstacle_antecedent["loin_gauche"] = fuzz.trapmf(obstacle_antecedent.universe, loin_gauche)
        #obstacle_antecedent["proche_gauche"] = fuzz.trapmf(obstacle_antecedent.universe, proche_gauche)
        #obstacle_antecedent["proche_droite"] = fuzz.trapmf(obstacle_antecedent.universe, np.flip(np.abs(proche_gauche)))
        #obstacle_antecedent["loin_droite"] = fuzz.trapmf(obstacle_antecedent.universe, np.flip(np.abs(loin_gauche)))

        #obstacle_opp_antecedent["loin_bas"] = fuzz.trapmf(obstacle_opp_antecedent.universe, loin_gauche)
        #obstacle_opp_antecedent["proche_bas"] = fuzz.trapmf(obstacle_opp_antecedent.universe, proche_gauche)
        #obstacle_opp_antecedent["proche_haut"] = fuzz.trapmf(obstacle_opp_antecedent.universe, np.flip(np.abs(proche_gauche)))
        #obstacle_opp_antecedent["loin_haut"] = fuzz.trapmf(obstacle_opp_antecedent.universe, np.flip(np.abs(loin_gauche)))

        movement_consequence['gauche'] = fuzz.trapmf(movement_consequence.universe, [-1, -1, -0.3 , -0.0])
        movement_consequence['milieu'] = fuzz.trimf(movement_consequence.universe, [-0.3,0,0.3])
        movement_consequence['droite'] = fuzz.trapmf(movement_consequence.universe, [0.0, 0.3, 1, 1])

        #rules
        rules = []
        rules.append(ctrl.Rule(antecedent=wall_antecedent['loin_gauche'], consequent=movement_consequence['milieu']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent['proche_gauche'], consequent=movement_consequence['droite']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent['proche_droite'], consequent=movement_consequence['gauche']))
        rules.append(ctrl.Rule(antecedent=wall_antecedent['loin_droite'], consequent=movement_consequence['milieu']))

        #rules.append(ctrl.Rule(antecedent=obstacle_antecedent['loin_gauche'], consequent=movement_consequence['milieu']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_gauche'] & obstacle_opp_antecedent['proche_bas']), consequent=movement_consequence['droite']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_gauche'] & obstacle_opp_antecedent['proche_haut']), consequent=movement_consequence['droite']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_gauche'] & obstacle_opp_antecedent['loin_bas']), consequent=movement_consequence['milieu']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_gauche'] & obstacle_opp_antecedent['loin_haut']), consequent=movement_consequence['milieu']))

        #rules.append(ctrl.Rule(antecedent=obstacle_antecedent['loin_droite'], consequent=movement_consequence['milieu']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_droite'] & obstacle_opp_antecedent['proche_bas']), consequent=movement_consequence['gauche']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_droite'] & obstacle_opp_antecedent['proche_haut']), consequent=movement_consequence['gauche']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_droite'] & obstacle_opp_antecedent['loin_bas']), consequent=movement_consequence['milieu']))
        #rules.append(ctrl.Rule(antecedent=(obstacle_antecedent['proche_droite'] & obstacle_opp_antecedent['loin_haut']), consequent=movement_consequence['milieu']))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(system)

        self.show_fuzzy_controls()

    def show_fuzzy_controls(self):
        # Display fuzzy variables
        for var in self.sim.ctrl.fuzzy_variables:
            var.view()
        plt.show()

    def get_direction(self, wall, obstacle, obstacle_opp):
        self.sim.input['wall'] = wall
        #self.sim.input['obstacle'] = obstacle
        #self.sim.input['obstacle_opp'] = obstacle_opp

        self.sim.compute()

        return self.sim.output['movement']