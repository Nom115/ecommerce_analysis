import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np

# Data cleaning
data = pd.read_csv('data.csv', encoding='latin-1')
print("Initial Data Summary:")
print(data.info())

# Remove rows without CustomerID's
data.dropna(subset=['CustomerID'], inplace=True)

# Remove duplicate rows
data.drop_duplicates(inplace=True)

# Standardising time format
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])

# Handling anomalies
data = data[(data['Quantity'] > 0) & (data['UnitPrice'] > 0)]

print("Cleansing complete")
print(data.info)

# data.to_csv('cleansed_data.csv', index=False)


cnx = mysql.connector.connect(
    host="localhost",
    user="Nom",
    password="",
    database="project_1"
)
cursor = cnx.cursor()

average_spent = """
SELECT Country, AVG(UnitPrice * Quantity) AS AverageSpent
FROM cleansed_data
GROUP BY Country
"""

cursor.execute(average_spent)
results = cursor.fetchall()

df = pd.DataFrame(results, columns=['Country', 'AverageSpent'])
average_spent_all_countries = df['AverageSpent'].mean()
df = df.sort_values('AverageSpent')

total_spent_query = """
SELECT Country, (UnitPrice * Quantity) AS MoneySpent
FROM cleansed_data
GROUP BY Country, UnitPrice, Quantity
"""

cursor.execute(total_spent_query)
results = cursor.fetchall()

df2 = pd.DataFrame(results, columns=['Country', 'MoneySpent'])
df2 = df2.sort_values('MoneySpent')
df2 = df2[df2['MoneySpent'] > 2000]

total_spent_by_user = """
SELECT CustomerID, (UnitPrice * Quantity) AS MoneySpentUser
FROM cleansed_data
GROUP BY CustomerID, UnitPrice, Quantity
"""

cursor.execute(total_spent_by_user)
results = cursor.fetchall()

df3 = pd.DataFrame(results, columns=['MoneySpentUser', 'CustomerID'])
df3 = df3.sort_values('MoneySpentUser', ascending=False)

top_8_customers = df3['CustomerID'].head(8)
df3 = df3[df3['CustomerID'].isin(top_8_customers)]
cursor.close()
cnx.close()
df3 = df3.reset_index(drop=True)
df3 = df3.pivot(index='CustomerID', columns='MoneySpentUser',
                values='MoneySpentUser')
df3 = np.array(df3)

print(f"Average spent across all countries: {average_spent_all_countries}")

plt.figure(figsize=(12, 6))

plt.subplot(1, 3, 1)
g1 = plt.bar(df['Country'], df['AverageSpent'])
plt.xticks(rotation=90, ha='right')  # Rotate and align x-axis labels
plt.tight_layout()

plt.subplot(1, 3, 2)
g2 = plt.bar(df2['Country'], df2['MoneySpent'])
plt.xticks(rotation=90, ha='right')  # Rotate and align x-axis labels
plt.tight_layout()


plt.subplot(1, 3, 3)

g3 = plt.imshow(df3, cmap='YlOrRd')
cbar = plt.colorbar(g3)
cbar.set_label('Money Spent')

plt.subplots_adjust(wspace=0.3)

plt.show()
