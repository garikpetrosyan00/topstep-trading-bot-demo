# Generating realistic sample data
import csv
import math
import random
from datetime import datetime, timedelta

def generate_csv(path):
    start_price = 4050.0 # Realistic ES price
    start_time = datetime(2023, 10, 27, 9, 30, 0)
    
    rows = []
    price = start_price
    trend = 0.5 # Slight upward trend
    
    for i in range(1000): # 1000 minutes
        # Sine wave for cyclicality + random noise + trend
        cycle = math.sin(i / 50.0) * 10
        noise = (random.random() - 0.5) * 2.0
        
        price = start_price + cycle + noise + (i * 0.02)
        
        ts = start_time + timedelta(minutes=i)
        rows.append({"timestamp": ts.isoformat(), "price": f"{price:.2f}"})

    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "price"])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    generate_csv("data/sample_prices.csv")
    print("Generated data/sample_prices.csv")
