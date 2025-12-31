import sqlite3

def get_top_pizza_restaurants(db_path, limit=10):
    """
    Connects to the takeaway.db database and retrieves the top N pizza restaurants
    based on ratings.

    Args:
        db_path (str): The path to the SQLite database file.
        limit (int): The number of top restaurants to return.

    Returns:
        list: A list of tuples, where each tuple contains the restaurant's
              name, ratings, and number of ratings.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT
            r.name,
            r.ratings,
            r.ratingsNumber
        FROM
            restaurants r
        WHERE
            r.primarySlug IN (
                SELECT DISTINCT mi.primarySlug
                FROM menuItems mi
                WHERE mi.name LIKE '%pizza%' OR mi.description LIKE '%pizza%'
            )
        ORDER BY
            r.ratings DESC,
            r.ratingsNumber DESC
        LIMIT ?;
    """

    cursor.execute(query, (limit,))
    top_restaurants = cursor.fetchall()

    conn.close()
    return top_restaurants

if __name__ == '__main__':
    db_path = 'databases/takeaway.db'
    top_10_pizza = get_top_pizza_restaurants(db_path)

    print("Top 10 Pizza Restaurants (by Rating):")
    for i, row in enumerate(top_10_pizza, 1):
        print(f"{i}. {row[0]} (Rating: {row[1]}, Reviews: {row[2]})")

