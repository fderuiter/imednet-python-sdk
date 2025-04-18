# Contents of /imednet-python-sdk/imednet-python-sdk/examples/usage_example.py

from imednet_sdk.client import ImednetClient

def main():
    # Initialize the ImednetClient with your API key
    api_key = 'your_api_key_here'
    client = ImednetClient(api_key)

    # Example of a GET request to fetch data
    response = client.get('/endpoint')
    print('GET Response:', response)

    # Example of a POST request to create a new resource
    data = {
        'key1': 'value1',
        'key2': 'value2'
    }
    response = client.post('/endpoint', json=data)
    print('POST Response:', response)

    # Example of a PUT request to update an existing resource
    update_data = {
        'key1': 'new_value1'
    }
    response = client.put('/endpoint/1', json=update_data)
    print('PUT Response:', response)

    # Example of a DELETE request to remove a resource
    response = client.delete('/endpoint/1')
    print('DELETE Response:', response)

if __name__ == '__main__':
    main()