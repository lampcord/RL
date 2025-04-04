import os, random
import numpy as np
import torch
from torch import nn
import itertools
from baselines_wrappers import DummyVecEnv
from pytorch_wrappers import make_atari_deepmind, BatchedPytorchFrameStack, PytorchLazyFrames
import time

import msgpack
from msgpack_numpy import patch as msgpack_numpy_patch
msgpack_numpy_patch()

RECORD = True
SKIPMOVES = 2
DELAY = False
CYCLE = False
RUNFILE = 'SpaceInvadersNoFrameskip-v4_5e-05_45.25.pack'
def nature_cnn(observation_space, depths=(32, 64, 64), final_layer=512):
    n_input_channels = observation_space.shape[0]

    cnn = nn.Sequential(
        nn.Conv2d(n_input_channels, depths[0], kernel_size=8, stride=4),
        nn.ReLU(),
        nn.Conv2d(depths[0], depths[1], kernel_size=4, stride=2),
        nn.ReLU(),
        nn.Conv2d(depths[1], depths[2], kernel_size=3, stride=1),
        nn.ReLU(),
        nn.Flatten())

    # Compute shape by doing one forward pass
    with torch.no_grad():
        n_flatten = cnn(torch.as_tensor(observation_space.sample()[None]).float()).shape[1]

    out = nn.Sequential(cnn, nn.Linear(n_flatten, final_layer), nn.ReLU())

    return out

class Network(nn.Module):
    def __init__(self, env, device):
        super().__init__()

        self.num_actions = env.action_space.n
        self.device = device

        conv_net = nature_cnn(env.observation_space)

        self.net = nn.Sequential(conv_net, nn.Linear(512, self.num_actions))

    def forward(self, x):
        return self.net(x)

    def act(self, obses, epsilon):
        obses_t = torch.as_tensor(obses, dtype=torch.float32, device=self.device)
        q_values = self(obses_t)

        max_q_indices = torch.argmax(q_values, dim=1)
        actions = max_q_indices.detach().tolist()

        for i in range(len(actions)):
            rnd_sample = random.random()
            if rnd_sample <= epsilon:
                actions[i] = random.randint(0, self.num_actions - 1)

        return actions
    
    def load(self, load_path):
        if not os.path.exists(load_path):
            raise FileNotFoundError(load_path)

        with open(load_path, 'rb') as f:
            params_numpy = msgpack.loads(f.read())

        params = {k: torch.as_tensor(v, device=self.device) for k,v in params_numpy.items()}

        self.load_state_dict(params)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#device = "cpu"
print('device:', device)

def run(skipmoves, show_render):
    #make_env = lambda: make_atari_deepmind('BreakoutNoFrameskip-v4', scale_values=True)
    make_env = lambda: make_atari_deepmind('SpaceInvadersNoFrameskip-v4', scale_values=True, record=RECORD, override_num_noops=skipmoves, clip_rewards=False)

    vec_env = DummyVecEnv([make_env for _ in range(1)])

    env = BatchedPytorchFrameStack(vec_env, k=4)

    net = Network(env, device)
    net = net.to(device)

    #net.load('play/atari_model_vanilla.pack')
    net.load(RUNFILE)

    obs = env.reset()
    beginning_episode = True
    total_games = 10
    total_reward = 0
    total_capped = 0
    total_steps = 0
    grand_total = 0
    grand_total_capped = 0

    for t in itertools.count():
        if isinstance(obs[0], PytorchLazyFrames):
            act_obs = np.stack([o.get_frames() for o in obs])
            action = net.act(act_obs, 0.0)
        else:
            action = net.act(obs, 0.0)

        if beginning_episode:
            time.sleep(1)
            action = [1]
            beginning_episode = False
            total_games -= 1

        obs, rew, done, info = env.step(action)
        total_reward += rew
        total_capped += rew if rew <= 1 else 1
        total_steps += 1
        if show_render:
            env.render()
        if DELAY:
            time.sleep(0.02)

        if done[0]:
            print(f"Total Reward: {total_reward} Total Capped: {total_capped} Total Steps: {total_steps} Info: {info}")
            grand_total += total_reward
            grand_total_capped += total_capped
            total_reward = 0
            total_capped = 0
            total_steps = 0
            obs = env.reset()
            beginning_episode = True

        if info[0]['ale.lives'] == 0:
            break

    print(f"{SKIPMOVES} Grand Total: {grand_total} Total Capped: {grand_total_capped}")
    time.sleep(1)
    env.close()


if CYCLE:
    for skipmoves in range(1,31):
        print(f"Skipmoves {skipmoves}")
        run(skipmoves, False)
else:
    run(SKIPMOVES, True)
