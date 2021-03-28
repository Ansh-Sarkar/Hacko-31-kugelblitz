# importing required libraries
import flask
from flask import request, jsonify
from vendor import create_transaction_id, public_key_decoder, sha256_hash_string_encoding_based
from time import time
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import pytezos.encoding as pe
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import matic_blockchain_interface as mbi
import requests

# configuring flask app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# dictionaries for storing transactions ( transit storage )
active_transactions = {}
accepted_transactions = {}
completed_transactions = {}

# the common entry endpoint for the API
BASE_ENTRY_POINT = 'shagun/api/v1'

# API info route ... non-essential route
@app.route('/{API}/'.format(API=BASE_ENTRY_POINT), methods=['GET'])
def home():
    return '''<h1 style="padding: 10px;">SHAGUN API IBN ( Intermediate BlockChain Network )</h1>
              <p style="margin-left : 10px;">A prototype API for providing an interface between flutter based Android App and Matic BlockChain.</p>
              <h2 style="margin-left : 10px;">Team : </h2>
              <hr>
              <p style="margin-left : 10px;">Binit Agarwal</p>
              <p style="margin-left : 10px;">Jigyanshu Rout</p>
              <p style="margin-left : 10px;">Ansh Sarkar</p>
              <p style="margin-left : 10px;">Anubhab Swain</p>
              <hr>'''

# debugging routes , protected with password . password = anshsarkar ; to be made more secure before production
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/debug/view_active_transactions?password={passord}
@app.route('/{API}/debug/view_active_transactions'.format(API=BASE_ENTRY_POINT), methods=['GET'])
def view_active_transactions():
    password = None
    if 'password' in request.args:
        if(hashlib.md5(request.args['password'].encode('utf-8')).hexdigest() == '92a8ab13ea90bba39fdffa9a4e4e64c9'):
            return jsonify(active_transactions)
    return jsonify({'error': 'failed authentication'})

@app.route('/{API}/debug/view_accepted_transactions'.format(API=BASE_ENTRY_POINT), methods=['GET'])
def view_accepted_transactions():
    password = None
    if 'password' in request.args:
        if(hashlib.md5(request.args['password'].encode('utf-8')).hexdigest() == '92a8ab13ea90bba39fdffa9a4e4e64c9'):
            return jsonify(accepted_transactions)
    return jsonify({'error': 'failed authentication'})

@app.route('/{API}/debug/view_completed_transactions'.format(API=BASE_ENTRY_POINT), methods=['GET'])
def view_completed_transactions():
    password = None
    if 'password' in request.args:
        if(hashlib.md5(request.args['password'].encode('utf-8')).hexdigest() == '92a8ab13ea90bba39fdffa9a4e4e64c9'):
            return jsonify(completed_transactions)
    return jsonify({'error': 'failed authentication'})

# route for generating public and private keys - No params required
# http://127.0.0.1:5000/shagun/api/v1/key_gen
@app.route('/{API}/key_gen'.format(API=BASE_ENTRY_POINT), methods=['GET'])
def entangledKeys():
    # generate private key 
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    # generate public key 
    public_key = private_key.public_key()
    # pem based private key intermediate
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    # pem based public key intermediate
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # encoded private key
    encoded_private_key = pe.base58.b58encode(pem_private)
    # encoded public key
    encoded_public_key = pe.base58.b58encode(pem_public)
    # return jsonify({'prk': str(encoded_private_key) , 'puk' : str(encoded_public_key)})
    # return jsonify({'str' : str(encoded_public_key) , 'decode' : encoded_public_key.decode("utf-8")})
    return jsonify({'prk': encoded_private_key.decode("utf-8"), 'puk': encoded_public_key.decode("utf-8")})

