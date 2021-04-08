"""Replaces all data in the cloud DynamoDB tables with data from the local DDB database."""
from boto3 import resource, client
from os import environ
from env_tools import apply_env


def create_cellar_table(provided_resource, table_name="Cellar"):
    print(f"Creating table {table_name} for {provided_resource.__str__()}")
    table = provided_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'beverage_id',
                'KeyType':       'HASH'
            },
            {
                'AttributeName': 'location',
                'KeyType':       'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'beverage_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'location',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits':  5,
            'WriteCapacityUnits': 2
        }
    )

    # Pause until the table is created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Table {table_name} created")


def create_picklist_table(provided_resource, table_name="CellarPicklists"):
    print(f"Creating table {table_name} for {provided_resource.__str__()}")
    table = provided_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'list_name',
                'KeyType':       'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'list_name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits':  1,
            'WriteCapacityUnits': 1
        }
    )

    # Pause until the table is created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Table {table_name} created")


def purge_all_table_data(table, hash_name=None, range_name=None):
    """Deletes all items from the provided DynamoDB table."""
    data = table.scan()
    print(f" --> Purging {len(data['Items'])} records from {table}")
    with table.batch_writer() as batch:
        for each in data['Items']:
            if range_name:
                batch.delete_item(
                    Key={
                        hash_name:  each[hash_name],
                        range_name: each[range_name]
                    }
                )
            else:
                batch.delete_item(
                    Key={
                        hash_name: each[hash_name]
                    }
                )


def copy_all_table_data(source_table, destination_table):
    """
    Reads all data from the source table, then writes to the destination table.
    Both tables must have the same schema.
    """
    data = source_table.scan()
    with destination_table.batch_writer() as batch:
        for each in data['Items']:
            batch.put_item(Item=each)


def display_all_table_data(table):
    """Prints a summary of data from the provided table."""
    data = table.scan()
    print(data, "\nItemized:")
    for each in data['Items']:
        print(each)
    print("=============\n")


# Environment variables
apply_env()
aws_region = environ.get('AWS_REGION')
aws_access_key = environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = environ.get('AWS_SECRET_ACCESS_KEY')

# Cloud connection (primary)
db_cloud_primary = resource('dynamodb',
                            region_name=aws_region,
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_access_key)

# Local connection
db_local = resource('dynamodb',
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_access_key,
                    endpoint_url='http://localhost:8008')
db_local_client = client('dynamodb',
                         region_name=aws_region,
                         aws_access_key_id=aws_access_key,
                         aws_secret_access_key=aws_secret_access_key,
                         endpoint_url='http://localhost:8008')

# Create tables, if necessary
if 'Cellar' not in db_cloud_primary.list_tables()['TableNames']:
    create_cellar_table(db_cloud_primary)

if 'CellarPicklists' not in db_cloud_primary.list_tables()['TableNames']:
    create_picklist_table(db_cloud_primary)

# Define local tables
cellar_table_local = db_local.Table('Cellar')
picklist_table_local = db_local.Table('CellarPicklists')

# Define cloud tables
cellar_table_cloud_primary = db_cloud_primary.Table('Cellar')
picklist_table_cloud_primary = db_cloud_primary.Table('CellarPicklists')

# Clear cloud primary tables
print("Clearing cloud primary tables")
purge_all_table_data(cellar_table_cloud_primary, 'beverage_id', 'location')
purge_all_table_data(picklist_table_cloud_primary, 'list_name')
print("Done clearing tables.")

# Local --> cloud primary
print("Writing to cloud primary tables")
copy_all_table_data(cellar_table_local, cellar_table_cloud_primary)
copy_all_table_data(picklist_table_local, picklist_table_cloud_primary)
print("Primary done")

print("Done writing to tables.")
