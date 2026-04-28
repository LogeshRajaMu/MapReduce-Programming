#!/usr/bin/env python3

import sys
from datetime import datetime

# Mapper
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
                vendor_id = fields[0]
                total_amount = float(fields[16])
                
                # Emit key-value pair: vendor_id \t 1,total_amount
                print(f'{vendor_id}\t1,{total_amount}')
                
        except ValueError:
            # Skip lines with invalid data
            continue

# Reducer
def reducer():
    current_vendor = None
    trip_count = 0
    total_revenue = 0.0
    
    for line in sys.stdin:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Parse input from mapper
        vendor_id, value = line.split('\t')
        count, amount = value.split(',')
        
        try:
            count = int(count)
            amount = float(amount)
        except ValueError:
            continue
            
        # If this is the first vendor or same vendor, accumulate
        if current_vendor == vendor_id:
            trip_count += count
            total_revenue += amount
        else:
            # If we have a previous vendor, output their results
            if current_vendor:
                print(f'{current_vendor}\t{trip_count},{total_revenue:.2f}')
            
            # Start accumulating for new vendor
            current_vendor = vendor_id
            trip_count = count
            total_revenue = amount
    
    # Output the last vendor
    if current_vendor:
        print(f'{current_vendor}\t{trip_count},{total_revenue:.2f}')

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()
