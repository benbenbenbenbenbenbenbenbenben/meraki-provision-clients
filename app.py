#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, request, render_template, jsonify
import meraki
import json
import os
import csv
import getpass


#----------------------------------------------------------------------------#
# Meraki Object
#----------------------------------------------------------------------------#

def get_meraki_dashboard():
    if 'MERAKI_DASHBOARD_API_KEY' in os.environ:
        api_key = os.environ['MERAKI_DASHBOARD_API_KEY']
    else:
        api_key = getpass.getpass("Enter your Meraki API key: ")

    # Initialize the Meraki Dashboard object
    dashboard = meraki.DashboardAPI(
        api_key=api_key,
        base_url='https://api.meraki.com/api/v1/',
        output_log=False,
        print_console=False
    )
    return dashboard

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
app_title = 'Meraki Client Provisioning Web App'
m = get_meraki_dashboard()

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

# Main Page
@app.route('/', methods=["GET"])
def home():
    orgs, code = get_organisations()
    if code != 200:
        return render_template('base.html', app_title=app_title, contents='form.html', orgs=[])
    else:
        return render_template('base.html', app_title=app_title, contents='form.html', orgs=orgs)

# Networks
@app.route('/networks', methods=["GET"])
def networks():
    orgId = request.args.get('orgId')
    data = get_networks(orgId)
    return jsonify(data)


@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()

    # Validate the form data
    errors = validate_form_data(data)

    if errors:
        return jsonify({'errors': errors}), 400
    
    # Group Policy ID
    if data['inputPolicy'] == 'Group policy' and 'inputGroupPolicy' in data:
        groupPolicyId = data['inputGroupPolicy']

    # Per connection - Create SSID Policy Dict
    if data['inputPolicy'] == 'Per connection':
        policiesBySsid = {}
        for k, v in data.items():
            if k.startswith('ssid-'):
                ssid = k.replace('ssid-', '')
                # Check if policy number
                try:
                    int(v)
                    policiesBySsid[ssid] = {
                        "devicePolicy": "Group policy",
                        'groupPolicyId': v
                    }
                except:
                    policiesBySsid[ssid] = {
                        "devicePolicy": v
                    }

    # Process the form data
    devices = json.loads(data['devices'])

    code = 200
    provision = True
    
    # Split the list into batches
    batches = split_list_into_batches(devices, 500)

    # Loop through the batches
    for batch in batches:
        if data['inputPolicy'] == 'Group policy' and 'inputGroupPolicy' in data:
            provision, code = provision_clients(data['inputNetwork'], batch, data['inputPolicy'], groupPolicyId=data['inputGroupPolicy'])
        elif data['inputPolicy'] == 'Per connection':
            provision, code = provision_clients(data['inputNetwork'], batch, data['inputPolicy'], policiesBySsid=policiesBySsid)
        else:
            provision, code = provision_clients(data['inputNetwork'], batch, data['inputPolicy'])
        if not isinstance(provision, bool):
            return jsonify(provision), code
    return jsonify(provision), code

# Policies
@app.route('/policy', methods=["GET"])
def policy():
    # Get the value from the query parameters
    value = request.args.get('value')
    networkId = request.args.get('networkId')
    data = {}
    # Process the value and generate the response
    if value.lower() == 'group policy' or value.lower() == 'per connection':
        data['policies'] = get_network_policies(networkId)
        data['ssids'] = get_wireless_ssids(networkId)

    else:
        data = {}

    # Return the response as JSON
    return jsonify(data)

# Policies
@app.route('/clients', methods=["GET"])
def clients():
    # Get the value from the query parameters
    networkId = request.args.get('networkId')
    data = get_clients(networkId)
    # Return the response as JSON
    return jsonify(data)

