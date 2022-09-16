import gym
import time
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import numpy as np
from Constants import PERCEPTION_RADIUS

class IA_FuzzyController2:
    def __init__(self, maze_tile_size):
        #Le linspace contient des distances
        perception_distance = maze_tile_size
        wall_x = ctrl.Antecedent(np.linspace(-10, perception_distance, 1000), 'wall_x')
        wall_y = ctrl.Antecedent(np.linspace(-10, perception_distance, 1000), 'wall_y')
        wall_opp_x = ctrl.Antecedent(np.linspace(-10, perception_distance, 1000), 'wall_opp_x')
        wall_opp_y = ctrl.Antecedent(np.linspace(-10, perception_distance, 1000), 'wall_opp_y')
        obstacle_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle_x')
        obstacle_y = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'obstacle_y')
        bloqueur_consigne_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'bloqueur_consigne_x')
        bloqueur_consigne_y = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'bloqueur_consigne_y')
        tresor_x = ctrl.Antecedent(np.linspace(-perception_distance, perception_distance, 1000), 'tresor_x')

        greediness = ctrl.Antecedent(np.linspace(0, perception_distance, 1000), 'greedy_x')

        consigne = ctrl.Antecedent(np.linspace(-1, 1, 3), 'consigne')

        movement = ctrl.Consequent(np.linspace(-1, 1, 1000), 'movement', defuzzify_method='centroid')

        #membership
        wall_x["loin"] = fuzz.trapmf(wall_x.universe, (perception_distance*0.4, perception_distance*0.6, perception_distance, perception_distance))
        wall_x["moyen"] = fuzz.trapmf(wall_x.universe, [perception_distance*0.15, perception_distance*0.17, perception_distance*0.45, perception_distance*0.6])
        wall_x["proche"] = fuzz.trapmf(wall_x.universe, [-10, -10, perception_distance*0.15, perception_distance*0.17])
        wall_y["loin"] = fuzz.trapmf(wall_y.universe, (perception_distance*0.7, perception_distance*0.8, perception_distance, perception_distance))
        wall_y["proche"] = fuzz.trapmf(wall_y.universe, [-10, -10, perception_distance*0.7, perception_distance*0.8])
        
        wall_opp_x["loin"] = fuzz.trapmf(wall_opp_x.universe, (perception_distance*0.4, perception_distance*0.6, perception_distance, perception_distance))
        wall_opp_x["moyen"] = fuzz.trapmf(wall_opp_x.universe, [perception_distance*0.15, perception_distance*0.17, perception_distance*0.45, perception_distance*0.6])
        wall_opp_x["proche"] = fuzz.trapmf(wall_opp_x.universe, [-10, -10, perception_distance*0.15, perception_distance*0.17])
        wall_opp_y["loin"] = fuzz.trapmf(wall_opp_y.universe, (perception_distance*0.7, perception_distance*0.8, perception_distance, perception_distance))
        wall_opp_y["proche"] = fuzz.trapmf(wall_opp_y.universe, [-10, -10, perception_distance*0.7, perception_distance*0.8])

        obstacle_x["loin_g"] = fuzz.trapmf(obstacle_x.universe, [-perception_distance, -perception_distance, -perception_distance*0.35, -perception_distance*0.29])
        obstacle_x["proche_g"] = fuzz.trapmf(obstacle_x.universe, [-perception_distance*0.4, -perception_distance*0.3, 0, 0,])
        obstacle_x["proche_d"] = fuzz.trapmf(obstacle_x.universe, [0, 0, perception_distance*0.3, perception_distance*0.4])
        obstacle_x["loin_d"] = fuzz.trapmf(obstacle_x.universe, [perception_distance*0.29, perception_distance*0.35, perception_distance, perception_distance])

        #obstacle_x["loin_opp"] = fuzz.trapmf(obstacle_x.universe, [-perception_distance, -perception_distance, -perception_distance*0.3, 0])
        obstacle_y["loin_g"] = fuzz.trapmf(obstacle_y.universe, [-perception_distance, -perception_distance, -perception_distance*0.5, -perception_distance*0.4])
        obstacle_y["proche_g"] = fuzz.trapmf(obstacle_y.universe, [-perception_distance*0.5, -perception_distance*0.4, 0, 0,])
        obstacle_y["proche_d"] = fuzz.trapmf(obstacle_y.universe, [0, 0, perception_distance*0.4, perception_distance*0.5])
        obstacle_y["loin_d"] = fuzz.trapmf(obstacle_y.universe, [perception_distance*0.4, perception_distance*0.5, perception_distance, perception_distance])
        #obstacle_y["loin_opp"] = fuzz.trapmf(obstacle_y.universe, [-perception_distance, -perception_distance, -perception_distance*0.3, 0])

        tresor_x["aucun_g"] = fuzz.trapmf(obstacle_y.universe, [-perception_distance, -perception_distance, -perception_distance*0.99, -perception_distance*0.98])
        tresor_x["loin_g"] = fuzz.trapmf(obstacle_y.universe, [-perception_distance*0.99, -perception_distance*0.98, -perception_distance*0.15, -perception_distance*0.10])
        tresor_x["dessus"] = fuzz.trapmf(obstacle_y.universe, [-perception_distance*0.15, -perception_distance*0.1, perception_distance*0.1, perception_distance*0.15])
        tresor_x["loin_d"] = fuzz.trapmf(obstacle_y.universe, [perception_distance*0.1, perception_distance*0.15, perception_distance*0.98, perception_distance*0.99])
        tresor_x["aucun_d"] = fuzz.trapmf(obstacle_y.universe, [perception_distance*0.98, perception_distance*0.99, perception_distance, perception_distance])

        #obstacle ou mur proche dans la direction de la consigne
        bloqueur_consigne_x["libre"] = fuzz.trapmf(bloqueur_consigne_x.universe, [perception_distance*0.25, perception_distance*0.35, perception_distance, perception_distance])
        bloqueur_consigne_x["obstruction"] = fuzz.trapmf(bloqueur_consigne_x.universe, [-perception_distance, -perception_distance, perception_distance*0.17, perception_distance*0.3])
        bloqueur_consigne_y["libre"] = fuzz.trapmf(bloqueur_consigne_y.universe, [perception_distance*0.25, perception_distance*0.35, perception_distance, perception_distance])
        bloqueur_consigne_y["obstruction"] = fuzz.trapmf(bloqueur_consigne_y.universe, [-perception_distance, -perception_distance, perception_distance*0.17, perception_distance*0.3])

        consigne["active"] = fuzz.trapmf(consigne.universe, [0.4, 0.5, 1.0, 1.0])
        consigne["inactive"] = fuzz.trapmf(consigne.universe, [0, 0, 0.2, 0.44])
        consigne["inverse"] = fuzz.trapmf(consigne.universe, [-1, -1, -0.5, -0.4])

        movement["recule"] = fuzz.trapmf(movement.universe, [-1, -1, -0.4, -0.2])
        movement["reste"] = fuzz.trapmf(movement.universe, [-0.4, -0.2, 0.2, 0.4])
        movement["avance"] = fuzz.trapmf(movement.universe, [0.2, 0.4, 1, 1])
        
        #rules
        rules = []

        rules.append(ctrl.Rule(consigne["active"] & (tresor_x["dessus"] | tresor_x["aucun_g"] | tresor_x["aucun_d"]), consequent=movement["avance"]%2))
        rules.append(ctrl.Rule(consigne["inverse"] & (tresor_x["dessus"] | tresor_x["aucun_g"] | tresor_x["aucun_d"]), consequent=movement["recule"]%2))

        rules.append(ctrl.Rule((wall_x["proche"] & wall_y["proche"]), consequent=movement["recule"]))
        rules.append(ctrl.Rule((wall_x["moyen"] & wall_y["proche"]), consequent=movement["recule"]%0.5))
        rules.append(ctrl.Rule((wall_opp_x["proche"] & wall_opp_y["proche"]), consequent=movement["avance"]))
        rules.append(ctrl.Rule((wall_opp_x["moyen"] & wall_opp_y["proche"]), consequent=movement["avance"]%0.5))

        rules.append(ctrl.Rule((obstacle_x["proche_d"] & (obstacle_y["proche_d"] | obstacle_y["proche_g"]) & consigne["inactive"]), consequent=movement["recule"]))
        rules.append(ctrl.Rule((obstacle_x["proche_g"] & (obstacle_y["proche_d"] | obstacle_y["proche_g"]) & consigne["inactive"]), consequent=movement["avance"]))

        rules.append(ctrl.Rule((tresor_x["loin_d"]), consequent=movement["avance"]))
        rules.append(ctrl.Rule((tresor_x["loin_g"]), consequent=movement["recule"]))

        rules.append(ctrl.Rule((bloqueur_consigne_y["obstruction"] & bloqueur_consigne_x["obstruction"]), consequent=movement["reste"]))
        rules.append(ctrl.Rule(antecedent=(consigne["inactive"] & 
            (wall_x["loin"] | wall_y["loin"]) & 
            (wall_x["loin"] | wall_y["loin"]) & 
            ((obstacle_x["loin_g"] | obstacle_x["loin_d"]) | 
            ((obstacle_x["loin_g"] | obstacle_x["loin_d"]) & (obstacle_y["proche_d"] | obstacle_y["proche_g"])) |
            (obstacle_y["loin_g"] | obstacle_y["loin_d"])) & 
            (bloqueur_consigne_y["libre"] | bloqueur_consigne_x["libre"])), consequent=movement["reste"]))

