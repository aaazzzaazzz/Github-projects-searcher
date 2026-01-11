#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="templates", **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_frontend_server():
    """启动前端服务器"""
    port = 8080
    server_address = ('', port)
    
    # 切换到templates目录
    os.chdir('templates')
    
    httpd = HTTPServer(server_address, CustomHandler)
    
    print(f"前端服务器启动在 http://localhost:{port}")
    print("修复后的前端页面: http://localhost:8080/index_fixed.html")
    print("按 Ctrl+C 停止服务器")
    
    # 自动打开浏览器
    def open_browser():
        time.sleep(1)  # 等待服务器启动
        webbrowser.open(f'http://localhost:{port}/index_fixed.html')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    start_frontend_server()