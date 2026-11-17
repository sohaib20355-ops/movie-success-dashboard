import pandas as pd
import numpy as np
import random

# --- CONFIGURATION ---
num_rows = 100000  # 1 Lakh Records

# --- 1. GENRES & PROBABILITIES ---
# Real life mein Drama/Comedy movies zyada banti hain, Sci-Fi kam.
genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Animation', 'Thriller', 'Romance', 'Documentary']
genre_weights = [0.15, 0.10, 0.20, 0.25, 0.10, 0.05, 0.05, 0.05, 0.04, 0.01] 

print("Generating Realistic Movie Data... Please wait.")

# Genre assign karna based on weights
selected_genres = np.random.choice(genres, num_rows, p=genre_weights)

# --- 2. BUDGET GENERATION (Genre ke hisaab se) ---
# Action movies mehngi hoti hain, Horror sasti hoti hain
budgets = np.zeros(num_rows, dtype=np.int64)

for i in range(num_rows):
    g = selected_genres[i]
    if g in ['Action', 'Sci-Fi', 'Adventure', 'Animation']:
        # High Budget: $50M to $250M
        budgets[i] = random.randint(50000000, 250000000)
    elif g in ['Drama', 'Romance', 'Comedy']:
        # Medium Budget: $5M to $60M
        budgets[i] = random.randint(5000000, 60000000)
    elif g in ['Horror', 'Thriller', 'Documentary']:
        # Low Budget: $500k to $20M
        budgets[i] = random.randint(500000, 20000000)
    else:
        budgets[i] = random.randint(1000000, 50000000)

# --- 3. RATINGS LOGIC (Correlated) ---
# IMDb Rating (Normal Distribution centered at 6.4)
imdb = np.random.normal(6.4, 1.3, num_rows)
imdb = np.clip(imdb, 1.1, 9.9).round(1)

# Rotten Tomatoes Critics (IMDb se related, thora strict)
rt_critics = (imdb * 10) + np.random.randint(-15, 10, num_rows) # Critics often harsh
rt_critics = np.clip(rt_critics, 0, 100).astype(int)

# Rotten Tomatoes Audience (IMDb se related, thora lenient)
rt_audience = (imdb * 10) + np.random.randint(-5, 15, num_rows) # Audience lenient
rt_audience = np.clip(rt_audience, 0, 100).astype(int)

# --- 4. BOX OFFICE REVENUE (The Realism Part) ---
# Revenue = Budget * (Quality Factor) * (Luck Factor)
# Agar Rating < 5.0 hai, to movie flop hone ka chance zyada hai.
box_office = []

for i in range(num_rows):
    b = budgets[i]
    r = imdb[i]
    
    # Base Multiplier based on rating
    if r > 8.0:
        multiplier = random.uniform(2.5, 6.0) # Super Hit
    elif r > 6.0:
        multiplier = random.uniform(1.2, 3.0) # Decent Hit
    elif r > 4.0:
        multiplier = random.uniform(0.6, 1.5) # Flop or Break-even
    else:
        multiplier = random.uniform(0.1, 0.8) # Disaster
        
    # Blockbuster Luck (Kabhi kabhi bekaar movie bhi kama leti hai marketing se)
    luck = random.uniform(0.8, 1.2)
    
    revenue = int(b * multiplier * luck)
    box_office.append(revenue)

# --- 5. FINAL TOUCHES ---
years = np.random.randint(1995, 2024, size=num_rows)
titles = [f"{selected_genres[i]}_Movie_{years[i]}_{x}" for i, x in enumerate(range(1, num_rows+1))]

# DataFrame banana
df = pd.DataFrame({
    'Movie_ID': range(1, num_rows + 1),
    'Title': titles,
    'Genre': selected_genres,
    'Release_Year': years,
    'Budget_USD': budgets,
    'Box_Office_Revenue_USD': box_office,
    'IMDb_Rating': imdb,
    'Rotten_Tomatoes_Critic': rt_critics,
    'Rotten_Tomatoes_Audience': rt_audience
})

# --- 6. SAVING ---
filename = 'Realistic_Movie_Dataset_1Lakh.csv'
df.to_csv(filename, index=False)

print(f"✅ SUCCESS! File Generated: {filename}")
print("-" * 30)
print("Data Preview:")
print(df[['Genre', 'Budget_USD', 'Box_Office_Revenue_USD', 'IMDb_Rating']].head(10))