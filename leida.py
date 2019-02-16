# -*- coding:UTF-8 -*-
import requests
import sys
import re
import math
import numpy
import serial
from time import sleep
import msvcrt

class DataProcess():

    def __init__(self):
        self.SaveFlag = False
        self.StartFlag = False
        self.CloseFlag = False
    def recv(self,serial):
        while True:
            data = serial.read_all()
            if data == '':
                continue
            else:
                break
        return data

    def get_data(self,data):
        Data_temp=data[4:]
        if Data_temp[0:2] == "00" and len(data)>100:#剔除非云图数据
            self.process(Data_temp)
        else:
            pass
    def process(self,list_data):
        num=int(list_data[2:4],16)
        step=4
        angle=[]
        distance=[]
        b = [list_data[i:i+step] for i in range(0,len(list_data),step)]
        angle.append(self.Rshiftbit(b[1]))#初始角
        distance.append(self.get_distance(b[4]))#初始距离
        if self.Rshiftbit(b[2])-angle[0]>0:
            diff=self.Rshiftbit(b[2])-angle[0]#角间距
        else:
            diff=self.Rshiftbit(b[2])-angle[0]+360
        for j in range(2,num):#其余角和其余距离
            angle_i=diff*(j-1)/(num-2)+angle[0]
            if angle_i>360:#特殊情况
                angle_i=angle_i-360
            else:
                pass
            try:
                angle.append(angle_i)
                distance.append(self.get_distance(b[4+j]))
            except IndexError:
                distance.append(self.get_distance('0000'))
        angle.append(self.Rshiftbit(b[2]))#终止角和终止距离
        distance.append(self.get_distance(b[-1]))
        angle=self.second_pro(angle,distance)#二次解析

    def writer(self,path,ang,dis):#写入TXT文件
        write_flag = True
        for i in range(0,len(ang)):
            with open(path,'a',encoding='utf-8') as f:
                f.writelines("angle:"+str(ang[i]))
                f.write('  ')
                f.writelines("distance:"+str(dis[i]))
                f.write('\n')
    def trans(self,data):#字节倒转
        data_temp1=data[0:2]
        data_temp2=data[2:4]
        data_temp=data_temp2+data_temp1
        return data_temp
    def get_distance(self,si):#计算距离
        si=self.trans(si)
        si=int(si,16)
        distance=si/4
        return distance
    def Rshiftbit(self,FSA):#计算角度
        FSA=self.trans(FSA)
        data=int(FSA,16)
        dt=data>>1    
        angle_f=dt/64
        return angle_f
    def second_pro(self,angle_f,Distance):#二级解析
        angle_finial=[]
        for i in range(0,len(angle_f)):
            if Distance[i]==0:
                angCorrect=0
            else:
                angCorrect=math.atan(21.8*(155.3-Distance[i])/(155.3*Distance[i]))
                angCorrect=math.degrees(angCorrect)
            angle_finial.append(angle_f[i]+angCorrect)
        if angle_finial[0]<20:
            self.StartFlag = True
            self.CloseFlag = False

        elif self.StartFlag == True and angle_finial[0] > 320:
            self.CloseFlag = True
            self.StartFlag =False

        if self.StartFlag == True and self.CloseFlag== False:
            print(angle_finial[0])
            self.writer('sss.txt',angle_finial,Distance)
        elif self.CloseFlag == True and self.StartFlag== False:
            print('`````````````````````````````\ns')
            print(angle_finial[0])
            self.SaveFlag = False
            self.CloseFlag = False
            self.StartFlag = False
            serial.write("\xA5\x65".encode("utf-8"))
            sys.exit(0)
if __name__=="__main__":
    serial = serial.Serial('COM5', 230400, timeout=0.1)  # /dev/ttyUSB0
    dp=DataProcess()
    if serial.isOpen():
        print("open success")
    else:
        print("open failed")

    while True:
        code = "\xA5\x60"
        serial.write(code.encode("utf-8"))
        sleep(0.1)
        while True:
            if msvcrt.kbhit() and msvcrt.getch().decode() == chr(113):##点击q，终止程序
                serial.write("\xA5\x65".encode("utf-8"))
                sys.exit(0)
            if msvcrt.kbhit() and msvcrt.getch().decode() == chr(115):##点击s，保存数据
                dp.SaveFlag = True
            data = dp.recv(serial)
            if data != b'':
                dp.get_data(data.hex())
    #dp=DataProcess()
    #dp.get_data()