# main Api route : transaction creation , called with creation of every post
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/transaction?customerID={customerID}&publicKey={publicKey}&sha256_checksum={sha256_sum}
@app.route('/{API}/transaction'.format(API=BASE_ENTRY_POINT), methods=['POST'])
def create_transaction():
    customerID = None
    publicKey = None
    # default size = 64 randomized string
    transaction_id = create_transaction_id()
    if 'customerID' in request.args and 'publicKey' in request.args and 'sha256_checksum' in request.args:
        # check for collisions in transaction id's
        if transaction_id in active_transactions.keys():
            # try returning 406 error code : Not Acceptable once totally implemented
            # return jsonify(transaction_block)
            return jsonify({'error': 'failed transaction', 'transactionID': transaction_id})
        else:
            customerID = request.args['customerID']
            publicKey = request.args['publicKey']
            sha256_checksum = request.args['sha256_checksum']
            # adding the ne transaction to the active transactions list
            active_transactions[transaction_id] = [sha256_checksum, transaction_id, customerID, publicKey, time(), []]
    # return all the active transactions 
    return jsonify(active_transactions[transaction_id])

# main Api route : bid creation , called with creation of every bid
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/bid?transactionID={transactionID}&bidderID={bidderID}&bidderPublicKey={bidderPublicKey}
@app.route('/{API}/bid'.format(API=BASE_ENTRY_POINT), methods=['POST'])
def create_bid():
    transactionID = None
    bidderID = None
    bidderPublicKey = None
    if 'transactionID' in request.args and 'bidderID' in request.args and 'bidderPublicKey' in request.args:
        transactionID = request.args['transactionID']
        bidderID = request.args['bidderID']
        bidderPublicKey = request.args['bidderPublicKey']
        # format : [ bidder_id , bidder_public_key , timestamp , bid_accepted ]
        bid = [bidderID, bidderPublicKey, time(), False]
        # push the new bid to the bidders list of that active transaction
        active_transactions[transactionID][-1].append(bid)
        # display the newly inserted bid
        return jsonify(active_transactions[transactionID])
    # if error then display , considering adding the http response codes
    return jsonify({'oops': 'invalid data'})

# main API route : accepting a bid , authorized link
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/accept?transactionID={transactionID}&sha256_checksum={sha256_checksum}&bidderID={bidderID}
@app.route('/{API}/accept'.format(API=BASE_ENTRY_POINT), methods=['POST', 'DELETE'])
def accept_transaction():
    if 'sha256_checksum' in request.args and 'transactionID' in request.args and 'bidderID' in request.args:
        print("first if passed")
        sha256_checksum = request.args['sha256_checksum']
        transactionID = request.args['transactionID']
        bidderID = request.args['bidderID']
        print("second if started")
        # check if the transactionID present in the active transactions dictionary
        if transactionID in active_transactions.keys():
            print("second if passed")
            # check whether the bidder is there on the bidding list
            for bid in active_transactions[transactionID][-1]:
                print(bid)
                # if match found
                if bid[0] == bidderID:
                    print("bid started")
                    # move current transaction to the accepted transactions dictionary 
                    accepted_transactions[transactionID] = active_transactions[transactionID][:-1]+bid[:-1]
                    # delete the moved transaction from the active transactions dictionary
                    del active_transactions[transactionID]
            return jsonify({'success' : 'transaction successful accepted'})
    # if not valid bid and transaction ID
    return jsonify({'error': 'invalid data'})

