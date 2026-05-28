import networkx as nx
from database.DAO import DAO


class Model:
    def __init__(self):
        self._nodi = []
        self.grafo = nx.Graph()
        self.idMap = {}
        self.best_percorso = []

    def getRating(self):
        return list(DAO.getRatings())

    def creaGrafo(self, anno1, anno2):
        self._nodi = []
        self.grafo.clear()
        self.idMap.clear()

        self._nodi = DAO.getNodi(anno1, anno2)
        for n in self._nodi:
            self.idMap[n.id] = n

        self.grafo.add_nodes_from(self._nodi)

        archi = list(DAO.getArchiPesati(anno1, anno2))
        for a1, a2, peso in archi:
            if a1 in self.idMap and a2 in self.idMap:
                attore1 = self.idMap[a1]
                attore2 = self.idMap[a2]
                self.grafo.add_edge(attore1, attore2, weight=peso)

        archi.sort(key=lambda x: x[2], reverse=True)
        top5ConNome = []
        for id1, id2, peso in archi[:5]:
            nome_attore1 = self.idMap[id1].name
            nome_attore2 = self.idMap[id2].name
            top5ConNome.append((nome_attore1, nome_attore2, peso))

        return top5ConNome

    def getDettagliComponenti(self):
        num_comp = nx.number_connected_components(self.grafo)
        comp_maggiore = max(nx.connected_components(self.grafo), key=len)
        dim_comp_maggiore = len(comp_maggiore)
        return num_comp, dim_comp_maggiore, comp_maggiore

    def getInfo(self):
        return self.grafo.number_of_nodes(), self.grafo.number_of_edges()

    # --- RICORSIONE GLOBALE ---
    def getPercorsoPiuLungo(self):
        self.best_percorso = []

        # Ciclo su TUTTI i nodi del grafo provandoli come punto di partenza
        for nodo_partenza in self.grafo.nodes:
            parziale = [nodo_partenza]
            self.ricorsione_eta(parziale)

        return self.best_percorso

    def ricorsione_eta(self, parziale):
        # 1. Condizione di ottimalità
        if len(parziale) > len(self.best_percorso):
            self.best_percorso = list(parziale)

        # 2. Esplorazione dei vicini
        ultimo_nodo = parziale[-1]
        for vicino in self.grafo.neighbors(ultimo_nodo):
            if vicino not in parziale:
                # Regola: Età decrescente -> Data di nascita strettamente maggiore
                if vicino.date_of_birth is not None and ultimo_nodo.date_of_birth is not None:
                    if vicino.date_of_birth > ultimo_nodo.date_of_birth:
                        parziale.append(vicino)
                        self.ricorsione_eta(parziale)
                        parziale.pop()