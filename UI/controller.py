import flet as ft


class Controller:
    def __init__(self, view, model):
        self._view = view
        self._model = model

    def fillDDsRating(self):
        self._view._ddrating1.options.clear()
        self._view._ddrating2.options.clear()
        for r in self._model.getRating():
            self._view._ddrating1.options.append(ft.dropdown.Option(str(r)))
            self._view._ddrating2.options.append(ft.dropdown.Option(str(r)))

    def handleCreaGrafo(self, e):
        # 1. Controllo di selezione
        if self._view._ddrating1.value is None or self._view._ddrating2.value is None:
            self._view.txt_result.clean()
            self._view.txt_result.controls.append(
                ft.Text("Errore: per definire un range di valutazione, è necessario selezionare i due valori!",
                        color="red"))
            self._view.update_page()
            return

        # 2. Cast esplicito a float
        anno1 = float(self._view._ddrating1.value)
        anno2 = float(self._view._ddrating2.value)

        # 3. Controllo logico
        if anno1 >= anno2:
            self._view.txt_result.clean()
            self._view.txt_result.controls.append(
                ft.Text("Errore: è necessario che il range sia definito da Valore 1 < Valore 2!", color="red"))
            self._view.update_page()
            return

        # 4. Creazione Grafo
        self._view.txt_result.clean()
        self._view.txt_result.controls.append(
            ft.Text(f"Creazione grafo a partire dal range di valutazione: ({anno1}) - ({anno2})...", color="green"))
        self._view.update_page()

        top5 = self._model.creaGrafo(anno1, anno2)

        # 5. Output dei risultati getInfo
        n_nodi, n_archi = self._model.getInfo()
        self._view.txt_result.controls.append(ft.Text(f"Grafo creato con successo!", color="green"))
        self._view.txt_result.controls.append(ft.Text(f"Nodi: {n_nodi}", color="green"))
        self._view.txt_result.controls.append(ft.Text(f"Archi: {n_archi}", color="green"))

        for nome1, nome2, peso in top5:
            self._view.txt_result.controls.append(
                ft.Text(f"{nome1} ---> {nome2} | somma denaro film insieme = {peso} $", color="purple"))

        # 6. Output Componenti Connesse
        numCompConnesse, dimensioneComponenteConnessaMax, componenteConnessaMax = self._model.getDettagliComponenti()
        self._view.txt_result.controls.append(ft.Text(
            f"Componenti connesse: {numCompConnesse} ; dimensione comp connessa max è {dimensioneComponenteConnessaMax} sotto..."))

        for c in componenteConnessaMax:
            self._view.txt_result.controls.append(ft.Text(c.name))

        self._view.update_page()

    def handleCammino(self, e):
        # 1. Messaggio di attesa nella ListView
        self._view.txt_result.clean()
        self._view.txt_result.controls.append(ft.Text("Ricerca del cammino massimo globale in corso...", color="blue"))
        self._view.update_page()

        # 2. Lancio la ricerca globale sul model
        percorso_migliore = self._model.getPercorsoPiuLungo()

        # 3. Stampo il cammino massimo trovato
        self._view.txt_result.clean()
        self._view.txt_result.controls.append(
            ft.Text(f"Cammino massimo globale trovato: {len(percorso_migliore)} nodi", color="green",
                    weight=ft.FontWeight.BOLD)
        )

        for attore in percorso_migliore:
            self._view.txt_result.controls.append(ft.Text(f"{attore.name} (Nato il: {attore.date_of_birth})"))

        self._view.update_page()