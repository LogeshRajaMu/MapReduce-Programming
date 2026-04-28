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
                total_amount = float(fields[16])  # total_amount
                
                if total_amount >= 0:  # Only consider non-negative amounts
                    # Emit: pickup_location \t total_amount,1
                    print(f'{pickup_location}\t{total_amount},1')
                
        except (ValueError, IndexError):
            # Skip lines with invalid data
            continue

def reducer():
    current_location = None
    total_revenue = 0.0
    trip_count = 0
    
    # Store results to sort later
    results = []
    
    for line in sys.stdin:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        try:
            # Parse input from mapper
            location, value = line.split('\t')
            amount, count = map(float, value.split(','))
            
            # If this is the first location or same location, accumulate
            if current_location == location:
                total_revenue += amount
                trip_count += count
            else:
                # If we have a previous location, store its results
                if current_location:
                    avg_revenue = total_revenue / trip_count
                    results.append((current_location, int(trip_count), total_revenue, avg_revenue))
                
                # Start accumulating for new location
                current_location = location
                total_revenue = amount
                trip_count = count
                
        except ValueError:
            continue
    
    # Store the last location
    if current_location:
        avg_revenue = total_revenue / trip_count
        results.append((current_location, int(trip_count), total_revenue, avg_revenue))
    
    # Sort results by total revenue in descending order
    results.sort(key=lambda x: x[2], reverse=True)
    
    # Print header
    print("LocationID\tTrip_Count\tTotal_Revenue\tAvg_Revenue")
    print("-" * 65)
    
    # Output sorted results
    for location, count, total_rev, avg_rev in results:
        print(f"{location}\t{count}\t${total_rev:.2f}\t${avg_rev:.2f}")

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()