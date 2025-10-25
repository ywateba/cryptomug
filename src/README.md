# AWS Lambda Crypto Notifier Setup Guide 💰

This guide provides a step-by-step walkthrough for setting up an **AWS Lambda function** to monitor cryptocurrency prices and dispatch notifications via **Amazon SNS**.

-----

## Prerequisites

  * An **AWS account** with access to Lambda, SNS, IAM, and Systems Manager Parameter Store.
  * **Python 3.8 or later** installed on your local machine.
  * The **AWS CLI** installed and configured.

-----

## Step 1: Create an SNS Topic 📧

This Amazon Simple Notification Service (**SNS**) topic will be the channel for price alert notifications (e.g., email or SMS).

1.  Go to the **Amazon SNS console**.
2.  In the left navigation pane, choose **Topics**.
3.  Choose **Create topic**.
      * For **Type**, choose **Standard**.
      * For **Name**, enter a descriptive name (e.g., `CryptoPriceAlerts`).
4.  Choose **Create topic**.
5.  **Create a Subscription**: This determines how you'll receive the alerts.
      * On the topic's page, choose **Create subscription**.
      * For **Protocol**, choose **Email** (or your preferred method).
      * For **Endpoint**, enter your email address.
      * Choose **Create subscription**.
6.  **Confirm Subscription**: Check your email and click the confirmation link.
7.  **Copy the ARN**: Copy the **ARN** (Amazon Resource Name) of the SNS topic. You'll need it for the Lambda environment variables.

-----

## Step 2: Create an IAM Role for the Lambda Function 🛡️

The AWS Identity and Access Management (**IAM**) role grants the Lambda function necessary permissions to interact with other AWS services.

1.  Go to the **IAM console**.
2.  In the left navigation pane, choose **Roles**.
3.  Choose **Create role**.
4.  For **Trusted entity type**, select **AWS service**.
5.  For **Use case**, select **Lambda**.
6.  Choose **Next**.
7.  **Attach Policies**: Search for and add the following four policies:
      * `AWSLambdaBasicExecutionRole` (for logging to CloudWatch)
      * `AmazonSNSFullAccess` (to publish notifications)
      * `AmazonSSMFullAccess` (to read and write to Parameter Store)
      * `SecretsManagerReadWrite` (if storing API keys securely)
8.  Choose **Next**.
9.  For **Role name**, enter a name (e.g., `CryptoNotifierLambdaRole`).
10. Choose **Create role**.

-----

## Step 3: Create the Lambda Function ☁️

1.  Go to the **AWS Lambda console**.
2.  Choose **Create function**.
3.  Select **Author from scratch**.
4.  **Basic Settings**:
      * For **Function name**, enter a name (e.g., `CryptoPriceMonitor`).
      * For **Runtime**, select **Python 3.9**.
      * For **Architecture**, select `x86_64`.
5.  **Permissions**:
      * Under **Permissions**, expand **Change default execution role**.
      * Select **Use an existing role**.
      * From the *Existing role* dropdown, select the IAM role you created in the previous step (`CryptoNotifierLambdaRole`).
6.  Choose **Create function**.

-----

## Step 4: Configure the Lambda Function ⚙️

### Package and Upload Code

1.  **Code**: In the *Code source* section, paste the Python code from your `crypto_notifier_lambda.py` file.
2.  **Dependencies**: Create a `requirements.txt` file (using the contents from the provided document).
3.  **Install Libraries**: Install the necessary Python libraries into a local directory for packaging:
    ```bash
    pip install -r requirements.txt -t .
    ```
4.  **Create ZIP**: Create a ZIP archive containing your Python script (`crypto_notifier_lambda.py`) and the directory containing the installed libraries.
5.  **Upload**: Upload this ZIP file to the Lambda function.

### Set Environment Variables

1.  Go to the **Configuration** tab, then **Environment variables**.
2.  Choose **Edit** and then **Add environment variable**.
      * **Key**: `SNS_TOPIC_ARN`
      * **Value**: Paste the ARN of the SNS topic you copied in Step 1.
3.  Choose **Save**.

### Set up a Trigger (Scheduler)

1.  Go to the **Configuration** tab, then **Triggers**.
2.  Choose **Add trigger**.
3.  **Select a source**: Select **EventBridge (CloudWatch Events)**.
4.  **Create new rule**:
      * For **Rule name**, enter a name (e.g., `CryptoMonitorSchedule`).
      * For **Schedule expression**, define how often the function runs. For example, to run every hour, use `rate(1 hour)`.
5.  Choose **Add**.

-----

## Step 5: (Optional) Store Binance API Keys in Secrets Manager 🔒

*The default provided code often uses public endpoints and may not require keys. This step is only necessary if you modify the code to use private, account-specific Binance endpoints.*

1.  Go to the **AWS Secrets Manager console**.
2.  Choose **Store a new secret**.
3.  For **Secret type**, select **Other type of secret**.
4.  **Key/Value Pairs**: Enter your Binance API and Secret keys:
      * Key: `BINANCE_API_KEY`, Value: *Your Binance API Key*
      * Key: `BINANCE_SECRET_KEY`, Value: *Your Binance Secret Key*
5.  Choose **Next**.
6.  For **Secret name**, enter `BinanceApiKeys`.
7.  Follow the prompts and choose **Store** to finish.

-----

## Step 6: Test the Function ✅

1.  In the Lambda console, go to the **Test** tab.
2.  Choose **Configure test event**.
      * For **Event name**, enter a name (e.g., `TestEvent`).
      * Leave the event JSON as the default `{}`.
3.  Choose **Save** and then **Test**.
4.  **Review Results**: Check the **Execution results** and the **Logs** in CloudWatch to see the output. You should also receive an email notification if a price change threshold was met by the code's logic.