# main API route : verifying the transaction and creating a message and appending it to the accepted transaction
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/verify?transactionID={transactionID}&sha256_checksum={sha256_checksum}&override={boolean}
@app.route('/{API}/verify'.format(API=BASE_ENTRY_POINT), methods=['GET'])
def get_verification_tools():
    if 'transactionID' in request.args and 'sha256_checksum' in request.args and 'override' in request.args:
        # raw message generation using 128 chars
        message_raw = create_transaction_id(size=128)
        # can override during testing environments
        override_message = request.args['override']
        # use the following message for debugging
        if override_message == 'true':
            message_raw = 'WNZChQ3LU8TvZ9MmF4sHvn6ICG95kcrOM3hffMrJ7TCSbF5MM0bI7clf5joNRybm'
            # expected sha256 hash : 77a501b0721b60e3faef91570609babf80cfdc5091779b9fac0974d644248027
            # message_raw = 'anshsarkaranubhabswaingautamchughbinitagarwaljigyanshuroutswayam'
        # convert to byte literal
        message = bytes(message_raw, 'utf-8')
        # extracting data from the request
        transactionID = request.args['transactionID']
        customer_public_key = accepted_transactions[transactionID][3]
        bidder_public_key = accepted_transactions[transactionID][6]
        # converting utf-8 back to byte literal for customer
        bytes_customer_public_key = bytes(customer_public_key, 'utf-8')
        # converting byte literal of customer to expected byte literal by decoding from base58
        customer_pem_public = pe.base58.b58decode(bytes_customer_public_key)
        # converting utf-8 back to byte literal for bidder
        bytes_bidder_public_key = bytes(bidder_public_key, 'utf-8')
        # converting byte literal of bidder to expected byte literal by decoding from base58
        bidder_pem_public = pe.base58.b58decode(bytes_bidder_public_key)
        # generating the decoded public key object for the customer
        customer_decoded_public_key = serialization.load_pem_public_key(
            customer_pem_public,
            backend=default_backend()
        )
        # encrypting the message using the derieved public key object of customer
        encrypt_for_customer = customer_decoded_public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # generating the decoded public key object for the bidder
        bidder_decoded_public_key = serialization.load_pem_public_key(
            bidder_pem_public,
            backend=default_backend()
        )
        # encrypting the message using the derieved public key object of bidder
        encrypt_for_bidder = bidder_decoded_public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # making ready for jsonification
        # encode using base58 customer
        base58_customer_code = pe.base58.b58encode(encrypt_for_customer)
        # encode using base58 bidder
        base58_bidder_code = pe.base58.b58encode(encrypt_for_bidder)
        # utf-8 encode customer code
        utf_customer_code = base58_customer_code.decode('utf-8')
        # utf-8 encode bidder code
        utf_bidder_code = base58_bidder_code.decode('utf-8')
        # encoding message from byte literal to utf-8
        coded_message = message.decode('utf-8')
        # adding the verified secured message to the end of the active transaction we are referring to
        accepted_transactions[transactionID].append(sha256_hash_string_encoding_based(coded_message))
        # return : success , message , msg to be sent to customer , msg to be sent to bidder
        return jsonify({'success': 'encrypted', 'message': coded_message, 'for_customer': utf_customer_code, 'for_bidder': utf_bidder_code})

# API route to get the storage data of the matic database
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/matic_chain
@app.route('/{API}/matic_chain'.format(API=BASE_ENTRY_POINT) , methods=['GET'])
def storage_data():
    return mbi.get_used_storage()

# main API route : verifying the transaction after scanning of the QR Code
# EndPoint Format : http://127.0.0.1:5000/shagun/api/v1/verification?transactionID={transactionID}&customer_decoded={customer_decoded}&bidder_decoded={bidder_decoded}
@app.route('/{API}/verification'.format(API=BASE_ENTRY_POINT), methods=['GET','DELETE'])
def verification():
    if 'transactionID' in request.args and 'customer_decoded' in request.args and 'bidder_decoded' in request.args:
        transactionID = request.args['transactionID']
        customer_decoded = request.args['customer_decoded']
        bidder_decoded = request.args['bidder_decoded']
        # obtaining the last element in the transaction idea which is the sha256 hash of the verification message
        encoded_message = accepted_transactions[transactionID][-1]
        # confirming that both decryptions give rise to the same message
        if sha256_hash_string_encoding_based(customer_decoded) == encoded_message and sha256_hash_string_encoding_based(bidder_decoded) == encoded_message:
            completed_transactions[transactionID] = accepted_transactions[transactionID]
            # writing the transaction to the block chain
            mbi.matic_push(completed_transactions,transactionID)
            
            # PARAMS = { transactionID : accepted_transactions[transactionID] }
            # proxies = {'https': 'http://127.0.0.1:8888'}
            # requests.post('https://localhost:5001/dictionary',params=PARAMS ,verify=False , proxies=proxies)
            
            # deleted the record from the accepted_transactions dictionary
            del accepted_transactions[transactionID]
            # return success message 
            return jsonify({'success': 'verification successfull'})
    # if verification unsuccessful
    return jsonify({'error': 'verification unsuccessful'})
if "__name__" == "__main__":
    app.run(host="0.0.0.0",port=8080)
