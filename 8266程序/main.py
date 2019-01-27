import socket
import network
import ure
import time
import machine
import mqtt

# �������Լ���������ip
HOST = '39.108.210.212'

# ��ʾ��תģ�� ������,�ֱ�����ʾ��,��תҳ��,�ȴ���תʱ��
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
  # ȡ��wifi��������
  print(request)
  r = ure.search('ssid=(.*)&password=(.*) H',request)
  ssid = r.group(1)
  password = r.group(2)
  
  # ����ҵ�����ssid��������
  try:
    r = ure.search('(%..)+', ssid)
    cn = r.group(0)
    cn_byte = cn.replace('%', r'\x')
    cn_byte = eval("b"+"\'"+cn_byte+"\'")
    ssid = ssid.replace(cn, cn_byte.decode())
  except:
    pass
	
  # ����wifi
  sta = network.WLAN(network.STA_IF)
  sta.active(True)
  sta.disconnect()
  sta.connect(ssid,password)
  return ssid,password

# ��ȡ����ҳ��  
def get_index_html(ap_list):
  aplist = []
  for a in ap_list:
    aplist.append(a[0].decode())
  with open('html.py') as fp:
    index_html = fp.read()
  for ssid in aplist:
    index_html = index_html.replace('ssid1',ssid,2)
  return index_html
  
# ��staģʽ
sta = network.WLAN(network.STA_IF)
sta.active(True)

# ���Դ�ssid�ļ���ȡ֮ǰ���õ�ssid
try:
  with open('ssid.py','r') as fp:
    ssid = fp.readline()
    password = fp.readline()
  sta.connect(ssid,password)
  time.sleep(5)
except:
  pass

# �����������������mqtt
if sta.isconnected():
  try:
    mqtt_c = mqtt.MQTT("mqtt_id",HOST,b'switch',2)
    mqtt_c.loop()
  except:
    pass
    # machine.reset()
# �����apģʽ���û���������
else:
  ap_list = sta.scan()
  index_html = get_index_html(ap_list)
  ap = network.WLAN(network.AP_IF)
  ap.active(False)
  ap.active(True)
  ap.config(essid='���ܲ���',authmode=0)

# ����webserver
addr = socket.getaddrinfo('192.168.4.1', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(5)
# ѭ������

while True:
  # ��ȡrequest
  cl, addr = s.accept()
  request = cl.recv(1024).decode()
  get = request.split('\n')[0]
  # ���ζ�favicon.ico������
  if 'favicon.ico' in get:
    cl.sendall('HTTP/1.1 404')
    cl.close()
    continue
  else:
    responseHeaders = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n"
    cl.send(responseHeaders)
	
  if 'ssid' in get:
    cl.sendall(HINT_HTML.format('<h1>�����С�����</h1>','tips',10000))
    cl.close()
    ssid,password = ConnectWifi(request.split('\n')[0])
    continue
	
  if 'tips' in get:
    if sta.isconnected():
      with open('ssid.py','w') as fp:
        fp.write(ssid)
        fp.write('\n')
        fp.write(password)
      tips = '<h1>�������,����ip:' + sta.ifconfig()[0] + ',�豸��������</h1><br><h1>����<a href="http://' + HOST + '">' + HOST + '</a>��½��̨����</h1>'
      cl.sendall(HINT_HTML.format(tips,'index',3000))
      cl.close()
      time.sleep(3)
      ap.active(False)
      machine.reset()
    else:
      cl.sendall(HINT_HTML.format('<h1>�������</h1>','index',3000))
      cl.close()
    continue
	  
  if ('index' in get) or (len(get)==15):
    cl.sendall(index_html)
    cl.close()

