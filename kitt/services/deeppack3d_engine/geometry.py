import numpy as np

def Point3D(x, y, z):
    return np.asarray((x, y, z))

class Cuboid:
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
    
    @property
    def left(self):
        return self.x
    
    @property
    def right(self):
        return self.x + self.width
    
    @property
    def bottom(self):
        return self.y
    
    @property
    def top(self):
        return self.y + self.height
    
    @property
    def back(self):
        return self.z
    
    @property
    def front(self):
        return self.z + self.depth
        
    @property
    def volume(self):
        return self.width * self.height * self.depth
    
    @property
    def size(self):
        return (self.width, self.height, self.depth)
    
    @property
    def coord(self):
        return (self.x, self.y, self.z)
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        yield self.width
        yield self.height
        yield self.depth
        
    def __repr__(self):
        return f'Cuboid({self.x}, {self.y}, {self.z}, {self.width}, {self.height}, {self.depth})'
    
    def bounding_box(self):
        min_coords = Point3D(self.left, self.bottom, self.back)
        max_coords = Point3D(self.right, self.top, self.front)
        return min_coords, max_coords
    
    def copy(self):
        return Cuboid(*self)
    
    def intersect(self, other, edge=False):
        if edge:
            return (
                (self.left <= other.right and self.right >= other.left) and
                (self.back <= other.front and self.front >= other.back) and
                (self.bottom <= other.top and self.top >= other.bottom)
            )
        else:
            return (
                (self.left < other.right and self.right > other.left) and
                (self.back < other.front and self.front > other.back) and
                (self.bottom < other.top and self.top > other.bottom)
            )
        
    def contain(self, other):
        return (
            (self.left <= other.left and self.right >= other.right) and
            (self.back <= other.back and self.front >= other.front) and
            (self.bottom <= other.bottom and self.top >= other.top)
        )
    
    def split(self, other, maximal=True):
        if not self.intersect(other):
            return [self]
        
        x, y, z, width, height, depth = self
        cuboids = []
        
        if maximal:
            if self.left < other.left:
                cuboids.append(Cuboid(self.left, y, z, other.left - self.left, height, depth))
            if self.right > other.right:
                cuboids.append(Cuboid(other.right, y, z, self.right - other.right, height, depth))
            if self.bottom < other.bottom:
                cuboids.append(Cuboid(x, self.bottom, z, width, other.bottom - self.bottom, depth))
            if self.top > other.top:
                cuboids.append(Cuboid(x, other.top, z, width, self.top - other.top, depth))
            if self.back < other.back:
                cuboids.append(Cuboid(x, y, self.back, width, height, other.back - self.back))
            if self.front > other.front:
                cuboids.append(Cuboid(x, y, other.front, width, height, self.front - other.front))
        else:
            if self.left < other.left:
                width -= other.left - self.left
                x = other.left
                cuboids.append(Cuboid(self.left, y, z, other.left - self.left, height, depth))
            if self.right > other.right:
                width -= self.right - other.right
                cuboids.append(Cuboid(other.right, y, z, self.right - other.right, height, depth)) 
            if self.bottom < other.bottom:
                height -= other.bottom - self.bottom
                y = other.bottom
                cuboids.append(Cuboid(x, self.bottom, z, width, other.bottom - self.bottom, depth))
            if self.top > other.top:
                height -= self.top - other.top
                cuboids.append(Cuboid(x, other.top, z, width, self.top - other.top, depth))
            if self.back < other.back:
                depth -= other.back - self.back
                z = other.back
                cuboids.append(Cuboid(x, y, self.back, width, height, other.back - self.back))
            if self.front > other.front:
                depth -= self.front - other.front
                cuboids.append(Cuboid(x, y, other.front, width, height, self.front - other.front))
        
        return cuboids
            
    def fit(self, item):
        width, height, depth = item
        return self.width >= width and self.height >= height and self.depth >= depth