import networkx as nx
import matplotlib.pyplot as plt
import sys
sys.path.append('.')

from graph import Graphical_map
from routes import get_routes, get_locations, MAPSIZE

locToRoutes = get_routes()
G = Graphical_map(locToRoutes).get_graph()

positions = get_locations()

# Transport type to color mapping
transport_color_map = {
    'taxi': 'gold',
    'bus': 'green',
    'underground': 'red',
    'black': 'black',
}

img = plt.imread('./map.jpg')

fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img, extent=[0, MAPSIZE[0], 0, MAPSIZE[1]])
ax.set_xlim(0, MAPSIZE[0])
ax.set_ylim(0, MAPSIZE[1])

# Draw nodes    
nx.draw_networkx_nodes(G, positions, node_size=150, node_color='skyblue', edgecolors='black')
nx.draw_networkx_labels(G, positions, font_size=5, font_weight='bold')


plt.title("Scotland Yard - City Map Graph")
plt.axis('off')
plt.tight_layout()
plt.show()