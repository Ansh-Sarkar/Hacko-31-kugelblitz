# importing required libraries
import http.client
import requests
import flask
from flask import jsonify, request
from requests.exceptions import HTTPError
import json
import vendor

# API config
API_KEY = '12D3KooWGYjLHbzbwig17M7dQm8dNKmWjEeKX8ekPwa5bGfXDkRD'
API_SECRET = '08011240158e81fe65f363b1c5ec1fe782ff86a17d5b9618591830edead399568b6f27fa64007243d49e8ae6cfc214dd53c6d2f3e89bfc7930078432de88a841bf31eac8'
API_ENDPOINT = 'https://kfs2.moibit.io'

# test URL : API_URL = "http://api.open-notify.org/astros.json"
# check connection stability , makes it easier to debug , default ping URL = 'https://google.com'
def check_connection_status(API_URL='https://google.com'):
    # try to get a valid HttpResponse from google
    try:
        response = requests.get(API_URL)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        print('Connection Stable')
        # True => the connection is stable and the network libraries are working properly
        return True
    # catch error if server sends a response code other than 'OK' - 200
    except HTTPError as http_err:
        # if it is a known error , output the error on the terminal and return False
        print("False , Error : {error}".format(error=http_err))
        return False
    # if an unknown exception , i.e. other than an Http Exception occurs , then catch here
    except Exception as err:
        # print to console and return false
        print("False , Error : {error}".format(error=err))
        return False
    # if the raised error is completely unexpected 
    else:
        # simply print the following message to the terminal and return false
        print("An UnKnown Error Occured")
        return False

# Matic API based getter function
# returns the amount of consumed storage on moibit : total alloted = 2 GB free space decentralized on matic blockchain
def get_used_storage():
    # fetch the storage usage data
    try:
        # default parameters containing tokens required for authorization
        PARAMS = {
            'api_key': API_KEY,
            'api_secret': API_SECRET
        }
        # test using requests library : response = requests.get('{API}/moibit/v0/storageused'.format(API=API_ENDPOINT), params=PARAMS)
        # passing tokens in request header , request times out after 10 seconds : Counter measure for sniffing
        response = requests.get(
            '{API}/moibit/v0/storageused'.format(API=API_ENDPOINT),
            headers={
                'api_key': API_KEY,
                'api_secret': API_SECRET
            },
            timeout=10
        )
        # check the status code returned by the moibit server
        response.raise_for_status()
        # print the status code to the terminal
        print(response.status_code)
        # convert the data into json format
        json_response = response.json()
        # print this json data to the console
        print(response.json())
        # return the json response for use by the calling function
        return json_response

        if json_response['meta']['message'] == 'got storage used successfully':
            # checks if the json object received has the required parameters : debug
            if json_response['data']['storageUsed'] is not None and json_response['data']['unit'] is not None:
                print(str(json_response['data']['storageUsed'])+' '+json_response['data']['unit'])
                # debug : return str(json_response['data']['storageUsed'])+' '+json_response['data']['unit']
            else:
                # prints to the terminal in case there is something wrong with the data
                print("Corrupted Data")
                # debug : return False
        else:
            # prints to the terminal in case there is something wrong with the data
            print("Corrupted Data")
            # debug : return False
    # catch the error which might be thrown
    except HTTPError as http_err:
        # if it is a known error , output the error on the terminal and return False
        print("False , Error : {error}".format(error=http_err))
        return json.loads({'error' : 'unsuccessful fetch'})
    # if it is a known error but not a HttpResponse error , output the error on the terminal and return False
    except Exception as err:
        print("False , Error : {error}".format(error=err))
        return json.loads({'error' : 'unsuccessful fetch'})
    
