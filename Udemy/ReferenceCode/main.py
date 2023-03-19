import argparse, os
import datetime

import gym
import numpy as np
import agents as Agents
from utils import plot_learning_curve, make_env, make_env_compact
from torch.utils.tensorboard import SummaryWriter
import torch as T

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    description='Deep Q Learning: From Paper to Code')
    # the hyphen makes the argument optional
    parser.add_argument('-n_games', type=int, default=1,
                        help='Number of games to play')
    parser.add_argument('-lr', type=float, default=0.0001,
                        help='Learning rate for optimizer')
    parser.add_argument('-eps_min', type=float, default=0.1,
            help='Minimum value for epsilon in epsilon-greedy action selection')
    parser.add_argument('-gamma', type=float, default=0.99,
                                    help='Discount factor for update equation.')
    parser.add_argument('-eps_dec', type=float, default=1e-5,
                        help='Linear factor for decreasing epsilon')
    parser.add_argument('-eps', type=float, default=1.0,
        help='Starting value for epsilon in epsilon-greedy action selection')
    parser.add_argument('-max_mem', type=int, default=50000, #~13Gb
                                help='Maximum size for memory replay buffer')
    parser.add_argument('-repeat', type=int, default=4,
                            help='Number of frames to repeat & stack')
    parser.add_argument('-bs', type=int, default=32,
                            help='Batch size for replay memory sampling')
    parser.add_argument('-replace', type=int, default=1000,
                        help='interval for replacing target network')
    parser.add_argument('-env', type=str, default='SpaceInvadersNoFrameskip-v4',
                            help='Atari environment.\nPongNoFrameskip-v4\n \
                                  BreakoutNoFrameskip-v4\n \
                                  SpaceInvadersNoFrameskip-v4\n \
                                  EnduroNoFrameskip-v4\n \
                                  AtlantisNoFrameskip-v4')
    parser.add_argument('-gpu', type=str, default='0', help='GPU: 0 or 1')
    parser.add_argument('-load_checkpoint', type=bool, default=False,
                        help='load model checkpoint')
    parser.add_argument('-path', type=str, default='models/',
                        help='path for model saving/loading')
    parser.add_argument('-algo', type=str, default='DQNAgent',
                    help='DQNAgent/DDQNAgent/DuelingDQNAgent/DuelingDDQNAgent')
    parser.add_argument('-clip_rewards', type=bool, default=False,
                        help='Clip rewards to range -1 to 1')
    parser.add_argument('-no_ops', type=int, default=0,
                        help='Max number of no ops for testing')
    parser.add_argument('-fire_first', type=bool, default=False,
                        help='Set first action of episode to fire')
    args = parser.parse_args()

    best_score = -np.inf
    #################################################################################
    args.load_checkpoint = False
    args.clip_rewards = True
    args.max_mem = 400000
    args.n_games = 100000
    args.no_ops = 30
    best_score = 0
    args.eps_dec = (args.eps - args.eps_min) / 1e6
    best_name = '27.74'
    LOG_DIR = './logs/' + args.env + '_' + str(args.lr) + '_' + datetime.datetime.now().strftime('%b%d_%H-%M-%S')
    summary_writer = SummaryWriter(LOG_DIR)
    args.fire_first = True
    args.algo = 'DDQNAgent'
    #################################################################################

    if args.load_checkpoint:
        args.eps = args.eps_min
        args.max_mem = 1000

    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

    # env = make_env(env_name=args.env, repeat=args.repeat,
    #               clip_rewards=args.clip_rewards, no_ops=args.no_ops,
    #               fire_first=args.fire_first)

    env = make_env_compact(env_name=args.env, repeat=args.repeat,
                  clip_rewards=args.clip_rewards, no_ops=args.no_ops,
                  fire_first=args.fire_first)

    # test_obs = env.reset()
    # test_obs_c = env_c.reset()
    # test_array = np.array(test_obs_c, dtype=np.float32) / 255.0
    # test_diff = test_array - test_obs
    # test_zeros = np.zeros((4,84,84), dtype=np.float32)
    # t1 = test_array == test_zeros
    # t2 = test_diff == test_zeros
    #
    # total = 0.0
    # for x in range(4):
    #     for y in range(84):
    #         for z in range(84):
    #             v = test_diff[x,y,z]
    #             total += v * v
    # exit()

    device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    agent_ = getattr(Agents, args.algo)
    agent = agent_(gamma=args.gamma,
                    epsilon=args.eps,
                    lr=args.lr,
                    input_dims=env.observation_space.shape,
                    n_actions=env.action_space.n,
                    mem_size=args.max_mem,
                    eps_min=args.eps_min,
                    batch_size=args.bs,
                    replace=args.replace,
                    eps_dec=args.eps_dec,
                    chkpt_dir=args.path,
                    algo=args.algo,
                    env_name=args.env,
                    device=device
                )

    # exit()
    if args.load_checkpoint:
        agent.load_models(best_name)

    fname = args.algo + '_' + args.env + '_alpha' + str(args.lr) +'_' \
            + str(args.n_games) + 'games'
    figure_file = 'plots/' + fname + '.png'
    scores_file = fname + '_scores.npy'
    avg_score = 0
    scores, eps_history = [], []
    n_steps = 0
    steps_array = []
    for game in range(args.n_games):
        done = False
        observation = env.reset()
        score = 0
        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done, info = env.step(action)
            score += reward

            if args.load_checkpoint:
                env.render()
            else:
                agent.store_transition(observation, action,
                                     reward, observation_, int(done))
                agent.learn()
            observation = observation_
            n_steps += 1

            if not args.load_checkpoint and n_steps % 100 == 0:
                summary_writer.add_scalar('AvgRew', avg_score, global_step=n_steps)
                summary_writer.add_scalar('BestAvgRew', best_score, global_step=n_steps)

        scores.append(score)
        steps_array.append(n_steps)

        avg_score = np.mean(scores[-100:])
        print('episode: ', game, 'score: ', score,
             ' average score %.1f' % avg_score, 'best score %.2f' % best_score,
            'epsilon %.2f' % agent.epsilon, 'steps', n_steps)

        if game >= 10 and avg_score > best_score:
            if not args.load_checkpoint:
                best_score = avg_score
                agent.save_models(best_score)

        eps_history.append(agent.epsilon)
        if args.load_checkpoint and n_steps >= 18000:
            break

    x = [i+1 for i in range(len(scores))]
    plot_learning_curve(steps_array, scores, eps_history, figure_file)
    #np.save(scores_file, np.array(scores))
