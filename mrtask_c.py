#!/usr/bin/env python3

import sys

def get_payment_type_name(code):
    """Convert payment type code to descriptive name"""
    payment_types = {
        '1': 'Credit card',
        '2': 'Cash',
        '3': 'No charge',
        '4': 'Dispute',
        '5': 'Unknown',
        '6': 'Voided trip'
    }
    return payment_types.get(code, 'Unknown')

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
            if len(fields) >= 10:  # Ensure we have enough fields
                payment_type = fields[9]  # payment_type field
                
                # Convert payment type code to name
                payment_name = get_payment_type_name(payment_type)
                
                # Emit key-value pair: payment_type \t 1
                print(f'{payment_name}\t1')
                
        except ValueError:
            # Skip lines with invalid data
            continue

def reducer():
    current_payment_type = None
    payment_count = 0
    
    # Store results to sort later
    results = []
    
    for line in sys.stdin:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Parse input from mapper
        payment_type, count = line.split('\t')
        
        try:
            count = int(count)
        except ValueError:
            continue
            
        # If this is the first payment type or same type, accumulate
        if current_payment_type == payment_type:
            payment_count += count
        else:
            # If we have a previous payment type, store its results
            if current_payment_type:
                results.append((current_payment_type, payment_count))
            
            # Start accumulating for new payment type
            current_payment_type = payment_type
            payment_count = count
    
    # Store the last payment type
    if current_payment_type:
        results.append((current_payment_type, payment_count))
    
    # Sort results by count in descending order
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Output sorted results
    for payment_type, count in results:
        print(f'{payment_type}\t{count}')

if __name__ == "__main__":
    if sys.argv[1] == "mapper":
        mapper()
    elif sys.argv[1] == "reducer":
        reducer()