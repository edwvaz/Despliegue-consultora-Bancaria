import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import warnings

dfReviewsSnappy = pd.read_csv("data/Cloud_Upload/Google_Maps/reviews/reviews.csv")

# Suprimir la advertencia sobre los nombres de las características
warnings.filterwarnings("ignore", category=UserWarning)

# Asignar nombres a las características
dfReviewsSnappy['user_id'] = dfReviewsSnappy['user_id']

# Definir umbral de satisfacción
umbral_satisfaccion = dfReviewsSnappy['rating'].mean()

# Crear variable objetivo (target)
dfReviewsSnappy['target'] = dfReviewsSnappy['rating'].apply(
    lambda x: 1 if x >= umbral_satisfaccion else 0)

# Seleccionar características relevantes (en este caso, solo user_id)
X = dfReviewsSnappy[['user_id']]
y = dfReviewsSnappy['target']

# Dividir conjunto de datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Crear y entrenar el modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)


# Función para recomendar servicios financieros basada en el user_id


def recomendar_servicio(user_id):
    # Predecir la satisfacción del usuario
    satisfaction_prediction = model.predict([[user_id]])[0]

    # Ofrecer servicio basado en la predicción
    if satisfaction_prediction == 1:
        return "¡Te recomendamos nuestro exclusivo servicio ElitePlus Banking Experience!"
    else:
        return "Descubre nuestro servicio FreshStart Financial Solutions para mejorar tu experiencia financiera."