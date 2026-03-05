import os
import csv
import math

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth surface."""
    R = 6371.0  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def create_custom_data():
    os.makedirs("data", exist_ok=True)

    # 1. Custom Facilities Data (Mapped near Saintgits College, Kerala)
    facilities = [
        ["Facility_ID", "Facility_Name", "Type", "Daily_Demand", "Latitude", "Longitude"],
        ["MED_CENTER", "Campus Medical Center", "Hospital", 80, 9.5485, 76.5412],
        ["ENG_BUILDING", "Engineering Building", "Academic", 30, 9.5490, 76.5415],
        ["SCIENCE_HALL", "Science Hall", "Academic", 35, 9.5475, 76.5420],
        ["DORM_A", "North Dormitory", "Residential", 55, 9.5500, 76.5405],
        ["DORM_B", "South Dormitory", "Residential", 45, 9.5460, 76.5430],
        ["LIBRARY", "Main Library", "Academic", 25, 9.5480, 76.5410]
    ]

    # 2. Custom Warehouses Data
    warehouses = [
        ["Warehouse_ID", "Warehouse_Name", "Daily_Capacity", "Construction_Cost", "Operational_Cost/Day", "Latitude", "Longitude"],
        ["WH_NORTH", "North Campus Warehouse", 400, 300000, 800, 9.5510, 76.5400],
        ["WH_SOUTH", "South Campus Warehouse", 350, 280000, 700, 9.5450, 76.5440],
        ["WH_EAST", "East Gate Warehouse", 450, 320000, 900, 9.5485, 76.5450]
    ]

    # 3. Dynamically Calculate Transportation Costs using Haversine
    transport_costs = [["Warehouse_ID", "Facility_ID", "Distance_km", "Cost"]]
    
    for w in warehouses[1:]:
        w_id, w_lat, w_lon = w[0], w[5], w[6]
        for f in facilities[1:]:
            f_id, f_lat, f_lon = f[0], f[4], f[5]
            
            # Calculate physical distance
            dist_km = haversine(w_lat, w_lon, f_lat, f_lon)
            
            # Base cost of $3.20 + $1.85 per kilometer (Keeps it realistic and within original constraints)
            cost = round(3.20 + (dist_km * 1.85), 2)
            
            transport_costs.append([w_id, f_id, round(dist_km, 2), cost])

    # Helper function to write CSVs
    def write_csv(filename, data):
        filepath = os.path.join("data", filename)
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"✅ Generated {filepath}")

    # Write files
    print("🌍 Relocating campus to Kerala and calculating Haversine distances...")
    write_csv("facilities.csv", facilities)
    write_csv("warehouses.csv", warehouses)
    write_csv("transportation_costs.csv", transport_costs)
    print("\n🚀 Custom datasets successfully created!")

if __name__ == "__main__":
    create_custom_data()