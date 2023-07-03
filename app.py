#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, request, render_template, jsonify
import meraki
import json
import os
import csv

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
app_title = 'Meraki - Provision Clients'
# Instantiate a Meraki dashboard API session
m = meraki.DashboardAPI(
    api_key='',
    base_url='https://api.meraki.com/api/v1/',
    output_log=False,
    print_console=False
)

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

# Main Page
@app.route('/', methods=["GET"])
def home():
    orgs = get_organisations()
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
    
    # Per connection - Create SSID Policy Dict
    policiesBySsid = {}
    if data['inputPolicy'] == 'Per connection':
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
        provision, code = provision_clients(data['inputNetwork'], batch, data['inputPolicy'], policiesBySsid=policiesBySsid)
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

# Read JSON File
def read_json_file(file):
    try:
        with open(f'static/{file}.json') as f:
            return json.load(f)
    except OSError as e: 
        print(e)
        return False
    
#######################
# MERAKI APIs
#######################

# Get Organisations
def get_organisations():
    try:
        orgs = m.organizations.getOrganizations()
        return orgs
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
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
        print(policies)
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
        print(ssids)
        return ssids
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
    except Exception as e:
        print(f'some other error: {e}')


# Provision Clients
def provision_clients(network, clients:list, policy, policiesBySsid=None):
    try:
        if policiesBySsid is None or not bool(policiesBySsid):
            provision = m.networks.provisionNetworkClients(network, clients, policy)
        else:
            provision = m.networks.provisionNetworkClients(network, clients, policy, policiesBySsid=policiesBySsid)
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
    print(clients)
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

# CSV Check and Remove BOM
def remove_bom(csv_data):
    if csv_data.startswith('\ufeff'):
        return csv_data[1:]
    return csv_data


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

# Specify the filename for the CSV file
filename = 'data.csv'



#----------------------------------------------------------------------------#
# Launch
#----------------------------------------------------------------------------#

# Debug:
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=True, host='0.0.0.0', port=port)
