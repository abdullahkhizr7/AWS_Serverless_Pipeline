## importing libaries
import json
import boto3
import pandas as pd
import io
from datetime import datetime

## defining a function to read data from json file
def flatten(data):
    orders_data =[]
    for order in data:
        for product in order['products']:
            row = {
                'order_id' : order['order_id'],
                'order_date' : order['order_date'],
                'total_amount' : order['total_amount'],
                'customer_id' : order['customer']['customer_id'],
                'name' : order['customer']['name'],
                'email' : order['customer']['email'],
                'address' : order['customer']['address'],
                'product_id' : product['product_id'],
                'product_name' : product['name'],
                'category' : product['category'],
                'price' : product['price'],
                'quantity' : product['quantity'],
            }
            orders_data.append(row)
        
    data = pd.DataFrame(orders_data)
    return data

## The lamda_handler will automatically callled
def lambda_handler(event, context):
    # TODO implement

    ## For files with any name can be read using bucket _name and key
    bucket_name= event['Records'][0]['s3']['bucket']['name']
    key=event['Records'][0]['s3']['object']['key']

    ## Interacting with s3
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=key)
    content = response['Body'].read().decode('utf-8')
    data = json.loads(content)
    df = flatten(data)
    
    ## to parquet file
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False, engine='pyarrow')

    ## Getting present Date and Time
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    ## Modifying uploading name
    key_stagging = f'parquet_files/orders_Etl_{timestamp}.parquet'
    ## putting to s3
    s3.put_object(Bucket=bucket_name, Key=key_stagging, Body=parquet_buffer.getvalue())

    ## Automatting the crawler
    crawler_name = 'etl_serverless_parquet'
    glue = boto3.client('glue')
    response = glue.start_crawler(Name=crawler_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
