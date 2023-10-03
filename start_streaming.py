from flask import Flask, Response
import cv2

app = Flask(__name__)

# Function to generate MJPEG frames from the webcam
def generate_frames():
    cap = cv2.VideoCapture(0)  # 0 for default webcam, you can change this if you have multiple cameras

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode the frame as JPEG
        _, encoded_frame = cv2.imencode('.jpg', frame)

        # Yield the MJPEG frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_frame) + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return "Welcome to the webcam streaming server!"

@app.route('/video_stream')
def video_stream():
    # Return the MJPEG response for the video element
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
