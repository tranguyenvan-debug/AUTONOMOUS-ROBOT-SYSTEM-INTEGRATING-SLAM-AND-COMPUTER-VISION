import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import cv2
import numpy as np
import json
import onnxruntime as ort
import time
import threading

CLASSES = ['person','bicycle','car','motorcycle','airplane','bus','train','truck','boat',
           'traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat',
           'dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack',
           'umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball',
           'kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket',
           'bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple',
           'sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair',
           'couch','potted plant','bed','dining table','toilet','tv','laptop','mouse',
           'remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator',
           'book','clock','vase','scissors','teddy bear','hair drier','toothbrush']

class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        self.sess = ort.InferenceSession('/home/vantra/yolov8n.onnx')
        self.input_name = self.sess.get_inputs()[0].name
        self.sub = self.create_subscription(CompressedImage, '/image_raw/compressed', self.callback, 10)
        self.pub_img = self.create_publisher(CompressedImage, '/detection/compressed', 10)
        self.pub_json = self.create_publisher(String, '/detection/objects', 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub_track = self.create_subscription(String, '/track/target', self.set_track, 10)
        self.lock = threading.Lock()
        self.latest_frame = None
        self.last_objects = []
        self.track_class = None
        self.last_yolo_time = 0
        self.lost_time = None
        threading.Thread(target=self.yolo_loop, daemon=True).start()
        self.get_logger().info('YOLO Detector started')

    def set_track(self, msg):
        with self.lock:
            self.track_class = msg.data if msg.data != '' else None
        self.get_logger().info(f'Track: {self.track_class}')

    def preprocess(self, frame):
        img = cv2.resize(frame, (640, 640))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        return np.expand_dims(np.transpose(img, (2, 0, 1)), 0)

    def yolo_detect(self, frame):
        h, w = frame.shape[:2]
        inp = self.preprocess(frame)
        output = self.sess.run(None, {self.input_name: inp})
        pred = output[0][0].T
        boxes, scores_list, class_ids = [], [], []
        for det in pred:
            scores = det[4:]
            cls = int(np.argmax(scores))
            conf = float(scores[cls])
            if conf < 0.35:
                continue
            cx, cy, bw, bh = det[:4]
            x1 = int((cx - bw/2) * w)
            y1 = int((cy - bh/2) * h)
            x2 = int((cx + bw/2) * w)
            y2 = int((cy + bh/2) * h)
            boxes.append([x1, y1, x2-x1, y2-y1])
            scores_list.append(conf)
            class_ids.append(cls)
        objects = []
        if boxes:
            indices = cv2.dnn.NMSBoxes(boxes, scores_list, 0.35, 0.45)
            if len(indices) > 0:
                for i in indices.flatten():
                    x,y,bw2,bh2 = boxes[i]
                    name = CLASSES[class_ids[i]] if class_ids[i] < len(CLASSES) else str(class_ids[i])
                    objects.append({'name': name, 'conf': round(scores_list[i],2), 'box': [x,y,x+bw2,y+bh2]})
        return objects

    def yolo_loop(self):
        while True:
            time.sleep(1.5)
            with self.lock:
                if self.latest_frame is None:
                    continue
                frame = self.latest_frame.copy()
            objects = self.yolo_detect(frame)
            with self.lock:
                self.last_objects = objects

    def control_robot(self, box, frame_w, frame_h):
        x1,y1,x2,y2 = box
        cx = (x1+x2)/2
        bw = x2-x1
        bh = y2-y1
        area = (bw*bh)/(frame_w*frame_h)
        error_x = (cx - frame_w/2) / (frame_w/2)
        twist = Twist()
        if area > 0.3:
            # Gan roi - dung lai
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif abs(error_x) > 0.3:
            # Lech nhieu - xoay cham, tien cham
            twist.linear.x = 0.03
            twist.angular.z = -error_x * 0.3
        elif abs(error_x) > 0.1:
            # Lech vua - tien va chinh nhe
            twist.linear.x = 0.06
            twist.angular.z = -error_x * 0.2
        else:
            # Thang - chi tien
            twist.linear.x = 0.08
            twist.angular.z = 0.0
        self.cmd_pub.publish(twist)

    def callback(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            return
        h, w = frame.shape[:2]
        with self.lock:
            self.latest_frame = frame.copy()
            objects = list(self.last_objects)
            track_class = self.track_class

        # Vẽ tất cả vật thể
        for o in objects:
            x1,y1,x2,y2 = o['box']
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 1)
            label = f'{o["name"]} {o["conf"]:.2f}'
            (tw,th),_ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1,y1-th-6), (x1+tw+4,y1), (0,255,0), -1)
            cv2.putText(frame, label, (x1+2,y1-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

        # Track
        if track_class and track_class != '':
            best = max((o for o in objects if o['name']==track_class),
                      key=lambda x: x['conf'], default=None)
            if best:
                x1,y1,x2,y2 = best['box']
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,100,255), 3)
                cx,cy = (x1+x2)//2, (y1+y2)//2
                cv2.line(frame, (cx-15,cy), (cx+15,cy), (0,100,255), 2)
                cv2.line(frame, (cx,cy-15), (cx,cy+15), (0,100,255), 2)
                cv2.putText(frame, f'TRACKING: {track_class}', (x1,y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,100,255), 2)
                self.control_robot(best['box'], w, h)
                with self.lock:
                    self.lost_time = None
            else:
                now = time.time()
                with self.lock:
                    if self.lost_time is None:
                        self.lost_time = now
                    elapsed = now - self.lost_time
                twist = Twist()
                if elapsed < 3.0:
                    cv2.putText(frame, f'TIM: {track_class}... {3-int(elapsed)}s', (10,30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                    twist.angular.z = 0.4
                else:
                    cv2.putText(frame, 'DUNG - MAT MUC TIEU', (10,30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                    twist.angular.z = 0.0
                self.cmd_pub.publish(twist)

        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        out = CompressedImage()
        out.header = msg.header
        out.format = 'jpeg'
        out.data = buf.tobytes()
        self.pub_img.publish(out)
        self.pub_json.publish(String(data=json.dumps(objects)))

def main():
    rclpy.init()
    node = YoloDetector()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
