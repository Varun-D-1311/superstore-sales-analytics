import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid')
plt.rcParams['figure.dpi'] = 110


# load data
df = pd.read_csv(
    r'C:\data\Sample - Superstore UTF8.csv',
    encoding='utf-8'
)

print(df.shape)
df.head()


# basic info
print(df.columns.tolist())
print(df.dtypes)
print(df.isnull().sum())
print("duplicates:", df.duplicated().sum())


# date columns
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

df['year'] = df['Order Date'].dt.year
df['month'] = df['Order Date'].dt.month
df['month_name'] = df['Order Date'].dt.strftime('%b')
df['quarter'] = df['Order Date'].dt.quarter
df['days_to_ship'] = (df['Ship Date'] - df['Order Date']).dt.days
df['profit_margin'] = (df['Profit'] / df['Sales'] * 100).round(2)


# quick stats
print(df[['Sales', 'Profit', 'Quantity', 'Discount']].describe().round(2))

total_sales = df['Sales'].sum()
total_profit = df['Profit'].sum()
margin = total_profit / total_sales * 100

print(f"total sales: ${total_sales:,.0f}")
print(f"total profit: ${total_profit:,.0f}")
print(f"margin: {margin:.2f}%")
print(f"unique orders: {df['Order ID'].nunique()}")
print(f"unique customers: {df['Customer ID'].nunique()}")
print(f"loss orders: {(df['Profit'] < 0).sum()}")


# chart 1 - sales by category
cat_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(cat_sales.index, cat_sales.values,
              color=['#2E75B6', '#ED7D31', '#70AD47'],
              edgecolor='white', width=0.5)

for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 5000,
            f'${bar.get_height():,.0f}',
            ha='center', va='bottom', fontsize=11)

ax.set_title('Sales by Category', fontsize=13, fontweight='bold')
ax.set_ylabel('Sales ($)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_ylim(0, cat_sales.max() * 1.15)
plt.tight_layout()
plt.savefig('chart1_sales_by_category.png', bbox_inches='tight')
plt.show()


# chart 2 - profit by category
cat_profit = df.groupby('Category')['Profit'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#70AD47' if v > 0 else '#FF4444' for v in cat_profit.values]
bars = ax.bar(cat_profit.index, cat_profit.values,
              color=colors, edgecolor='white', width=0.5)

for bar in bars:
    ypos = bar.get_height() + 1000 if bar.get_height() > 0 else bar.get_height() - 3000
    ax.text(bar.get_x() + bar.get_width()/2, ypos,
            f'${bar.get_height():,.0f}',
            ha='center', va='bottom', fontsize=11)

ax.set_title('Profit by Category', fontsize=13, fontweight='bold')
ax.set_ylabel('Profit ($)')
ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('chart2_profit_by_category.png', bbox_inches='tight')
plt.show()


# chart 3 - profit by sub-category (horizontal)
subcat_profit = df.groupby('Sub-Category')['Profit'].sum().sort_values()

fig, ax = plt.subplots(figsize=(10, 7))
colors = ['#FF4444' if v < 0 else '#2E75B6' for v in subcat_profit.values]
bars = ax.barh(subcat_profit.index, subcat_profit.values,
               color=colors, edgecolor='white')

for bar in bars:
    w = bar.get_width()
    xpos = w + 400 if w > 0 else w - 400
    ax.text(xpos, bar.get_y() + bar.get_height()/2,
            f'${w:,.0f}',
            ha='left' if w > 0 else 'right', va='center', fontsize=9)

ax.set_title('Profit by Sub-Category (red = loss)', fontsize=13, fontweight='bold')
ax.axvline(x=0, color='black', linewidth=0.8, linestyle='--')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('chart3_profit_by_subcategory.png', bbox_inches='tight')
plt.show()


# chart 4 - monthly sales trend
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

monthly = df.groupby('month_name')['Sales'].sum().reindex(month_order)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly.index, monthly.values,
        color='#2E75B6', linewidth=2.5,
        marker='o', markersize=7,
        markerfacecolor='white', markeredgecolor='#2E75B6')

# highlight q4
ax.axvspan(9.5, 11.5, alpha=0.12, color='orange', label='Q4 (Nov-Dec)')

for i, (m, v) in enumerate(zip(monthly.index, monthly.values)):
    ax.text(i, v + 3000, f'${v/1000:.0f}K',
            ha='center', fontsize=9, color='#2E75B6')

ax.set_title('Monthly Sales Trend - All Years Combined', fontsize=13, fontweight='bold')
ax.set_ylabel('Sales ($)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.legend()
plt.tight_layout()
plt.savefig('chart4_monthly_trend.png', bbox_inches='tight')
plt.show()


# chart 5 - region pie chart
region_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 6))
colors = ['#2E75B6', '#ED7D31', '#A5A5A5', '#FFC000']
wedges, texts, autotexts = ax.pie(
    region_sales.values,
    labels=region_sales.index,
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    wedgeprops=dict(edgecolor='white', linewidth=2)
)
for t in autotexts:
    t.set_fontsize(11)
    t.set_fontweight('bold')

