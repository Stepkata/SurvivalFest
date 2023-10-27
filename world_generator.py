import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
from matplotlib.colors import ListedColormap

noise1 = PerlinNoise(octaves=3)
noise2 = PerlinNoise(octaves=6)
noise3 = PerlinNoise(octaves=12)
noise4 = PerlinNoise(octaves=24)


terrain = {
    (0, 0, 1)  :'water' ,
    (0, 0.6, 0):'swamp',
    (0, 1, 0)  :'grass' ,
    (0, 0.4, 0):'forest' 
}

colors = terrain.keys() # RGB values in the range [0, 1]
custom_cmap = ListedColormap(colors)

def generateWorld(xpix = 200, ypix = 100):
    world = {}

    points = []

    #pic = []
    for i in range(ypix):
        #row = []
        for j in range(xpix):
            noise_val = noise1([i/xpix, j/ypix])
            noise_val += 0.5 * noise2([i/xpix, j/ypix])
            noise_val += 0.25 * noise3([i/xpix, j/ypix])
            noise_val += 0.125 * noise4([i/xpix, j/ypix])
            #row.append(noise_val)
            points.append(((j, i), noise_val))
        #pic.append(row)

    maxv = max(points, key=lambda x: x[1])[1]
    minv = min(points, key=lambda x: x[1])[1]

    for ((x,y), value) in points:
        normalized = (value - minv) / (maxv - minv)
        (r,g,b,a) = custom_cmap(abs(normalized))
        world[(x,y)] = ((r,g,b,a), terrain[(r,g,b)])

    #plt.imshow(pic, cmap=custom_cmap)

    #plt.show()

    return world

#generateWorld()