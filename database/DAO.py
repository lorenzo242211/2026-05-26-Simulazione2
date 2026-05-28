from database.DB_connect import DBConnect
from model.attore import Attore


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getRatings():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT DISTINCT r.avg_rating 
        FROM ratings r 
        ORDER BY r.avg_rating ASC
        """

        cursor.execute(query)

        for row in cursor:
            result.append(row['avg_rating'])

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getNodi(anno1, anno2):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)

        # Aggiunto DISTINCT: essenziale, altrimenti l'attore viene caricato
        # tante volte quanti sono i film validi che ha fatto!
        query = """
        SELECT DISTINCT n.id, n.name, n.height, n.date_of_birth, n.known_for_movies
        FROM names n, role_mapping rm, movie m, ratings r 
        WHERE n.id = rm.name_id AND rm.movie_id = m.id AND m.id = r.movie_id 
        AND r.avg_rating > %s AND r.avg_rating < %s
        AND n.date_of_birth IS NOT NULL AND rm.category IN ('actor', 'actress')
        """

        cursor.execute(query, (anno1, anno2))

        for row in cursor:
            result.append(Attore(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getArchiPesati(anno1, anno2):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)

        # 1. Usato id1 e id2 come alias per mapparli facilmente
        # 2. Ottimizzazione estrema: nelle subquery ho estratto SOLO id e movie_id,
        #    eliminando name, height, ecc. che appesantiscono la memoria per niente.
        # 3. Inserita la doppia REPLACE per togliere sia il dollaro che la virgola.
        query = """
        SELECT attori1.id AS id1, attori2.id AS id2, 
               SUM(COALESCE(REPLACE(REPLACE(attori1.worlwide_gross_income, '$ ', ''), ',', ''), 0)) AS pesoArco
        FROM (
            SELECT n.id, r.movie_id, m.worlwide_gross_income 
            FROM names n, role_mapping rm, movie m, ratings r 
            WHERE n.id = rm.name_id AND rm.movie_id = m.id AND m.id = r.movie_id 
            AND r.avg_rating > %s AND r.avg_rating < %s
            AND n.date_of_birth IS NOT NULL AND rm.category IN ('actor', 'actress')
        ) AS attori1, 
        (
            SELECT n.id, r.movie_id, m.worlwide_gross_income  
            FROM names n, role_mapping rm, movie m, ratings r 
            WHERE n.id = rm.name_id AND rm.movie_id = m.id AND m.id = r.movie_id 
            AND r.avg_rating > %s AND r.avg_rating < %s
            AND n.date_of_birth IS NOT NULL AND rm.category IN ('actor', 'actress')
        ) AS attori2
        WHERE attori1.id < attori2.id AND attori1.movie_id = attori2.movie_id  
        GROUP BY attori1.id, attori2.id;
        """

        # ERRORE CRUCIALE RISOLTO:
        # Nella query ci sono QUATTRO %s (due nella prima subquery, due nella seconda).
        # Quindi devi passare i parametri duplicati nella tupla, altrimenti va in crash!
        cursor.execute(query, (anno1, anno2, anno1, anno2))

        for row in cursor:
            # Sostituito il "rowblablabla" creando la tupla pulita con i dati esatti
            # che ti serviranno nel Model per fare add_edge(id1, id2, weight=pesoArco)
            result.append((row['id1'], row['id2'], row['pesoArco']))

        cursor.close()
        conn.close()
        return result