from flask import Flask, request

app = Flask(__name__)
messages = {}

@app.route('/store_message', methods=['POST'])
def store_message():
    sender = request.headers.get('Sender')
    msg = request.data.decode('utf-8')
    messages[sender] = msg  # Store the message with the sender as the key
    return 'Message stored', 200

@app.route('/get_message/<sender>', methods=['GET'])
def get_message(sender):
    msg = messages.get(sender)
    if msg:
        return msg, 200
    return 'No message found', 404

if __name__ == '__main__':
    app.run(debug=True)