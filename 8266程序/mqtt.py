from simple import MQTTClient
from machine import Pin
import utime

class MQTT():
	def __init__(self,id,host,topic,pin=2):
		self.host = host
		self.topic = topic
		self.id = id
		self.pin = Pin(pin,Pin.OUT)
		
	def loop(self):
		c = MQTTClient(self.id, self.host) #建立一个MQTT客户端,传入连接id号和主机
		c.set_callback(self.sub_cb) #设置回调函数
		c.connect() #建立连接
		c.subscribe(self.topic) #监控这个通道，接收控制命令,
		while True:
			c.check_msg()
			if utime.time() % 10 == 0:
				c.ping()


	def sub_cb(self,topic, msg):   #回调函数，收到服务器消息后会调用这个函数
		print(topic, msg)
		if msg == b'true':
		  self.pin.value(1)
		if msg == b'false':
		  self.pin.value(0)
		  
if __name__ == '__main__':
	mqtt = MQTT('39.108.210.212',b'test',2)
	mqtt.loop()
