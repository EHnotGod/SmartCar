# **数智先锋智能小车大作业（详述）**

---

[TOC]

## **思路分析**

此次作业的要求是：利用单片机，实现小车跑图并实时传递数据到linux平台上显示。

此次作业的主要材料有：车模，电机，舵机，光耦对射传感器，MPU6050三轴传感器，ESP32单片机

首先，学习单片机的基础知识，然后就是简单分析一下如何驱动电机和舵机，写出跑图程序。接着就是对那两个传感器的分析，结合自己的理解写出可操作的函数。接下来就是搭建一个linux平台，我这里使用的是虚拟机终端，利用socket模块解决信号传输的问题，最后就是用多线程的方式综合一下代码。

-----

## **ESP32基础知识**

### 什么是单片机

可以理解为没有可视化操作系统的电脑。（信息处理能力不差的好吧）

单片机若要使用需烧录程序，用USB连电脑（指示灯会亮的）。

我使用micropython操作。

烧录micripython:

![烧录.png](https://s2.loli.net/2024/01/20/KU2Q1EgsY7FvuZM.png)

### I/O接口

单片机上有很多引脚，并拥有着对应的序号。引脚就是接口。

I就是IN的意思，表示输入；O指OUT，输出。

每个引脚一般要么是高电平要么是低电平。

引脚设置为in的时候，如果没有外界电压影响，它会按照你的设置表示对应电平。如果有，则受到外界电压影响则表示外界电平。适合用来判断。（Pin.PULL_UP指打开上拉电阻，某种情况更稳定一些）

```python
from machine import Pin
led = Pin(5,Pin.IN,Pin.PULL_UP,value=1)
```

引脚为out的时候，输出对应电平，用于驱动。

```python
from machine import Pin
led = Pin(5,Pin.OUT,value=1)
```

### Time模块

这个很简单，但是为啥再提一下呢？

常用呗。（除此外python其他基础代码块则忽略）

```python
import time
time.sleep(1)
time.sleep_ms(10)
time.sleep_us(100)
```

### PWM波

这是单片机的一个模块而已。

类似于电磁波，用它设置后的引脚（一般OUT），会以特定的频率和占空比发出电流脉冲。应用eg.呼吸灯。

频率顾名思义，没有特别大的影响，占空比(0-1024)则会影响平均电平大小（反比）

![pwm.png](https://s2.loli.net/2024/01/20/R3go4B7VzfTQlmd.png)

```python
from machine import Pin,PWM
import time
p2 = PWM(Pin(33),Pin.OUT)
p2.freq(100)
for i in range(1,1023):
    p2.duty(i)
    time.sleep_ms(10)
```

----

## **小车各模块讲解**

### 电机和舵机

在引航计划作业给的开发板中，由于其电机和电池模块的特殊性，连接方式也特殊。这里的例子也许并不适用于所有的ESP32单片机。

控制电机和舵机都需要用到PWM。连接方式：

![电机.jpg](https://s2.loli.net/2024/01/20/TIdwcQm4ZGk8KYF.jpg)

电机对应的引脚为26，27。（双低则不稳定，不推荐）

| 26  | 27  | 表现  |
|:---:|:---:|:---:|
| 高电平 | 低电平 | 正转  |
| 低电平 | 高电平 | 反转  |
| 高电平 | 高电平 | 不转  |

```python
from machine import Pin,PWM
led1 = PWM(Pin(26))
led2 = PWM(Pin(27))
led1.freq(100)
led2.freq(100)
led1.duty(1023)
led2.duty(1)
time.sleep_ms(6000)
```

现在来看一下舵机，它有三条线，一个信号线，一个VCC，一个GND，别搞错了哈。

每个舵机的共同点是一般转向是正90°逆90°，不同点是控制角度的duty范围有点不一样。

```python
from machine import Pin,PWM
p2 = PWM(Pin(15),Pin.OUT)
p2.freq(100)
#左转
p2.duty(60)
#右转
p2.duty(250)
```

### 光耦对射传感器

它的原理是这样的：它除了VCC和GND之外，它还有一个OUT口，当两个黑色柱子中间无东西遮挡时，它会输出低电平，有东西遮挡时它会断电（等同于无外部电平），设置开发板上一个引脚（IN）与之相连，便可以检测它是否被遮挡。电机转动时会带动码盘旋转，码盘是网状结构的，有时候会遮挡有时候不遮挡，通过计算单位时间内被遮挡的次数便可以获得电机的转速。所以，它是测速度和距离的!

测试代码如下：

```python
from machine import Pin
import time
hong = Pin(5,Pin.IN,Pin.PULL_UP,value=1)
while 1:
    print(hong.value())
    time.sleep(1)
```

### MPU6050三轴传感器

这个的用法要根据具体操作文件的代码来。如果使用此处的代码，请将MPU6050操作文件（在文件夹里）也烧录。这个传感器能测的东西很多，有8个引脚，此处我们只取4个，SCL:22，SDA:21，VCC，GND，可以测速度、加速度、温度。

测试代码如下：

```python
from MPU6050 import MPU6050
from machine import Pin
import time
mpu = MPU6050()
while True:
    #加速度 Data
    accel = mpu.read_accel_data() # [ms^-2]
    #字典索引哈
    aX = accel["x"]
    aY = accel["y"]
    aZ = accel["z"]
    print("acx: " + str(aX) + " acy: " + str(aY) + " acz: " + str(aZ))
    # 陀螺仪 Data
    gyro = mpu.read_gyro_data()   # [角度/s]
    gX = gyro["x"]
    gY = gyro["y"]
    gZ = gyro["z"]
    print("gx:" + str(gX) + " gy:" + str(gY) + " gz:" + str(gZ))
    # 温度 Data
    temp = mpu.read_temperature()   # [摄氏度]
    print("Temperature: " + str(temp) + "°C")
    #间隔时间
    time.sleep(1)
```

------

## **用SOCKET通信**

### 思路

让电脑和单片机都连接手机热点。然后读取单片机的网络ip地址，再分别在单片机和linux的py文件里写代码，使一个作为服务器，一个是客户端，利用TCP传输协议传输数据。

### 连接wifi热点

单片机有两种模式，一种是STA，可以连接别人的热点。还有一种是AP，可以作为热点被连接。

这里我的方法是使用STA，让电脑和单片机都连接手机热点。电脑怎么连不用我说。单片机倒是有很多要注意的：

1.单片机大概率不会出问题，但是可能连不上你的手机。这并不意味着这个单片机连不上任何手机，它也许可以连接上其他手机的热点。同理，你的手机也可能可以连接上其他单片机，原理不明，但事实存在。

2.连接需要一定的时间，耐心一点哈。

3.频段不能为5G，请选择2.4G的。

```python
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)     
wlan.scan()
wlan.connect('ssid', 'password')
wlan.isconnected()  
```

等待终端中的wlan.isconnected()为True时，就连上了，这个时候采用wlan.ifconfig()获得单片机ip（第一个就是）

### TCP

socket（套接字）是进程（就是运行中的程序）间通信的一种方式，它与其他进程间通信的一个主要不同是：

它能实现不同主机间的进程间通信，我们网络上各种各样的服务大多都是基于 socket 来完成通信的

例如: 我们每天浏览网页、QQ 聊天、收发 email 等等

py的一个库就是socket

套接字使用流程与文件的使用流程很类似

1. 创建套接字
2. 使用套接字收/发数据
3. 关闭套接字

一般的通信方式有udp和tcp，使用udp发送数据容易丢失，而tcp能够保证数据稳定传送

TCP协议，传输控制协议（英语：Transmission Control Protocol，缩写为 TCP）是一种面向连接的、可靠的传输通信协议。

![__VO_DV6GS_EYC3DMYF55QE.png](https://s2.loli.net/2024/01/20/oiLGMOqDv8glfJP.png)

我个人的想法是颠倒服务器和客户端（因为单片机的ip好找）。对了哈，先启动服务器再启动客户端。

以下是代码示例：

服务器：

```python
import socket
# 1. 创建TCP套接字
server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 2. 绑定本地信息
server_s.bind(("", 7788))
# 3. 设置为被动的
server_s.listen(128)
# 4. 等待客户端链接
new_s, client_info = server_s.accept()
# 5. 用新的套接字为已经连接好的客户端服务器
recv_content = new_s.recv(1024)
print("%s>>>%s" % (str(client_info), recv_content.decode("gbk")))
# 6. 关闭套接字
new_s.close()
server_s.close()
```

客户端：

```python
from socket import *
# 1. 创建socket
tcp_client_socket = socket(AF_INET, SOCK_STREAM)
# 2. 链接服务器
tcp_client_socket.connect(("", 7788))
# 提示用户输入数据
send_data = input("请输入要发送的数据：")
# 3. 向服务器发送数据
tcp_client_socket.send(send_data.encode("utf-8"))
# 4. 关闭套接字
tcp_client_socket.close()
```

-----

## **多线程综合控制**

小车既要跑图又要信号传输，但是普通的py是单线程语言，我们需要用到一个库，叫做_thread，使用方法非常简单哈：

```python
import time
import _thread
def worker():
    for i in range(10):
        print("Worker thread is running")
        time.sleep(1) 
    thread.exit()
_thread.start_new_thread(worker, ())
while 1:
    print(10086)
    time.sleep(2)
```

----

## **bug整理**

1.  connection lost链接丢失
解决方案：多重连几次（但不一定稳定）

![图1.jpg](https://s2.loli.net/2024/02/23/a7zjFxXp4WLdcmH.jpg)

2. SyntaxError
syntax error是语法错误，在我们初学中很容易的遇到的报错，不仅包括代码完整性还包括格式等问题。

![图2.png](https://s2.loli.net/2024/02/23/uGxBjkcWEdbom3N.png)

3. 解释器的处理
连接丢失，单片机断开或者连接不稳定时会出现bug，只需连好即可

![图3.png](https://s2.loli.net/2024/02/23/XykJjsQOLM7blEH.png)

4. wifi internal error wifi内部错误
解决方案：先关闭（false）再启动（true）wlan
除此也可能是wifi密码名称错误，wifi未启动或者wifi信号不稳定等问题导致

![图4.jpg](https://s2.loli.net/2024/02/23/RqHmvkYdj936oEt.jpg)

5. 粘包问题是指数据在传输时，在一条消息中读取到了另一条消息的部分数据，这种现象就叫做粘包。
解决方案：输入前加空子符，输出时对应空格分隔

![图5.jpg](https://s2.loli.net/2024/02/23/ovmOJZYyXQf2th3.jpg)

## **最终代码展示**

单片机：

```python
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
```
虚拟机：

![图6.jpg](https://s2.loli.net/2024/02/23/dWy5whKiSrXRuaO.jpg)


----
