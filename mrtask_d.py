#!/usr/bin/env python3

import sys
from datetime import datetime

def calculate_trip_duration(pickup_str, dropoff_str):
    """Calculate trip duration in minutes"""
    try:
        pickup_time = datetime.strptime(pickup_str, '%Y-%m-%d %H:%M:%S')
        dropoff_time = datetime.strptime(dropoff_str, '%Y-%m-%d %H:%M:%S')
        duration = (dropoff_time - pickup_time).total_seconds() / 60.0
        return duration if duration >= 0 else 0
    except ValueError:
        return 0

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
            if len(fields) >= 8:  # Ensure we have enough fields
                pickup_location = fields[7]  # PULocationID
                pickup_time = fields[1]      # tpep_pickup_datetime
                dropoff_time = fields[2]     # tpep_dropoff_datetime
                
                # Calculate trip duration in minutes
                duration = calculate_trip_duration(pickup_time, dropoff_time)
                
                if duration > 0:  # Only emit valid durations
                    # Emit: pickup_location \t duration,1
                    print(f'{pickup_location}\t{duration},1')
                
        except (ValueError, IndexError):
            # Skip lines with invalid data
            continue

def reducer():
    current_location = None
    total_duration = 0.0
    trip_count = 0
    
    # Store results to sort later
    results = []
    
    # Print header first
    print("Location_ID\tTrip_Count\tAverage_Duration_Minutes")
    
    for line in sys.stdin:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Parse input from mapper
        try:
            location, value = line.split('\t')
            duration, count = map(float, value.split(','))
            
            # If this is the first location or same location, accumulate
            if current_location == location:
                total_duration += duration
                trip_count += count
            else:
                # If we have a previous location, store its results
                if current_location:
                    avg_duration = total_duration / trip_count
                    results.append((current_location, trip_count, avg_duration))
                
                # Start accumulating for new location
                current_location = location
                total_duration = duration
                trip_count = count
                
        except ValueError:
            continue
    
    # Store the last location
    if current_location:
        avg_duration = total_duration / trip_count
        results.append((current_location, trip_count, avg_duration))
    
    # Sort results by average duration in descending order
    results.sort(key=lambda x: x[2], reverse=True)
    
    # Output sorted results
    for location, count, avg_duration in results:
        print(f'{location}\t{int(count)}\t{avg_duration:.2f}')

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()