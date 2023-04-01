import numpy as np

class Node:
    def __init__(self, parent=None, action=None, env=None):
        self.parent = parent
        self.action = action
        self.env = env.clone() if env else None
        self.children = []
        self.num_visits = 0
        self.total_reward = 0
        self.is_expanded = False

    def expand(self):
        legal_moves = self.env.get_legal_moves()
        self.children = [Node(parent=self, action=move, env=self.env) for move in legal_moves]
        for child in self.children:
            _, reward, done, _ = child.env.step(child.action)
            self.backpropagate(reward)

        self.is_expanded = True

    def uct(self, c=1):
        if self.num_visits == 0:
            return np.inf
        return (self.total_reward / self.num_visits) + c * np.sqrt(np.log(self.parent.num_visits) / self.num_visits)

    def best_child(self, c=1):
        return max(self.children, key=lambda child: child.uct(c))

    def rollout(self):
        env_copy = self.env.clone()
        done = False
        reward = 0
        mult = 1
        while not done:
            legal_moves = env_copy.get_legal_moves()
            if len(legal_moves) == 0:
                reward, t = env_copy.check_for_win()
                break
            random_move = np.random.choice(legal_moves)
            if self.env.turn == env_copy.turn:
                mult = 1
            else:
                mult = -1
            _, reward, done, _ = env_copy.step(random_move)
            reward = reward * mult
        return reward

    def backpropagate(self, reward):
        self.num_visits += 1
        self.total_reward += reward
        if self.parent:
            if self.parent.env.turn != self.env.turn:
                reward = -1 * reward
            self.parent.backpropagate(reward)

    def dump(self, level=1):
        for x in range(level):
            print(' ', end='')
        print(self.action, self.total_reward)
        for c in self.children:
            c.dump(level + 1)

def mcts(env, num_simulations=1000, c=0.1):
    root = Node(env=env)

    for _ in range(num_simulations):
        node = root
        while node.is_expanded and node.children:
            node = node.best_child(c)
        if not node.is_expanded:
            node.expand()
        rollout_reward = node.rollout()
        node.backpropagate(rollout_reward)

    best_move = root.best_child(c=0).action
    # root.dump()
    return best_move
