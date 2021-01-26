import cv2
import numpy as np
import utlis
import urllib.request 
import paho.mqtt.client as mqtt
import time

curveList = []
avgVal=10
 
def getLaneCurve(img,display=2):
 
    imgCopy = img.copy()
    imgResult = img.copy()
    #### STEP 1
    imgThres = utlis.thresholding(img)
 
    #### STEP 2
    hT, wT, c = img.shape
    points = utlis.valTrackbars()
    imgWarp = utlis.warpImg(imgThres,points,wT,hT)
    imgWarpPoints = utlis.drawPoints(imgCopy,points)
 
    #### STEP 3
    middlePoint,imgHist = utlis.getHistogram(imgWarp,display=True,minPer=0.5,region=4)
    curveAveragePoint, imgHist = utlis.getHistogram(imgWarp, display=True, minPer=0.9)
    curveRaw = curveAveragePoint - middlePoint
 
    #### SETP 4
    curveList.append(curveRaw)
    if len(curveList)>avgVal:
        curveList.pop(0)
    curve = int(sum(curveList)/len(curveList))
 
    #### STEP 5
    if display != 0:
        imgInvWarp = utlis.warpImg(imgWarp, points, wT, hT, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0:hT // 3, 0:wT] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 0, 255, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
        imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
        midY = 450
        cv2.putText(imgResult, str(curve), (wT // 2 - 80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
        cv2.line(imgResult, (wT // 2, midY), (wT // 2 + (curve * 3), midY), (255, 0, 255), 5)
        cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY - 25), (wT // 2 + (curve * 3), midY + 25), (0, 255, 0), 5)
        for x in range(-30, 30):
            w = wT // 20
            cv2.line(imgResult, (w * x + int(curve // 50), midY - 10),
                     (w * x + int(curve // 50), midY + 10), (0, 0, 255), 2)
        #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
        #cv2.putText(imgResult, 'FPS ' + str(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (230, 50, 50), 3);
    if display == 2:
        imgStacked = utlis.stackImages(0.7, ([img, imgWarpPoints, imgWarp],
                                             [imgHist, imgLaneColor, imgResult]))
        cv2.imshow('ImageStack', imgStacked)
    elif display == 1:
        cv2.imshow('Resutlt', imgResult)
 
    #### NORMALIZATION
    curve = curve/100
    if curve>1: curve ==1
    if curve<-1:curve == -1
 
    return curve
 
def on_connect(client, userdata, rc):
    if rc == 0:
        print("Connected successfully.")
    else:
        print("Connection failed. rc= "+str(rc))

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribe with mid "+str(mid)+" received.")

def on_message(client, userdata, msg):
    print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)


if __name__ == '__main__':
    url = 'http://192.168.1.2/cam-hi.jpg'
    winName = 'Cam'
    cv2.namedWindow(winName,cv2.WINDOW_AUTOSIZE)

    host = "broker host"
    user = "username"
    pw = "password"
    client = mqtt.Client("ClientID")
    print("Connecting...........")
    client.username_pw_set(user, pw)
    client.connect(host, 1883)
    print("connected")

    intialTrackBarVals = [117, 80, 70, 137]
    utlis.initializeTrackbars(intialTrackBarVals)
    while True:
        imgResponse = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResponse.read()),dtype = np.uint8)
        img = cv2.imdecode(imgNp, -1)
        img = cv2.resize(img,(480,240))
        cv2.imshow("src", img)
        curve = getLaneCurve(img,display=2)
        #print(curve)
        c = curve * 100
        print(c)
        if c < -20:
            client.publish("topic subscribe", "R")
            time.sleep(0.5)
            client.publish("topic subscribe", "S")
        if -20 <= c <= 20:
            client.publish("topic subscribe", "F")
            client.publish("topic subscribe", "S")
        if c > 20:
            client.publish("topic subscribe", "L")
            time.sleep(0.5)
            client.publish("topic subscribe", "S")
        #cv2.imshow('Vid',img)
        cv2.waitKey(500)
    cv.destroyAllWindows()