import gym
import random
import numpy as np
import matplotlib.pyplot as plt
import pickle

environment = gym.make('FrozenLake-v1')
environment.render()

EPSILON_START = 1.0
EPSILON_END = 0.01
EPISODES = 10000
LEARNING_RATE = 0.001
DISCOUNT_FACTOR = 0.9


class Agent:
    def __init__(self, q, learning_rate, discount_factor, epsilon_start, epsilon_end, episodes):
        self.q = q
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon_start = epsilon_start
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.episodes = episodes
        self.episode = 0
        self.update_epsilon()

    def update_epsilon(self):
        self.epsilon = np.interp(self.episode, [0, self.episodes], [self.epsilon_start, self.epsilon_end])

    def choose_action(self, env, obs):
        self.update_epsilon()
        if random.random() < self.epsilon:
            act = env.action_space.sample()
        else:
            act = self.q.get_best_action(obs)
        return act

    def update_qtable(self, obs, act, new_obs, rew):
        '''
        Q(s,a) = Q(s,a) + learning_rate * (reward + discount_factor * max Q(s', a_max) - Q(s,a))
        '''
        current_reward = self.q.get_reward_for_action(obs, act)
        best_future_action = self.q.get_best_action(new_obs)
        best_future_reward = self.q.get_reward_for_action(new_obs, best_future_action)
        new_current_reward = current_reward + self.learning_rate * (
                    rew + self.discount_factor * best_future_reward - current_reward)
        #if new_current_reward > 1.0:
        #    raise Exception('bad calc')
        self.q.update_reward(obs, act, new_current_reward)


class Qtable:
    def __init__(self, env):
        self.table = {}
        self.actions = [a for a in range(env.action_space.n)]
        for obs in range(env.observation_space.n):
            for act in range(env.action_space.n):
                key = (obs, act)
                # self.table[key] = random.random()
                self.table[key] = 0

    def get_reward_for_action(self, obs, act):
        key = (obs, act)
        rew = self.table.get(key, None)
        if rew is None: print("ERROR")
        return rew

    def update_reward(self, obs, act, rew):
        key = (obs, act)
        self.table[key] = rew

    def get_best_action(self, obs):
        best_action = None
        best_reward = None
        for act in self.actions:
            key = (obs, act)
            rew = self.table.get(key, None)
            if rew is None:
                continue

            if best_action is None or rew > best_reward:
                best_action = act
                best_reward = rew

        if best_action is None: print("ERROR")
        return best_action

    def print(self):
        for key in self.table.keys():
            obs, act = key
            best_act = self.get_best_action(obs)
            label = ''
            if best_act == act:
                label = '***'
            print(key, self.table[key], label)

    def load(self):
        with open('best.pickle', 'rb') as handle:
            self.table = pickle.load(handle)

    def save(self):
        with open('best.pickle', 'wb') as handle:
            pickle.dump(self.table, handle, protocol=pickle.HIGHEST_PROTOCOL)

qtable = Qtable(environment)
qtable.load()

agent = Agent(qtable, LEARNING_RATE, DISCOUNT_FACTOR, EPSILON_START, EPSILON_END, EPISODES)

rewards = []
average_rewards = []
for episode in range(EPISODES):
    observation = environment.reset()
    agent.episode = episode
    total_reward = 0
    while True:
        action = agent.choose_action(environment, observation)
        new_observation, reward, done, info = environment.step(action)
        agent.update_qtable(observation, action, new_observation, reward)

        observation = new_observation
        total_reward += reward

        if done is True:
            break

    rewards.append(total_reward)
    if episode > 0 and episode % 100 == 0:
        average_rewards.append(np.mean(rewards[-100:]))

plt.plot(average_rewards)
plt.show()

agent.q.print()
agent.q.save()



