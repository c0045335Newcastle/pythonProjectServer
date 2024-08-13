from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import ssl
import logging
import json

app = Flask(__name__, static_folder='public', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to store messages and pre_key_bundles
messages = {}
files = {}
pre_key_bundles = {}

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to see more details


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@socketio.on('connect')
def handle_connect():
    logging.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info(f"Client disconnected: {request.sid}")

@socketio.on('*')
def catch_all(event, data):
    print(f"Caught event: {event}, Data: {data}")

@socketio.on('send_message')
def handle_send_message(json, callback):
    app.logger.info(f"Received message via WebSocket: {json}")
    #logging.info(f"Received message via WebSocket: {json}")
    sender = json.get('sender')
    receiver = json.get('receiver')
    message = json.get('message')
    played = json.get('played')

    print(f"RECEIVED: {json}")

    messages.setdefault(receiver, []).append({'sender': sender, 'message': message, 'played': played})
    emit('message_response', {'status': 'success'}, room=request.sid)

    # ack?
    callback('Message received')


@socketio.on('fetch_message')
def handle_fetch_message(data):
    receiver = data.get('receiver')
    unread_messages = [m for m in messages.get(receiver, []) if m['played'] == "N"]
    for message in unread_messages:
        message['played'] = True

    if len(unread_messages) == 0:
        emit('message_response', '0', room=request.sid)
    else:
        emit('message_response', {'messages': unread_messages}, room=request.sid)


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
                                              'played': played})

    return jsonify({'status': 'success'}), 200

@app.route('/send_file', methods=['POST'])
def send_file():
    #logging.info(f"Received message: {request.json}")
    app.logger.info(f"Received file: {request.json}")


    sender = request.json.get('sender')
    receiver = request.json.get('receiver')
    contents = request.json.get('contents')
    checksum = request.json.get('checksum')
    # Store the message
    # Do this in DB serverside
    print(f"For: {receiver}")

    files.setdefault(receiver, []).append({'sender': sender, 'contents': contents,
                                              'checksum': checksum})



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

@app.route('/fetch_files/<receiver>', methods=['GET'])
def receive_file(receiver):
    print(f"Check for {receiver}")
    # retrieve only user files
    user_files = files.get(receiver, [])

    if len(user_files) == 0:
        return "0"

    return jsonify({'files': user_files}), 200



if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('cert.pem', 'key.pem')
    socketio = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*", transports=['websocket'])
    socketio.run(app, host='0.0.0.0', port=8080, ssl_context=context, debug=True, allow_unsafe_werkzeug=True)
