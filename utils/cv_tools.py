'''
Author: Xe-No
Date: 2023-05-17 21:45:43
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-06-27 17:36:19
Description: 一些cv工具

Copyright (c) 2023 by Xe-No, All Rights Reserved. 
'''

import os
import time
import win32api
import cv2 as cv
import numpy as np
import pygetwindow as gw

from PIL import ImageGrab, Image
from pynput.mouse import Controller as MouseController

from .log import log

def get_binary(img, threshold=200):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)
    return binary

def show_img(img, scale=1, title='Image'):
    # cv.namedWindow('image', cv.WINDOW_NORMAL)
    h, w = img.shape[:2]
    img = cv.resize( img ,(int(w*scale), int(h*scale))  )
    cv.imshow(title, img)
    cv.waitKey(0)  # 显示图像并等待1秒
    cv.destroyAllWindows()  

def show_imgs(imgs, title='Image'):
    cv.imshow(title, np.hstack(imgs))
    cv.waitKey(0)
    cv.destroyAllWindows()  

def get_loc(im, imt):
    result = cv.matchTemplate(im, imt, cv.TM_CCORR_NORMED)
    return cv.minMaxLoc(result)

def take_screenshot(rect, platform="PC", order="127.0.0.1:62001", adb_path="temp\\adb\\adb"):
    # 返回RGB图像
    if platform == "PC":
        window = gw.getWindowsWithTitle('崩坏：星穹铁道')[0]
        left, top, right, bottom = window.left, window.top, window.right, window.bottom
        #temp = pyautogui.screenshot(region=rect1)
        #print((rect[0],rect[1],rect[3],rect[2]))
        temp = ImageGrab.grab((rect[0]+left,rect[1]+top,rect[3]+left,rect[2]+top), all_screens=True)
    elif platform == "模拟器":
        os.system(f"{adb_path} -s {order} shell screencap -p /sdcard/Pictures/screencast.png")
        os.system(f"{adb_path} -s {order} pull /sdcard/Pictures/screencast.png")
        img_fp = Image.open("./screencast.png")
        left, top = img_fp.size
        temp = img_fp.crop((rect[0],rect[1],rect[3],rect[2]))
    screenshot = np.array(temp)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    #show_img(screenshot)
    return screenshot

def take_minimap(rect = [47,58,187,187]):
    return take_screenshot(rect)

def take_fine_screenshot(rect = [47,58,187,187], platform="PC", order="127.0.0.1:62001", adb_path="temp\\adb\\adb"):
    total = take_screenshot(rect, platform, order, adb_path)
    n = 5
    for i in range(n):
        if platform == "PC":
            win32api.mouse_event(1, 0, -200)  # 进行视角移动
        elif platform == "模拟器":
            os.system(f"{adb_path} -s {order} shell input swipe 636 359 636 184 50")
        mask = cv.compare(total, take_screenshot(rect, platform, order, adb_path), cv.CMP_EQ )
        total = cv.bitwise_and(total, mask )
        time.sleep(0.01)
    time.sleep(0.1)
    for i in range(n):
        if platform == "PC":
            win32api.mouse_event(1, 0, 200)  # 进行视角移动
        elif platform == "模拟器":
            os.system(f"{adb_path} -s {order} shell input swipe 636 362 636 495 50")
        mask = cv.compare(total, take_screenshot(rect, platform, order, adb_path), cv.CMP_EQ )
        total = cv.bitwise_and(total, mask )
        time.sleep(0.01)
    minimap = cv.bitwise_and(total, mask )
    return minimap

def get_mask(img, color_range):
    lower, upper = color_range
    return cv.inRange(img, lower, upper)

