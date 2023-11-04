import numpy as np
import cv2
from PIL import Image,ImageFile
import socket
import requests
import time
import io

ImageFile.LOAD_TRUNCATED_IMAGES = True
CHUNK_LENGTH = 200
#CHUNK_LENGTH = 1460

ipESP32 = '192.168.43.184'
ipPC = '192.168.43.96'

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.bind((ipPC, 8000))



fps = 0
img_bytes = b''
lenData = 0
while True:
    data, IP = s.recvfrom(10000)
    data_size = len(data)
    if data_size == CHUNK_LENGTH and data[0] == 255 and data[1] == 216 and data[2] == 255 : # FF D8 FF        
        img_bytes = b''

    img_bytes = img_bytes + data
    lenData = lenData + data_size
    
    if data_size != CHUNK_LENGTH and data[data_size - 2] == 255 and data[data_size - 1] == 217 : # FF D9
        lenKirim = int.from_bytes(bytes([data[data_size - 4],data[data_size - 3]]), "big")
        #print(lenKirim,' ',lenData)
        if lenKirim == lenData:
            start = time.time()
            byteImgIO = io.BytesIO()
            byteImgIO.write(img_bytes)
            image = Image.open(byteImgIO)
            frame = cv2.cvtColor(np.asarray(image),cv2.COLOR_BGR2RGB)
            image = cv2.flip(frame,1)



            gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
            ret, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            contours = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            for cnt in contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    if 40000> w*h > 30000:                    
                        print((w*h))
                        # make a rectangle box around each curve
                        

                        peri = cv2.arcLength(cnt,True)
                        approx = cv2.approxPolyDP(cnt, 0.01* peri, True)
                        x = approx.ravel()[0]
                        y = approx.ravel()[1] - 5


                        if len(approx) < 11:
                            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 1)                            
                            cv2.drawContours(image, cnt, -1, (255, 0, 255), 7)    


                        if len(approx) == 3:
                            cv2.putText( image, "Triangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                            requests.get('http://'+ipESP32+':8080/?data=triangle')
                        elif len(approx) == 4 :
                            x, y , w, h = cv2.boundingRect(approx)
                            aspectRatio = float(w)/h
                            #print(aspectRatio)
                            if aspectRatio >= 0.95 and aspectRatio < 1.4:
                                cv2.putText(image, "square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                                requests.get('http://'+ipESP32+':8080/?data=square')
                            else:
                                cv2.putText(image, "rectangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                                requests.get('http://'+ipESP32+':8080/?data=rectangle')

                        elif len(approx) == 5 :
                            cv2.putText(image, "pentagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                            requests.get('http://'+ipESP32+':8080/?data=pentagon')
                        elif len(approx) == 6 :
                            cv2.putText(image, "hexagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                            requests.get('http://'+ipESP32+':8080/?data=hexagon')
                        elif len(approx) == 7 :
                            cv2.putText(image, "heptagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                            requests.get('http://'+ipESP32+':8080/?data=heptagon')
                        elif len(approx) == 8 :
                            cv2.putText(image, "octagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                            requests.get('http://'+ipESP32+':8080/?data=octagon')
                        elif len(approx) == 10 :
                            cv2.putText(image, "star", (x, y-5), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                            requests.get('http://'+ipESP32+':8080/?data=star')
                        #else:
                        #    cv2.putText(imgContour, "circle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))




            end = time.time()
            totalTime = end - start
            if totalTime != 0 :
                fps = 1 / totalTime
            cv2.putText(image, f'FPS: {int(fps)}', (20,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,0,255), 2)
            cv2.imshow("Image", image)
        lenData = 0
        if cv2.waitKey(1) == ord('q'):
            break
cv2.destroyAllWindows()



'''
webcam = cv2.VideoCapture()
webcam.open(1,cv2.CAP_DSHOW)
while True:
    status , image = webcam.read()
        
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    ret, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # make a rectangle box around each curve
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 1)
            
            cv2.drawContours(image, cnt, -1, (255, 0, 255), 7)    

            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt, 0.01* peri, True)
            x = approx.ravel()[0]
            y = approx.ravel()[1] - 5
            if len(approx) == 3:
                cv2.putText( image, "Triangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
            elif len(approx) == 4 :
                x, y , w, h = cv2.boundingRect(approx)
                aspectRatio = float(w)/h
                #print(aspectRatio)
                if aspectRatio >= 0.95 and aspectRatio < 1.4:
                    cv2.putText(image, "square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
                else:
                    cv2.putText(image, "rectangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)

            elif len(approx) == 5 :
                cv2.putText(image, "pentagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
            elif len(approx) == 6 :
                cv2.putText(image, "hexagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
            elif len(approx) == 7 :
                cv2.putText(image, "heptagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
            elif len(approx) == 8 :
                cv2.putText(image, "octagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
            elif len(approx) == 10 :
                cv2.putText(image, "star", (x, y-5), cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0),2)
            #else:
            #    cv2.putText(imgContour, "circle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))

    
    cv2.imshow("image", image)
    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()
webcam.release()
'''