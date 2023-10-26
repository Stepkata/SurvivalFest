import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
from matplotlib.colors import ListedColormap

noise1 = PerlinNoise(octaves=3)
noise2 = PerlinNoise(octaves=6)
noise3 = PerlinNoise(octaves=12)
noise4 = PerlinNoise(octaves=24)

def merge(list1, list2, list3, list4):
 
    merged_list = [(list1[i], list2[i], list3[i], list4[i]) for i in range(0, len(list1))]
     
    return merged_list

terrain = {
    'water' : (0, 0, 1),
    'forest' : (0, 0.6, 0),
    'grass' : (0, 1, 0),
    'swamp' : (0, 0.4, 0)
}

world = []
colors = [terrain['water'], terrain['forest'], terrain['grass'], terrain['swamp']]  # RGB values in the range [0, 1]
custom_cmap = ListedColormap(colors)

points = []
xpix, ypix = 200, 100
pic = []
for i in range(ypix):
    row = []
    for j in range(xpix):
        noise_val = noise1([i/xpix, j/ypix])
        noise_val += 0.5 * noise2([i/xpix, j/ypix])
        noise_val += 0.25 * noise3([i/xpix, j/ypix])
        noise_val += 0.125 * noise4([i/xpix, j/ypix])
        row.append(noise_val)
        points.append(((j, i), noise_val))
    pic.append(row)

maxv = max(points, key=lambda x: x[1])[1]
minv = min(points, key=lambda x: x[1])[1]

for ((x,y), value) in points:
    normalized = (value - minv) / (maxv - minv)
    (r,g,b,a) = custom_cmap(abs(normalized))
    world.append(((x,y), (r,g,b,a), list(terrain.keys())[list(terrain.values()).index((r,g,b))]))

with open('world.txt', 'w') as f:
    for item in world:
        f.write(str(item) + "\n")


#plt.imshow(pic, cmap=custom_cmap)

x, y = [], []
r, g, b, a = [], [], [], []

for (xi, yi), (ri, gi, bi, ai), name in world:
    x.append(xi)
    y.append(yi)
    r.append(ri)
    g.append(gi)
    b.append(bi)
    a.append(ai)

print(len(r))
# Create a scatter plot with RGBA colors
_, ax = plt.subplots(1,2)
ax[0].scatter(x, y, c=(merge(r, g, b, a)), s=1)
ax[0].set_aspect('equal', adjustable='box')
ax[1].imshow(pic, cmap=custom_cmap)
ax[1].set_aspect('equal', adjustable='box')

plt.show()