# experimental requests , secure header method ; DO NOT USE 
def experimental_function_write_message_to_moibit(message):
    # trying fetching response 
    try:
        # body parameters required for fetching
        PARAMS = {
            'fileName': 'matic_transaction_ledger',
            'text': message,
            'create': 'false',
            'createFolders': 'false',
            'pinVersion': 'false'
        }
        # fetching using requests : response = requests.get('{API}/moibit/v0/storageused'.format(API=API_ENDPOINT), params=PARAMS)
        # posting message and appending to end of existing file
        response = requests.post(
            '{API}/moibit/v0/writetexttofile'.format(API=API_ENDPOINT),
            headers={
                'api_key': API_KEY,         # API_KEY : to be shifted and stored into .env file
                'api_secret': API_SECRET    # API_SECRET :  to be shifted and stored into .env file
            },
            params=PARAMS,
            timeout=10                      # timeout after 10 seconds , to avoid hanging of server and occupied ports
        )
        # check the status code sent by moibit server
        response.raise_for_status()
        # print the response to the terminal
        print(response.status_code)
        # convert response to json format
        json_response = response.json()
        # print out the json object to the console
        print(response.json())
    # if it is a known error , output the error on the terminal and return False
    except HTTPError as http_err:
        print("False , Error : {error}".format(error=http_err))
        return json.loads({'error' : 'unsuccessful fetch'})
    # if it is a known error but not a HttpResponse error , output the error on the terminal and return False
    except Exception as err:
        print("False , Error : {error}".format(error=err))
        return json.loads({'error' : 'unsuccessful fetch'})

# Matic API based setter function
# writes a given message to the moibit matic_transaction_ledger file
def write_to_moibit(message, flush='false'):
    # establish connection to API_URL and try to fetch response
    try:
        # establishing http connection
        conn = http.client.HTTPSConnection("kfs2.moibit.io")
        # creating a unique key for the input , dosent really matter as we wont be using it much
        transactionKEY = vendor.create_transaction_id(5)
        # message structure in stringified json format , sent for appending to matic_transaction_ledger
        payload = "{\"fileName\":\"matic_transaction_ledger\",\"text\":\"{\\\"blocks\\\":[{\\\"key\\\":\\\"" + str(
            transactionKEY) + "\\\",\\\"text\\\":\\\""+str(
                message)+"\\\",\\\"type\\\":\\\"unstyled\\\",\\\"depth\\\":0,\\\"inlineStyleRanges\\\":[],\\\"entityRanges\\\":[],\\\"data\\\":{}}],\\\"entityMap\\\":{}}\",\"create\":\""+str(
                    flush)+"\",\"createFolders\":\"false\",\"pinVersion\":\"false\"}"
        # request headers for authetication
        headers = {
            'api_key': API_KEY,
            'api_secret': API_SECRET,
            'content-type': "application/json"
        }
        # sending the POST request with payload and authentication settings
        conn.request("POST", "/moibit/v0/writetexttofile", payload, headers)
        # fetch response from the server
        res = conn.getresponse()
        # read response from server
        data = res.read()
        # deocode response fetched from server
        decoded_data = data.decode("utf-8")
        # load fetched data as json for enhancing ease of handling data
        decoded_data = json.loads(decoded_data)
        # print the decoded data to the terminal : debug 
        print(decoded_data)
        # testing for decoded data to contain json object as dictionary : print(decoded_data['meta']['message'])
        return decoded_data
    # in case of any error while writing to matic_transaction_ledger
    except HTTPError as http_err:
        # if it is a known error , output the error on the terminal and return False
        print("False , Error : {error}".format(error=http_err))
        return json.loads({'error' : 'unsuccessful fetch'})
    except Exception as err:
        # if it is a known error but not a HttpResponse error , output the error on the terminal and return False
        print("False , Error : {error}".format(error=err))
        return json.loads({'error' : 'unsuccessful fetch'})

