import os
import csv

def create_project_data():
    # 1. Create the data directory
    os.makedirs("data", exist_ok=True)
    print("Created 'data/' directory.")

    # 2. Facilities Data
    facilities = [
        ["Facility_ID", "Facility_Name", "Type", "Daily_Demand"],
        ["MED_CENTER", "Campus Medical Center", "Hospital", 80],
        ["ENG_BUILDING", "Engineering Building", "Academic", 30],
        ["SCIENCE_HALL", "Science Hall", "Academic", 35],
        ["DORM_A", "North Dormitory", "Residential", 55],
        ["DORM_B", "South Dormitory", "Residential", 45],
        ["LIBRARY", "Main Library", "Academic", 25]
    ]

    # 3. Warehouses Data
    warehouses = [
        ["Warehouse_ID", "Warehouse_Name", "Daily_Capacity", "Construction_Cost", "Operational_Cost/Day"],
        ["WH_NORTH", "North Campus Warehouse", 400, 300000, 800],
        ["WH_SOUTH", "South Campus Warehouse", 350, 280000, 700],
        ["WH_EAST", "East Gate Warehouse", 450, 320000, 900]
    ]

    # 4. Transportation Costs Data
    transport_costs = [
        ["Warehouse_ID", "Facility_ID", "Cost"],
        ["WH_NORTH", "MED_CENTER", 4.50], ["WH_NORTH", "ENG_BUILDING", 3.80], 
        ["WH_NORTH", "SCIENCE_HALL", 4.10], ["WH_NORTH", "DORM_A", 3.75], 
        ["WH_NORTH", "DORM_B", 4.80], ["WH_NORTH", "LIBRARY", 4.20],
        
        ["WH_SOUTH", "MED_CENTER", 4.90], ["WH_SOUTH", "ENG_BUILDING", 4.60], 
        ["WH_SOUTH", "SCIENCE_HALL", 4.25], ["WH_SOUTH", "DORM_A", 4.95], 
        ["WH_SOUTH", "DORM_B", 3.68], ["WH_SOUTH", "LIBRARY", 4.15],
        
        ["WH_EAST", "MED_CENTER", 4.30], ["WH_EAST", "ENG_BUILDING", 4.15], 
        ["WH_EAST", "SCIENCE_HALL", 3.90], ["WH_EAST", "DORM_A", 4.40], 
        ["WH_EAST", "DORM_B", 4.75], ["WH_EAST", "LIBRARY", 3.85]
    ]

    # Helper function to write CSVs
    def write_csv(filename, data):
        filepath = os.path.join("data", filename)
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        print(f"Generated {filepath}")

    # Generate the files
    write_csv("facilities.csv", facilities)
    write_csv("warehouses.csv", warehouses)
    write_csv("transportation_costs.csv", transport_costs)
    
    print("\nAll datasets created successfully. You can now run your main.py script.")

if __name__ == "__main__":
    create_project_data()