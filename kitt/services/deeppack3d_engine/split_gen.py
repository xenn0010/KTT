import numpy as np

from geometry import *
# from binpacker import *
from SpacePartitioner import SpacePartitioner

rng = None

def reset_rng(seed=None):
    global rng
    np.random.seed(seed=None)
    rng = np.random.default_rng(seed=seed)
    
reset_rng()

def _split_sort(splits):
#     ind = np.lexsort((dist, bottom))
#     sorted_splits = []
    
#     for i in ind:
#         sorted_splits.append(splits[i])
        
#     print(np.asarray(sorted(splits, key=lambda split: (
#         split.bottom,
#         np.sqrt(np.sum(np.power(split.coord, 2)))
#     ))) == np.asarray(sorted_splits))
        
# #     print(np.asarray(sorted(splits, key=lambda split: (
# #         split.bottom,
# #         np.sqrt(np.sum(np.power(split.coord, 2)))
# #     ))), np.asarray(sorted_splits))
    
#     import timeit
    
#     print('sorted', timeit.timeit(lambda: sorted(splits, key=lambda split: (
#         split.bottom,
#         np.sqrt(np.sum(np.power(split.coord, 2)))
#     )), number=10000))
    
#     print('lexsort', timeit.timeit(lambda: [splits[i] for i in np.lexsort(([np.sqrt(np.sum(np.power(split.coord, 2))) for split in splits], [split.bottom for split in splits]))], number=10000))
    
#     splits = sorted_splits

    bottom = np.asarray([split.bottom for split in splits])
    dist = np.sqrt(np.sum(np.power([split.coord for split in splits], 2), axis=-1))
    
    return [splits[i] for i in np.lexsort((dist, bottom))]

def _gullotine_cut(space, min_size, max_size, p, p_decay):
    splits = []
    x, y, z, width, height, depth = space
    
    coord = np.asarray((x, y, z))
    size = np.asarray((width, height, depth))
    min_size = np.asarray(min_size)
    max_size = np.asarray(max_size)
    
    must_split = size > max_size
    rand_split = (min_size * 2 <= size) & (rng.random(3) < p)
    axes = must_split | rand_split
    
    if np.any(axes):
        axis = rng.choice(np.count_nonzero(axes))
        axis = np.argwhere(axes)[axis, 0]
        
        low, high = min_size[axis], size[axis] - min_size[axis]
        
        pivot = rng.choice(np.arange(low, high + 1))
        
        mask = np.zeros_like(axes)
        mask[axis] = True
        
        a = Cuboid(*coord, *np.where(mask, pivot, size))
        b = Cuboid(*np.where(mask, coord + pivot, coord), *np.where(mask, size - pivot, size))
        
        splits.extend(_gullotine_cut(a, min_size, max_size, p * p_decay, p_decay))
        splits.extend(_gullotine_cut(b, min_size, max_size, p * p_decay, p_decay))
    else:
        splits.append(space)
    
    return splits

def gullotine_cut(size, min_size, max_size, p, p_decay):
    packer = SpacePartitioner(size)
    splits = _gullotine_cut(Cuboid(0, 0, 0, *size), min_size, max_size, p, p_decay)
    splits = _split_sort(splits)
    for split in splits:
        packer.add(split)
    return packer

def _nongullotine_cut(size, min_size, max_size, p, p_decay, verbose=False):
    packer = SpacePartitioner(size)
    
    min_size = np.asarray(min_size)
    max_size = np.asarray(max_size)
    
    while len(packer.free_splits) > 0:
        free_split = packer.free_splits[np.argmin(np.prod([split.size for split in packer.free_splits], axis=-1))]
        
        size = np.asarray(free_split.size)
        must_split = size > max_size
        rand_split = (min_size * 2 <= size) & (rng.random(3) < p)
        axes = must_split | rand_split
        
        if np.any(axes) and not np.any(size < min_size):
            low, high = min_size[axes], np.amin((max_size, size // 2), axis=0)[axes]
            rand_size = np.copy(low)
            mask = low != high
            rand_size[mask] = rng.integers(low[mask], high[mask])
            
            if verbose:
                print(size, must_split, rand_split, axes, low, high, p)
            
            new_size = np.copy(size)
            new_size[axes] = rand_size
            
            if verbose:
                print(new_size)
                print(*free_split.coord, *new_size)
                
            if not packer.add(Cuboid(*free_split.coord, *new_size)):
                raise Exception('invalid split', Cuboid(*free_split.coord, *new_size))
        
            p = p * p_decay
        else:
            if not np.any(size < min_size):
                if verbose:
                    print('unexpected size', size)
                if not packer.add(Cuboid(*free_split.coord, *size)):
                    raise Exception('invalid split', Cuboid(*free_split.coord, *new_size))
            else:
                packer.free_splits.remove(free_split)

                if verbose:
                    print('wtf')
        
    return packer

def nongullotine_cut(size, lb, ub, p, p_decay, verbose=False, shuffle=False):
    splits = _nongullotine_cut(size, lb, ub, p, p_decay, verbose).splits
    splits = _split_sort(splits)
#     print('before', splits)
    if shuffle:
        splits = np.asarray(splits)
        rng.shuffle(splits)
        splits = list(splits)
#     print('after', splits)
    return splits
        
def test():
    print('gullotine_cut')
    
    packer = gullotine_cut((64, 64, 64), low, high, 0.0, 1.0)

    packer.render()

    print(packer.space_utilization())
    
    print('nongullotine_cut')
    
    packer = nongullotine_cut((64, 64, 64), low, high, 0.0, 1.0)

    packer.render()
    packer.render(free=True)
    
    r = Renderer()
    for i, box in enumerate(packer.splits):
        r.draw(box, color=(*(np.ones(3,)*i/(len(packer.splits) - 1)), 1.0))
               
    r.draw(Cuboid(0, 0, 0, *packer.size), color='red', mode='stroke')
    r.show()

    print(packer.space_utilization())