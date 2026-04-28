import csv
import happybase
from datetime import datetime

def connect_to_hbase():
    """Establish connection to HBase"""
    connection = happybase.Connection('localhost')
    return connection

def create_row_key(row):
    """Create composite row key based on the specified columns"""
    vendor_id = str(row.get('VendorID', ''))
    pickup_datetime = str(row.get('tpep_pickup_datetime', ''))
    pu_location_id = str(row.get('PULocationID', ''))
    do_location_id = str(row.get('DOLocationID', ''))
    
    # Combine the values with a separator
    row_key = f"{vendor_id}_{pickup_datetime}_{pu_location_id}_{do_location_id}"
    return row_key.encode('utf-8')

def process_csv_file(filename, table):
    """Process CSV file and insert data into HBase"""
    with open(filename, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        batch = table.batch()
        row_count = 0
        
        for row in csvreader:
            # Create composite row key
            row_key = create_row_key(row)
            
            # Prepare data for cf1 column family
            data = {
                b'cf1:VendorID': str(row.get('VendorID', '')).encode('utf-8'),
                b'cf1:tpep_pickup_datetime': str(row.get('tpep_pickup_datetime', '')).encode('utf-8'),
                b'cf1:tpep_dropoff_datetime': str(row.get('tpep_dropoff_datetime', '')).encode('utf-8'),
                b'cf1:passenger_count': str(row.get('passenger_count', '')).encode('utf-8'),
                b'cf1:trip_distance': str(row.get('trip_distance', '')).encode('utf-8'),
                b'cf1:RatecodeID': str(row.get('RatecodeID', '')).encode('utf-8'),
                b'cf1:store_and_fwd_flag': str(row.get('store_and_fwd_flag', '')).encode('utf-8'),
                b'cf1:PULocationID': str(row.get('PULocationID', '')).encode('utf-8'),
                b'cf1:DOLocationID': str(row.get('DOLocationID', '')).encode('utf-8'),
                b'cf1:payment_type': str(row.get('payment_type', '')).encode('utf-8'),
                b'cf1:fare_amount': str(row.get('fare_amount', '')).encode('utf-8'),
                b'cf1:extra': str(row.get('extra', '')).encode('utf-8'),
                b'cf1:mta_tax': str(row.get('mta_tax', '')).encode('utf-8'),
                b'cf1:tip_amount': str(row.get('tip_amount', '')).encode('utf-8'),
                b'cf1:tolls_amount': str(row.get('tolls_amount', '')).encode('utf-8'),
                b'cf1:improvement_surcharge': str(row.get('improvement_surcharge', '')).encode('utf-8'),
                b'cf1:total_amount': str(row.get('total_amount', '')).encode('utf-8'),
                b'cf1:Airport_fee': str(row.get('Airport_fee', '0')).encode('utf-8')
            }
            
            # Put the data into the batch
            batch.put(row_key, data)
            row_count += 1
            
            # Commit every 10000 records
            if row_count % 10000 == 0:
                batch.send()
                print(f"Processed {row_count} records")
                batch = table.batch()
        
        # Send any remaining records
        batch.send()
        print(f"Finished processing {row_count} records from {filename}")

def verify_data(table, num_rows=5):
    """Verify the imported data by displaying sample rows"""
    print("\nSample data from HBase table:")
    for key, data in table.scan(limit=num_rows):
        print(f"\nRow key: {key.decode('utf-8')}")
        for column, value in data.items():
            print(f"{column.decode('utf-8')}: {value.decode('utf-8')}")

def main():
    try:
        # Connect to HBase
        connection = connect_to_hbase()
        
        # Get the existing table
        table_name = 'yellow_taxi_hbase'
        table = connection.table(table_name)
        
        # Process each CSV file
        input_files = [
            '/home/hadoop/mr_assign/input_dataset/yellow_tripdata_2017-03.csv',
            '/home/hadoop/mr_assign/input_dataset/yellow_tripdata_2017-04.csv'
        ]
        
        for file in input_files:
            print(f"\nProcessing file: {file}")
            process_csv_file(file, table)
        
        # Verify the imported data
        verify_data(table)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()