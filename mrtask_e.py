#!/usr/bin/env python3

import sys

def mapper():
    # Skip header
    header = True
    
    for line in sys.stdin:
        if header:
            header = False
            continue
            
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Split the line into fields
        fields = line.split(',')
        
        try:
            if len(fields) >= 17:  # Ensure we have enough fields
                pickup_location = fields[7]    # PULocationID
                fare_amount = float(fields[10])  # fare_amount
                tip_amount = float(fields[13])   # tip_amount
                
                # Only consider rides with valid fare amounts
                if fare_amount > 0:
                    # Emit: pickup_location \t tip_amount,fare_amount,1
                    print(f'{pickup_location}\t{tip_amount},{fare_amount},1')
                
        except (ValueError, IndexError):
            # Skip lines with invalid data
            continue

def reducer():
    current_location = None
    total_tips = 0.0
    total_fare = 0.0
    trip_count = 0
    
    # Store results to sort later
    results = []
    
    # Print header
    print("Location_ID\tTrip_Count\tTotal_Tips\tTotal_Fare\tTip_Ratio_Percentage")
    
    for line in sys.stdin:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        try:
            # Parse input from mapper
            location, values = line.split('\t')
            tip, fare, count = map(float, values.split(','))
            
            # If this is the first location or same location, accumulate
            if current_location == location:
                total_tips += tip
                total_fare += fare
                trip_count += count
            else:
                # If we have a previous location, calculate and store its results
                if current_location:
                    if total_fare > 0:  # Avoid division by zero
                        tip_ratio = (total_tips / total_fare) * 100  # Convert to percentage
                        results.append((current_location, trip_count, total_tips, total_fare, tip_ratio))
                
                # Start accumulating for new location
                current_location = location
                total_tips = tip
                total_fare = fare
                trip_count = count
                
        except ValueError:
            continue
    
    # Calculate and store the last location
    if current_location and total_fare > 0:
        tip_ratio = (total_tips / total_fare) * 100
        results.append((current_location, trip_count, total_tips, total_fare, tip_ratio))
    
    # Sort results by tip ratio in descending order
    results.sort(key=lambda x: x[4], reverse=True)
    
    # Output sorted results with formatted numbers
    for location, count, tips, fare, ratio in results:
        print(f'{location}\t{int(count)}\t${tips:.2f}\t${fare:.2f}\t{ratio:.2f}%')

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()