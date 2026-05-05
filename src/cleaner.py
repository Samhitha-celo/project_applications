# src/cleaner.py
import pandas as pd

def clean_data(filepath="data/raw/food_orders.csv"):
    df = pd.read_csv(filepath)
    
    # Convert date
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['order_date'].dt.to_period('M').astype(str)
    df['week'] = df['order_date'].dt.to_period('W').astype(str)
    df['day_of_week'] = df['order_date'].dt.day_name()
    df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M').dt.hour
    
    # Meal time classification
    def get_meal_time(hour):
        if 6 <= hour <= 10: return 'Breakfast'
        elif 11 <= hour <= 15: return 'Lunch'
        elif 16 <= hour <= 18: return 'Snacks'
        else: return 'Dinner'
    
    df['meal_time'] = df['hour'].apply(get_meal_time)
    
    # Remove negatives
    df = df[df['total_amount'] >= 0]
    
    df.to_csv("./data/processed/food_orders_clean.csv", index=False)
    print("✅ Cleaned data saved!")
    return df

if __name__ == "__main__":
    clean_data()