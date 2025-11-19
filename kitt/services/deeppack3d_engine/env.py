import numpy as np
from conveyor import *
from SpacePartitioner import *
from geometry import *
from binpacker import *

class Env:
    def __init__(self, verbose):
        self.verbose = verbose
        self._state = None
        
    def reset(self):
        raise Exception('not implemented')
        
    def state(self, step=False):
        raise Exception('not implemented')
        
    def step(self, action):
        raise Exception('not implemented')
        
    def actions(self):
        raise Exception('not implemented')
        
def indices(actions):
    return [
        (i, j, k) 
        for i in range(len(actions)) 
        for j in range(len(actions[i])) 
        for k in range(len(actions[i][j]))
    ]

class MultiBinPackerEnv(Env):
    def __init__(self, n_bins, size, k=1, max_bins=None, max_items=None, replace='all', verbose=False, prealloc_bins=0, prealloc_items=0, shuffle=False, use_rotate=True, use_skip=True):
        super().__init__(verbose)
        self.n_bins = n_bins
        self.size = size
        self.k = k
        
        self.packers = [SpacePartitioner(size) for _ in range(n_bins)]
        self.conveyor = Conveyor(k, 
                                 max_items=max_items, 
                                 prealloc_bins=prealloc_bins, 
                                 prealloc_items=prealloc_items, 
                                 shuffle=shuffle
                                )
        
        self.max_bins = -1 if max_bins is None else max_bins
        self.used_bins = n_bins
        
        self.used_packers = [] + self.packers
        self.replace = replace # {'max', 'min', 'all'}
        
        self.use_rotate = use_rotate
        self.use_skip = use_skip
        
    def reset(self):
        for packer in self.packers:
            packer.reset()
        self.conveyor.reset()
        
        self._state = None
        self.used_bins = self.n_bins
        self.used_packers = []
        return self.state()
    
    def state(self, step=False):
        if step or self._state is None:
            items = list(self.conveyor.peek())
            h_maps = np.array(self._height_maps())
#             print(items)
#             print(self.actions(items, h_maps, rotate=True, skip=True))
            actions = list(self.actions(items, h_maps, rotate=self.use_rotate, skip=self.use_skip))
    
            self._state = (items, h_maps, actions)
        
        return self._state
    
    def _height_maps(self):
        return [packer.height_map.copy() for packer in self.packers]
    
    def placeable_coords(self, packer, h_map, size):
        xz = []
        splits = {}
        for split in packer.free_splits:
            if (split.top < self.size[1]) or (not split.fit(size)):
                continue
            x, y, z = split.coord
            xz.append((x, z))
            splits[(x, z)] = split
        xz = set(xz)
        
        w, h, d = size
        xyz = []
        for x, z in xz:
            placement = h_map[z:z + d, x:x + w]
            y = np.amax(placement)
            # placement and stability constraints
            if np.count_nonzero(placement == y) / (d * w) > 0.5:
                xyz.append((x, y, z, splits[(x, z)]))
        
        return xyz
    
    def actions(self, items, h_maps, rotate, skip):
        actions = []
        
        for item in items:
            if item is None:
                continue
            
            bin_actions = []
            for i, packer in enumerate(self.packers):
                item_actions = []
#                 print(items)
                for size in rotated_sizes(item, rotate):
                    for x, y, z, split in self.placeable_coords(packer, h_maps[i], size):
                        item_actions.append((i, (x, y, z), size, split))
                bin_actions.append(item_actions)
            actions.append(bin_actions)
                
            # always pick the first available item
            if not skip:
                return actions
            
        return actions
    
    def step(self, action):
        items, h_maps, actions = self.state()
        
        # item, bin, rotation_placement
        i, j, k = action
        _, (x, y, z), (w, h, d), _ = actions[i][j][k]
        
        packer = self.packers[j]
        cuboid = Cuboid(x, y, z, w, h, d)
        if not packer.add(cuboid):
            raise Exception(f'invalid space {cuboid}')
        self.conveyor.grab(i)
        
