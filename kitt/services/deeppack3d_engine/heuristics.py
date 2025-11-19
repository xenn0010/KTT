"""
Heuristic functions for 3D bin packing
Extracted from agent.py to avoid tensorflow dependency
"""

import itertools
from env import MultiBinPackerEnv


class HeuristicAgent:
    def __init__(self, heuristic, env=MultiBinPackerEnv(n_bins=2, max_bins=-1, size=(32, 32, 32), k=10, verbose=True), verbose=True, visualize=False):
        self.env = env

        self.heuristic = heuristic
        self.ep_history = []

        self.verbose = verbose
        self.visualize = visualize

    def select(self, state):
        # state = (items, h_map, actions)

        items, h_map, actions = state
        action = self.heuristic(actions)

        return action

    def run(self, max_ep=1, verbose=False):
        iters = (i for i, _ in enumerate(iter(bool, True))) if max_ep == -1 else range(max_ep)

        for ep in iters:
            if verbose:
                print(f'ep {ep}:')

            state = self.env.reset()
            ep_reward = 0

            history = []

            for step in itertools.count():
                if verbose:
                    print(f'\nstep {step}')

                items, h_map, actions = state
                if len(actions) == 0: raise Exception('0 actions')

                action = self.select(state)

                if verbose:
                    print(f'action: {action}')

                next_state, reward, done = self.env.step(action)

                history.append((state, action, next_state, reward, done))

                if verbose:
                    print(f'actions: {actions}')
                    print(f'reward: {reward}, done: {done}')
                    print(f'placement: {actions[action[0]][action[1]][action[2]]}')

                yield actions[action[0]][action[1]][action[2]]

                ep_reward += reward

                if self.visualize:
                    for i, packer in enumerate(self.env.packers):
                        packer.render().savefig(f'./outputs/{ep}_{step}_{i}.jpg')

                if done:
                    break

                state = next_state

            self.ep_history.append(([packer.space_utilization() for packer in self.env.used_packers], self.env.used_bins, ep_reward))

            yield None

            utils = [round(packer.space_utilization() * 100, 2) for packer in self.env.used_packers]
            if self.verbose: print(f'Episode {ep}, util: {utils}, used bins: {self.env.used_bins}, ep_reward: {ep_reward:.2f}')


def bottom_left(actions):
    scores = []
    for i, item in enumerate(actions):
        for j, bin_ in enumerate(item):
            for k, placement in enumerate(bin_):
                item, (x, y, z), (w, h, d), _ = placement
                y = y + h
                x = x + w
                z = z + d
                scores.append(([y, x, z, i, j, k], [i, j, k]))

    indices = sorted(range(len(scores)), key=lambda i: scores[i][0])
    return scores[indices[0]][1]


def best_short_side_fit(actions):
    scores = []
    for i, item in enumerate(actions):
        for j, bin_ in enumerate(item):
            for k, placement in enumerate(bin_):
                item, (x, y, z), (w, h, d), split = placement
                W, H = split.width, split.height
                scores.append(((min(W - w, H - h), i, j, k), [i, j, k]))

    indices = sorted(range(len(scores)), key=lambda i: scores[i][0])
    return scores[indices[0]][1]


def best_area_fit(actions):
    scores = []
    for i, item in enumerate(actions):
        for j, bin_ in enumerate(item):
            for k, placement in enumerate(bin_):
                item, (x, y, z), (w, h, d), split = placement
                W, H = split.width, split.height
                scores.append(((split.volume, min(W - w, H - h), i, j, k), [i, j, k]))

    indices = sorted(range(len(scores)), key=lambda i: scores[i][0])
    return scores[indices[0]][1]


def best_long_side_fit(actions):
    scores = []
    for i, item in enumerate(actions):
        for j, bin_ in enumerate(item):
            for k, placement in enumerate(bin_):
                item, (x, y, z), (w, h, d), split = placement
                W, H = split.width, split.height
                scores.append(((max(W - w, H - h), i, j, k), [i, j, k]))

    indices = sorted(range(len(scores)), key=lambda i: scores[i][0])
    return scores[indices[0]][1]
