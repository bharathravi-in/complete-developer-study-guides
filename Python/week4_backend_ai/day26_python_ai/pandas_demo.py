#!/usr/bin/env python3
"""Day 26 - Pandas Data Analysis"""

print("=" * 50)
print("PANDAS FUNDAMENTALS")
print("=" * 50)


# ============================================
# 1. DATAFRAME CREATION
# ============================================
print("\n--- 1. DataFrame Creation ---")

DATAFRAME_CREATION = """
import pandas as pd

# From dictionary
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
})

# From list of dicts
data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
df = pd.DataFrame(data)

# From NumPy array
import numpy as np
arr = np.random.rand(3, 4)
df = pd.DataFrame(arr, columns=['A', 'B', 'C', 'D'])

# From CSV file
df = pd.read_csv('data.csv')

# From JSON
df = pd.read_json('data.json')

# From SQL
from sqlalchemy import create_engine
engine = create_engine('sqlite:///db.sqlite')
df = pd.read_sql('SELECT * FROM users', engine)
"""
print(DATAFRAME_CREATION)


# ============================================
# 2. DATA INSPECTION
# ============================================
print("\n--- 2. Data Inspection ---")

DATA_INSPECTION = """
# Basic info
df.head()           # First 5 rows
df.tail()           # Last 5 rows
df.sample(5)        # Random 5 rows
df.shape            # (rows, columns)
df.columns          # Column names
df.dtypes           # Data types
df.info()           # Summary info
df.describe()       # Statistical summary

# Check for missing values
df.isnull().sum()   # Count nulls per column
df.isna().any()     # Boolean: any nulls?

# Value counts
df['column'].value_counts()
df['column'].unique()
df['column'].nunique()
"""
print(DATA_INSPECTION)


# ============================================
# 3. DATA SELECTION
# ============================================
print("\n--- 3. Data Selection ---")

DATA_SELECTION = """
# Select columns
df['name']              # Single column (Series)
df[['name', 'age']]     # Multiple columns (DataFrame)

# Select rows by index
df.iloc[0]              # First row
df.iloc[0:5]            # First 5 rows
df.iloc[[0, 2, 4]]      # Specific rows

# Select by label
df.loc[0, 'name']       # Specific cell
df.loc[0:5, 'name':'age']  # Range

# Boolean indexing
df[df['age'] > 25]
df[(df['age'] > 25) & (df['city'] == 'NYC')]
df[df['name'].str.contains('Ali')]
df[df['city'].isin(['NYC', 'LA'])]

# Query syntax
df.query('age > 25 and city == "NYC"')
"""
print(DATA_SELECTION)


# ============================================
# 4. DATA MANIPULATION
# ============================================
print("\n--- 4. Data Manipulation ---")

DATA_MANIPULATION = """
# Add columns
df['new_col'] = df['age'] * 2
df['full_name'] = df['first'] + ' ' + df['last']

# Apply functions
df['age_group'] = df['age'].apply(lambda x: 'adult' if x >= 18 else 'minor')
df['upper_name'] = df['name'].str.upper()

# Map values
mapping = {'NYC': 'New York', 'LA': 'Los Angeles'}
df['city_full'] = df['city'].map(mapping)

# Replace values
df['col'].replace({'old': 'new'})
df.replace({'col1': {'a': 'b'}, 'col2': {'x': 'y'}})

# Drop columns/rows
df.drop(['col1', 'col2'], axis=1)  # Drop columns
df.drop([0, 1], axis=0)            # Drop rows
df.dropna()                         # Drop rows with nulls
df.dropna(subset=['col1'])          # Drop if col1 is null

# Fill missing values
df['col'].fillna(0)
df['col'].fillna(df['col'].mean())
df.fillna(method='ffill')           # Forward fill
"""
print(DATA_MANIPULATION)


# ============================================
# 5. GROUPING & AGGREGATION
# ============================================
print("\n--- 5. Grouping & Aggregation ---")

