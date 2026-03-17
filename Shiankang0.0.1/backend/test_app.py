# -*- coding: utf-8 -*-
from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>测试成功！Flask服务器运行正常</h1>'

if __name__ == '__main__':
    print("启动测试服务器...")
    print("访问: http://localhost:5000")
    
    # 如果是调试模式，添加输入等待
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.run(debug=True, port=5000, host='0.0.0.0')
        input("按Enter退出...")  # 这行不会执行，因为app.run()会阻塞
    else:
        app.run(debug=True, port=5000, host='0.0.0.0')