import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib


df = pd.read_csv("Agora.csv", encoding="latin1")
df.columns = df.columns.str.strip()
df.rename(columns={'Category': 'Threat Type'}, inplace=True)
cols_to_drop = ['Vendor', 'Price', 'Origin', 'Destination', 'Rating', 'Remarks']
df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)
df.dropna(subset=['Item', 'Item Description', 'Threat Type'], inplace=True)
df["text"] = df["Item"] + " " + df["Item Description"]
df = df[["text", "Threat Type"]]
class_counts = df['Threat Type'].value_counts()
valid_classes = class_counts[class_counts > 1].index
df = df[df['Threat Type'].isin(valid_classes)]
X = df["text"]
y = df["Threat Type"]


vectorizer = TfidfVectorizer(max_features=8000, stop_words="english", ngram_range=(1,2))
X_vec = vectorizer.fit_transform(X)


X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42, stratify=y)


model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))
joblib.dump(model, "rf_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("Model and vectorizer saved successfully")
