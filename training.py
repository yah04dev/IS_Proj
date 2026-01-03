import os
import re
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ======================================================
# FEATURE EXTRACTION (30 FEATURES – SAME LOGIC AS BEFORE)
# ======================================================
def extract_features(path):
    rows = []

    with open(path, "r") as f:
        for line in f:
            nums = re.findall(r'-?\d+\.?\d*', line)
            if len(nums) == 6:
                rows.append([float(n) for n in nums])

    data = np.array(rows)

    # If fewer than 15 rows, pad with the mean of existing rows
    if len(data) < 15:
        mean_row = data.mean(axis=0) if len(data) > 0 else np.zeros(6)
        while len(data) < 15:
            data = np.vstack([data, mean_row])

    features = []
    for i in range(6):
        a = data[:, i]
        features.extend([
            a.mean(),
            a.std(),
            a.min(),
            a.max(),
            np.var(a)
        ])

    return features

# ======================================================
# LOAD DATASET
# ======================================================
X, y = [], []

for label, folder in [(1, "dataset/good"), (0, "dataset/bad")]:
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            X.append(extract_features(os.path.join(folder, file)))
            y.append(label)

X = np.array(X)
y = np.array(y)

print(f"Dataset: {len(y)} samples")
print(f"GOOD: {sum(y)} | BAD: {len(y)-sum(y)}")
print("Features:", X.shape[1])

# ======================================================
# TRAIN / TEST SPLIT
# ======================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    stratify=y,
    random_state=42
)

# ======================================================
# SVM PIPELINE (IMPORTANT)
# ======================================================
model = SVC(
    kernel="rbf",
    C=10,                   # controls margin
    gamma="scale",          # good default
    class_weight="balanced",# handles imbalance
    probability=True        # needed for proba
)

# normalize + svm
from sklearn.pipeline import make_pipeline
pipeline = make_pipeline(StandardScaler(), model)

pipeline.fit(X_train, y_train)


y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

print("\nAccuracy:", round(accuracy_score(y_test, y_pred)*100, 2), "%")
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))


joblib.dump(pipeline, "handwriting_svm.pkl")
print("\nSaved: handwriting_svm.pkl")
