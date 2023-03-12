import gym
import torch
import random
import numpy as np
import matplotlib.pyplot as plt

device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
print('device:', device)

env = gym.make('FrozenLake-v1')
env.render()

L = 0
D = 1
R = 2
U = 3

policy = {}

'''
My had built policy
policy[0] = R
policy[1] = U
policy[2] = D
policy[3] = U

policy[4] = L
policy[5] = D
policy[6] = D
policy[7] = L

policy[8] = U
policy[9] = D
policy[10] = L
policy[11] = D

policy[12] = R
policy[13] = R
policy[14] = R
policy[15] = R
'''
# Q Tabular 3.5 million steps
'''
(0, 0) 0.06967642277849012 ***
(0, 1) 0.06529042103756208 
(0, 2) 0.06546108062276561 
(0, 3) 0.05963363774211486 
(1, 0) 0.039290026145066104 
(1, 1) 0.04286748549421583 
(1, 2) 0.040996949721732186 
(1, 3) 0.06055967128318014 ***
(2, 0) 0.07271712383239669 ***
(2, 1) 0.06898687097876047 
(2, 2) 0.07241913669083615 
(2, 3) 0.057674110989248115 
(3, 0) 0.04013449753141441 
(3, 1) 0.040055826524659284 
(3, 2) 0.03417493095329138 
(3, 3) 0.05612090279936258 ***
(4, 0) 0.09310660773475743 ***
(4, 1) 0.07133213815556952 
(4, 2) 0.06545005231860584 
(4, 3) 0.04803340209124915 
(5, 0) 0 ***
(5, 1) 0 
(5, 2) 0 
(5, 3) 0 
(6, 0) 0.10510947569251072 
(6, 1) 0.09415393361278378 
(6, 2) 0.10615290952544298 ***
(6, 3) 0.02227296011494444 
(7, 0) 0 ***
(7, 1) 0 
(7, 2) 0 
(7, 3) 0 
(8, 0) 0.0715804946790961 
(8, 1) 0.11765870062548482 
(8, 2) 0.10044458076038497 
(8, 3) 0.1464786308287619 ***
(9, 0) 0.15297529508493785 
(9, 1) 0.24949685287502332 ***
(9, 2) 0.19810555482718156 
(9, 3) 0.1338813512315923 
(10, 0) 0.2930378555018585 ***
(10, 1) 0.25482308273456905 
(10, 2) 0.23650294428820898 
(10, 3) 0.11093705473463858 
(11, 0) 0 ***
(11, 1) 0 
(11, 2) 0 
(11, 3) 0 
(12, 0) 0 ***
(12, 1) 0 
(12, 2) 0 
(12, 3) 0 
(13, 0) 0.1846827734103343 
(13, 1) 0.3053703256823011 
(13, 2) 0.3816552886077249 ***
(13, 3) 0.2573098880504169 
(14, 0) 0.3975176081593996 
(14, 1) 0.6428336486258841 ***
(14, 2) 0.6115875186115206 
(14, 3) 0.5407656559650136 
(15, 0) 0 ***
(15, 1) 0 
(15, 2) 0 
(15, 3) 0 

'''
policy[0] = 0
policy[1] = 3
policy[2] = 0
policy[3] = 3

policy[4] = 0
policy[5] = D
policy[6] = 2
policy[7] = L

policy[8] = 3
policy[9] = 1
policy[10] = 0
policy[11] = D

policy[12] = R
policy[13] = 2
policy[14] = 1
policy[15] = R


scores = []
averages = []

for step in range(1000):
    obs = env.reset()

    done = False
    score = 0
    while not done:
        #action = env.action_space.sample()
        action = policy[obs]
        obs, rew, done, info = env.step(action)
        score += rew
    scores.append(score)

    if step >= 10 and step % 10 == 0:
        average = np.mean(scores[-10:])
        averages.append(average)

print("Overall Average: ", np.mean(scores))
plt.plot(averages)
plt.show()
