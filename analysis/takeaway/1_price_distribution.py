
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('databases/takeaway.db')

# Query the data
query = "SELECT price FROM menuItems"
df = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# Data cleaning: convert price to numeric, coercing errors
df['price'] = pd.to_numeric(df['price'], errors='coerce')
# remove rows with NaN prices
df.dropna(subset=['price'], inplace=True)

# Create the histogram
plt.figure(figsize=(10, 6))
plt.xlim(0,50)
plt.hist(df['price'], bins=120, edgecolor='black')
plt.title('Price Distribution of Menu Items (Takeaway)')
plt.xlabel('Price (in EUR)')
plt.ylabel('Number of Items')
plt.grid(axis='y', alpha=0.75)

# Save the plot
plt.savefig('analysis/takeaway/price_distribution.png')

# Print summary statistics
print("Price Distribution Summary (Takeaway):")
print(df['price'].describe())
