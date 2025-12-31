import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('databases/takeaway.db')

# Query the data for restaurants per city, counting DISTINCT restaurants
query_city = """
SELECT
    city,
    COUNT(DISTINCT primarySlug) AS restaurant_count
FROM
    restaurants
GROUP BY
    city
ORDER BY
    restaurant_count DESC
"""
df_city = pd.read_sql_query(query_city, conn)

# Close the connection
conn.close()

# --- Data processing ---
# The total for percentage calculation should be the sum of unique restaurants per city,
# as a restaurant can exist in multiple cities.
total_for_percentage = df_city['restaurant_count'].sum()
df_city['percentage'] = (df_city['restaurant_count'] / total_for_percentage) * 100


# --- Visualization 1: Top 20 cities by number of restaurants ---
top_20 = df_city.head(20)
plt.figure(figsize=(12, 8))
plt.barh(top_20['city'], top_20['restaurant_count'], color='skyblue')
plt.xlabel('Number of Unique Restaurants')
plt.ylabel('City')
plt.title('Top 20 Cities by Number of Unique Restaurants (Takeaway)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('analysis/takeaway/restaurants_per_location.png')
plt.close()


# --- Visualization 2: Concentration of restaurants ---
# Prepare data for the pie chart
top_10_pie = df_city.head(10).copy()
other_percentage = df_city['percentage'][10:].sum()
top_10_pie.loc[len(top_10_pie)] = {'city': 'Other', 'restaurant_count': 0, 'percentage': other_percentage}


plt.figure(figsize=(10, 10))
plt.pie(top_10_pie['percentage'], labels=top_10_pie['city'], autopct='%1.1f%%', startangle=140)
plt.title('Restaurant Concentration in Top 10 Cities (Takeaway)')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.savefig('analysis/takeaway/restaurants_concentration.png')
plt.close()


# --- Print summary ---
print("Top 10 cities with most unique restaurants (Takeaway):")
print(df_city.head(10).to_markdown(index=False))

