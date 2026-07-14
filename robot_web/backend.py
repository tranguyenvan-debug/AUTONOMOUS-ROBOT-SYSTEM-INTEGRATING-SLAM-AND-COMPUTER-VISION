from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os

slam_proc = None
nav2_proc = None
current_map = None
current_map = None

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        global slam_proc, nav2_proc, current_map
        try:
            path = self.path
            if path == '/slam/start':
                if slam_proc is None:
                    # Kill slam cu neu con
                    subprocess.run(['bash', '-c', 'pkill -f slam_toolbox || true'], shell=False)
                    import time; time.sleep(1)
                    slam_proc = subprocess.Popen(
                        ['bash', '-c', 'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && /home/vantra/run_slam.sh']
                    )
                content = json.dumps({"ok": True, "msg": "SLAM started"}).encode()
                ct = 'application/json'
            elif path == '/slam/stop':
                if slam_proc:
                    slam_proc.terminate()
                    slam_proc = None
                subprocess.run(['bash', '-c', 'pkill -f async_slam_toolbox || pkill -f slam_toolbox || true'], shell=False)
                content = json.dumps({"ok": True, "msg": "SLAM stopped"}).encode()
                ct = 'application/json'
            elif path == '/nav2/start':
                if nav2_proc is None:
                    import glob
                    maps = glob.glob('/home/vantra/maps/*.yaml')
                    maps = [m for m in maps if '_waypoints' not in m]
                    if not maps:
                        content = json.dumps({"ok": False, "msg": "Khong co map! Hay ve map truoc."}).encode()
                        ct = 'application/json'
                        self.send_response(200)
                        self.send_header('Content-Type', ct)
                        self.send_header('Content-Length', len(content))
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(content)
                        return
                    latest_map = max(maps, key=os.path.getmtime)
                    current_map = os.path.splitext(os.path.basename(latest_map))[0]
                    nav2_proc = subprocess.Popen(
                        ['bash', '-c', f'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 launch robot_base nav2_only.launch.py map_file:={latest_map}']
                    )
                content = json.dumps({"ok": True, "msg": "Nav2 started"}).encode()
                ct = 'application/json'
            elif path == '/nav2/cancel':
                try:
                    subprocess.run(
                        ['bash', '-c', 'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 service call /navigate_to_pose/_action/cancel_goal action_msgs/srv/CancelGoal "{goal_info: {goal_id: {uuid: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}, stamp: {sec: 0, nanosec: 0}}}" 2>/dev/null'],
                        shell=False, timeout=5
                    )
                except: pass
                content = json.dumps({"ok": True, "msg": "Cancelled"}).encode()
                ct = 'application/json'
                subprocess.Popen(['bash', '-c', 'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 action send_goal --feedback /navigate_to_pose nav2_msgs/action/NavigateToPose "{}" & sleep 0.1 && pkill -f "action send_goal" || true'], shell=False)
                subprocess.run(['bash', '-c', 'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 service call /navigate_to_pose/_action/cancel_goal action_msgs/srv/CancelGoal "{}" 2>/dev/null || true'], shell=False, timeout=3)
                content = json.dumps({"ok": True, "msg": "Goal cancelled"}).encode()
                ct = 'application/json'
            elif path == '/nav2/stop':
                if nav2_proc:
                    nav2_proc.terminate()
                    nav2_proc = None
                    current_map = None
                content = json.dumps({"ok": True, "msg": "Nav2 stopped"}).encode()
                ct = 'application/json'
            elif path.startswith('/map/save'):
                from urllib.parse import parse_qs, urlparse
                params = parse_qs(urlparse(path).query)
                name = params.get('name', ['my_map'])[0]
                os.makedirs('/home/vantra/maps', exist_ok=True)
                cmd = f'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \'{{name: {{data: /home/vantra/maps/{name}}}}}\''
                subprocess.Popen(['bash', '-c', cmd])
                content = json.dumps({"ok": True, "msg": f"Map saved: {name}"}).encode()
                ct = 'application/json'
            elif path.startswith('/waypoint/save'):
                from urllib.parse import parse_qs, urlparse
                params = parse_qs(urlparse(path).query)
                wp_name = params.get('name', [''])[0]
                x = float(params.get('x', [0])[0])
                y = float(params.get('y', [0])[0])
                import glob
                maps = glob.glob('/home/vantra/maps/*.yaml')
                maps = [m for m in maps if '_waypoints' not in m]
                map_name = os.path.splitext(os.path.basename(max(maps, key=os.path.getmtime)))[0] if maps else 'default'
                wp_file = f'/home/vantra/maps/{map_name}_waypoints.json'
                wps = []
                if os.path.exists(wp_file):
                    with open(wp_file) as f: wps = json.load(f)
                wps = [w for w in wps if w['name'] != wp_name]
                wps.append({'name': wp_name, 'x': x, 'y': y})
                with open(wp_file, 'w') as f: json.dump(wps, f)
                content = json.dumps({"ok": True, "map": map_name}).encode()
                ct = 'application/json'
            elif path == '/waypoint/list':
                import glob
                wps = []
                map_name = current_map
                if map_name is None:
                    maps = glob.glob('/home/vantra/maps/*.yaml')
                    maps = [m for m in maps if '_waypoints' not in m]
                    if maps:
                        map_name = os.path.splitext(os.path.basename(max(maps, key=os.path.getmtime)))[0]
                if map_name:
                    wp_file = f'/home/vantra/maps/{map_name}_waypoints.json'
                    if os.path.exists(wp_file):
                        with open(wp_file) as f: wps = json.load(f)
                content = json.dumps({"ok": True, "waypoints": wps, "map": map_name}).encode()
                ct = 'application/json'
            elif path.startswith('/waypoint/delete'):
                from urllib.parse import parse_qs, urlparse
                params = parse_qs(urlparse(path).query)
                wp_name = params.get('name', [''])[0]
                import glob
                maps = glob.glob('/home/vantra/maps/*.yaml')
                maps = [m for m in maps if '_waypoints' not in m]
                if maps:
                    map_name = os.path.splitext(os.path.basename(max(maps, key=os.path.getmtime)))[0]
                    wp_file = f'/home/vantra/maps/{map_name}_waypoints.json'
                    wps = []
                    if os.path.exists(wp_file):
                        with open(wp_file) as f: wps = json.load(f)
                    wps = [w for w in wps if w['name'] != wp_name]
                    with open(wp_file, 'w') as f: json.dump(wps, f)
                content = json.dumps({"ok": True}).encode()
                ct = 'application/json'
            elif path == '/sysinfo':
                import shutil
                cpu = subprocess.run(['top','-bn1'], capture_output=True, text=True).stdout
                cpu_line = [l for l in cpu.split('\n') if 'Cpu' in l]
                cpu_pct = cpu_line[0].split()[1].replace('%us,','').strip() if cpu_line else '--'
                with open('/proc/meminfo') as f2:
                    mem = f2.read()
                mem_total = int([l for l in mem.split('\n') if 'MemTotal' in l][0].split()[1])
                mem_free = int([l for l in mem.split('\n') if 'MemAvailable' in l][0].split()[1])
                ram_pct = round((mem_total-mem_free)/mem_total*100)
                disk = shutil.disk_usage('/')
                disk_free = round(disk.free/1024/1024/1024, 1)
                try:
                    wifi = subprocess.run(['iwconfig','wlan0'], capture_output=True, text=True).stdout
                    import re
                    sig = re.search(r'Signal level=(-\d+)', wifi)
                    wifi_dbm = sig.group(1) if sig else '--'
                except:
                    wifi_dbm = '--'
                content = json.dumps({"ok":True,"cpu":cpu_pct,"ram":ram_pct,"disk":disk_free,"wifi":wifi_dbm}).encode()
                ct = 'application/json'
            elif path == '/ai/start':
                subprocess.Popen(['bash', '-c', 'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 run robot_base yolo_detector'])
                content = json.dumps({"ok": True, "msg": "AI started"}).encode()
                ct = 'application/json'
            elif path == '/ai/stop':
                subprocess.run(['bash', '-c', 'pkill -f yolo_detector || true'], shell=False)
                content = json.dumps({"ok": True, "msg": "AI stopped"}).encode()
                ct = 'application/json'
            elif path == '/set_initial_pose':
                subprocess.Popen(['bash', '-c', 'source /opt/ros/jazzy/setup.bash && source /home/vantra/robot_ws/install/setup.bash && ros2 topic pub --once /initialpose geometry_msgs/PoseWithCovarianceStamped "{header: {frame_id: \'map\'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0, 0,0.25,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.068]}}"'])
                content = json.dumps({"ok": True, "msg": "Da set vi tri ban dau!"}).encode()
                ct = 'application/json'
            elif path == '/status':
                content = json.dumps({
                    "slam": slam_proc is not None,
                    "nav2": nav2_proc is not None
                }).encode()
                ct = 'application/json'
            elif path == '/' or path == '/index.html':
                with open('/home/vantra/robot_web/index.html', 'rb') as f:
                    content = f.read()
                ct = 'text/html'
            elif path.endswith('.css'):
                with open('/home/vantra/robot_web' + path, 'rb') as f:
                    content = f.read()
                ct = 'text/css'
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header('Content-Type', ct)
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print("ERROR:", e)
            self.send_response(500)
            self.end_headers()

if __name__ == '__main__':
    print('Backend running at http://0.0.0.0:8080')
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    server.serve_forever()
