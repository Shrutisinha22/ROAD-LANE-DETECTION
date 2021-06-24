import cv2
import numpy as np

def canny(image):
    grayImage = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurImage = cv2.GaussianBlur(grayImage,(5,5),0)
    cannyImage = cv2.Canny(blurImage,50, 100)
    return cannyImage

def areaOfInterest(image):
    height = image.shape[0]
    polygons = np.array([[(200, height), (1100,height), (550, 250)]])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    maskedImage = cv2.bitwise_and(image, mask)
    return maskedImage

def displayLine(image, lines):
    lineImage = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line
            cv2.line(lineimg, (x1,y1), (x2,y2), (0,0,255), 10)
        # Below: Coloring the lane using polygon.
        if lines.shape == (2,4):
            
            polygon2 = np.array([[(lines[0,0]+10, lines[0,1]), (lines[0,2]+5,lines[0,3]), (lines[1,2]-5, lines[1,3]), (lines[1,0]-10,lines[1,1])]])
            cv2.fillPoly(lineImage, polygon2, (50,255,0))
    return lineImage

def status(image, lines):
    if averagedLines is not None:
        if averagedLines.shape == (2,4):
            cv2.rectangle(image,(480,510),(760,580),(50,200,0),-6)
            cv2.putText(image,"Lane Visibility Good", (500,550),cv2.FONT_HERSHEY_PLAIN,1.5,(0,0,255),2)
            
        else:
            cv2.rectangle(image,(480,510),(760,580),(5,0,180),-6)
            cv2.putText(image,"Low Lane Visibility", (500,550),cv2.FONT_HERSHEY_PLAIN,1.5,(0,255,255),2)
    return image
    
def averageSlopeIntercept(image, lines):
    leftFit = []
    rightFit = []
    l=0
    r=0
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1,y2), 1)
        slope = parameters[0]
        intercept = parameters[1 ]
        if slope < 0:
            leftFit.append((slope, intercept))
        else:
            rightFit.append((slope, intercept))
    if len(leftFit) > 0:
        leftFitAverage = np.average(leftFit, axis = 0)
        leftLine = makeCoordinates(image, leftFitAverage)
        l=1
    if len(rightFit) > 0:
        rightFitAverage = np.average(rightFit, axis = 0)
        rightLine = makeCoordinates(image, rightFitAverage)
        r=1
    
    if l==1 and r==1:
        return np.array([leftLine, rightLine])
    elif l==0 and r==1:
        return np.array([rightLine])
    elif l==1 and r==0:
        return np.array([lefttLine])
    
    
def makeCoordinates(image, lineParameters):
    slope, intercept = lineParameters
    y1 = image.shape[0]
    y2 = int(y1*(3/6))
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return np.array([x1, y1, x2, y2])

cap = cv2.VideoCapture("road.mp4") # <- The Video that we will use

while{cap.isOpened()}:
    _, frame = cap.read()
    cannyImage = canny(frame)
    croppedArea = areaOfInterest(cannyImage)

    lines = cv2.HoughLinesP(croppedArea,2, np.pi/180, 100, np.array([]), minLineLength = 40, maxLineGap = 5)
    averagedLines = averageSlopeIntercept(frame, lines)
    lineImage = displayLine(frame, averagedLines)

    displayImage = cv2.addWeighted(frame, 1, lineImage, 0.3, 1)
    status(displayImage, averagedlines)

    cv2.imshow("results", displayImage)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
