#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()


#导入需要的库
import network
import time
from MPU6050 import MPU6050
from machine import Pin, PWM,Timer
import socket
import _thread

#设置需要的引脚（用于后续判断链接）
led=Pin(32,Pin.OUT,value=1)
beeper = PWM(Pin(25, Pin.OUT), freq=1000, duty=0)

#链接网络(已连接则跳过，未连接则连接）
if network.WLAN().isconnected():
    wlan=network.WLAN()
    pass
else:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)     
    wlan.scan()
    wlan.connect('EHlatex', 'overleaf')
#判断链接
while True:
    if wlan.isconnected():
        for i in range(4):
            led.value(0)
            time.sleep(0.1)
            led.value(1)
            time.sleep(0.1)
        beeper.duty(500)
        time.sleep(1)
        beeper.duty(0)
        break  
    time.sleep(1)
#主线程：信号传递（服务器）

# 1. 创建TCP套接字
server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. 绑定本地信息
server_s.bind(("192.168.50.193", 12345))

# 3. 设置为被动的
server_s.listen(128)

# 4. 等待客户端链接
new_s, client_info = server_s.accept()

a=0
recv_content = new_s.recv(1024)
print("%s>>>%s" % (str(client_info), recv_content.decode("gbk")))
#测量加速度和角度
def get_ac():
    # 加速度 Data
    mpu = MPU6050()
    accel = mpu.read_accel_data() # [ms^-2]
    #字典索引
    aX = round(accel["x"],2)
    aY = round(accel["y"],2)
    aZ = round(accel["z"],2)
    ac="acx:" + str(aX) + "||acy:" + str(aY) + "||acz:" + str(aZ)
    return ac
def get_g():
    mpu = MPU6050()
    gyro = mpu.read_gyro_data()   # [角度/s]
    gX = round(gyro["x"],2)
    gY = round(gyro["y"],2)
    gZ = round(gyro["z"],2)
    g="gx:" + str(gX) + "||gy:" + str(gY) + "||gz:" + str(gZ)
    return g

#测量速度和距离
k=0
length=0
speed = 0
def timi():
    global k
    def lsp(tim):
        global speed,length
        speed=round((k/33-length),2)
        length=round((k/33),2)
    tim = Timer(1)
    tim.init(period=1000, mode=Timer.PERIODIC, callback=lsp)
    
    
    while 1:
        response = get_ac()+' '
        new_s.send(response.encode())
        response = get_g()+' '
        new_s.send(response.encode())
        response = 'speed:'+str(speed)+'||length:'+str(length)+' '
        new_s.send(response.encode())
        time.sleep(1)

def number():
    
    hong=Pin(23,Pin.IN,Pin.PULL_UP,value=1)
    x=0
    y=0
    while 1:
        global k
        if hong.value() == 0 and x == 0 :
            x = 1
        if hong.value() == 1 and y == 0 :
            y = 1
        if x == 1 and y == 1:
            k+=1
            x=0
            y=0

th1 = _thread.start_new_thread(timi, ())
th2 = _thread.start_new_thread(number, ())
K1=Pin(35,Pin.IN)
K2=Pin(34,Pin.IN)
#170，250，70
b=0
while 1:
    if K1.value()==0 and b==0:
        b=1
        dianji1 = PWM(Pin(26, Pin.OUT))  
        dianji2 = PWM(Pin(27, Pin.OUT))
        duoji = PWM(Pin(15, Pin.OUT), freq=50)
        dianji1.duty(700)
        dianji2.duty(0)
        time.sleep(2)
        dianji1.duty(750)
        dianji2.duty(0)
        time.sleep(2)
        dianji1.duty(850)
        dianji2.duty(0)
        time.sleep(2)#直线
        
        duoji.duty(60)
        dianji1.duty(750)
        dianji2.duty(0)
        time.sleep(1)
        duoji.duty(55)
        dianji1.duty(550)
        dianji2.duty(0)
        time.sleep(0.6)
        duoji.duty(50)
        dianji1.duty(450)
        dianji2.duty(0)
        time.sleep(2)        
        duoji.duty(30)
        dianji1.duty(250)
        dianji2.duty(0)
        time.sleep(3)
        duoji.duty(30)
        dianji1.duty(250)
        dianji2.duty(0)
        time.sleep(1.3)#第一个弯道

        duoji.duty(90)
        dianji1.duty(600)
        dianji2.duty(0)
        time.sleep(5.2)
        duoji.duty(80)
        dianji1.duty(850)
        dianji2.duty(0)
        time.sleep(2)#直线

        dianji1.duty(1023)
        dianji2.duty(1023)
        duoji.duty(40)
        time.sleep(1)
        dianji1.duty(0)
        dianji2.duty(250)
        time.sleep(7)
        
        duoji.duty(85)
        dianji1.duty(0)
        dianji2.duty(1023)
        time.sleep(2.7)#入库直线

        dianji1.duty(1023)
        dianji2.duty(1023)
        time.sleep(2)
        
        duoji.duty(85)
        dianji1.duty(1023)
        dianji2.duty(0)
        time.sleep(2.7)#出库直线
        
        duoji.duty(30)
        dianji1.duty(250)
        dianji2.duty(0)
        time.sleep(3)
        duoji.duty(85)
        dianji1.duty(0)
        dianji2.duty(500)
        time.sleep(1)
        duoji.duty(55)
        dianji1.duty(350)
        dianji2.duty(0)
        time.sleep(5)#出库1
        
        duoji.duty(100)
        dianji1.duty(0)
        dianji2.duty(500)
        time.sleep(4)#出库2

        duoji.duty(55)
        dianji1.duty(700)
        dianji2.duty(0)
        time.sleep(2.5)
        duoji.duty(40)
        dianji1.duty(600)
        dianji2.duty(0)
        time.sleep(6)#第二个弯道
        
        duoji.duty(85)
        dianji1.duty(1023)
        dianji2.duty(0)
        time.sleep(6)#直线

        dianji1.duty(1023)
        dianji2.duty(1023)#停车
    if b==1 and K2.value()==0:
        b=0
        dianji1.duty(1)