def get_camera_fan(color = [130, 130, 60],angle=0, w=187, h=187, delta=90):
    center = (w//2, h//2)
    radius = min(h, w)//2
    fan = np.zeros((h, w, 3), np.uint8)
    # 计算圆心位置
    cx, cy = w // 2, h // 2
    axes = (w // 2, h // 2) 
    
    startAngle, endAngle = angle -45, angle +45 # 画90度

    cv.ellipse(fan, (cx, cy), axes, 0, startAngle, endAngle, color , -1)
    return fan

def get_gradient_mask(w,h):
    center = [w // 2, h // 2]
    radius = 0.8 *w
    # 创建渐变掩码
    gradient_mask = np.zeros((w, h), dtype=np.uint8)
    for r in range(gradient_mask.shape[0]):
        for c in range(gradient_mask.shape[1]):
            dist = np.sqrt((r-center[1])**2 + (c-center[0])**2)
            value =  max(0, min(1 - 2*dist/radius, 1))
            gradient_mask[r,c] = int(value * 255)
    return gradient_mask


def filter_contours_surround_point(gray, point):
    """过滤掉不包围指定点的轮廓"""
    contours, hierarchy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    # 过滤掉所有不包含指定点的轮廓
    filtered_contours = []
    for i in range(len(contours)):
        if cv.pointPolygonTest(contours[i], point, False) < 0:
            filtered_contours.append(contours[i])
            
    # 过滤掉所有不包围指定点的轮廓
    surrounded_contours = []
    for i in range(len(filtered_contours)):
        rect = cv.boundingRect(filtered_contours[i])
        if rect[0] <= point[0] <= rect[0] + rect[2] and \
           rect[1] <= point[1] <= rect[1] + rect[3]:
            surrounded_contours.append(filtered_contours[i])
            
    return surrounded_contours

def get_furthest_point(points):
	# 计算中心点坐标
	center = np.mean(points, axis=0)
	# 初始化最大距离为 0，最远点为第一个点
	max_distance = 0
	furthest_point = points[0]
	# 枚举每个点
	for point in points:
		# 计算该点到中心点的距离
		distance = np.linalg.norm(point - center)
		# 如果该点到中心点的距离大于当前最大距离，则更新最大距离和最远点
		if distance > max_distance:
			max_distance = distance
			furthest_point = point
	return furthest_point

def match_scaled(img, template, scale, mask=False):
    # 返回最大相似度，中心点x、y
    t0 = time.time()
    # finish = cv.imread(".imgs/finish_fighting.jpg")
    # while True:
    #     result = calculated.scan_screenshot(finish,pos=(0,95,100,100))
    #     if result["max_val"] > 0.98:
    #         print("未进入战斗")                       
    #         break

    resized_template = cv.resize(template, (0,0), fx=scale, fy=scale)
    if mask ==False:
        res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED)
    else:
        res = cv.matchTemplate(img, resized_template, cv.TM_CCORR_NORMED, mask=resized_template)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    h, w = resized_template.shape[:2]
    x, y = max_loc[0] + w/2, max_loc[1] + h/2
    return max_val, (int(x), int(y))

def find_best_match(img, template, scale_range=(140, 170, 1)):
    """
    说明:
        缩放图片并与进行模板匹配
    参数:
        :param img: 图片
        :param img: 匹配的模板
        :param img: 缩放区间以及步长
    返回:
        最佳缩放大小, 最大匹配度, 最近位置, 模板缩放后的长度, 模板缩放后的宽度
    """
    best_match = None
    max_corr = 0
    length = 0
    width = 0
    
    for scale_percent in range(scale_range[0], scale_range[1],scale_range[2]):
        
        # width = int(template.shape[1] * scale_percent / 100)
        # height = int(template.shape[0] * scale_percent / 100)
        # dim = (width, height)
        # resized_template = cv.resize(template, dim, interpolation=cv.INTER_AREA)
        resized_template = cv.resize(template, (0,0), fx=scale_percent/100.0, fy=scale_percent/100.0)

        res = cv.matchTemplate(img, resized_template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        log.debug(f'正在匹配 {scale_percent}，相似度{max_loc}')
        if max_val > max_corr:
            length, width, __ = resized_template.shape
            length = int(length)
            width = int(width)
            max_corr = max_val

    return scale_percent, max_corr, max_loc, length, width

def get_angle(debug=False, use_sample_image=False):
	x,y = [117,128]
	w,h = [47,47]

	if use_sample_image:
		# 任意一张截图即可，最重要的是保留左上部分
		img = cv.imread('temp/sample.png')[y:y+h, x:x+w]
	else:
		img = np.array(ImageGrab.grab())[y:y+h, x:x+w] 
		img = cv.cvtColor(img, cv.COLOR_RGB2BGR) # pyautogui截取的图为RGB
	img0 = img.copy()
	hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
	
	# 定义青色掩膜
	lower_cyan = np.array([78, 200, 200]) # 使用较高饱和度下界，过滤掉摄像头圆弧
	upper_cyan = np.array([99, 255, 255])
	cyan_mask = cv.inRange(hsv, lower_cyan, upper_cyan)

	# 查找轮廓
	contours, hierarchy = cv.findContours(cyan_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

	# 暴力断定只有一个青色箭头，获取箭头顶点
	if len(contours) != 1:
		return False
	contour = contours[0]
	peri = cv.arcLength(contour, True)
	approx = cv.approxPolyDP(contour, 0.03 * peri, True)
	fp = get_furthest_point(approx[:,0,:])


	# 获取角度
	fx, fy = fp
	dx = fx - w // 2
	dy = fy - h // 2
	angle = np.degrees(np.arctan2(dy, dx))
	angle = np.around(angle, 2)	

	print(angle)
	if debug:
		# 画出原图、二值掩膜图以及轮廓图
		cv.polylines(img, [approx], True, (0, 0, 255), thickness=2)
		cv.circle(img, fp, 0, (255,255,255),9)
		cv.imshow("result", np.hstack((img0,hsv,img)))
		cv.waitKey(0)
		cv.destroyAllWindows()

	return angle

