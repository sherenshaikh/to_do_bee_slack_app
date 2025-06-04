import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ToDoBeeUserDataTable')
days_cutoff = 15
workspace_name='' # set your workspace here

# Function to store emoji data in DynamoDB with a timestamp
def store_user_data(user, channel, ts):
    current_time = int(datetime.now().timestamp())  # Get current timestamp
    ts_formatted = ts.replace('.', '')
    table.put_item(
        Item={
            'user': user,
            'channel': channel,
            'ts': ts,
            'timestamp': current_time,  # Save the time the reaction was added
            'link': f"https://{workspace_name}.slack.com/archives/{channel}/p{ts_formatted}"
        }
    )

# Function to retrieve emoji data for a user
def get_user_data_for_user(user):
    response = table.query(
        KeyConditionExpression=Key('user').eq(user)
    )
    return response.get('Items', [])

def get_user_data():
    response = table.scan()
    return response.get('Items', [])

def get_old_data():
    # Calculate the timestamp for 7 days ago
    days_filter = int((datetime.now() - timedelta(days=days_cutoff)).timestamp())
    
    response = table.scan(
        FilterExpression=Key('timestamp').gt(days_filter)
    )
    
    return response.get('Items', [])


def delete_user_data(user, ts):
    try:
        table.delete_item(
            Key={
                'user': user,
                'ts': ts
            }
        )
        print(f"Deleted reaction for user {user} on thread {ts}")
    except Exception as e:
        print(f"Error deleting reaction: {str(e)}")

# Function to delete old records
def delete_old_user_data():

    old_items = get_old_data()

    for item in old_items:
        delete_user_data(item["user"], item["ts"])
    return {"status": "Old records deleted successfully", "deleted_count": len(old_items)}
