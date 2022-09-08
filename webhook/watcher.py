from flask import Flask, request, jsonify
import subprocess
import os
from git import Repo
import json
from Crypto.Hash import HMAC, SHA256

print('Starting...')

app = Flask(__name__)  # Standard Flask app

HASH_ALGO = 'SHA256'
PROJECT_NAME = 'OnlyOne'
PROJECT_URL  = 'https://github.com/OneSock-inc/OnlyOne.git'
# do not store your secret key in your code, pull from environment variable
PROJECT_PARENT_DIR = '/home/ubuntu'
PROJECT_WEBHOOK_KEY = os.environ.get('WEBHOOK_KEY')

if (not(PROJECT_URL and PROJECT_URL and PROJECT_WEBHOOK_KEY)):
    raise Exception("Not defined env variable(s) ... ABORTING")

@app.route('/', methods=['GET'])
def default():
    return "", 404

@app.route('/', methods=['POST'])
def foo():

    if 'X-Hub-Signature-256' not in request.headers:
        return jsonify({'message': 'failure no header'}), 404

    if len(request.data) == 0:
        return jsonify({'message': 'failure'}), 404
    
    if len(request.data) > 2**20:
        return jsonify({'message': 'Too much data'}), 404

    os.chdir(PROJECT_PARENT_DIR)

    # get the Github signature from the request header
    header_signature = request.headers.get('X-Hub-Signature-256')
    # pass request data and signature to verify function
    verify_signature(request.get_data(), header_signature)

    dic = json.loads(request.data)
    with open("webhook_data","w") as file:
       json_data = json.dumps(dic, indent=4)
       file.write(json_data)
    
    # This is a ping query from GitHub
    if 'zen' in dic:
        return jsonify({'message': dic['zen']}), 200

    # We only want to proceed if the hook comes from main branch
    if not 'main' in dic['ref']:
       print("Pushed not to main, ignoring...")
       return jsonify({'message': 'No action required'}), 200
    
    print("rm last project")
    subprocess.run(["rm","-rf", PROJECT_NAME])
    print("git clone ", end="")
    Repo.clone_from(PROJECT_URL, "./" + PROJECT_NAME)
    os.chdir("./" + PROJECT_NAME)
    print("Upgrading services...",end="")
    subprocess.run(["sudo" ,"docker-compose","up","--build", "-d"])
    return jsonify({'message': 'success'}), 200

def verify_signature(request_data, header_signature):
    
    secret_key = PROJECT_WEBHOOK_KEY

    if not header_signature:
        return jsonify({'message': 'failure'}), 404

    # separate the signature from the HASH_ALGO indication
    sha_name, signature = header_signature.split('=')
    if sha_name != HASH_ALGO:
        return jsonify({'message': 'failure'}), 501

    # create a new hmac with the secret key and the request data
    mac = HMAC.new(secret_key.encode(), msg=request_data, digestmod=SHA256)

    # verify the digest matches the signature
    if not HMAC.compare_digest(mac.hexdigest(), signature):
        return jsonify({'message': 'failure'}), 404

if __name__ == '__main__':
    app.run()