#!/usr/bin/env python3

import sys
from datetime import datetime

def get_time_category(hour):
    """Categorize hour as day (6AM-6PM) or night (6PM-6AM)"""
    return 'day' if 6 <= hour < 18 else 'night'

def is_weekend(day_of_week):
    """Check if day is weekend (Saturday=5, Sunday=6)"""
    return day_of_week >= 5

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
                pickup_time_str = fields[1]  # tpep_pickup_datetime
                total_amount = float(fields[16])  # total_amount
                
                # Parse datetime
                pickup_time = datetime.strptime(pickup_time_str, '%Y-%m-%d %H:%M:%S')
                
                # Extract time components
                month_year = pickup_time.strftime('%Y-%m')
                hour = pickup_time.hour
                day_of_week = pickup_time.weekday()  # Monday=0, Sunday=6
                
                # Categorize time periods
                time_of_day = get_time_category(hour)
                day_type = 'weekend' if is_weekend(day_of_week) else 'weekday'
                
                # Create composite key: month_year,time_of_day,day_type
                composite_key = f'{month_year},{time_of_day},{day_type}'
                
                # Emit: composite_key \t amount,1
                print(f'{composite_key}\t{total_amount},1')
                
        except (ValueError, IndexError):
            # Skip lines with invalid data
            continue

def reducer():
    current_key = None
    total_revenue = 0.0
    trip_count = 0
    
    # Store results to sort later
    results = []
    
    for line in sys.stdin:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        try:
            # Parse input from mapper
            key, value = line.split('\t')
            revenue, count = map(float, value.split(','))
            
            # If this is the first key or same key, accumulate
            if current_key == key:
                total_revenue += revenue
                trip_count += count
            else:
                # If we have a previous key, calculate and store its results
                if current_key:
                    avg_revenue = total_revenue / trip_count
                    month, time_category, day_type = current_key.split(',')
                    results.append((month, time_category, day_type, trip_count, avg_revenue))
                
                # Start accumulating for new key
                current_key = key
                total_revenue = revenue
                trip_count = count
                
        except ValueError:
            continue
    
    # Calculate and store the last key
    if current_key:
        avg_revenue = total_revenue / trip_count
        month, time_category, day_type = current_key.split(',')
        results.append((month, time_category, day_type, trip_count, avg_revenue))
    
    # Sort results by month, then time_category, then day_type
    results.sort(key=lambda x: (x[0], x[1], x[2]))
    
    # Output sorted results with formatted header
    print("Month\tTime\tDay Type\tTrip Count\tAvg Revenue")
    print("-" * 60)
    for month, time_cat, day_type, count, avg_rev in results:
        print(f"{month}\t{time_cat}\t{day_type}\t{int(count)}\t${avg_rev:.2f}")

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()