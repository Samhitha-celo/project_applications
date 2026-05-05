# src/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_food_data(num_orders=300, days=180):
    
    restaurants = {
        "Burger King": ["Whopper", "Cheese Fries", "Chocolate Shake", "Crispy Chicken"],
        "McDonald's": ["McAloo Tikki", "McSpicy Paneer", "Large Fries", "McFlurry"],
        "Subway": ["Veggie Delight Sub", "Chicken Teriyaki", "Multigrain Sandwich"],
        "Zomato Kitchen": ["Dal Rice Bowl", "Paneer Butter Masala", "Chicken Biryani"],
        "Freshmenu": ["Grilled Chicken Salad", "Quinoa Bowl", "Fruit Smoothie"],
        "Box8": ["Rajma Chawal", "Butter Chicken", "Paneer Tikka Wrap"],
        "Starbucks": ["Frappuccino", "Cold Brew", "Croissant"],
        "Wow Momo": ["Steamed Momos", "Fried Momos", "Momo Soup"],
        "Oven Story": ["Margherita Pizza", "BBQ Chicken Pizza", "Pasta"],
        "Licious": ["Grilled Fish", "Chicken Kebab", "Mutton Curry"]
    }

    food_health_map = {
        "Whopper": "Unhealthy", "Cheese Fries": "Unhealthy",
        "Chocolate Shake": "Unhealthy", "Crispy Chicken": "Unhealthy",
        "McAloo Tikki": "Moderate", "McSpicy Paneer": "Unhealthy",
        "Large Fries": "Unhealthy", "McFlurry": "Unhealthy",
        "Veggie Delight Sub": "Healthy", "Chicken Teriyaki": "Moderate",
        "Multigrain Sandwich": "Healthy", "Dal Rice Bowl": "Healthy",
        "Paneer Butter Masala": "Moderate", "Chicken Biryani": "Moderate",
        "Grilled Chicken Salad": "Healthy", "Quinoa Bowl": "Healthy",
        "Fruit Smoothie": "Healthy", "Rajma Chawal": "Healthy",
        "Butter Chicken": "Moderate", "Paneer Tikka Wrap": "Moderate",
        "Frappuccino": "Unhealthy", "Cold Brew": "Moderate",
        "Croissant": "Unhealthy", "Steamed Momos": "Moderate",
        "Fried Momos": "Unhealthy", "Momo Soup": "Healthy",
        "Margherita Pizza": "Unhealthy", "BBQ Chicken Pizza": "Unhealthy",
        "Pasta": "Moderate", "Grilled Fish": "Healthy",
        "Chicken Kebab": "Healthy", "Mutton Curry": "Moderate"
    }

    price_map = {
        "Whopper": 229, "Cheese Fries": 149, "Chocolate Shake": 179,
        "Crispy Chicken": 199, "McAloo Tikki": 89, "McSpicy Paneer": 179,
        "Large Fries": 139, "McFlurry": 149, "Veggie Delight Sub": 299,
        "Chicken Teriyaki": 399, "Multigrain Sandwich": 249,
        "Dal Rice Bowl": 149, "Paneer Butter Masala": 249,
        "Chicken Biryani": 299, "Grilled Chicken Salad": 349,
        "Quinoa Bowl": 399, "Fruit Smoothie": 199, "Rajma Chawal": 179,
        "Butter Chicken": 299, "Paneer Tikka Wrap": 249,
        "Frappuccino": 399, "Cold Brew": 299, "Croissant": 199,
        "Steamed Momos": 149, "Fried Momos": 169, "Momo Soup": 129,
        "Margherita Pizza": 449, "BBQ Chicken Pizza": 599,
        "Pasta": 349, "Grilled Fish": 449,
        "Chicken Kebab": 399, "Mutton Curry": 349
    }

    orders = []
    start_date = datetime.now() - timedelta(days=days)

    for i in range(num_orders):
        restaurant = random.choice(list(restaurants.keys()))
        item = random.choice(restaurants[restaurant])
        order_date = start_date + timedelta(
            days=random.randint(0, days),
            hours=random.choice([8,9,13,14,19,20,21])
        )
        quantity = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        base_price = price_map[item]
        delivery_fee = random.choice([0, 29, 39, 49])
        discount = random.choice([0, 20, 30, 50, 100])
        total = (base_price * quantity) + delivery_fee - discount

        orders.append({
            "order_id": f"ORD{1000+i}",
            "order_date": order_date.strftime("%Y-%m-%d"),
            "order_time": order_date.strftime("%H:%M"),
            "restaurant": restaurant,
            "item": item,
            "quantity": quantity,
            "base_price": base_price,
            "delivery_fee": delivery_fee,
            "discount": discount,
            "total_amount": max(total, 0),
            "health_category": food_health_map[item],
            "platform": random.choice(["Zomato", "Swiggy", "Blinkit"])
        })

    df = pd.DataFrame(orders)
    df.to_csv("./data/raw/food_orders.csv", index=False)
    print(f"✅ Generated {num_orders} orders saved to data/raw/food_orders.csv")
    return df

if __name__ == "__main__":
    df = generate_food_data()
    print(df.head())