import numpy as np
import matplotlib.pyplot as plt

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
            ax.plot3D(xx, yy, [z] * 5, **kwargs)
            ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)
            ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
            ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)
            
        return color
    
    def show(self):
        return (self.fig)
        
def render(size, spaces, colors):
    r = Renderer()

    for box in spaces:
        colors[box] = r.draw(box, color=colors[box] if box in colors else None)

    r.draw(Cuboid(0, 0, 0, *size), color='red', mode='stroke')
    return r.show()
    
class SpacePartitioner:
    def __init__(self, size):
        self.size = size
        self.reset()
        self._colors = {}
        
    def reset(self):
        w, h, d = self.size
        self.free_splits = [Cuboid(0, 0, 0, w, h, d)]
        self.splits = []
        self.height_map = np.zeros((d, w), dtype=int)
        
    def fit(self, cuboid):
        outer = Cuboid(0, 0, 0, *self.size)
        
        if not outer.contain(cuboid):
            return False
        
        # print(len(self.splits), len(self.free_splits))
        if len(self.splits) < len(self.free_splits):
            for split in self.splits:
                if split.intersect(cuboid):
                    return False
            return True
        
        for split in self.free_splits:
            if split.contain(cuboid):
                return True
        return False
    
    def add(self, cuboid):
        if not self.fit(cuboid):
            return False
            
        self.splits.append(cuboid)
        
        (left, bottom, back), (right, top, front) = cuboid.bounding_box()
        cover = np.maximum(self.height_map[back:front, left:right], top)
        self.height_map[back:front, left:right] = cover
        
        partitions = []
        new_partitions = []
        for partition in self.free_splits:
            if partition.intersect(cuboid):
                new_partitions.extend(partition.split(cuboid))
            else:
                partitions.append(partition)
                
        n_partitions = len(partitions)
        # only overlapped partitions create smaller partitions
        # no need to check new_partition.contain(non_overlapped)
        for i in range(len(new_partitions)):
            contained = False
            
            partition = new_partitions[i]
            
            # possible to have contained partitions in new partitions
            for j in range(len(new_partitions)):
                # impossible to have two identical partitions
                # no need to check both a.contain(b) and b.contain(a)
                if i != j and new_partitions[j].contain(partition):
                    contained = True
                    break
                    
            if not contained:
                for j in range(n_partitions):
                    if partitions[j].contain(partition):
                        contained = True
                        break
            
            # preserve order
            if not contained:
                partitions.append(partition)
                
        self.free_splits = partitions
        
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
        return render(self.size, splits, self._colors)
    