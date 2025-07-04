import json
import os
import boto3
from botocore.exceptions import ClientError
import requests

# CONFIGURATION
# Add the cryptocurrency symbols you want to monitor here
CRYPTO_ASSETS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
# Set the percentage change threshold for notifications
PRICE_CHANGE_THRESHOLD = 5  # e.g., 5 for 5%

# AWS Secrets Manager configuration
SECRET_NAME = "BinanceApiKeys"
REGION_NAME = "us-east-1" # Change to your AWS region

# Binance API URL
BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/24hr"

# Initialize AWS clients
sns_client = boto3.client('sns')
secrets_client = boto3.client(
    service_name='secretsmanager',
    region_name=REGION_NAME
)
ssm_client = boto3.client('ssm')

def get_binance_api_keys():
    """Retrieves Binance API keys from AWS Secrets Manager."""
    try:
        get_secret_value_response = secrets_client.get_secret_value(
            SecretId=SECRET_NAME
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def get_last_prices():
    """Retrieves the last known prices from SSM Parameter Store."""
    try:
        parameter = ssm_client.get_parameter(Name='CryptoLastPrices', WithDecryption=False)
        return json.loads(parameter['Parameter']['Value'])
    except ssm_client.exceptions.ParameterNotFound:
        return {}

def store_last_prices(prices):
    """Stores the current prices in SSM Parameter Store."""
    ssm_client.put_parameter(
        Name='CryptoLastPrices',
        Value=json.dumps(prices),
        Type='String',
        Overwrite=True
    )

def send_notification(message):
    """Sends a notification using AWS SNS."""
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=message,
        Subject='Crypto Price Alert'
    )

def lambda_handler(event, context):
    """
    Main Lambda function handler.
    
    This function fetches cryptocurrency prices from Binance,
    compares them to the last known prices, and sends a notification
    via SNS if the price change exceeds the defined threshold.
    """
    try:
        # The following line is commented out as API keys are not required for the public ticker endpoint.
        # api_keys = get_binance_api_keys() 
        
        last_prices = get_last_prices()
        current_prices = {}
        notifications = []

        # Fetch current prices from Binance
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        all_tickers = response.json()
        
        # Filter for the assets we are interested in
        for ticker in all_tickers:
            if ticker['symbol'] in CRYPTO_ASSETS:
                current_prices[ticker['symbol']] = float(ticker['lastPrice'])

        # Compare prices and prepare notifications
        for asset, current_price in current_prices.items():
            last_price = last_prices.get(asset)

            if last_price:
                price_change_percent = ((current_price - last_price) / last_price) * 100
                
                if abs(price_change_percent) >= PRICE_CHANGE_THRESHOLD:
                    direction = "increased" if price_change_percent > 0 else "decreased"
                    message = (
                        f"ALERT: {asset} has {direction} by "
                        f"{price_change_percent:.2f}% in the last 24 hours. "
                        f"Current price: {current_price}"
                    )
                    notifications.append(message)

        # Send notifications if there are any
        if notifications:
            full_notification = "\n".join(notifications)
            send_notification(full_notification)

        # Store the current prices for the next run
        store_last_prices(current_prices)

        return {
            'statusCode': 200,
            'body': json.dumps('Crypto prices checked successfully!')
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Binance: {e}")
        return {'statusCode': 500, 'body': json.dumps(f'Error fetching data from Binance: {e}')}
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally send an error notification
        # send_notification(f"An error occurred in the Crypto Notifier Lambda: {e}")
        return {'statusCode': 500, 'body': json.dumps(f'An error occurred: {e}')}

