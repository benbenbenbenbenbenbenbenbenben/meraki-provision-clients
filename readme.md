# Meraki Client Provisioning Web App

This web application allows you to provision Meraki clients using data from a CSV file.

![Provision Preview](https://github.com/benbenbenbenbenbenbenbenbenben/meraki-provision-clients/blob/main/provision.gif?raw=true)

![Dashboard](https://github.com/benbenbenbenbenbenbenbenbenben/meraki-provision-clients/blob/main/dashboard.png?raw=true)
## Introduction

The Meraki Client Provisioning Web App simplifies the process of provisioning Meraki clients by automating the data import from a CSV file. It provides a user-friendly interface to map the CSV columns to the required Meraki client attributes and performs the provisioning with the help of the Meraki Dashboard API.

## Requirements

To use this web application, you will need the following:

- Python 3.x installed on your machine
- Meraki Dashboard API key
- CSV file containing the client data

## Setup

Follow the steps below to set up the Meraki Client Provisioning Web App:

1. Obtain a [Meraki Dashboard API key](https://developer.cisco.com/meraki/api-v1/#!authorization/obtaining-your-meraki-api-key) by following these steps:
   - Log in to your Meraki Dashboard account.
   - Navigate to **Organization** > **Settings** > **Dashboard API access**.
   - Ensure that the API Access is set to **“Enable access to the Cisco Meraki Dashboard API”**
   - Then go to your profile by clicking on your account email address (on the upper-right) > My profile to generate the API key.
   - Copy the generated API key and keep it secure.

2. Clone or download the Meraki Client Provisioning Web App from the GitHub repository.

3. Setup project
   - In terminal, navigate to the directory of the app
   - Run the following command to create a new virtual environment
     ```bash
     python3 -m venv env
     ```
   - Activate the environment
     ```bash
     source env/bin/activate
     ```   

4. Install the required Python packages:
   - Run the following command to install the dependencies:
     ```bash
     pip install -r requirements.txt
     ```

5. Add Meraki API Key (optional):
   - Run the following command to add the key:
     ```bash
     export MERAKI_DASHBOARD_API_KEY=your_api_key_here
     ```

6. Run the web application:
   - Execute the following command to start the web application:

     ```bash
     python app.py
     ```

   - The web application will be accessible at `http://127.0.0.1:5000`

   - If you did not add Meraki API Key (step 5), the terminal will request you add now.


## CSV
 - CSV headers can only be `name` and `mac`.
 - Max name field is `255` characters
 - Valid name characters are: `a-z`, `A-Z`, `0-9`, `! ? @ # ( ) - _ : ' . /`

## Notes
To view provisioned clients that have not yet connected to a Meraki Device goto **Network-wide** > **Clients** and select **"all clients with a policy"** from Clients dropdown.

Create test csv file of mac addresses and names `http://127.0.0.1:5000/test_file?max=1000`. Default is 100 or change max value for custom number. File saves to project folder.

Flask server is accessible locally only (127.0.0.1). You may wish to change to make this public, however the API Key is server side and the client to server requests are without any authentication. Therefore any network user could make requests.

There is a limit of 3,000 clients that can have a group policy manually applied per network - [Meraki Documentation](https://documentation.meraki.com/General_Administration/Cross-Platform_Content/Creating_and_Applying_Group_Policies).

Provision clients splits the list of clients into batches of 500 per API. Above 500 clients per API sometimes resulted in timeouts from meraki python SDK.

Create exe:
pyinstaller -w -F --add-data "templates:templates" --add-data "static:static" app.py

## Questions

If you have any questions or need further assistance, please reach out to the [github page](https://github.com/benbenbenbenbenbenbenbenbenben/meraki-provision-clients).

Happy provisioning!