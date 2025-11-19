def parse_args():
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('method', metavar='method', 
                        type=str, choices=['rl', 'bl', 'baf', 'bssf', 'blsf'], 
                        help='choose the method from {"rl", "bl", "baf", "bssf", "blsf"}.')
    
    parser.add_argument('lookahead', metavar='lookahead', 
                        type=int,
                        help='choose the lookahead value.')
    
    parser.add_argument('--data', metavar='', 
                        type=str, default='generated', choices=['generated', 'input', 'file'], 
                        help='choose the input source from {"generated", "input", "file"} (default: generated).')
    
    parser.add_argument('--path', metavar='', 
                        type=str, default=None, 
                        help='set the file path, only used if --data is "file" (default: None).')
    
    parser.add_argument('--n_iterations', metavar='', 
                        type=int, default=100, 
                        help='set the number of iterations, only used if --data is "generated" (default: 100).')
    
    parser.add_argument('--seed', metavar='', 
                        type=str, default=None, 
                        help='set the random seed for reproducibility, only used if --data is "generated" (default: None).')
    
    parser.add_argument('--verbose', metavar='', 
                        type=int, default=1, 
                        help='set verbose level (default: 1).')
    
    parser.add_argument('--train', 
                        action='store_true', 
                        help='enable training mode, only used if method is "rl" (default: False).')
    
    parser.add_argument('--batch_size', metavar='', 
                        type=int, default=32, 
                        help='set batch_size, only used if train is True (default: 32).')
    
    parser.add_argument('--visualize', 
                        action='store_true', 
                        help='enable visualization mode (default: False).')
    
    return parser.parse_args()

import numpy as np
import os, shutil, time

from env import *
from heuristics import (
    HeuristicAgent,
    bottom_left,
    best_area_fit,
    best_short_side_fit,
    best_long_side_fit
)

# Lazy import agent only when RL is needed (avoids tensorflow dependency)
Agent = None

heuristics = {
    'bl': bottom_left,
    'baf': best_area_fit,
    'bssf': best_short_side_fit,
    'blsf': best_long_side_fit,
}

def deeppack3d(method, lookahead, *, n_iterations=100, seed=None, verbose=1, data='generated', path=None, train=False, visualize=False, batch_size=32):
    global Agent  # Declare Agent as global at function start
    reset_rng(seed)
    
    env = MultiBinPackerEnv(n_bins=1, 
                            max_bins=1, 
                            size=(32, 32, 32), 
                            k=lookahead, 
                            prealloc_items=100, 
                            verbose=verbose)

    if data == 'file':
        env.conveyor = FileConveyor(k=env.k, path=path).reset()
    elif data == 'input':
        env.conveyor = InputConveyor(k=env.k).reset()

    if visualize:
        if os.path.exists('./outputs'):
            shutil.rmtree('./outputs')
        os.makedirs('./outputs')

    if train:
        print(f'Training with method "{method}" and lookahead {lookahead}...')

        if method != 'rl':
            raise Exception('training mode can only be used if method is "rl"')

        # Lazy load agent module (requires tensorflow)
        if Agent is None:
            from agent import Agent as AgentClass
            Agent = AgentClass

        # env = BinPackerEnv(size=(32, 32, 32), k=env.k, bin_size=(32, 32, 32))
        agent = Agent(env, train=True, verbose=verbose > 0, visualize=visualize, batch_size=batch_size)

        agent.eps = 1.0
        for i in range(n_iterations):
            print(f'Iteration {i}')
            start_time = time.time()
            yield from agent.run(100, verbose=verbose > 1)
            agent.eps = max(agent.eps * 0.95, 0.025)
            
        data = np.asarray([utils for utils, n_bins, ep_reward in agent.ep_history])
        # y = np.ones(100)
        # data = np.convolve(data, y, 'valid') / len(y)
        sns.lineplot(data=data)
        plt.savefig(f'./util.jpg')
        plt.show()
        
        data = np.asarray([ep_reward for utils, n_bins, ep_reward in agent.ep_history])
        # y = np.ones(100)
        # data = np.convolve(data, y, 'valid') / len(y)
        sns.lineplot(data=data)
        plt.savefig(f'./ep_reward.jpg')
        plt.show()

        import uuid
        uid = uuid.uuid4()
        print(f'saved model at ./{uid}.h5')
        agent.q_net.save(f'{uid}.h5')
    else:
        if verbose > 0:
            print(f'Testing with method "{method}" and lookahead {lookahead}...')
        
        if method == 'rl':
            # Lazy load agent module (requires tensorflow)
            if Agent is None:
                from agent import Agent as AgentClass
                Agent = AgentClass
            import tensorflow as tf

            model_path = f'./models/k={lookahead}.h5'
            agent = Agent(env, train=False, verbose=verbose > 0, visualize=visualize, batch_size=batch_size)
            agent.q_net = tf.keras.models.load_model(model_path, compile=False)
            agent.eps = 0.0
        else:
            agent = HeuristicAgent(heuristics[method], env, verbose=verbose > 0, visualize=visualize)
        
        start_time = time.time()
        
        try:
            yield from agent.run(n_iterations, verbose=verbose > 1)
        except Exception as e:
            if np.all(np.array(env.conveyor.reset().peek()) == None):
                if verbose > 0:
                    print('\n=====the end of conveyor line=====')
            else:
                print(e)

        if verbose > 0:
            print()
            next_items = np.array(env.conveyor.reset().peek()).tolist()
            avg_util = np.mean([util for utils, n_bins, ep_reward in agent.ep_history[:] for util in utils[:]])
            used_items = np.sum([n_bins for utils, n_bins, ep_reward in agent.ep_history[:] for util in utils[:]])
            
            print(f'Used time: {int(time.time() - start_time)} seconds')
            print(f'Next items: {next_items}')
            print(f'Average space util: {avg_util}')
            print(f'Used bins: {used_items}')

def main():
    args = parse_args()
    
    reset_rng(args.seed)

    for _ in deeppack3d(args.method, 
                        args.lookahead, 
                        n_iterations=args.n_iterations, 
                        seed=args.seed, 
                        train=args.train, 
                        verbose=args.verbose, 
                        data=args.data, 
                        path=args.path,
                        visualize=args.visualize, 
                        batch_size=args.batch_size):
        pass

if __name__ == "__main__":
    main()