import db


def promotion_film_members():
    """
    Retorna o nome e a função dos membros de filmes que estejam na promoção
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT movie_cast.cast_name, "function" \
                    FROM movie_with_item item \
                    JOIN movie_cast ON (item.id = movie_cast.movie_id) \
                    WHERE is_promotion = true;')
    return [{'name': obj[0], 'function': obj[1]} for obj in cursor.fetchall()]

def artists_and_albuns_with_longer_musics(minutes = 3):
    """
    Retorna o nome do álbum e do artista, dos álbuns que tenham músicas mais longas do que `minutes`
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT "name" album_name, artist_name \
                    FROM album_with_item item \
                    WHERE item.id IN ( \
                        SELECT album_id \
                        FROM track \
                        WHERE duration > %s * 60 \
                    ) \
                    ORDER BY artist_name;', (minutes, ))
    return [{'album_name': obj[0], 'artist_name': obj[1]} for obj in cursor.fetchall()]

def download_statistics():
    """
    Retorna as estatísticas de download para todos usuários do sistema
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT u.name, email, COUNT(DISTINCT item_id) downloads_count \
                    FROM "User" u \
                    LEFT JOIN download ON (download.user_email = u.email) \
                    GROUP BY email, u.name \
                    ORDER BY u.name;')
    return [{'name': obj[0], 'email': obj[1], 'downloads_count': obj[2]} for obj in cursor.fetchall()]

def movie_by_cast(cast = 'Jason Momoa'):
    """
    Retorna nome de todos usuários que baixaram algum filme em que `cast` participou
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT u.name \
                    FROM "User" u \
                    JOIN download ON (download.user_email = u.email) \
                    JOIN movie_with_item item ON (item.id = download.item_id) \
                    JOIN movie_cast ON (movie_cast.movie_id = item.id) \
                    WHERE cast_name = %s;', (cast, ))
    return [{'name': obj[0]} for obj in cursor.fetchall()]

def wishlist_books_by_language(language = 'Português'):
    """
    Retorna o nome de todos usuários que adicionaram algum livro escrito em `language`
    à sua Wishlist, juntamente com a data de adição e o nome do livro
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT u.name user_name, date, item.name book_name \
                    FROM "User" u \
                    JOIN wishlist ON (wishlist.user_email = u.email) \
                    JOIN book_with_item item ON (item.id = wishlist.item_id) \
                    WHERE language_name = %s;', (language, ))
    return [{'user_name': obj[0], 'date': obj[1], 'book_name': obj[2]} for obj in cursor.fetchall()]

def downloads_by_developer():
    """
    Retorna uma lista com a quantidade de downloads de cada `developer` de `App`
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT developer.name, COUNT(*) \
                    FROM download \
                    JOIN app_with_item item ON (download.item_id = item.id) \
                    JOIN developer ON (item.developer_email = developer.email) \
                    GROUP BY id, developer.name \
                    ORDER BY COUNT(*) DESC;')
    return [{'developer_name': obj[0], 'download_count': obj[1]} for obj in cursor.fetchall()]

def higher_than_average_albuns():
    """
    Retorna uma lista com o nome do álbum e do seu artista, para todo album
    que foi baixado mais do que a média de download de álbuns
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT name album_name, artist_name \
                    FROM album_with_item item \
                    JOIN download ON (download.item_id = item.id) \
                    GROUP BY item.id, name, artist_name \
                    HAVING COUNT(*) >= ( \
                        SELECT AVG(count) \
                        FROM ( \
                            SELECT COUNT(*) count \
                            FROM download \
                            JOIN album_with_item item ON (download.item_id = item.id) \
                            GROUP BY item.id \
                        ) download_count \
                    );')
    return [{'album_name': obj[0], 'artist_name': obj[1]} for obj in cursor.fetchall()]

def person_didnt_downloaded_same_apps(other_email = 'rbaudibert@inf.ufrgs.br'):
    """
    Retorna uma lista com o nome de todas as pessoas que nunca baixaram nenhum app
    igual ao da pessoa com email `other_email`
    """
    cursor = db.get_cursor()
    cursor.execute('SELECT email \
                    FROM "User" u \
                    WHERE NOT EXISTS ( \
                        SELECT * \
                        FROM download \
                        WHERE (u.email = download.user_email) \
                            AND item_id IN ( \
                                SELECT item_id \
                                FROM download \
                                WHERE (user_email = %s) \
                        ) \
                    );', (other_email,))
    return [{'email': obj[0]} for obj in cursor.fetchall()]