#         if self.verbose:
#             print(f'action: {action}, item: {i}, bin: {j}, rotated item: {(w, h, d)}, coord: {(x, y, z)}')
#             sns.heatmap(self.p_map(cuboid), vmin=0.0, vmax=1.0, cmap='coolwarm')
#             plt.show()
        
        next_state = self.state(step=True)
        
        # reward shaping
        items, h_maps, actions = next_state
        
        item = items[i]
        h_map = h_maps[j]
        
        volume = np.sum([split.volume for split in packer.splits])
        pyramid = volume / np.sum(h_map)
        compactness = volume / np.prod((packer.size[0], np.amax(h_map), packer.size[2]))
        reward = (pyramid + compactness) / 2
        
        done = len(indices(actions)) == 0
        
        if done:
            if self.max_bins != -1 and self.used_bins + 1 > self.max_bins:
                for i, packer in enumerate(packer for packer in self.packers if packer.space_utilization() != 0):
                    self.used_packers.append(packer)
                    loc = self.packers.index(packer)
                    if self.verbose:
                        print(f'bin {self.used_bins - self.n_bins + i}, loc: {loc}, space util: {packer.space_utilization() * 100:.2f}, packed items: {len(packer.splits)}')
                done = True
            else:
                if self.replace == 'max':
                    loc = np.argmax([packer.space_utilization() for packer in self.packers])
                    packer = self.packers[loc]
                    if self.verbose:
                        print(f'bin {self.used_bins - self.n_bins}, loc: {loc}, space util: {packer.space_utilization() * 100:.2f}, packed items: {len(packer.splits)}')

                    self.used_packers.append(self.packers[loc])
                    self.packers[loc] = SpacePartitioner(self.size)
                    self.packers[loc].reset()
                    added = 1
                    self.used_bins += 1
                elif self.replace == 'all':
                    added = 0
                    while True:
                        loc = np.argmax([packer.space_utilization() for packer in self.packers])
                        packer = self.packers[loc]
                        
                        if packer.space_utilization() == 0:
                            break
                        if self.max_bins != -1 and self.used_bins + 1 > self.max_bins:
                            break
                        if self.verbose:
                            print(f'bin {self.used_bins - self.n_bins}, loc: {loc}, space util: {packer.space_utilization() * 100:.2f}, packed items: {len(packer.splits)}')

                        self.used_packers.append(self.packers[loc])
                        self.packers[loc] = SpacePartitioner(self.size)
                        self.packers[loc].reset()
                        added += 1
                        self.used_bins += 1
                else:
                    raise Exception('not implemented')
                
                next_state = self.state(step=True)
                items, h_maps, actions = next_state
                done = len(indices(actions)) == 0
                if done:
                    for i, packer in enumerate(packer for packer in self.packers if packer.space_utilization() != 0):
                        self.used_packers.append(packer)
                        loc = self.packers.index(packer)
                        if self.verbose:
                            print(f'bin {self.used_bins - self.n_bins + i + 1}, loc: {loc}, space util: {packer.space_utilization() * 100:.2f}, packed items: {len(packer.splits)}')
                    self.used_bins -= len([packer for packer in self.packers if packer.space_utilization() == 0])
#                 if not done:
#                     self.used_bins += added
#                     pass
            if self.verbose: print()
                
        return next_state, reward, done
    
    def p_map(self, i_bin, cuboid):
        x, y, z, w, h, d = cuboid
        
        W, H, D = self.packers[i_bin].size
        mask = np.zeros((W, D))
        mask[z:z + d, x:x + w] = h / H
        
        return mask
    
    def i_map(self, i_bin, items):
        W, H, D = self.packers[i_bin].size
        
        masks = np.zeros((self.k, 3))
        for i, item in enumerate(items):
            if item is None:
                continue
            w, h, d = item
            masks[i] = (w / W, h / H, d / D)

        return masks
    