ax.set_title('Sales by Region', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('chart5_sales_by_region.png', bbox_inches='tight')
plt.show()


# chart 6 - discount vs profit scatter
fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(df['Discount'], df['Profit'],
                alpha=0.4, c=df['Profit'], cmap='RdYlGn', s=18)

# trend line
z = np.polyfit(df['Discount'], df['Profit'], 1)
p = np.poly1d(z)
xline = np.linspace(df['Discount'].min(), df['Discount'].max(), 100)
ax.plot(xline, p(xline), 'r--', linewidth=2, label='trend')

corr = df['Discount'].corr(df['Profit'])
ax.text(0.05, 0.95, f'correlation: {corr:.2f}',
        transform=ax.transAxes, fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

ax.axhline(y=0, color='black', linewidth=0.7)
ax.axvline(x=0.2, color='orange', linewidth=1.5, linestyle='--', label='20% discount line')
ax.set_title('Discount vs Profit', fontsize=13, fontweight='bold')
ax.set_xlabel('Discount')
ax.set_ylabel('Profit ($)')
ax.legend()
plt.colorbar(sc, ax=ax)
plt.tight_layout()
plt.savefig('chart6_discount_vs_profit.png', bbox_inches='tight')
plt.show()

print(f"discount-profit correlation: {corr:.2f}")


# chart 7 - year over year
yearly = df.groupby('year').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).reset_index()

x = np.arange(len(yearly))
w = 0.35

fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar(x - w/2, yearly['Sales'], w, label='Sales', color='#2E75B6', edgecolor='white')
b2 = ax.bar(x + w/2, yearly['Profit'], w, label='Profit', color='#70AD47', edgecolor='white')

for bar in b1:
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 4000,
            f'${bar.get_height()/1000:.0f}K',
            ha='center', fontsize=10)
for bar in b2:
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 1500,
            f'${bar.get_height()/1000:.0f}K',
            ha='center', fontsize=10, color='#4a7a30')

ax.set_title('Year over Year - Sales & Profit', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(yearly['year'])
ax.set_ylabel('Amount ($)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.legend()
plt.tight_layout()
plt.savefig('chart7_yearly_sales.png', bbox_inches='tight')
plt.show()


# chart 8 - correlation heatmap
cols = df[['Sales', 'Profit', 'Quantity', 'Discount', 'days_to_ship']]
corr_matrix = cols.corr().round(2)

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt='.2f',
            cmap='coolwarm', center=0,
            linewidths=0.5, linecolor='white',
            ax=ax, annot_kws={'size': 12})
ax.set_title('Correlation Heatmap', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('chart8_correlation_heatmap.png', bbox_inches='tight')
plt.show()


# summary findings
print("\n--- key findings ---")
print(f"best category by margin: Technology ({df[df['Category']=='Technology']['Profit'].sum() / df[df['Category']=='Technology']['Sales'].sum()*100:.1f}%)")
print(f"worst sub-category: Tables (profit = {df[df['Sub-Category']=='Tables']['Profit'].sum():,.0f})")
print(f"q4 sales share: {df[df['quarter']==4]['Sales'].sum() / df['Sales'].sum()*100:.1f}%")
print(f"discount-profit correlation: {df['Discount'].corr(df['Profit']):.2f}")
print(f"avg profit with no discount: ${df[df['Discount']==0]['Profit'].mean():,.2f}")
print(f"avg profit with >20% discount: ${df[df['Discount']>0.2]['Profit'].mean():,.2f}")
print(df.groupby('Region').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).sort_values('Sales', ascending=False))
