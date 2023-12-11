from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import time
import threading
from volume import get_volume

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
cond = threading.Condition()
rsc = None
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def gen_frames_async():
    global rsc
    print("entering generate thread")
    camera = cv2.VideoCapture(0)
    start_time = time.time()
    last_external_flush_time = time.time()
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("Can not read from camera")
            time.sleep(1)
        else:
                                  # Convert to grayscale for face detection
            resize_scale = 0.3
            small_frame = cv2.resize(frame,(0, 0), fx=resize_scale, fy=resize_scale)
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            time_flush_cond = time.time() - start_time > 1
            face_flush_cond = len(faces) >= 1
            volume_flush_cond = get_volume() >= 70
            external_flush_cond = face_flush_cond or volume_flush_cond
            
            if external_flush_cond:
                last_external_flush_time = time.time()

            with cond:
                if time_flush_cond or external_flush_cond or time.time() - last_external_flush_time < 5:
                    start_time = time.time()
                    # Draw rectangles around the faces
                    for (x, y, w, h) in faces:
                        x, y, w, h = [int(dim / resize_scale) for dim in (x, y, w, h)]
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    rsc = (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    cond.notify_all()

@app.route('/')
def index():
    # 主页面
    return render_template('index.html')

def gen_frames():  
    fps = 0
    frame_count = 0
    start_time = time.time()
    last_frm = None
    last_volume = 0
    global rsc
    while True:
            # Emit FPS to client via socket.io
        with cond:
            if rsc is None or rsc == last_frm:
                cond.wait()
            last_frm = rsc
        assert not last_frm is None
        frame_count += 1
        end_time = time.time()
        if (end_time - start_time) > 1:
            fps = frame_count / (end_time - start_time)
            frame_count = 0
            start_time = time.time()
        socketio.emit('FPS', {'fps': fps, 'volume': get_volume()})
        yield last_frm
            
@app.route('/video_feed')
def video_feed():
    # 视频流路由
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    thread = threading.Thread(target=gen_frames_async)
    # Start the thread
    thread.start()
    # 开始 Flask 应用
    socketio.run(app, use_reloader=False, debug=True, port=5001)