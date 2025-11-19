import numpy as np
from split_gen import *

class ItemGenerator:
    def __init__(self, k=1):
        assert 0 < k, f'invalid argument k={k}'
        self.k = k
        
    def reset(self): 
        raise Exception('not implemened')
        
    def peek(self):
        # lookahead incoming (k) items
        items = self._items
        while len(items) < self.k:
            try:
                item = next(self._item_iter)
            except:
                item = None
            items.append(item)
        return items
        
    def grab(self, n=0):
        assert 0 <= n < self.k, f'invalid argument n={n}'
        return self.peek().pop(n)

class FileConveyor(ItemGenerator):
    def __init__(self, k=1, path='./input.txt'):
        super().__init__(k)

        self.path = path
        
        self._items = None
        self._item_iter = None

        self.loaded = False
        
    def _iter(self):
        with open(self.path, 'r') as file:
            for line in file.readlines():
                w, h, d = map(int, line.split(' '))
                yield w, h, d
        
    def reset(self):
        if not self.loaded:
            self.loaded = True
            self.buffer = []
            self._items = []
            self._item_iter = self._iter()
        return self

class InputConveyor(ItemGenerator):
    def __init__(self, k=1):
        super().__init__(k)
        
        self._items = None
        self._item_iter = None

        self.loaded = False
        
    def _iter(self):
        while True:
            try:
                input_str = input('item: ')
                if input_str == '-1':
                    break
                w, h, d = map(int, input_str.split(' '))
                yield (w, h, d)
            except KeyboardInterrupt:
                break
            except:
                print(f'invalid format. each line must contain [w: int] [h: int] [d: int]')
                print(f'for example: 4 5 6')
                continue
        
    def reset(self):
        if not self.loaded:
            self.loaded = True
            self.buffer = []
            self._items = []
            self._item_iter = self._iter()
        return self

class Conveyor(ItemGenerator):
    def __init__(self, k=1, prealloc_bins=0, prealloc_items=0, max_items=None, max_spaces=None, size=(32, 32, 32), lb=(6, 6, 6), ub=(12, 12, 12), p=0.0, p_decay=1.0, shuffle=False, assigned_items=None):
        super().__init__(k)
        
        self._items = None
        self._item_iter = None
        
        self.max_items = max_items
        self.max_spaces = max_spaces
        
        if self.max_spaces is not None and self.prealloc_bins > self.max_spaces:
            raise Exception('self.prealloc_bins > max_spaces')
        
        self.prealloc_bins = prealloc_bins
        self.prealloc_items = prealloc_items
        self.buffer = None
        
        self.assigned_items = assigned_items
        
        self.split_generator = lambda: nongullotine_cut(size, lb, ub, p, p_decay, shuffle=shuffle)
        
    def _iter(self):
        if self.assigned_items is not None:
            for item in (np.asarray(item) for item in self.assigned_items):
                yield item
            return
        
        n_items = 0
        n_spaces = 0
        
        for split in self.buffer:
            n_items += 1
            if self.max_items is not None and n_items > self.max_items:
                return
            yield np.asarray(split.size)
        n_spaces += self.prealloc_bins
        
        while True:
            n_spaces += 1
            if self.max_spaces is not None and n_spaces > self.max_spaces:
                return
                
            splits = self.split_generator()
            for split in splits:
                n_items += 1
                if self.max_items is not None and n_items > self.max_items:
                    return
                yield np.asarray(split.size)

    def dump(self, n_items, path):
        self.reset()
        file = open(path, 'w')
        for _ in range(n_items):
            print(' '.join(map(str, self.grab())), file=file)
        file.close()
        
    def reset(self):
        self.buffer = [] # consistent rng
        for i in range(self.prealloc_bins):
            self.buffer.extend(self.split_generator())
        
        while len(self.buffer) < self.prealloc_items:
            self.buffer.extend(self.split_generator())
            
        self._items = []
        self._item_iter = self._iter()
        return self
    
def rotated_sizes(item, rotate=True, remove_duplicate=True):
    if rotate is True:
        rotate = 'xyz'
    elif rotate is False:
        rotate = ''
    
    w, h, d = item
    sizes = [(w, h, d)]
    if 'x' in rotate:
        sizes.extend((w, d, h) for w, h, d in sizes[:])
    if 'y' in rotate:
        sizes.extend((d, h, w) for w, h, d in sizes[:])
    if 'z' in rotate:
        sizes.extend((h, w, d) for w, h, d in sizes[:])
            
    if remove_duplicate:
        sizes = list(set(sizes))
        
    return sizes