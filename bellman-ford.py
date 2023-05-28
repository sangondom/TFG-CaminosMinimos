import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import io
import json
import base64 

def numpy_int64_to_int(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError(repr(o) + " is not JSON serializable")

def gen_new_graph(G, origen, P):
    nuevo_grafo = nx.DiGraph()
    nuevo_grafo.add_nodes_from(G.nodes)  # Agregar todos los nodos al nuevo grafo
    
    # Recorrer la lista de predecesores y agregar las aristas correspondientes con sus pesos
    for i, predecesor in enumerate(P):
        if i != origen:  # Ignorar el nodo origen
            peso = G[predecesor][i]["weight"]  # Obtener el peso de la arista en el grafo original
            nuevo_grafo.add_edge(predecesor, i, weight=peso)  # Agregar la arista con el peso
            
    return nuevo_grafo

#añadir dar color a los nodos adyacentes, variable para ver si hay que pintar el nodo destino seleccionado o no
def draw_graph(G,origen):
    pos = nx.circular_layout(G)
    dark_blue = (0.3, 0.5, 0.9)
    node_colors = ['green' if node == origen else dark_blue for node in G.nodes()]
    edge_colors = ['black' for e in G.edges()]

    # Dibujar las aristas con los colores correspondientes antes de dibujar los nodos
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors)

    edge_labels = {(n1, n2): G[n1][n2]['weight'] for n1, n2 in G.edges()}

    # Modificar el parámetro label_pos para ajustar el espaciado de las etiquetas de peso
    label_pos = nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.4)

    # Ajustar el espaciado entre las etiquetas de peso
    for (_, text) in label_pos.items():
        text.set_rotation('horizontal')

    node_labels = {node: str(node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels)

    plt.title("Grafo caminos mínimos")

    # Imagen en variable
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='svg')
    img_buffer.seek(0)
    # Devolver el contenido del objeto BytesIO
    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')

def gen_digraph(matriz_pesos):
    # Creamos el grafo
    G = nx.DiGraph()

    # Transformamos la matriz de pesos en un grafo 
    for i in range(len(matriz_pesos)):
        for j in range(len(matriz_pesos[0])):
            if matriz_pesos[i][j] != "null":
                G.add_edge(i, j, weight=int(matriz_pesos[i][j]))
    return G

def bellman(matriz_pesos,origen):
    G = gen_digraph(matriz_pesos)
    # Se inicializan la lista de distancias y predecesores
    D = np.full(G.number_of_nodes(), float('inf'))
    P = np.full(G.number_of_nodes(), None)
    # Se asigna valor 0 a la distancia al nodo origen
    D[origen] = 0
    resultado = []
    for i in range(G.number_of_nodes()-1):
        iteracion = {"Iteracion":i, "D":[],"P":[]}
        modificado = False
        for u,v in G.edges():
            if D[v] > D[u] + G.get_edge_data(u, v)['weight']:
                D[v] = D[u] + G.get_edge_data(u, v)['weight']
                P[v] = u
                modificado = True
        D_copia = [float(x) if x is not None else float('inf') if x is float('inf') else "null" for x in D]
        iteracion["D"].append(D_copia)
        P_copia = [int(x) if x is not None else "null" for x in P]
        iteracion["P"].append(P_copia)
        resultado.append(iteracion)
        if modificado == False:
            break
    for u,v in G.edges():
        if D[v] > D[u] + G.get_edge_data(u, v)['weight']:
            return False
    imagen = draw_graph(gen_new_graph(G,origen,P),origen)
    D_list = D.tolist()
    P_list = P.tolist()
    P_list = [int(x) if x is not None else None for x in P_list]
    for iteracion in resultado:
        iteracion["D"] = [float(x) if x is not None else float('inf') if x == float('inf') else None for x in iteracion["D"][0]]
        iteracion["P"] = [int(x) if x is not None and x != "null" else None for x in iteracion["P"][0]]
    res = {
        'D': D_list,
        'P': P_list,
        'Numero iteraciones':i,
        'Iteraciones':resultado,
        'Imagen resultado': imagen
    }
    return json.dumps(res, default=numpy_int64_to_int)
            
            


# Estas dos primeras variables serían el input de la función
matriz_pesos = [
    ["null", "3", "7","12", "null", "4"],        #s
    ["3", "null", "3", "null", "5", "null"],        #a
    ["7", "3", "null", "4", "5", "null"],           #b
    ["12","null", "4", "null", "6", "null"],        #c
    ["null", "5", "5", "6", "null", "6"],           #d
    ["4", "null", "null", "null", "6", "null"]   #e
]
origen = 0
D = bellman(matriz_pesos,origen)
print(D)
