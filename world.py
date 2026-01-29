

class vec3:
    x, y, z = 0,0,0
    def __init__(self, _x, _y, _z):
        self.x, self.y, self.z = _x, _y, _z

gen = [

]
for x in range(10):
    for z in range(10):
        gen.append(vec3(x-5,0,z-5))

#for x in range(1000):
#    for z in range(1000):
#        gen.append(vec3(x, 0, z))