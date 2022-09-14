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
        perception_distance = PERCEPTION_RADIUS*maze_tile_size + 1
        wall = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall')
        obstacle = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle')
        obstacle_opp = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle_opp')
        greedy_antecedent_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'greedy_x')

        movement = ctrl.Consequent(np.linspace(-1, 1, 1000), 'movement', defuzzify_method='centroid')

        #membership
        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.4, -perception_distance*0.2]
        moyen_gauche = [-perception_distance*0.4, -perception_distance*0.2, -perception_distance*0.11, -perception_distance*0.1]
        proche_gauche = [-perception_distance*0.11, -perception_distance*0.1, 0, 0]

        wall["loin_gauche"] = fuzz.trapmf(wall.universe, loin_gauche)
        wall["moyen_gauche"] = fuzz.trapmf(wall.universe, moyen_gauche)
        wall["proche_gauche"] = fuzz.trapmf(wall.universe, proche_gauche)
        wall["proche_droite"] = fuzz.trapmf(wall.universe, [abs(elem) for elem in reversed(proche_gauche)])
        wall["moyen_droite"] = fuzz.trapmf(wall.universe, [abs(elem) for elem in reversed(moyen_gauche)])
        wall["loin_droite"] = fuzz.trapmf(wall.universe, [abs(elem) for elem in reversed(loin_gauche)])

        #loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.25, -perception_distance*0.2]
        #moyen_gauche = [-perception_distance*0.25, -perception_distance*0.2, -perception_distance*0.16, -perception_distance*0.15]

        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.4, -perception_distance*0.2]
        proche_gauche = [-perception_distance*0.5, -perception_distance*0.15, 0, 0]
        
        obstacle["loin_gauche"] = fuzz.trapmf(obstacle.universe, loin_gauche)
        #obstacle["moyen_gauche"] = fuzz.trapmf(obstacle.universe, moyen_gauche)
        obstacle["proche_gauche"] = fuzz.trapmf(obstacle.universe, proche_gauche)
        obstacle["proche_droite"] = fuzz.trapmf(obstacle.universe, [abs(elem) for elem in reversed(proche_gauche)])
        #obstacle["moyen_droite"] = fuzz.trapmf(obstacle.universe, [abs(elem) for elem in reversed(moyen_gauche)])
        obstacle["loin_droite"] = fuzz.trapmf(obstacle.universe, [abs(elem) for elem in reversed(loin_gauche)])

        loin_bas = [-perception_distance, -perception_distance, -perception_distance*0.3, -perception_distance*0.15]
        proche_bas = [-perception_distance*0.3, -perception_distance*0.15, 0, 0]
        obstacle_opp["loin_bas"] = fuzz.trapmf(obstacle_opp.universe, loin_bas)
        obstacle_opp["proche_bas"] = fuzz.trapmf(obstacle_opp.universe, proche_bas)
        obstacle_opp["proche_haut"] = fuzz.trapmf(obstacle_opp.universe, [abs(elem) for elem in reversed(loin_bas)])
        obstacle_opp["loin_haut"] = fuzz.trapmf(obstacle_opp.universe, [abs(elem) for elem in reversed(proche_bas)])

        movement["gauche"] = fuzz.trapmf(movement.universe, [-1, -1, -0.3 , -0.0])
        movement["milieu"] = fuzz.trimf(movement.universe, [-0.3,0,0.3])
        movement["droite"] = fuzz.trapmf(movement.universe, [0, 0.3, 1, 1])

        #pre-rule
        obstacle_loin = (obstacle["loin_gauche"] | obstacle["loin_droite"])

        #rules
        rules = []
        rules.append(ctrl.Rule(antecedent=wall["proche_gauche"] | obstacle["proche_gauche"], consequent=movement["droite"]))
        rules.append(ctrl.Rule(antecedent=wall["proche_droite"] | obstacle["proche_droite"], consequent=movement["gauche"]))

        rules.append(ctrl.Rule(antecedent=(wall["loin_gauche"] | obstacle_loin), consequent=movement["milieu"]))
        rules.append(ctrl.Rule(antecedent=(wall["loin_droite"] | obstacle_loin), consequent=movement["milieu"]))

        rules.append(ctrl.Rule(antecedent=(wall["moyen_gauche"] & ~obstacle["proche_droite"]), consequent=movement["droite"]))
        rules.append(ctrl.Rule(antecedent=(wall["moyen_droite"] & ~obstacle["proche_gauche"]), consequent=movement["gauche"]))
        #rules.append(ctrl.Rule(antecedent=(obstacle["proche_gauche"] & obstacle_opp["loin_bas"]), consequent=movement["milieu"]))
        #rules.append(ctrl.Rule(antecedent=(obstacle["proche_droite"] & obstacle_opp["loin_haut"]), consequent=movement["milieu"]))

        #rules.append(ctrl.Rule(antecedent=obstacle["loin_gauche"], consequent=movement["milieu"]))
        #rules.append(ctrl.Rule(antecedent=obstacle["loin_droite"], consequent=movement["milieu"])

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(system)

       # self.show_fuzzy_controls()

    def show_fuzzy_controls(self):
        # Display fuzzy variables
        for var in self.sim.ctrl.fuzzy_variables:
            var.view()
        plt.show()

    def get_direction(self, wall, obstacle):
        self.sim.input["wall"] = wall
        self.sim.input["obstacle"] = obstacle
        #self.sim.input["obstacle_opp"] = obstacle_opp

        self.sim.compute()

        return self.sim.output["movement"]