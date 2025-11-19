import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
import itertools
import random

from geometry import Cuboid

class Renderer:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        plt.close()
        
    def clear(self):
        self.ax.clear()
        
    def draw(self, box, color=None, mode='fill'):
        if color is None:
            color = (*np.random.random((3,)) * 0.7 + 0.3, 0.6)
            
        ax = self.ax
        x, y, z = box.left, box.back, box.bottom
        dx, dy, dz = box.width, box.depth, box.height
        if mode == 'fill':
            xx = np.linspace(x, x + dx, 2)
            yy = np.linspace(y, y + dy, 2)
            zz = np.linspace(z, z + dz, 2)

            xx, yy = np.meshgrid(xx, yy)

            l1, l2 = xx.shape
            z0 = np.ones([l1, l2]) * z
            ax.plot_surface(xx, yy, z0, color=color)
            ax.plot_surface(xx, yy, z0 + dz, color=color)

            yy, zz = np.meshgrid(yy, zz)
            ax.plot_surface(x, yy, zz, color=color)
            ax.plot_surface(x + dx, yy, zz, color=color)

            xx, zz = np.meshgrid(xx, zz)
            ax.plot_surface(xx, y, zz, color=color)
            ax.plot_surface(xx, y + dy, zz, color=color)
        elif mode == 'stroke':
            xx = [x, x, x + dx, x + dx, x]
            yy = [y, y + dy, y + dy, y, y]
            kwargs = {'alpha': 1, 'color': color}
            ax.plot3D(xx, yy, [z]*5, **kwargs)
            ax.plot3D(xx, yy, [z + dz]*5, **kwargs)
            ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
            ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)
            
        return color
    
    def show(self):
        display(self.fig)
        
def render(size, spaces):
    r = Renderer()

    for box in spaces:
        r.draw(box)

    r.draw(Cuboid(0, 0, 0, *size), color='red', mode='stroke')
    r.show()
    
def first_fit(boxes, item, boxspace):
    size = np.asarray(item)
    for box in boxes:
        if np.all(box.size >= size):
            return box
    return None
    
class BinPacker:
    def __init__(self, size, fitness=first_fit):
        self.size = size
        self.fitness = fitness
        self.reset()
        
    def reset(self):
        w, h, d = self.size
        self.free_splits = [Cuboid(0, 0, 0, w, h, d)]
        self.splits = []
        self.height_map = np.zeros((d, w), int)
        
    def fit(self, cuboid):
        outer = Cuboid(0, 0, 0, *self.size)
        if not outer.contain(cuboid):
            return False
        
        for split in self.splits:
            if split.intersect(cuboid):
                return False
        
        return True
    
    def add(self, cuboid):
        if not self.fit(cuboid):
            return False
            
        self.splits.append(cuboid)
        
        (left, bottom, back), (right, top, front) = cuboid.bounding_box()
        cover = np.maximum(self.height_map[back:front, left:right], top)
        self.height_map[back:front, left:right] = cover
        
        free_splits = [split for free_split in self.free_splits for split in free_split.split(cuboid)]
        
        removed = []
        for a, b in itertools.combinations(free_splits, 2):
            if a.contain(b):
                removed.append(b)
            elif b.contain(a):
                removed.append(a)
                
        self.free_splits = [split for split in free_splits if split not in removed]
        
        return True
    
    def space_utilization(self):
        used = np.sum([split.volume for split in self.splits])
        
        free = []
        for free_split in self.free_splits:
            new_splits = [free_split]
            for added in free:
                new_splits = [split for new_split in new_splits for split in new_split.split(added, False)]
            free.extend(new_splits)
        free = np.sum([split.volume for split in free])
        if used + free != np.prod(self.size):
            raise Exception('wtf')
        
        return used / np.prod(self.size)
        
    def render(self, free=False):
        if free:
            splits = self.free_splits
        else:
            splits = self.splits
        return render(self.size, splits)