import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

# Define car brands
brands = ['Tesla', 'Ford', 'Chevrolet', 'Nissan', 'Hyundai', 'Kia', 'Volkswagen', 'Audi', 'Porsche', 'Rivian', 'Polestar', 'BMW', 'Mercedes-Benz']

def generate_ev_data(num_samples=1500):
    data = []
    for _ in range(num_samples):
        brand = np.random.choice(brands)
        
        # Battery capacity (kWh) - typical range 30 to 130
        battery_capacity = round(np.random.uniform(30.0, 130.0), 1)
        
        # Motor power (kW) - typical range 100 to 750
        motor_power = int(np.random.uniform(100, 750))
        
        # Weight (kg) - correlated with battery and power
        weight = int(1500 + (battery_capacity * 8) + (motor_power * 0.5) + np.random.normal(0, 100))
        
        # Charging capability (kW) - max charging speed
        charging_capability_options = [50, 100, 150, 250, 350]
        charging_capability = int(np.random.choice(charging_capability_options))
        
        # Aerodynamics (Cd)
        drag_coefficient = round(np.random.uniform(0.20, 0.35), 2)
        
        # EFFICIENCY calculation (km per kWh).
        # Lower weight, lower drag -> better efficiency
        efficiency = 8.0 - (weight / 1000) - (drag_coefficient * 5) + np.random.normal(0, 0.5)
        efficiency = max(3.0, efficiency) # Ensure minimum efficiency
        
        # TARGET 1: Range (km) = Battery Capacity * Efficiency
        # Added a bit of noise
        range_km = int((battery_capacity * efficiency) + np.random.normal(0, 15))
        range_km = max(100, range_km) # Minimum 100 km range
        
        # TARGET 2: Charge time (mins) to go from 10% to 80% (70% of battery)
        energy_to_charge = battery_capacity * 0.7
        # Effective charging power is lower than max capability on average
        effective_charge_power = charging_capability * 0.8
        charge_time_mins = int((energy_to_charge / effective_charge_power) * 60) + int(np.random.normal(5, 2))
        charge_time_mins = max(10, charge_time_mins) # Minimum 10 minutes
        
        # Price (USD)
        price = int(25000 + (battery_capacity * 200) + (motor_power * 50) + np.random.normal(0, 5000))
        
        data.append({
            'Brand': brand,
            'Battery_Capacity_kWh': battery_capacity,
            'Motor_Power_kW': motor_power,
            'Weight_kg': weight,
            'Max_Charge_Power_kW': charging_capability,
            'Drag_Coefficient': drag_coefficient,
            'Price_USD': price,
            'Range_km': range_km,
            'Charge_Time_mins': charge_time_mins
        })
        
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    print("Generating synthetic EV dataset...")
    df = generate_ev_data(2000)
    output_path = os.path.join(os.path.dirname(__file__), 'ev_data_synthetic.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path} with {len(df)} records.")
    print("Sample data:")
    print(df.head())
