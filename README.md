# **智能小车大作业（详述）**


---

## **前言及思路分析**

### 前言

这份思路分析起草于2024年1月19号，此时EH正在回家的动车上。

小车任务的主要的技术问题都解决了，写一下。

### 思路分析

此次作业的要求是：利用单片机，实现小车跑图并实时传递数据到linux平台上显示。

此次作业的主要材料有：车模，电机，舵机，光耦对射传感器，MPU6050三轴传感器，ESP32单片机

首先，得学习单片机的基础知识嘛，然后就是简单分析一下如何驱动电机和舵机，写出跑图程序。接着就是对那两个传感器的分析，结合自己的理解写出可操作的函数。接下来就是搭建一个linux平台，我这里使用的是虚拟机终端，在网络上冲浪一会儿，便可以找到方法解决信号传输的问题的方法。最后就是用多线程的方式综合一下代码。

我在探索的过程中发现几个比较大的问题：

1.小车不好跑图，图小车大，容错率低。这个放在创新想法里讲。

2.单片机的wifi连接成功率因手机而异。这个就得试了，放在通信里讲。

-----

## **ESP32基础知识**

### 什么是单片机

可以理解为没有可视化操作系统的电脑。信息处理能力不差的好吧。

单片机若要使用需烧录程序，用USB连电脑（指示灯会亮的）。

我使用micropython操作。

烧录micripython:（Port选端口，Firmware放入bin文件，官网上有）

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

|   26   |   27   | 表现 |
| :----: | :----: | :--: |
| 高电平 | 低电平 | 正转 |
| 低电平 | 高电平 | 反转 |
| 高电平 | 高电平 | 不转 |

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

1.单片机大概率不会出问题，但是可能连不上你的手机。这并不意味着这个单片机连不上任何手机，它也许可以连接上其他手机的热点。同理，你的手机也可能可以连接上其他单片机，原理不明，单事实存在。

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

### 粘包问题的解决

怎么说呢，间隔一段时间发数据嘛，就是虽然不会丢包，但是会使数据有时候堆起来一股脑地打印出来。比如，

```txt
run1s
run2s
run3srun4srun5s
run6s
```

这时候，可以对收发数据进行处理。比如，对发送的字符串末尾添加一个" "，然后，对收到的数据这么简单处理：

```python
a=new_s.recv(1024)
b=a.split()
for i in b:
    print(i)
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

## **一些创新的想法**

小车跑道很窄，车子自身又很宽，很容易出线或者压线。这需要非常精细的微调，除此之外还有更恶心的：前轮的活动空间太大了，导致起步容易走歪；电池的电压高低也会影响小车的行进速度和距离。

这些情况让我很难受。

我有两个想法：

一、遥控，但伪装成自动驾驶。

二、改造车，换成铰接结构，让车变小，增大容错。

![铰接.jpg](https://s2.loli.net/2024/01/20/yiTSh2J1c3aVnGj.jpg)

其他方面，我还有其他有意思的想法：

一、一边跑，一边播放《千本樱》

二、一边跑，一边用数码管显示数字

----

## **浅谈总结和感受**

这份大作业够有意思的。

EH，永不言败！