# Create test file of device names and mac addresses
@app.route('/test_file', methods=["GET"])
def provision():
    if request.method == "GET":
        data = []
        mac = '00:00:00:'
        max = 2000

        for number in range(max):
            hex_num = hex(number)[2:].zfill(6)
            client = "{}{}{}:{}{}:{}{}".format(mac,*hex_num)
            data.append({
                            "mac": client,
                            "name": f"Device {number}"
                        })
        export_to_csv(data, 'test.csv')
        return render_template('base.html', app_title=app_title, contents='404.html', serial='test.csv created!'), 200

# 404
@app.errorhandler(404)
def page_not_found(error):
   return render_template('base.html', app_title=app_title, contents='404.html', serial='Alakazam!'), 404

#----------------------------------------------------------------------------#
# Functions
#----------------------------------------------------------------------------#

# Form Validation
def validate_form_data(data):
    # Check each field in the data dictionary and
    # return a dictionary of errors, if any

    errors = {}

    if 'inputNetwork' not in data or not data['inputNetwork']:
        errors['inputNetwork'] = 'Network ID is missing or empty'

    if 'inputPolicy' not in data or not data['inputPolicy']:
        errors['inputPolicy'] = 'Policy is missing or empty'

    # if 'devices' not in data or not data['devices'] or not isinstance(data['devices'], list) or len(data['devices']) == 0:
    #     errors['devices'] = 'Devices is missing or empty'

    # Add more validation checks for other fields as needed
    print("Errors: ",errors)
    return errors
    
#######################
# MERAKI APIs
#######################

# Get Organisations
def get_organisations():
    try:
        orgs = m.organizations.getOrganizations()
        return orgs, 200
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
        return {
            'message':e.message,
            'error':e.status
        }, e.status
    except Exception as e:
        print(f'some other error: {e}')

# Get Networks
def get_networks(orgId):
    try:
        networks = m.organizations.getOrganizationNetworks(orgId, total_pages='all')
        return networks
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
    except Exception as e:
        print(f'some other error: {e}')

# Get Network Policies
def get_network_policies(networkId):
    try:
        policies = m.networks.getNetworkGroupPolicies(networkId)
        return policies
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
    except Exception as e:
        print(f'some other error: {e}')

# Get Wireless SSIDs
def get_wireless_ssids(networkId):
    try:
        ssids = m.wireless.getNetworkWirelessSsids(networkId)
        return ssids
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
    except Exception as e:
        print(f'some other error: {e}')


# Provision Clients
def provision_clients(network, clients:list, policy, **kwargs):
    try:
        # if 'policiesBySsid' in kwargs:
        #     provision = m.networks.provisionNetworkClients(network, clients, policy, policiesBySsid=kwargs['policiesBySsid'])
        # elif 'groupPolicyId' in kwargs:
        #     provision = m.networks.provisionNetworkClients(network, clients, policy, groupPolicyId=kwargs['groupPolicyId'])
        # else:
        provision = m.networks.provisionNetworkClients(network, clients, policy, **kwargs)
        return True, 200
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
        return {
            'message':e.message,
            'error':e.status
        }, e.status
    except Exception as e:
        print(f'some other error: {e}')
        return f'reason = {e}'
    
        
# Get policies for all clients with policies
def get_clients(networkId):
    # try:
    clients = m.networks.getNetworkPoliciesByClient(networkId, total_pages='all', perPage=500)
    return clients
    # except meraki.APIError as e:
    #     print(f'Meraki API error: {e}')
    #     print(f'status code = {e.status}')
    #     print(f'reason = {e.reason}')
    #     print(f'error = {e.message}')
    # except Exception as e:
    #     print(f'some other error: {e}')


# General Functions
def split_list_into_batches(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def export_to_csv(data, filename):
    # Specify the field names and data rows
    fieldnames = ['name', 'mac']

    # Write the data to a CSV file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        for row in data:
            writer.writerow(row)

    print(f"CSV file '{filename}' exported successfully!")

#----------------------------------------------------------------------------#
# Launch
#----------------------------------------------------------------------------#

# Debug:
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='127.0.0.1', port=port)

