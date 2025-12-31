import sqlite3
import pandas as pd

def get_top_pizza_restaurants_ubereats(db_path, limit=10):
    """
    Connects to the ubereats.db database and retrieves the top N pizza restaurants
    based on ratings.

    Args:
        db_path (str): The path to the SQLite database file.
        limit (int): The number of top restaurants to return.

    Returns:
        list: A list of tuples, where each tuple contains the restaurant's
              name, rating, and number of reviews.
    """
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            r.title AS restaurant_name,
            r.rating__rating_value AS rating,
            r.rating__review_count AS review_count
        FROM
            restaurants r
        WHERE
            r.id IN (
                SELECT DISTINCT mi.restaurant_id
                FROM menu_items mi
                WHERE mi.name LIKE '%pizza%' OR mi.description LIKE '%pizza%'
            )
        ORDER BY
            rating DESC,
            review_count DESC
        LIMIT ?;
    """

    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()

    return df.values.tolist()

if __name__ == '__main__':
    db_path = 'databases/ubereats.db'
    top_10_pizza = get_top_pizza_restaurants_ubereats(db_path)

    print("Top 10 Pizza Restaurants (by Rating - Uber Eats):")
    for i, row in enumerate(top_10_pizza, 1):
        print(f"{i}. {row[0]} (Rating: {row[1]}, Reviews: {row[2]})")
