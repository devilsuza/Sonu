from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'boss-super-secret-key'

# CORS इनेबल कर रहे हैं ताकि आपकी वेबसाइट इस सर्वर से बात कर सके
CORS(app)

# यहाँ async_mode 'gevent' कर दिया गया है (Render के एरर को फिक्स करने के लिए)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

@app.route('/')
def index():
    return "Boss Remote Signaling Server is Running Live with Gevent!"

@socketio.on('connect')
def test_connect():
    print(f"नया डिवाइस कनेक्ट हुआ: {request.sid}")

@socketio.on('disconnect')
def test_disconnect():
    print(f"डिवाइस डिस्कनेक्ट हो गया: {request.sid}")

# पिन (PIN) या सेशन आईडी के ज़रिए रूम जॉइन करना
@socketio.on('join-room')
def on_join(data):
    room = data.get('room') # यह आपका 1234 वाला पिन या सेशन ID होगा
    if room:
        join_room(room)
        print(f"यूज़र {request.sid} ने रूम {room} जॉइन किया")
        # रूम में मौजूद दूसरे व्यक्ति को बताएं कि कोई नया जुड़ गया है
        emit('user-joined', {'sid': request.sid}, to=room, include_self=False)

# WebRTC Signaling (वीडियो/स्क्रीन शेयर करने के लिए कनेक्शन डेटा)
@socketio.on('webrtc-offer')
def handle_offer(data):
    emit('webrtc-offer', data, to=data['room'], include_self=False)

@socketio.on('webrtc-answer')
def handle_answer(data):
    emit('webrtc-answer', data, to=data['room'], include_self=False)

@socketio.on('webrtc-ice-candidate')
def handle_ice(data):
    emit('webrtc-ice-candidate', data, to=data['room'], include_self=False)

# रिमोट कंट्रोल कमांड्स (जैसे माउस क्लिक, कीबोर्ड टाइप भेजना)
@socketio.on('remote-command')
def handle_command(data):
    # एडमिन जो भी कमांड भेजेगा, वो क्लाइंट को पास हो जाएगा
    emit('remote-command', data, to=data['room'], include_self=False)

if __name__ == '__main__':
    # लोकल टेस्टिंग के लिए
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
