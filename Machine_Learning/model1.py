import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
#import matplotlib.pyplot as plt # para el mapa
# import seaborn as sns # para el mapa

pd.set_option('io.parquet.engine', 'fastparquet')
# dfMetadata = pd.read_parquet("data/Cloud Upload/Google Maps/metadata-sitios.snappy.parquet")
dfMetadata = pd.read_csv("data/Cloud_Upload/Google_Maps/metadata/metadata.csv")
dfBusinessSnappy = pd.read_csv("data/Cloud_Upload/Yelp/business/business.csv")

def generar_nuevos_bancos(num_new_banks, min_rating):
    # Accedo a los dataframes dfMetadata y dfBusinessSnappy
    # (Estos dataframes están definidos fuera de la función)

    # Seleccionar las ubicaciones donde avg_rating es menor al valor especificado
    locations_to_cluster = dfMetadata[dfMetadata['avg_rating'] < min_rating][['latitude', 'longitude']].values

    # Aplicar KMeans para encontrar los centroides
    kmeans = KMeans(n_clusters=num_new_banks, random_state=42)
    kmeans.fit(locations_to_cluster)

    # Obtener las ubicaciones de los nuevos bancos (centroides)
    new_banks_centroids = kmeans.cluster_centers_

    # Crear un DataFrame con las coordenadas de los nuevos bancos
    df_nuevos_bancos = pd.DataFrame({
        'Latitud': new_banks_centroids[:, 0],
        'Longitud': new_banks_centroids[:, 1]
    })

    # Agregar la columna 'Estado' al DataFrame de los nuevos bancos
    df_nuevos_bancos['Estado'] = df_nuevos_bancos.apply(lambda row: obtener_estado_cercano(row), axis=1)

    # Imprimir el DataFrame de los nuevos bancos con coordenadas y estados
    print("Coordenadas de los nuevos bancos con estados:")
    print(df_nuevos_bancos)

    # # Mapa de dispersión geoespacial con centroides en rojo.
    # plt.figure(figsize=(12, 8))
    # sns.scatterplot(x='longitude', y='latitude', data=dfMetadata, hue='avg_rating', palette='viridis', size='num_of_reviews', sizes=(20, 200))
    # plt.scatter(new_banks_centroids[:, 1], new_banks_centroids[:, 0], c='red', marker='X', s=100, label='Nuevos Bancos')
    # plt.title(f'Nuevos bancos de acuerdo a la insatisfacción del cliente ({num_new_banks} bancos)')
    # plt.xlabel('Longitud')
    # plt.ylabel('Latitud')
    # plt.legend(title='Puntuación Promedio')
    # plt.show()


    return df_nuevos_bancos


def obtener_estado_cercano(row):
    # Función para obtener el estado más cercano a una ubicación dada
    min_distance = float('inf')
    nearest_state = None

    for _, business_row in dfBusinessSnappy.iterrows():
        location_business = (business_row['latitude'], business_row['longitude'])
        distance = ((row['Latitud'] - location_business[0])**2 + (row['Longitud'] - location_business[1])**2)**0.5

        if distance < min_distance:
            min_distance = distance
            nearest_state = business_row['state']

    return nearest_state

    # # Mapa de dispersión geoespacial con centroides en rojo.
    # plt.figure(figsize=(12, 8))
    # sns.scatterplot(x='longitude', y='latitude', data=dfMetadata, hue='avg_rating', palette='viridis', size='num_of_reviews', sizes=(20, 200))
    # plt.scatter(new_banks_centroids[:, 1], new_banks_centroids[:, 0], c='red', marker='X', s=100, label='Nuevos Bancos')
    # plt.title(f'Nuevos bancos de acuerdo a la insatisfacción del cliente ({num_new_banks} bancos)')
    # plt.xlabel('Longitud')
    # plt.ylabel('Latitud')
    # plt.legend(title='Puntuación Promedio')
    # plt.show()

