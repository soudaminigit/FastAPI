import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Sample synthetic dataset
data = pd.DataFrame({
    'rooms': [1, 2, 3, 4, 5],
    'area': [300, 500, 700, 900, 1100],
    'location': ['A', 'A', 'B', 'B', 'C'],
    'price': [100, 150, 210, 260, 300]
})

# Define features and target
X = data[['rooms', 'area', 'location']]
y = data['price']

# Pipeline: One-hot encode location + LinearRegression
preprocessor = ColumnTransformer(
    transformers=[('cat', OneHotEncoder(), ['location'])],
    remainder='passthrough'
)
model = Pipeline(steps=[('pre', preprocessor), ('reg', LinearRegression())])

# Train and export model
model.fit(X, y)
joblib.dump(model, 'price_model.pkl')

print(" Model saved as 'price_model.pkl'")
