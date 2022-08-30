from flask import Flask, request, jsonify
import subprocess
import os
from git import Repo
import json
from Crypto.Hash import HMAC, SHA256

print('Starting...')

app = Flask(__name__)  # Standard Flask app
HASH_ALGO = 'SHA256'
HASH_HEADER_NAME = 'X-Hub-Signature-256'

@app.route('/', methods=['GET'])
def default():
    return ""

@app.route('/', methods=['POST'])
def foo():

    if HASH_HEADER_NAME not in request.headers:
        return jsonify({'message': 'failure no header'}), 404

    if len(request.data) == 0:
        return jsonify({'message': 'failure'}), 404
    
    if len(request.data) > 2**20:
        return jsonify({'message': 'Too much data'}), 404

    # get the Github signature from the request header
    header_signature = request.headers.get(HASH_HEADER_NAME)
    # pass request data and signature to verify function
    verify_signature(request.get_data(), header_signature)

    dic = json.loads(request.data)
    with open("webhook_data","w") as file:
       json_data = json.dumps(dic, indent=4)
       file.write(json_data)

    if 'zen' in dic:
        return jsonify({'message': dic['zen']}), 200

    if not 'main' in dic['ref']:
       print("Pushed not to main, ignoring...")
       print(f"Branch :{dic['ref'].split('/')}")
       return jsonify({'message': 'No action required'}), 200
    
    print(f"Branch :{dic['ref'].split('/')}")
    print("rm last project")
    subprocess.run(["rm","-rf","onlyone"])
    print("git Cloning ", end="")
    Repo.clone_from("https://github.com/OneSock-inc/OnlyOne.git", "./onlyone")
    print("!")
    os.chdir("./onlyone")
    print("Upgrading services...",end="")
    subprocess.run(["sudo" ,"docker-compose","up","--build", "-d"])
    print("   DONE")
    os.chdir("..")  
    return jsonify({'message': 'success'}), 200

def verify_signature(request_data, header_signature):
    # do not store your secret key in your code, pull from environment variable
    secret_key = os.environ.get('WEBHOOK_KEY')

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