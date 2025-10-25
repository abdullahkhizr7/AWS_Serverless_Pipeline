# AWS_Serverless_Pipeline
Serverless ETL Pipeline for JSON to Parquet

Project Overview

This AWS Lambda function implements a serverless ETL (Extract, Transform, Load) pipeline. Its primary purpose is to automatically process raw, nested JSON order files uploaded to an S3 bucket, transform them into a flattened, columnar Parquet format, and catalog them for analysis with Amazon Athena.

The pipeline is event-driven and leverages several key AWS services, including S3, Lambda, Glue, and CloudWatch, to create an automated and scalable data processing workflow.

Architecture and Workflow

The data flows through the system in the following steps:

1.  Trigger (Amazon S3): The entire process begins when a new JSON file (e.g., `orders.json`) is uploaded to a specific S3 bucket. An S3 Event Notification is configured to act as a trigger, invoking the Lambda function automatically.

2.  Extract (AWS Lambda & S3): The `lambda_handler` function receives the S3 event. It identifies the `bucket_name` and `key` (file name) of the newly uploaded object. Using the Boto3 (AWS SDK for Python) S3 client, it reads the raw JSON file from S3 into memory.

3.  Transform (AWS Lambda & Pandas):
    * The raw JSON content, which contains nested data (customers and a list of products), is loaded.
    * A helper function, `flatten()`, is used with the Pandas library to denormalize this nested structure. It creates a flat tabular format where each row represents a single product item within an order.
    * This Pandas DataFrame is then converted from its in-memory representation into the Parquet file format. Parquet is a highly efficient, columnar storage format optimized for analytics.

4.  Load (AWS Lambda & S3):
    * The function generates a unique file name for the new Parquet file using a timestamp (e.g., `orders_Etl_20251025_133000.parquet`).
    * Using the Boto3 S3 client, it uploads this Parquet file to a different prefix (folder) within the same S3 bucket, such as `parquet_files/`. This separates the raw data (source) from the processed data (destination).

5.  Catalog (AWS Glue):
    * Immediately after uploading the Parquet file, the function uses the Boto3 Glue client to start an AWS Glue Crawler (named `etl_serverless_parquet` in the code).
    * This crawler is pre-configured in AWS Glue to scan the `parquet_files/` S3 prefix. It automatically detects the new Parquet file, infers its schema (column names and data types), and updates the metadata in the AWS Glue Data Catalog.

6.  Query (Amazon Athena):
    * (Implied use) With the Glue Data Catalog updated, an analyst can now use Amazon Athena to run standard SQL queries directly on the Parquet files in S3. Athena uses the Glue Catalog as its "database" and "table" definitions, allowing for powerful, serverless data analysis without needing to manage any infrastructure.

---

Services Used in This Pipeline

* AWS Lambda: The core compute service that runs the Python code. It acts as the "glue" that orchestrates the entire ETL process, responding to the trigger and interacting with other services.
* Amazon S3 (Simple Storage Service): Acts as the data lake.
    * Source Storage: Holds the incoming raw JSON files.
    * Event Trigger: Provides the event notification that starts the pipeline.
    * Destination Storage: Stores the processed, analytics-ready Parquet files.
* AWS Glue: A fully managed ETL and data catalog service.
    * Glue Crawler: Used to automate schema discovery. The Lambda function triggers the crawler (`etl_serverless_parquet`) to scan the processed data.
    * Glue Data Catalog: A central metadata repository. The crawler populates this catalog with table definitions that Athena uses for querying.
* Amazon Athena: (End-goal) The interactive query service that allows users to analyze the data in S3 using standard SQL. It reads directly from the Parquet files, using the schema defined in the Glue Data Catalog.
* Amazon CloudWatch Logs: (Implicit) All AWS Lambda functions automatically stream their execution logs, `print()` statements, and any errors to CloudWatch Logs. This is essential for monitoring the pipeline's health and debugging any issues that may arise during processing.
* Boto3 (AWS SDK): The Python library used within the Lambda function to make API calls to S3 (`get_object`, `put_object`) and Glue (`start_crawler`).
* Pandas: A popular Python library used for the in-memory data transformation, specifically to flatten the JSON and create the DataFrame that is then saved as Parquet.
