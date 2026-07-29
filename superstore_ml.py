import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             r2_score, accuracy_score,
                             confusion_matrix, classification_report)

sns.set_theme(style='whitegrid')
plt.rcParams['figure.dpi'] = 110


# load data
df = pd.read_csv(
    r'C:\data\Sample - Superstore UTF8.csv',
    encoding='utf-8'
)

df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

df['year'] = df['Order Date'].dt.year
df['month'] = df['Order Date'].dt.month
df['days_to_ship'] = (df['Ship Date'] - df['Order Date']).dt.days

# target column for classification - 1 if profit > 0 else 0
df['profitable'] = (df['Profit'] > 0).astype(int)

print(df.shape)
print(df['profitable'].value_counts())


# feature engineering
# encode categorical columns to numbers
features = ['month', 'year', 'Quantity', 'Discount',
            'days_to_ship', 'Category', 'Region', 'Segment', 'Ship Mode']

data = df[features + ['Sales', 'Profit', 'profitable']].copy()

le = LabelEncoder()
for col in ['Category', 'Region', 'Segment', 'Ship Mode']:
    data[col] = le.fit_transform(data[col])

print(data[features].head())


# -----------------------------------------------
# model 1 - linear regression to predict sales
# -----------------------------------------------

X = data[features]
y = data['Sales']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model1 = LinearRegression()
model1.fit(X_train, y_train)

preds = model1.predict(X_test)

r2 = r2_score(y_test, preds)
mae = mean_absolute_error(y_test, preds)
rmse = np.sqrt(mean_squared_error(y_test, preds))

print(f"\nlinear regression results:")
print(f"r2 score : {r2:.4f}")
print(f"mae      : ${mae:.2f}")
print(f"rmse     : ${rmse:.2f}")


# actual vs predicted plot
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(y_test, preds, alpha=0.4, color='#2E75B6', s=15)
axes[0].plot([y_test.min(), y_test.max()],
             [y_test.min(), y_test.max()],
             'r--', linewidth=2, label='perfect prediction')
axes[0].set_xlabel('actual sales')
axes[0].set_ylabel('predicted sales')
axes[0].set_title(f'actual vs predicted sales (r2={r2:.2f})', fontweight='bold')
axes[0].legend()

# feature importance
imp = pd.DataFrame({
    'feature': features,
    'coef': np.abs(model1.coef_)
}).sort_values('coef', ascending=True)

axes[1].barh(imp['feature'], imp['coef'], color='#2E75B6', edgecolor='white')
axes[1].set_title('feature importance (linear regression)', fontweight='bold')
axes[1].set_xlabel('coefficient')

plt.tight_layout()
plt.savefig('ml_model1_linear_regression.png', bbox_inches='tight')
plt.show()


# sample prediction
sample = pd.DataFrame({
    'month': [11], 'year': [2022], 'Quantity': [3],
    'Discount': [0.0], 'days_to_ship': [3],
    'Category': [2], 'Region': [3], 'Segment': [0], 'Ship Mode': [2]
})
pred_sales = model1.predict(sample)[0]
print(f"\nsample prediction (tech, nov, qty=3, no discount): ${pred_sales:,.2f}")


# -----------------------------------------------
# model 2 - logistic regression to classify profit/loss
# -----------------------------------------------

X2 = data[features]
y2 = data['profitable']

X2_train, X2_test, y2_train, y2_test = train_test_split(X2, y2, test_size=0.2, random_state=42)

# scale features - important for logistic regression
scaler = StandardScaler()
X2_train_sc = scaler.fit_transform(X2_train)
X2_test_sc = scaler.transform(X2_test)

model2 = LogisticRegression(max_iter=1000, random_state=42)
model2.fit(X2_train_sc, y2_train)

y2_pred = model2.predict(X2_test_sc)

acc = accuracy_score(y2_test, y2_pred)
cm = confusion_matrix(y2_test, y2_pred)

print(f"\nlogistic regression results:")
print(f"accuracy: {acc*100:.2f}%")
print("\nclassification report:")
print(classification_report(y2_test, y2_pred, target_names=['loss', 'profitable']))


# confusion matrix and feature importance
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['loss', 'profitable'],
            yticklabels=['loss', 'profitable'],
            ax=axes[0], linewidths=1, linecolor='white',
            annot_kws={'size': 13})
axes[0].set_xlabel('predicted')
axes[0].set_ylabel('actual')
axes[0].set_title(f'confusion matrix (accuracy={acc*100:.1f}%)', fontweight='bold')

imp2 = pd.DataFrame({
    'feature': features,
    'importance': np.abs(model2.coef_[0])
}).sort_values('importance', ascending=True)

colors = ['#FF4444' if f == 'Discount' else '#2E75B6' for f in imp2['feature']]
axes[1].barh(imp2['feature'], imp2['importance'], color=colors, edgecolor='white')
axes[1].set_title('feature importance (logistic regression)', fontweight='bold')
axes[1].set_xlabel('importance')

plt.tight_layout()
plt.savefig('ml_model2_logistic_regression.png', bbox_inches='tight')
plt.show()


# test with a risky order (high discount, furniture)
risky = pd.DataFrame({
    'month': [6], 'year': [2022], 'Quantity': [2],
    'Discount': [0.5], 'days_to_ship': [5],
    'Category': [1], 'Region': [0], 'Segment': [0], 'Ship Mode': [2]
})
risky_sc = scaler.transform(risky)
pred = model2.predict(risky_sc)[0]
prob = model2.predict_proba(risky_sc)[0]
print(f"\nrisky order (furniture, 50% discount):")
print(f"prediction : {'profitable' if pred == 1 else 'loss'}")
print(f"probability: loss={prob[0]*100:.1f}%, profit={prob[1]*100:.1f}%")

# test with a safe order (no discount, technology)
safe = pd.DataFrame({
    'month': [11], 'year': [2022], 'Quantity': [4],
    'Discount': [0.0], 'days_to_ship': [2],
    'Category': [2], 'Region': [3], 'Segment': [1], 'Ship Mode': [1]
})
safe_sc = scaler.transform(safe)
pred2 = model2.predict(safe_sc)[0]
prob2 = model2.predict_proba(safe_sc)[0]
print(f"\nsafe order (technology, no discount):")
print(f"prediction : {'profitable' if pred2 == 1 else 'loss'}")
print(f"probability: loss={prob2[0]*100:.1f}%, profit={prob2[1]*100:.1f}%")


# final summary
print("\n--- model summary ---")
print(f"model 1 (linear regression) - r2: {r2:.2f}, mae: ${mae:.0f}")
print(f"model 2 (logistic regression) - accuracy: {acc*100:.1f}%")
print("charts saved: ml_model1_linear_regression.png, ml_model2_logistic_regression.png")
