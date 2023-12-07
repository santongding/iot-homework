from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import time
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    # 主页面
    return render_template('index.html')

def gen_frames():  
    camera = cv2.VideoCapture(0)
    fps = 0
    frame_count = 0
    start_time = time.time()
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("Can not read from camera")
            break
        else:
            frame_count += 1
            end_time = time.time()
            if (end_time - start_time) > 1:
                fps = frame_count / (end_time - start_time)
                frame_count = 0
                start_time = time.time()
                
                # Emit FPS to client via socket.io
                socketio.emit('FPS', {'fps': fps})
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  

@app.route('/video_feed')
def video_feed():
    # 视频流路由
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # 开始 Flask 应用
    socketio.run(app, debug=True, port=5001)