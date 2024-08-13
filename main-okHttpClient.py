from flask import Flask, request, jsonify, send_from_directory
import ssl
import logging
import json

app = Flask(__name__, static_folder='public', static_url_path='')

# Dictionary to store messages
messages = {}
pre_key_bundles = {}

logging.basicConfig(level=logging.INFO)

@app.route('/send', methods=['POST'])
def send_message():
    #logging.info(f"Received message: {request.json}")
    app.logger.info(f"Received message: {request.json}")
    sender = request.json.get('sender')
    receiver = request.json.get('receiver')
    message = request.json.get('message')
    played = request.json.get('played')

    # Store the message
    # Do this in DB serverside
    messages.setdefault(receiver, []).append({'sender': sender, 'message': message,
                                              'played': played,})



    return jsonify({'status': 'success'}), 200

@app.route('/fetch_message/<receiver>', methods=['GET'])
def receive_message(receiver):

    # retrieve only unplayed messages
    unread_messages = [m for m in messages.get(receiver, []) if m['played'] == "N"]

    # update fetched to played
    for message in unread_messages:
        message['played'] = True

    if len(unread_messages) == 0:
        return "0"

    return jsonify({'messages': unread_messages}), 200

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/upload_prekey_bundle', methods=['POST'])
def upload_prekey_bundle():
    data = request.get_json()

    # Extracting individual components directly as sent by the client
    userId = data['userId']
    registrationId = data['registrationId']
    deviceId = data['deviceId']
    preKeyId = data['preKeyId']
    preKeyPublic = data['preKeyPublic']
    signedPreKeyId = data['signedPreKeyId']
    signedPreKey = data['signedPreKey']
    signedPreKeySignature = data['signedPreKeySignature']
    identityKey = data['identityKey']

    # making the PreKeyBundle dictionary
    # to store in your pre_key_bundles
    # may need to deserialize Base64 strings to actual key objects
    preKeyBundle = {
        "registrationId": registrationId,
        "deviceId": deviceId,
        "preKeyId": preKeyId,
        "preKeyPublic": preKeyPublic,
        "signedPreKeyId": signedPreKeyId,
        "signedPreKey": signedPreKey,
        "signedPreKeySignature": signedPreKeySignature,
        "identityKey": identityKey
    }

    # Store the PreKeyBundle associated with the userId
    print(f"{userId} keyBundle received: ", preKeyBundle)
    pre_key_bundles[userId] = preKeyBundle

    return jsonify({"message": "PreKeyBundle uploaded successfully."}), 200


@app.route('/get_prekey_bundle/<userId>', methods=['GET'])
def get_prekey_bundle(userId):
    # Retrieve the PreKeyBundle associated with the userId
    preKeyBundle = pre_key_bundles.get(userId, None)

    if preKeyBundle is None:
        return jsonify({"error": "PreKeyBundle not found."}), 404

    print(f"{userId}'s preKeyBundle fetched")
    return jsonify({"userId": userId, "preKeyBundle": preKeyBundle}), 200



if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('cert.pem', 'key.pem')

    app.run(host='0.0.0.0', port=8080, ssl_context=context, debug=True)