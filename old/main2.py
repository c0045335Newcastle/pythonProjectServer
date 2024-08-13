from flask import Flask, request

app = Flask(__name__)

# Dictionary to store messages
messages = {}

@app.route('/send', methods=['POST'])
def send_message():
    sender = request.json.get('sender')
    receiver = request.json.get('receiver')
    message = request.json.get('message')
    # Store the message
    messages.setdefault(receiver, []).append((sender, message))
    return {'status': 'success'}, 200

@app.route('/receive/<receiver>', methods=['GET'])
def receive_message(receiver):
    received_messages = messages.get(receiver, [])
    return {'messages': received_messages}, 200

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True)