import networkx as nx
# Create a directed graph (or undirected based on game design)

class Graphical_map():
    def __init__(self, locToRoutes):
        self.locToRoutes = locToRoutes
        self.G = nx.Graph()  # Initialize an empty graph
        self.create_graph()

    def create_graph(self):
        for current_loc, routes in enumerate(self.locToRoutes):
            if not routes:
                continue
            for dest, methods in routes:
                for method in methods:
                    if not self.G.has_edge(current_loc, dest):
                        self.G.add_edge(current_loc, dest, transport=[method])
                    else:
                        if method not in self.G[current_loc][dest]['transport']:
                            self.G[current_loc][dest]['transport'].append(method)

    def get_graph(self):
        return self.G