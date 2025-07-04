How to DeploySave the Files: Save the code above into three separate files in the same directory: main.tf, variables.tf, and outputs.tf.Create the Lambda Deployment Package:Save the Python code from the crypto_notifier_lambda artifact into a file named crypto_notifier_lambda.py.Create a requirements.txt file with the following content:boto3
requests
Install the dependencies into the current directory:pip install -r requirements.txt -t .
Create a zip file that includes the Python script and the installed libraries:zip -r lambda_function.zip .
Create a terraform.tfvars file: This file will contain the value for the notification_email variable. Create a file named terraform.tfvars and add the following, replacing the email with your own:notification_email = "your-email@example.com"
Initialize Terraform: Open your terminal in the directory where you saved the files and run:terraform init
Plan the Deployment: See what resources Terraform will create:terraform plan
Apply the Configuration: Deploy the resources to your AWS account:terraform apply
You will be prompted to confirm the deployment. Type yes to proceed.After the deployment is complete, the Lambda function will be triggered every hour to check cryptocurrency prices and send you an email notification if the price change threshold is met.
