from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import time
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

camera = cv2.VideoCapture(0)
@app.route('/')
def index():
    # 主页面
    return render_template('index.html')

def gen_frames():  
    fps = 0
    frame_count = 0
    start_time = time.time()
    while True:
        global camera
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("Can not read from camera")
            time.sleep(1)
        else:
            frame_count += 1
            end_time = time.time()
            if (end_time - start_time) > 1:
                fps = frame_count / (end_time - start_time)
                frame_count = 0
                start_time = time.time()
                
                # Emit FPS to client via socket.io
                socketio.emit('FPS', {'fps': fps})
            
                        # Convert to grayscale for face detection
            resize_scale = 0.3
            small_frame = cv2.resize(frame,(0, 0), fx=resize_scale, fy=resize_scale)
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # Draw rectangles around the faces
            for (x, y, w, h) in faces:
                x, y, w, h = [int(dim / resize_scale) for dim in (x, y, w, h)]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)


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
    socketio.run(app, use_reloader=False, debug=True, port=5003)