# Matic API based getter function
# returns the entire data store on the matic_transaction_ledger in json format
def read_data_moibit():
    # try to fetch entire data from the transaction ledger
    try:
        # establish http connection with the site
        conn = http.client.HTTPSConnection("kfs2.moibit.io")
        # simple payload : fileName which needs to be fetched : matic_transaction_ledger in our case
        payload = "{\"fileName\":\"matic_transaction_ledger\"}"
        # headers for authentication        
        headers = {
            'api_key': API_KEY,
            'api_secret': API_SECRET,
            'content-type': "application/json"
        }
        # send the request to the server
        conn.request("POST", "/moibit/v0/readfile", payload, headers)
        # get moibit server response
        res = conn.getresponse()
        # read returned response 
        data = res.read()
        # decode the data received
        decoded_data = data.decode("utf-8")
        # print the decoded data to the terminal
        print(decoded_data)
        # return the received data in json format 
        return json.loads(decoded_data)
    # in case of any error while writing to matic_transaction_ledger
    except HTTPError as http_err:
        # if it is a known error , output the error on the terminal and return False
        print("False , Error : {error}".format(error=http_err))
        return json.loads({'error' : 'unsuccessful fetch'})
    except Exception as err:
        # if it is a known error but not a HttpResponse error , output the error on the terminal and return False
        print("False , Error : {error}".format(error=err))
        return json.loads({'error' : 'unsuccessful fetch'})

# Matic API based setter function
# flushes the entire file and populates with demo string 
def flush_transaction_file():
    return write_to_moibit('!@#$%^&', 'true')

# Matic API based setter function
# pushing the completed transaction once it has been completed to the matic blockchain
def matic_push(completed_transactions, transactionID):
    # the sha checksum of the transaction
    sha256_checksum = completed_transactions[transactionID][0]                              # added
    # the transaction ID 
    transaction_ID = completed_transactions[transactionID][1]                               # added
    # just another extra check just before pushing to the blockchain
    if transactionID == transaction_ID:
        # the customer ID
        customerID = completed_transactions[transactionID][2]                               # added
        # public key of the customer
        customerPublicKey = completed_transactions[transactionID][3]                        # added
        # time at which the post / transaction was created : UNIX
        transaction_creation_timestamp = completed_transactions[transactionID][4]           # added
        # the bidder ID
        bidderID = completed_transactions[transactionID][5]                                 # added
        # the public key of the bidder
        bidderPublicKey = completed_transactions[transactionID][6]                          # added
        # the time at which the bid was made
        bid_creation_timestamp = completed_transactions[transactionID][7]                   # added
        # verification message which was used to verify the transaction
        verification_message_sha = completed_transactions[transactionID][8]                 # added
        
        # making the transaction string for easy writing to the matic blockchain using moibit API
        # adding sha checksum
        transaction_string = "sha256_trans : " + str(sha256_checksum) + " , "
        # adding transaction ID
        transaction_string += "transID : " + str(transaction_ID) + " , "
        # adding custoemr ID
        transaction_string += "customerID : " + str(customerID) + " , "
        # adding customer public key
        transaction_string += "customerPublicKey : " + str(customerPublicKey) + " , "
        # adding the transaction creation timestamp
        transaction_string += "trans_timestamp : " + str(transaction_creation_timestamp) + " , "
        # adding the bidder ID
        transaction_string += "bidderID : " + str(bidderID) + " , "
        # adding the bidder public key 
        transaction_string += "bidderPublicKey : " + str(bidderPublicKey) + " , "
        # adding the bid timestamp
        transaction_string += "bid_timestamp : " + str(bid_creation_timestamp) + " , "
        # adding the sha code of the verification message used to verify the message
        transaction_string += "message_sha : " + str(verification_message_sha) + " ."
        
        write_to_moibit(transaction_string)
        
# For DEBUGGING : 
# check_connection_status()
# print("Testing the used storage function : ")
# get_used_storage()
# print("Testing the moibit write function : ")
# write_message_to_moibit('my name is ansh sarkar and I have written this message using an API')
