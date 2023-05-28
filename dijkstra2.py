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

#añadir dar color a los nodos adyacentes, variable para ver si hay que pintar el nodo destino seleccionado o no
def draw_graph(G, u, v, edge, iteration,visitados,adyacentes,destino):
    pos = nx.circular_layout(G)
    node_no_adyt = (0.7, 0.9, 1.0)
    dark_blue = (0.3, 0.5, 0.9)
    node_colors = ['green' if node == u else 'red' if node == v else 'violet' if node == destino else 'yellow' if node in visitados else dark_blue if node in adyacentes else node_no_adyt for node in G.nodes()]
    edge_colors = ['black' if e == edge else 'gray' for e in G.edges()]

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

    plt.title(f"Iteración {iteration}")

    # Imagen en variable
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='svg')
    img_buffer.seek(0)
    # Devolver el contenido del objeto BytesIO
    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')


def gen_graph(matriz_pesos):
    # Creamos el grafo
    G = nx.Graph()

    # Transformamos la matriz de pesos en un grafo 
    for i in range(len(matriz_pesos)):
        for j in range(len(matriz_pesos[0])):
            if matriz_pesos[i][j] != "null":
                G.add_edge(i, j, weight=int(matriz_pesos[i][j]))
    return G

def dijkstra(matriz_pesos,origen,destino):
    # Se trata la matriz de pesos para obtener un grafo G
    G = gen_graph(matriz_pesos)
    # Se comprueba que el grafo es conexo
    if not nx.is_connected(G):
         return json.dumps({"Error": "el grafo proporcionado es no conexo, compruebe la informacion proporcionada"}) 
    # Se inicializan la lista de distancias y predecesores
    D = np.full(G.number_of_nodes(), float('inf'))
    P = np.full(G.number_of_nodes(), None)
    # Se asigna valor 0 a la distancia al nodo origen
    D[origen] = 0
    # Se crea la lista Q que contendrá los nodos que faltan por visitarse
    Q = list(range(G.number_of_nodes()))
    # Se marca el nodo origen como visitado
    Q.remove(origen)
    # Se marca el nodo origen como activo
    activo = origen
    # Se crea una lista que contiene los nodos ya visitados añadiendo el nodo origen
    visitados = [origen]
    # Contador de iteraciones del bucle
    i = 0
    resultado = []

    while Q:
        iteracion = {"Iteracion":i, "D":[],"P":[],"Visitados":[],"No visitados":[],"imagenI":[],"imagenF":[]}
        imagen = draw_graph(G, activo,"", "",i,visitados,list(set(vecino for nodo in visitados for vecino in G.neighbors(nodo))),destino)
        iteracion["imagenI"].append(imagen)
        if activo == destino:
            break
        for n in G.neighbors(activo):
            if n in Q and D[activo] + G.get_edge_data(activo, n)['weight'] < D[n]:
                D[n] = D[activo] + G.get_edge_data(activo, n)['weight']
                P[n] = activo
        D_copia = D.copy()
        # Se ponen en infinito los nodos ya visitados para no volver a elegirlos
        for v in visitados:
            D_copia[v] = float('inf')
        posicion_minimo = np.argmin(D_copia)
        imagen = draw_graph(G, P[posicion_minimo], posicion_minimo, (P[posicion_minimo], posicion_minimo),i,visitados,list(set(vecino for nodo in visitados for vecino in G.neighbors(nodo))),destino)
        D_copia = [float(x) if x is not None else float('inf') if x is float('inf') else "null" for x in D]
        iteracion["D"].append(D_copia)
        P_copia = [int(x) if x is not None else "null" for x in P]
        iteracion["P"].append(P_copia)
        iteracion["imagenF"].append(imagen)
        i += 1
        activo = posicion_minimo
        Q.remove(activo)
        visitados.append(activo)
        if activo == destino:
            break
        iteracion["Visitados"].append(visitados)
        iteracion["No visitados"].append(Q)
        resultado.append(iteracion)
        
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
        'Iteraciones':resultado
    }
    return json.dumps(res, default=numpy_int64_to_int)

# Estas tres primeras variables serían el input de la función
matriz_pesos = [
    ["null", "3", "7","12", "null", "null"],        #s
    ["3", "null", "3", "null", "5", "null"],        #a
    ["7", "3", "null", "4", "5", "null"],           #b
    ["12","null", "4", "null", "6", "null"],        #c
    ["null", "5", "5", "6", "null", "6"],           #d
    ["null", "null", "null", "null", "6", "null"]   #e
]
origen = 0
destino = 4
resultado = dijkstra(matriz_pesos,origen,destino)
print(resultado)