#        rules.append(ctrl.Rule(antecedent=(
#            ((wall_x["proche"] & wall_y["proche"]) | 
#            (obstacle_x["proche"] & obstacle_y["proche"]))), consequent=movement["recule"]))

#        rules.append(ctrl.Rule(antecedent=(wall_x["moyen"] & wall_y["proche"]), consequent=movement["recule"]%0.5))

#        rules.append(ctrl.Rule(antecedent=(
#            ((wall_x["proche"] & wall_y["proche"]) | 
#            (obstacle_x["proche"] & obstacle_y["proche"]))), consequent=movement["recule"]))
        
#        rules.append(ctrl.Rule(antecedent=(
#            wall_x["loin"] &
#            (bloqueur_consigne_x["obstruction"] & bloqueur_consigne_y["obstruction"])), consequent=movement["avance"]))

#        rules.append(ctrl.Rule(antecedent=(
#            wall_x["moyen"] &
#            (bloqueur_consigne_x["obstruction"] & bloqueur_consigne_y["obstruction"])), consequent=movement["reste"]))
        
#        rules.append(ctrl.Rule(antecedent=(
#            wall_x["proche"] &
#            (bloqueur_consigne_x["obstruction"] & bloqueur_consigne_y["obstruction"])), consequent=movement["recule"]))
        
        #rules.append(ctrl.Rule(antecedent=(consigne["inactive"] & (wall_x["loin"] & wall_y["loin"]) & (obstacle_x["loin"] & obstacle_y["loin"]) & (bloqueur_consigne_y["libre"] )), consequent=movement["reste"]))
        
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

    def get_direction(self, wall_x, wall_y, wall_opp_x, wall_opp_y, obstacle_x, obstacle_y, bloqueur_consigne_x, bloqueur_consigne_y, tresor_x, consigne):
        self.sim.input["wall_x"] = wall_x
        self.sim.input["wall_y"] = wall_y
        self.sim.input["wall_opp_x"] = wall_opp_x
        self.sim.input["wall_opp_y"] = wall_opp_y
        self.sim.input["obstacle_x"] = obstacle_x
        self.sim.input["obstacle_y"] = obstacle_y
        self.sim.input["bloqueur_consigne_x"] = bloqueur_consigne_x
        self.sim.input["bloqueur_consigne_y"] = bloqueur_consigne_y
        self.sim.input["tresor_x"] = tresor_x
        self.sim.input["consigne"] = consigne

        self.sim.compute()
        
        return self.sim.output["movement"]