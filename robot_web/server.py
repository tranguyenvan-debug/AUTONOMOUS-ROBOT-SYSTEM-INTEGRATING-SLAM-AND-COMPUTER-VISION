import http.server, socketserver, os
os.chdir('/home/vantra/robot_web')
with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as s:
    print("Web: http://192.168.1.185:8080")
    s.serve_forever()
