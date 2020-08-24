import pandas as pd
from pandas import DataFrame
from haversine import haversine
from geopy.geocoders import Nominatim
import networkx as nx
from staticmap import *
import collections
import json

# Named tuple amb atributs latitud i longitud
Coord = collections.namedtuple('Coord', 'lat lon')

# Precondicio: El graf ja conte tots els nodes estacions.
# Input: Graf d'estacions
# Output: Vertexs del requadre de coordenades on s'hi encabeixen totes les
#         estacions funcionables.
# Invariant: A cada iteracio sabem els vertexs del graf recorregut fins llavors
'''
   ·-------.        ·-------.---
   | ·   .·|   ·    | ·   .·   ·|
   | . · . |  ----> | . · .     |
   -----·---        -----·-------
'''


def bbox(G):
    max_lat, min_lat, max_lon, min_lon = -1, -1, -1, -1
    for node in G:
        if (max_lat == -1 or max_lat < node.lat):
            max_lat = node.lat
        if (min_lat == -1 or min_lat > node.lat):
            min_lat = node.lat
        if (max_lat == -1 or max_lon < node.lon):
            max_lon = node.lon
        if (min_lon == -1 or min_lon > node.lon):
            min_lon = node.lon
    return max_lat, min_lat, max_lon, min_lon


# Funcio que utilitzant els límits del graf col·loca els nodes en quadrats de
# mida de la distància.
# Aquesta manera optimitza la cerca d'estacions ja que només cal mirar aquelles
# que estan aprop.
# Precondicio: El graf ja conte els nodes.
# Input: El graf i els límits de la graella on s'hi encabeix.
# Output: Vector de tres dimensions: en cada zona mod(dist) hi ha la llista
#         d'estacions que hi pertanyen
'''
       |--------num_cols*dist--------| ___
       |¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|  |                   ..
       |¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|  |                _  |X posicio: 0 <= i < nr , 0 <= j < nc
       |¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨| num_row *dist    |X| |llista de les estacions
       |¨|¨|¨|¨|¨|¨|¨|¨|X|¨|¨|¨|¨|¨|¨|  |                ¨  |que compleixen |num_row mod(dist) = i
       |¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨|¨| _|_                  ··              |num_cols mod(dist) = j
       ¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
'''


