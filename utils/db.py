# based off the excellent gist by Martina Pugliese
# https://gist.github.com/martinapugliese/cae86eb68f5aab59e87332725935fd5f
import boto3
from boto3.dynamodb.conditions import Key, Attr
from boto3.dynamodb.types import DYNAMODB_CONTEXT

dynamodb = boto3.resource('dynamodb')

class DynamoDBClient:
    def __init__(self):
        print()

    def read_table_item(self, table_name, pk_name, pk_value):
        """
        Return item read by primary key.
        """
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={pk_name: pk_value})

        return response
    
    def read_table_item_ck(self, table_name, key):
        """
        Return item read by primary key.
        """
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=key)

        return response

    def add_item(self, table_name, col_dict):
        """
        Add one item (row) to table. col_dict is a dictionary {col_name: value}.
        """
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=col_dict)

        return response

    def update_item(self, table_name, pk_name, pk_value, col_dict):
        """
        update one item (row) to table. col_dict is a dictionary {col_name: value}.
        """

        update_expression = 'SET {}'.format(','.join(f'#{k}=:{k}' for k in col_dict))
        expression_attribute_values = {f':{k}': v for k, v in col_dict.items()}
        expression_attribute_names = {f'#{k}': k for k in col_dict}

        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key={'{}'.format(pk_name): pk_value},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues='UPDATED_NEW',
        )

        return response

    def delete_item(self, table_name, pk_name, pk_value):
        """
        Delete an item (row) in table from its primary key.
        """
        table = dynamodb.Table(table_name)
        return table.delete_item(Key={pk_name: pk_value})

    def query_table(self, table_name, filter_key=None, filter_value=None):
        """
        Perform a query operation on the table.
        Can specify filter_key (col name) and its value to be filtered.
        """
        table = dynamodb.Table(table_name)

        if filter_key and filter_value:
            filtering_exp = Key(filter_key).eq(filter_value)
            response = table.query(KeyConditionExpression=filtering_exp)
        else:
            response = table.query()

        return response

    def execute_query(
        self,
        table_name,
        key_expression=None,
        expression_values={},
        sort=False
    ):
        """
        queries the 'table_name'.
        'key_expression' must be of type FilterExpression
        'filter_expression' must be of type KeyConditionExpression
        """
        table = dynamodb.Table(table_name)
        # if filter_expression and not projection_expression:
        #     response = table.query(
        #         KeyConditionExpression=key_expression,
        #         FilterExpression=filter_expression,
        #     )
        # elif not filter_expression and projection_expression:
        #     response = table.query(
        #         KeyConditionExpression=key_expression,
        #         ProjectionExpression=projection_expression,
        #     )
        # elif filter_expression and projection_expression:
        #     response = table.query(
        #         KeyConditionExpression=key_expression,
        #         FilterExpression=filter_expression,
        #         ProjectionExpression=projection_expression,
        #     )
        # else:
        response = table.query(
            KeyConditionExpression=key_expression,
            ExpressionAttributeValues=expression_values,
            ScanIndexForward=sort
        )

        items = response["Items"]
        while True:
            if response.get("LastEvaluatedKey"):
                response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                items += response["Items"]
            else:
                break

        return items

    def scan_table_firstpage(self, table_name, filter_key=None, filter_value=None):
        """
        Perform a scan operation on table.
        Can specify filter_key (col name) and its value to be filtered.
        This gets only first page of results in pagination. Returns the response.
        """
        table = dynamodb.Table(table_name)

        if filter_key and filter_value:
            filtering_exp = Attr(filter_key).is_in(filter_value)
            response = table.scan(FilterExpression=filtering_exp)
        else:
            response = table.scan()

        return response

    def scan_table_allpages(self, table_name, filter_key=None, filter_value=None):
        """
        Perform a scan operation on table.
        Can specify filter_key (col name) and its value to be filtered.
        This gets all pages of results.
        Returns list of items.
        """
        table = dynamodb.Table(table_name)
        filtering_exp=None
        
        if filter_key and filter_value:
            filtering_exp = Attr(filter_key).is_in(filter_value)
            response = table.scan(FilterExpression=filtering_exp)
        else:
            response = table.scan()

        items = response["Items"]
        while True:
            if response.get("LastEvaluatedKey"):
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'], FilterExpression=filtering_exp)
                items += response["Items"]
            else:
                break

        return items

    def execute_scan(self, table_name, filter_expression=None, expression_values={}):
        """
        scans the 'table_name'.
        'filter_expression' must be of type FilterExpression
        """
        table = dynamodb.Table(table_name)
        if (filter_expression is None):
            response = table.scan()
        else:
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_values
            )

        items = response["Items"]
        while True:
            if response.get("LastEvaluatedKey"):
                response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                items += response["Items"]
            else:
                break

        return items

    def get_table(self, table_name):
        return dynamodb.Table(table_name)