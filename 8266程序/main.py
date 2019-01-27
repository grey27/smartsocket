import socket
import network
import ure
import time
import machine
import mqtt

# 填入你自己服务器的ip
HOST = '39.108.210.212'

# 提示跳转模板 三个空,分别是提示词,跳转页面,等待跳转时间
HINT_HTML = '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title></title>
      </head>
      <body>
      {}
      <script>window.setTimeout("window.location='{}'",{});</script>
      </body>
    </html>
'''


def ConnectWifi(request):
  # 取出wifi名字密码
  print(request)
  r = ure.search('ssid=(.*)&password=(.*) H',request)
  ssid = r.group(1)
  password = r.group(2)
  
  # 如果找到中文ssid进行译码
  try:
    r = ure.search('(%..)+', ssid)
    cn = r.group(0)
    cn_byte = cn.replace('%', r'\x')
    cn_byte = eval("b"+"\'"+cn_byte+"\'")
    ssid = ssid.replace(cn, cn_byte.decode())
  except:
    pass
	
  # 连接wifi
  sta = network.WLAN(network.STA_IF)
  sta.active(True)
  sta.disconnect()
  sta.connect(ssid,password)
  return ssid,password

# 获取配置页面  
def get_index_html(ap_list):
  aplist = []
  for a in ap_list:
    aplist.append(a[0].decode())
  with open('html.py') as fp:
    index_html = fp.read()
  for ssid in aplist:
    index_html = index_html.replace('ssid1',ssid,2)
  return index_html
  
# 打开sta模式
sta = network.WLAN(network.STA_IF)
sta.active(True)

# 尝试打开ssid文件获取之前配置的ssid
try:
  with open('ssid.py','r') as fp:
    ssid = fp.readline()
    password = fp.readline()
  sta.connect(ssid,password)
  time.sleep(5)
except:
  pass

# 如果可以联网即监听mqtt
if sta.isconnected():
  try:
    mqtt_c = mqtt.MQTT("mqtt_id",HOST,b'switch',12)
    mqtt_c.loop()
  except:
    pass
    # machine.reset()
# 否则打开ap模式让用户连接配置
else:
  ap_list = sta.scan()
  index_html = get_index_html(ap_list)
  ap = network.WLAN(network.AP_IF)
  ap.active(False)
  ap.active(True)
  ap.config(essid='智能插座',authmode=0)

# 设置webserver
addr = socket.getaddrinfo('192.168.4.1', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
# 循环监听

while True:
  # 获取request
  cl, addr = s.accept()
  request = cl.recv(1024).decode()
  get = request.split('\n')[0]
  # 屏蔽对favicon.ico的请求
  if 'favicon.ico' in get:
    cl.sendall('HTTP/1.1 404')
    cl.close()
    continue
  else:
    responseHeaders = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n"
    cl.send(responseHeaders)
	
  if 'ssid' in get:
    cl.sendall(HINT_HTML.format('<h1>连接中。。。</h1>','tips',10000))
    cl.close()
    ssid,password = ConnectWifi(request.split('\n')[0])
    continue
	
  if 'tips' in get:
    if sta.isconnected():
      with open('ssid.py','w') as fp:
        fp.write(ssid)
        fp.write('\n')
        fp.write(password)
      tips = '<h1>配置完成,本机ip:' + sta.ifconfig()[0] + ',设备即将重启</h1><br><h1>访问<a href="http://' + HOST + '">' + HOST + '</a>登陆后台控制</h1>'
      cl.sendall(HINT_HTML.format(tips,'index',3000))
      cl.close()
      time.sleep(3)
      ap.active(False)
      machine.reset()
    else:
      cl.sendall(HINT_HTML.format('<h1>密码错误</h1>','index',3000))
      cl.close()
    continue
	  
  if ('index' in get) or (len(get)==15):
    cl.sendall(index_html)
    cl.close()

