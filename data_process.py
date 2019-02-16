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
        self.data=[]
    def get_data(self):
        with open('serial.log','r+',encoding='utf-8') as f:
            line=f.read()
        try:
            line = line.replace('\n','')#除去换行
        except IndexError:
            pass
        self.data=line.split('aa55')
        Data_temp=self.data
        for i in range(len(Data_temp)):#剔除非云图数据
            if Data_temp[i][0:2] == "00":
                self.process(Data_temp[i])
            else:
                continue
    def process(self,list_data):
        num=int(list_data[2:4],16)
        step=4
        angle=[]
        distance=[]
        b = [list_data[i:i+step] for i in range(0,len(list_data),step)]
        angle.append(self.Rshiftbit(b[1]))#初始角
        distance.append(self.get_distance(b[4]))#初始距离
        diff=self.Rshiftbit(b[2])-angle[0]#角间距
        for j in range(2,num):#其余角和其余距离
            angle.append(diff*(j-1)/(num-2)+angle[0])
            distance.append(self.get_distance(b[4+j]))
        angle.append(self.Rshiftbit(b[2]))#终止角和终止距离
        distance.append(self.get_distance(b[-1]))
        angle=self.second_pro(angle,distance)
    def writer(self,path,ang,dis):#写入TXT文件
        write_flag = True
        with open(path,'a',encoding='utf-8') as f:
            f.writelines("angle:"+str(ang))
            f.write('  ')
            f.writelines("distance:"+str(dis))
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
            self.writer('sss.txt',angle_finial[i],Distance[i])

if __name__=="__main__":

    dp=DataProcess()
    dp.get_data()


