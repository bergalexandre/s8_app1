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
        perception_distance = maze_tile_size
        wall = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall')
        obstacle = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle')
        wall_obstacle = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'wall_obstacle')
        greediness = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'greedy_x')

        movement = ctrl.Consequent(np.linspace(-1, 1, 1000), 'movement', defuzzify_method='centroid')

        #membership
        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.5, -perception_distance*0.4]
        moyen_gauche = [-perception_distance*0.5, -perception_distance*0.34, -perception_distance*0.17, -perception_distance*0.15]
        proche_gauche = [-perception_distance*0.17, -perception_distance*0.15, 0, 0]

        wall["loin_gauche"] = fuzz.trapmf(wall.universe, loin_gauche)
        wall["moyen_gauche"] = fuzz.trapmf(wall.universe, moyen_gauche)
        wall["proche_gauche"] = fuzz.trapmf(wall.universe, proche_gauche)
        wall["proche_droite"] = fuzz.trapmf(wall.universe, [elem*-1 for elem in reversed(proche_gauche)])
        wall["moyen_droite"] = fuzz.trapmf(wall.universe, [elem*-1 for elem in reversed(moyen_gauche)])
        wall["loin_droite"] = fuzz.trapmf(wall.universe, [elem*-1 for elem in reversed(loin_gauche)])

        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.7, -perception_distance*0.4]
        proche_gauche = [-perception_distance*0.6, -perception_distance*0.5, 0, 0]

        wall_obstacle["loin_gauche"] = fuzz.trapmf(wall_obstacle.universe, loin_gauche)
        wall_obstacle["proche_gauche"] = fuzz.trapmf(wall_obstacle.universe, proche_gauche)
        wall_obstacle["proche_droite"] = fuzz.trapmf(wall_obstacle.universe, [elem*-1 for elem in reversed(proche_gauche)])
        wall_obstacle["loin_droite"] = fuzz.trapmf(wall_obstacle.universe, [elem*-1 for elem in reversed(loin_gauche)])

        #greediness["no_gold_gauche"] = fuzz.trapmf(greediness.universe, [-perception_distance])
        #greediness["gold"]
        #loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.25, -perception_distance*0.2]
        #moyen_gauche = [-perception_distance*0.25, -perception_distance*0.2, -perception_distance*0.16, -perception_distance*0.15]

        loin_gauche = [-perception_distance, -perception_distance, -perception_distance*0.35, -perception_distance*0.29]
        proche_gauche = [-perception_distance*0.3, -perception_distance*0.25, -perception_distance*0.1, -perception_distance*0.05]
        
        obstacle["loin_gauche"] = fuzz.trapmf(obstacle.universe, loin_gauche)
        #obstacle["moyen_gauche"] = fuzz.trapmf(obstacle.universe, moyen_gauche)
        obstacle["proche_gauche"] = fuzz.trapmf(obstacle.universe, proche_gauche)
        obstacle["milieu"] = fuzz.trapmf(obstacle.universe, [proche_gauche[-2], proche_gauche[-1], proche_gauche[-1]*-1, proche_gauche[-2]*-1])
        obstacle["proche_droite"] = fuzz.trapmf(obstacle.universe, [elem*-1 for elem in reversed(proche_gauche)])
        #obstacle["moyen_droite"] = fuzz.trapmf(obstacle.universe, [abs(elem) for elem in reversed(moyen_gauche)])
        obstacle["loin_droite"] = fuzz.trapmf(obstacle.universe, [elem*-1 for elem in reversed(loin_gauche)])

        movement["gauche"] = fuzz.trapmf(movement.universe, [-1, -1, -0.3 , -0.0])
        movement["milieu"] = fuzz.trimf(movement.universe, [-0.3,0,0.3])
        movement["droite"] = fuzz.trapmf(movement.universe, [0, 0.3, 1, 1])

        #pre-rule
        obstacle_loin = (obstacle["loin_gauche"] | obstacle["loin_droite"]) & (wall_obstacle["loin_gauche"] | wall_obstacle["loin_droite"])
        #rules
        rules = []

        rules.append(ctrl.Rule(antecedent=(wall["loin_gauche"] & obstacle_loin), consequent=movement["milieu"]))
        rules.append(ctrl.Rule(antecedent=(wall["loin_droite"] & obstacle_loin), consequent=movement["milieu"]))

        rules.append(ctrl.Rule(antecedent=(wall["moyen_gauche"] & obstacle_loin), consequent=movement["droite"]))
        rules.append(ctrl.Rule(antecedent=(wall["moyen_droite"] & obstacle_loin), consequent=movement["gauche"]))

        rules.append(ctrl.Rule(antecedent=(wall_obstacle["proche_droite"]), consequent=movement["gauche"]))
        rules.append(ctrl.Rule(antecedent=(wall_obstacle["proche_gauche"]), consequent=movement["droite"]))

        rules.append(ctrl.Rule(antecedent=(wall["proche_droite"]), consequent=movement["gauche"]))
        rules.append(ctrl.Rule(antecedent=(wall["proche_gauche"]), consequent=movement["droite"]))

        rules.append(ctrl.Rule(antecedent=(obstacle["proche_droite"] & (~wall["proche_gauche"] | ~wall["moyen_gauche"])), consequent=movement["gauche"]))
        rules.append(ctrl.Rule(antecedent=(obstacle["proche_gauche"] & (~wall["proche_droite"] | ~wall["moyen_droite"])), consequent=movement["droite"]))

        rules.append(ctrl.Rule(antecedent=((wall["loin_droite"] | wall["moyen_droite"]) & obstacle["milieu"]), consequent=movement["droite"], and_func=np.add))
        rules.append(ctrl.Rule(antecedent=((wall["loin_gauche"] | wall["moyen_gauche"]) & obstacle["milieu"]), consequent=movement["droite"], and_func=np.add))

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

    def get_direction(self, wall, obstacle, wall_obstacle):
        self.sim.input["wall"] = wall
        self.sim.input["obstacle"] = obstacle
        self.sim.input["wall_obstacle"] = wall_obstacle
        #self.sim.input["obstacle_opp"] = obstacle_opp

        self.sim.compute()
        
        return self.sim.output["movement"]