GROUPING = """
# Group by single column
df.groupby('city').mean()
df.groupby('city')['age'].mean()

# Group by multiple columns
df.groupby(['city', 'gender']).agg({
    'age': 'mean',
    'salary': ['sum', 'min', 'max']
})

# Multiple aggregations
df.groupby('city').agg({
    'age': 'mean',
    'salary': 'sum',
    'count': 'size'
})

# Transform (preserves shape)
df['age_normalized'] = df.groupby('city')['age'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Pivot tables
pd.pivot_table(df, 
    values='salary',
    index='city',
    columns='gender',
    aggfunc='mean'
)
"""
print(GROUPING)


# ============================================
# 6. MERGING & JOINING
# ============================================
print("\n--- 6. Merging & Joining ---")

MERGING = """
# Merge (like SQL JOIN)
pd.merge(df1, df2, on='key')
pd.merge(df1, df2, left_on='key1', right_on='key2')
pd.merge(df1, df2, on='key', how='left')    # left, right, inner, outer

# Join (on index)
df1.join(df2, lsuffix='_left', rsuffix='_right')

# Concatenate
pd.concat([df1, df2])                       # Stack vertically
pd.concat([df1, df2], axis=1)               # Stack horizontally

# Append (deprecated, use concat)
# df1.append(df2)  # Use pd.concat([df1, df2]) instead
"""
print(MERGING)


# ============================================
# 7. TIME SERIES
# ============================================
print("\n--- 7. Time Series ---")

TIME_SERIES = """
# Create datetime
df['date'] = pd.to_datetime(df['date'])
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Set as index
df.set_index('date', inplace=True)

# Date components
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['dayofweek'] = df['date'].dt.dayofweek

# Resampling
df.resample('M').mean()     # Monthly average
df.resample('W').sum()      # Weekly sum
df.resample('Q').last()     # Quarterly last value

# Rolling windows
df['rolling_mean'] = df['value'].rolling(window=7).mean()
df['rolling_std'] = df['value'].rolling(window=7).std()

# Date range
dates = pd.date_range('2024-01-01', periods=30, freq='D')
"""
print(TIME_SERIES)


# ============================================
# 8. PERFORMANCE TIPS
# ============================================
print("\n--- 8. Performance Tips ---")

PERFORMANCE = """
# 1. Use appropriate dtypes
df['category_col'] = df['category_col'].astype('category')
df['int_col'] = df['int_col'].astype('int32')

# 2. Read only needed columns
pd.read_csv('data.csv', usecols=['col1', 'col2'])

# 3. Use chunking for large files
for chunk in pd.read_csv('large.csv', chunksize=10000):
    process(chunk)

# 4. Vectorized operations (avoid loops)
# Slow:
df['result'] = df.apply(lambda row: row['a'] + row['b'], axis=1)
# Fast:
df['result'] = df['a'] + df['b']

# 5. Use query() for filtering
df.query('age > 25 and city == "NYC"')  # Faster than boolean indexing

# 6. Consider Polars for large datasets
# import polars as pl
# df = pl.read_csv('data.csv')  # Much faster than pandas
"""
print(PERFORMANCE)


# ============================================
# DEMONSTRATION
# ============================================
print("\n" + "=" * 50)
print("LIVE DEMONSTRATION")
print("=" * 50)

try:
    import pandas as pd
    import numpy as np
    
    # Create sample data
    print("\n--- Create DataFrame ---")
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'city': ['NYC', 'LA', 'NYC', 'Chicago', 'LA'],
        'salary': [50000, 60000, 75000, 55000, 80000]
    })
    print(df)
    
    # Basic operations
    print("\n--- Basic Info ---")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Filtering
    print("\n--- Filtering (age > 28) ---")
    print(df[df['age'] > 28])
    
    # Grouping
    print("\n--- Group by City ---")
    print(df.groupby('city').agg({
        'salary': 'mean',
        'age': 'mean'
    }).round(2))
    
    # Add computed column
    print("\n--- Add Tax Column ---")
    df['tax'] = df['salary'] * 0.25
    print(df[['name', 'salary', 'tax']])
    
    # Statistics
    print("\n--- Statistics ---")
    print(df.describe())

except ImportError:
    print("\nPandas not installed. Run: pip install pandas")
    print("The concepts above are still valid!")