def distribution(G, columns, rows, max_lat, min_lon, d_meters):
    matrix = [[[] for i in range(columns)]for i in range(rows)]
    for node in G:
        i = int(haversine((max_lat, min_lon), (node.lat, min_lon)) // d_meters)
        j = int(haversine((max_lat, min_lon), (max_lat, node.lon)) // d_meters)
        matrix[i][j].append(node)
    return matrix

# La Funcio determina les estacions que s'han de connectar
# d'un quadrant a un altre
# Precondicio: Cal tenir una matriu de distribucio que permet saber les
#              estacions properes
# Input: ens cal l'ubicacio dels dos quadrants, el graf i la seva matriu
#        de distribucio i la dist.
# Output: ens retornen les estacions visitades amb les
#         seves corresponents arestes.
''' ____ ____ ........
   | X  |  · | --
   |____|_·__| |  estem a X: els quadrats propers tambe tenen candidats.
   |. . |·   | |  cal que comprovem si es poden connectar amb alguna estacio
   |____|____| --  del quadrat actual(a,b)
   |----|
   .    -distancia del graf (constant)
   :
'''


def make_edges(G, a, b, I, J, columns, rows, matrix, d_meters):
    if(I >= 0 and J >= 0 and I < rows and J < columns):
        for station1 in matrix[a][b]:
            for station2 in matrix[I][J]:
                distance = haversine((station1.lat, station1.lon),
                                     (station2.lat, station2.lon))
                if distance <= d_meters and station1 != station2:
                    # S'afegeixen totes les estacions de ruta en bicicleta
                    G.add_edge(station1, station2, weight=distance*6)
    return G

# Creacio d'un nou graf amb conneccions de distancia >= donada per l'usuari
# (o 1000 per defecte)
# Input: distancia maxima de connexio
# Es llegeix la base de dades del bicing per saber info de les estacions
# Output: Graf de nodes compresos d'estacions del bicing connectades
#         si nomes si estan a < d


def new_graph(d):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'],
                                       index='station_id')

    G = nx.Graph()
    d_meters = d/1000  # Conversion from meters to kilometers.

    for station in bicing.itertuples():
        G.add_node(station)

    max_lat, min_lat, max_lon, min_lon = bbox(G)

    columns = int((haversine((max_lat, min_lon),
                  (max_lat, max_lon))) // d_meters + 1)
    rows = int((haversine((max_lat, min_lon),
               (min_lat, min_lon))) // d_meters + 1)

    matrix = distribution(G, columns, rows, max_lat, min_lon, d_meters)

    # Nomes cal mirar 5 caselles des d'on ens trobem: ja s'hauran visitat,
    # les arestes no son bidireccionals.
    for i in range(rows):
        for j in range(columns):
            make_edges(G, i, j, i, j, columns, rows, matrix, d_meters)
            make_edges(G, i, j, i-1, j, columns, rows, matrix, d_meters)
            make_edges(G, i, j, i, j+1, columns, rows, matrix, d_meters)
            make_edges(G, i, j, i+1, j+1, columns, rows, matrix, d_meters)
            make_edges(G, i, j, i-1, j+1, columns, rows, matrix, d_meters)
    return G

# Nombre de nodes


def number_nodes(G):
    return (G.number_of_nodes())

# Nombre d'arestes


def number_edges(G):
    return (G.number_of_edges())

# Nombre de components connexes


def components(G):
    return(nx.number_connected_components(G))

# Mapa de barcelona


def mapa(G, name):
    mapa = StaticMap(500, 500)

    # Pintem els marcadors
    for node in G.nodes:
        coord = (node.lon, node.lat)
        border = CircleMarker(coord, 'black', 6)
        marker = CircleMarker(coord, 'red', 4)
        mapa.add_marker(border)
        mapa.add_marker(marker)

    # Pintem les linies
    for edge in G.edges:
        coord1 = (edge[0].lon, edge[0].lat)
        coord2 = (edge[1].lon, edge[1].lat)
        mapa.add_line(Line((coord1, coord2), 'blue', 1))

    image = mapa.render()
    image.save(name)

# Converteix adreces postals en coordenades
# Input: dues adreces qualssevulla.
# Output: si l'adreça existeix i està registrada


def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent="bicing_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return ((location1.latitude, location1.longitude),
                (location2.latitude, location2.longitude))
    except:
        return None

# Dibuixa la ruta demanada en un mapa guardat com arxiu imatge


def plot_route_graph(min_route, name):
    mapa_ruta = StaticMap(500, 500)

    for node in min_route:
        coord = (node.lon, node.lat)
        border = CircleMarker(coord, 'black', 8)
        marker = CircleMarker(coord, 'green', 5)
        mapa_ruta.add_marker(border)
        mapa_ruta.add_marker(marker)

    for i in range(len(min_route)-1):
        coord1 = (min_route[i].lon, min_route[i].lat)
        coord2 = (min_route[i+1].lon, min_route[i+1].lat)
        mapa_ruta.add_line(Line((coord1, coord2), 'black', 1))

    ruta = mapa_ruta.render()
    ruta.save(name)

# La funcio estima el temps que tardara l'usuari a arribar al
# seu desti utilitzant la ruta trobada
# Input: calen, el graf que conté les coordenades de les estacions,
#        la ruta mínima i dist(origen, destí)
# Output: es retornen dos valors: hores i minuts.


def time(G, min_route, dist):
    av_time, h, m, n = 0, 0, 0, len(min_route)
    if n == 2:
        av_time = dist*15
    else:
        av_time = haversine((min_route[0].lat, min_route[0].lon),
                            (min_route[1].lat, min_route[1].lon))*15
        i = 1
        while i < n-2:
            av_time = av_time + haversine((min_route[i].lat,
                                           min_route[i].lon),
                                          (min_route[i+1].lat,
                                           min_route[i+1].lon))*6
            i += 1
        av_time = av_time + haversine((min_route[n-2].lat,
                                       min_route[n-2].lon),
                                      (min_route[n-1].lat,
                                       min_route[n-1].lon))*15

    if(av_time >= 60):
        h = av_time // 60
        m = av_time % 60
        return int(h), int(m)
    else:
        return int(h), int(av_time)

# La funcio calcula la ruta mes rapida entre una ubicacio d'origen i
# una d'arribada.
# Precondicio: Les dues adreces han d'existir per trobar una ruta.
# Input: El graf, les noves coordenades i el nom de l'arxiu
#        on es guardara la ruta.
# Output: La ruta es guarda en un arxiu i es retorna el
#         temps estimat de duració.
'''         .___.___.
    X --> ./ \./ \__| --> X
 ORIGEN     GRAF      DESTINACIO
   |-----distancia maxima-----|
S'afegeixen dos nodes nous connectats amb les estacions més properes que O/D
Sabem que la ruta pot ser:
- O : A peu -----> Bicicleta ------> A peu : D
- O : ------ A peu ------> : D
A totes les arestes noves se'ls afegeix d'atribut el temps tardat caminant.
Llavors l'algorisme de Dikstra recorre el graf per trobar la millor ruta.
'''


def shortest_route(G, coords, name):
    coord1, coord2 = coords
    source = Coord(lat=coord1[0], lon=coord1[1])
    end = Coord(lat=coord2[0], lon=coord2[1])

    maxdist = haversine(source, end)

    G.add_nodes_from([source, end])

    for node in G.nodes:
        dist_from_source = haversine((node.lat, node.lon),
                                     (source.lat, source.lon))
        dist_from_end = haversine((node.lat, node.lon), (end.lat, end.lon))
        if(dist_from_source <= maxdist and dist_from_source != 0):
            G.add_edge(source, node, weight=dist_from_source*15)
        if(dist_from_end <= maxdist and dist_from_end != 0):
            G.add_edge(end, node, weight=dist_from_end*15)

    min = nx.dijkstra_path(G, source, end)

    plot_route_graph(min, name)
    G.remove_nodes_from([source, end])

    return time(G, min, maxdist)


def Nodes_of_graf(G):
    list = []
    for node in G.nodes():
        list.append(node[0])
    return list


def flow(G, rb, rd):
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    bikes = DataFrame.from_records(pd.read_json(url_status)
                                   ['data']['stations'], index='station_id')

    DG = nx.DiGraph()
    DG.add_node('TOP')  # The green node
    demand = 0

    for station in bikes.itertuples():
        idx = station.Index
        if idx not in Nodes_of_graf(G):
            continue
        stridx = str(idx)
        # The blue (s), black (g) and red (t) nodes of the graph
        s_idx, g_idx, t_idx = 's'+stridx, 'g'+stridx, 't'+stridx
        DG.add_node(g_idx)
        DG.add_node(s_idx)
        DG.add_node(t_idx)

        b, d = station.num_bikes_available, station.num_docks_available
        req_bikes = max(0, int(rb) - b)
        req_docks = max(0, int(rd) - d)

        DG.add_edge('TOP', s_idx)
        DG.add_edge(t_idx, 'TOP')
        DG.add_edge(s_idx, g_idx)
        DG.add_edge(g_idx, t_idx)

        if req_bikes > 0:
            demand += req_bikes
            DG.nodes[t_idx]['demand'] = req_bikes
            DG.edges[s_idx, g_idx]['offer'] = 0
        elif req_docks > 0:
            demand -= req_docks
            DG.nodes[s_idx]['demand'] = -req_docks
            DG.edges[g_idx, t_idx]['offer'] = 0

    DG.nodes['TOP']['demand'] = -demand

    for edge in G.edges():
        first = edge[0]
        second = edge[1]
        ID1 = first[0]
        ID2 = second[0]
        dist = G[first][second]['weight']*10
        DG.add_edge('g'+str(ID1), 'g'+str(ID2),
                    cost=int(1000*dist), weight=dist)
        DG.add_edge('g'+str(ID2), 'g'+str(ID1),
                    cost=int(1000*dist), weight=dist)

    # This variable will indicate if a solution can be found
    err = True

    try:
        Fc, Fd = nx.network_simplex(DG, weight='cost')

    except nx.NetworkXUnfeasible:
        err = False
        return err, 0, 0

    if err:
        total = 0
        first = True
        for sd in Fd:
            if sd[0] != 'g':
                continue
            sd_ID = int(sd[1:])
            for dst, a in Fd[sd].items():
                if dst[0] == 'g' and a > 0:
                    dt_ID = int(dst[1:])
                    total += DG.edges[sd, dst]['weight']
                    w_aresta = (DG.edges[sd, dst]['weight'] * a,
                                sd_ID, dt_ID)
                    if first:
                        first = False
                        maxim = w_aresta
                    elif w_aresta[0] > maxim[0]:
                        maxim = w_aresta
        if total == 0:
            return err, total, 0
        return err, str(int(total)), str(int(maxim[0]))
