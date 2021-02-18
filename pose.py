import cv2
import os
import pandas as pd
import numpy as np

print(os.getcwd())

#os.chdir('./../../openpose')

# fashion_pose.py : MPII를 사용한 신체부위 검출
import cv2

# MPII에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
BODY_PARTS = {"Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
              "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
              "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
              "Background": 15}

POSE_PAIRS = [["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
              ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
              ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
              ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"]]

# 각 파일 path
protoFile = "./data/pose_deploy_linevec_faster_4_stages.prototxt"
weightsFile = "./data/pose_iter_160000.caffemodel"

# 위의 path에 있는 network 불러오기
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

# 이미지 읽어오기
image = cv2.imread("./data/original_pose.jpg")

# frame.shape = 불러온 이미지에서 height, width, color 받아옴
imageHeight, imageWidth, _ = image.shape

# network에 넣기위해 전처리
inpBlob = cv2.dnn.blobFromImage(image, 1.0 / 255, (imageWidth, imageHeight), (0, 0, 0), swapRB=False, crop=False)

# network에 넣어주기
net.setInput(inpBlob)

# 결과 받아오기
output = net.forward()

# output.shape[0] = 이미지 ID, [1] = 출력 맵의 높이, [2] = 너비
H = output.shape[2]
W = output.shape[3]
print("이미지 ID : ", len(output[0]), ", H : ", output.shape[2], ", W : ", output.shape[3])  # 이미지 ID

# 키포인트 검출시 이미지에 그려줌
points = []
for i in range(0, 15):
    # 해당 신체부위 신뢰도 얻음.
    probMap = output[0, i, :, :]

    # global 최대값 찾기
    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

    # 원래 이미지에 맞게 점 위치 변경
    x = (imageWidth * point[0]) / W
    y = (imageHeight * point[1]) / H

    # 키포인트 검출한 결과가 0.1보다 크면(검출한곳이 위 BODY_PARTS랑 맞는 부위면) points에 추가, 검출했는데 부위가 없으면 None으로
    if prob > 0.1:
        print("i = ", i, "x = ", int(x), "y = ", int(y))
        cv2.circle(image, (int(x), int(y)), 3, (0, 255, 255), thickness=-1,
                   lineType=cv2.FILLED)  # circle(그릴곳, 원의 중심, 반지름, 색)
        cv2.putText(image, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                    lineType=cv2.LINE_AA)
        points.append((int(x), int(y)))
    else:
        print(i)
        points.append(None)

cv2.imshow("Output-Keypoints", image)
cv2.waitKey(0)

# 이미지 복사
imageCopy = image

# 각 POSE_PAIRS별로 선 그어줌 (머리 - 목, 목 - 왼쪽어깨, ...)
n = 1
for pair in POSE_PAIRS:
    partA = pair[0]  # Head
    partA = BODY_PARTS[partA]  # 0
    partB = pair[1]  # Neck
    partB = BODY_PARTS[partB]  # 1

    # print(partA," 와 ", partB, " 연결\n")
    if points[partA] and points[partB]:
        cv2.line(imageCopy, points[partA], points[partB], (0, 255, 0), 2)

print(points)
print(type(points))
print(points[1])

dict = {}

a=0
for key in BODY_PARTS:
    if key == "Background":
        break
    dict[key] = points[a]
    a+=1
print(dict)

dict = pd.DataFrame(dict)
dict.to_excel(excel_writer='./data/excel.xlsx')


cv2.imshow("Output-Keypoints", imageCopy)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite('./data/example.jpg',imageCopy)

#2-4 오른쪽 어깨 - 오른쪽 손목
inc_2_4 = (dict['RShoulder'][1] - dict['RWrist'][1]) / (dict['RShoulder'][0] - dict['RWrist'][0])
inc_2_4_r = np.round(inc_2_4,5)
print('오른쪽 팔 기울기 = ', inc_2_4)
print('(반올림)오른쪽 팔 기울기 = ', inc_2_4_r)

#5-7 왼쪽 어깨 - 왼쪽 손목
inc_5_7 = (dict['LShoulder'][1] - dict['LWrist'][1]) / (dict['LShoulder'][0] - dict['LWrist'][0])
inc_5_7_r = np.round(inc_5_7, 5)
print('왼쪽 팔 기울기 = ', inc_5_7)
print('(반올림)왼쪽 팔 기울기 = ', inc_5_7_r)

#8-10 오른쪽 엉덩이 오른쪽 무릎
inc_8_10 = (dict['RHip'][1] - dict['RKnee'][1]) / (dict['RHip'][0] - dict['RKnee'][0])
inc_8_10_r = np.round(inc_8_10,5)
print('오른쪽 다리 기울기 = ', inc_8_10)
print('(반올림)오른쪽 다리 기울기 = ', inc_8_10_r)

#11-12 왼쪽 엉덩이 왼쪽 무릎
inc_11_12 = (dict['LHip'][1] - dict['LKnee'][1]) / (dict['LHip'][0] - dict['LKnee'][0])
inc_11_12_r = np.round(inc_11_12,5)
print('왼쪽 다리 기울기 = ', inc_11_12)
print('(반올림)왼쪽 다리 기울기 = ', inc_11_12_r)

inc = {}

inc['RS_RW'] = inc_2_4_r
inc['LS_LW'] = inc_5_7_r
inc['RH_RK'] = inc_8_10_r
inc['Lh_LK'] = inc_11_12_r

print(inc)

inc = pd.DataFrame(inc, index=[0])
inc.to_excel(excel_writer='./data/original.xlsx')

#기울기가 음수일 때 값이 작을수록 -> 기울기가 가파름 / 값이 클수록 -> 기울기가 완만함
#기울기가 양수일 때 값이 클수록 -> 기울기가 가파름 / 값이 작을수록 -> 기울기가 완만함

#기울기 음수
if inc_2_4_r > user_2_4 : #사용자 기울기가 작다면(절대값이 크다면) 팔을 더 올려주세요

if inc_2_4_r < user_2_4 : #사용자 기울기가 크다면(절대값이 작다면) 팔을 더 내려주세요

if inc_2_4 == user_2_4 : #사용자 기울기가 같다면 아무말 안함

if inc_5_7 > user_5_7 : #사용자 기울기가 작다면(절대값이 크다면) 팔을 더 올려주세요

if inc_5_7 > user_5_7 : #사용자 기울기가 크다면(절대값이 작다면) 팔을 더 내려주세요

if inc_5_7 == user_5_7 : #사용자 기울기가 같다면 아무말 안함

if inc_8_10 > user_8_10 : #사용자 기울기가 작다면(절대값이 크다면) 팔을 더 올려주세요

if inc_8_10 < user_8_10 : #사용자 기울기가 크다면(절대값이 작다면) 팔을 더 내려주세요

if inc_8_10 == user_8_10 : #사용자 기울기가 같다면 아무말 안함

#기울기 양수
if inc_11_12 > user_11_12 : #사용자 기울기가 작다면  굳이 할 필요가 잇을까? 더 앉으면 좋은거 아님?

if inc_11_12 < user_11_12 : #사용자 기울기가 크다면(사용자가 더 앉아야 함) 더 앉아주세요

if inc_11_12 == user_11_12 : #사용자 기울기가 같다면 아무말 안함




'''
#MPII에서 각 파트 번호, 선으로 연결된 POSE_PAIRS
BODY_PARTS = {"Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
              "LShoulder": 5, "LElbow": 6, "LWrist":7, "RHip": 8, "RKnee": 9,
              "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
              "Background": 15}

POSE_PAIRS = [ ["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
               ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
               ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"]]


#각 파일 path
protoFile = "./pose_deploy_linevec_faster_4_stages.prototxt"
weightsFile = "./pose_iter_160000.caffemodel"

#위의 path에 있는 network 불러오기
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

#이미지 읽어오기
image = cv2.imread("./37.jpg")

#이미지의 height, width, color 받기
imageHeight, imageWidth, _ = image.shape

#network에 넣기 위해 전처리
inpBlob = cv2.dnn.blobFromImage(image, 1.0/255, (imageWidth,imageHeight),(0, 0, 0), swapRB=False, crop=False)

#network에 넣어주기
net.setInput(inpBlob)

#결과 받아오기
output = net.forward()

#output.shape[0] = 이미지 ID, [1] = 출력 맵의 높이, [2] = 너비
H = output.shape[2]
W = output.shape[3]
print("이미지 ID: ", len(output[0]), ", H : ", output.shape[2], ",W : ", output.shape[3])

#키포인트 검출시 이미지에 그려줌
points = []

for i in range(0,15):
    #해당 신체부위 신뢰도 얻음
    probMap = output[0, i, :, :]

    #global 최대값 찾기
    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

    x = (imageWidth * point[0]) / W
    y = (imageHeight * point[1]) / H

    #키포인트 검출한 결과가 0.1보다 크면(검출한 곳이 위 BODY_PARTS랑 맞는 부위면) points 추가, 검출했는데 부위가 없으면 None으로
    if prob > 0.1:
        cv2.circle(image, (int(x), int(y)), 3, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
        cv2.putText(image, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv2.LINE_AA)
        points.append((int(x), int(y)))
    else:
        points.append(None)

cv2.imshow("Output-KeyPoints", image)
cv2.waitKey(0)

imageCopy = image

for pair in POSE_PAIRS:
    partA = pair[0]  #HEAD
    partA = BODY_PARTS[partA] #0
    partB = pair[1]
    parrB = BODY_PARTS[partB] #1

    if points[partA] and points[partB]:
        cv2.line(imageCopy, points[partA], points[partB], (0, 255, 0),2)

cv2.imshow("Output-Keypoints", imageCopy)
cv2.waitKey(0)
cv2.destroyAllWindows()'''

