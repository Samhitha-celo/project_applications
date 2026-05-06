# Run this once to patch your existing CSV
import pandas as pd
import random

df = pd.read_csv("data/raw/food_orders.csv")

# Reassign hours with proper distribution across all meal times
all_hours = [7,8,9,10,   # Breakfast
             12,13,14,15, # Lunch  
             16,17,18,    # Snacks
             19,20,21,22] # Dinner
df['order_time'] = [f"{random.choice(all_hours):02d}:00" for _ in range(len(df))]
df.to_csv("data/raw/food_orders.csv", index=False)
print("Done! Now run cleaner.py")