# Routing Lib

A Python library for routing and graph-based pathfinding, including shortest-path algorithms, TSP heuristics, and data loaders.

## Features

- Load graphs from **JSON**, **CSV**, or **OSM** formats.  
- Core data structures: `Graph`, `Node`.  
- Shortest-path computation via **Dijkstra** (with optional target stopping).  
- Distance-matrix construction for subsets of stops.  
- Traveling Salesman Problem heuristics:  
  - Nearest-neighbor (`tsp_nn`)  
  - Local refinement via 2-opt (`tsp_2opt`)  
  - Exact solution for small sets using Held–Karp dynamic programming (`tsp_held_karp`)  
- Spatial utilities: `closest_pair` between two graphs using haversine metric + BallTree.  
- Graph visualization using Folium (nodes, edges, tours).  


## Installation

```bash
git clone https://github.com/leragogogo/routing_lib.git
cd routing_lib
pip install -r requirements.txt
```


## Data Sources
The following example datasets are too large for GitHub but can be downloaded here: [Google Drive link](https://drive.google.com/drive/folders/1_R7Gu4nAhIhvs0jxwZ32Ex2HaJ6MfSCQ?usp=sharing)

The folder contains Moabit(Berlin neighbourhood) network in JSON, CSV, and OSM format. 
Additionaly it contains Gesundbrunnen(Berlin neighbourhood) network in OSM format, 
so that the closest pair algorithm can be checked on two graphs.

## Usage 
Usage examples can be found in main.py. 
If you run main.py, the script will load three graphs from JSON, CSV, OSM files, 
perform on them three TSP algorithms(nn, 2-opt, Held-Karp), and visualize graphs and tours on a map.

The algorithms runs on the same graphs and on the same stops that are needed to be visited. 
Therefore, the difference in the final tour can be observed.

To run main.py download data sources from the previous section and put them in data/ folder.
Then:
```bash
python main.py
```

Or here are some common workflows:

### Load a graph

```python
from graph.loader.loader_factory import load_graph
from graph.loader.loader import JSONSource, LoadOptions

graph = load_graph(JSONSource("data/city.json"), LoadOptions(strategy="largest"))
```
### Compute distance matrix and solve TSP

```python
from algorithms.distance_matrix import distance_matrix
from algorithms.tsp_nn import tsp_nn
from algorithms.tsp_2opt import tsp_2opt

stops = ["A", "B", "C", "D"]
D, node_to_index, index_to_node, paths = distance_matrix(graph, stops)

# Nearest-neighbor heuristic
tour, length = tsp_nn(stops, D, node_to_index, start=stops[0], return_to_start=True)

# Refine with 2-opt
tour2, length2 = tsp_2opt(D, node_to_index, tour, length)

print("NN Tour:", tour, "Length:", length)
print("2-opt Tour:", tour2, "Length:", length2)

```

### Find closest nodes between two graphs
```python
from algorithms.closest_pair import closest_pair

node1, node2, dist_m = closest_pair(graph1, graph2)
print(f"Closest pair: {node1} ↔ {node2}, distance ≈ {dist_m:.2f} m")
```

### Visualization
```python
from graph.visualizer import GraphVisualizer

viz = GraphVisualizer()
viz.add_graph(graph)
viz.add_tour(graph, tour2, paths, length2)
viz.save_file("map.html")
```

