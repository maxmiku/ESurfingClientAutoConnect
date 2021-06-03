#coding=utf-8


#qt 截图
import win32gui, win32con, win32process, cv2, time
import numpy, psutil


# #获取所有窗口的句柄

# hwnd_title = dict()
# def get_all_hwnd(hwnd,mouse):
#   if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
#     hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})

# win32gui.EnumWindows(get_all_hwnd, 0)
 
# for h,t in hwnd_title.items()
#   if t is not "":
#     print(h, t)


# 检查窗口是否最小化，如果是最大化
def showWindow(hwnd):


    #下方两句显示最小化窗口并前置窗口
    win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    win32gui.SetForegroundWindow(hwnd)

    # win32gui.ShowWindow(hwnd, 1)
    time.sleep(0.5)
    # if(win32gui.IsIconic(hwnd)):
    # #   win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    #     win32gui.ShowWindow(hwnd, 1)
    #     time.sleep(0.5)


#QT5 全屏截图部分
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import win32gui
import sys



nowStage = 6 #当前状态 详细见下表
preStage_1 = 6 #上次检测的状态 防止某次的识别失灵
preSatge_2 = 6
stageTexts=["有错误信息","待登录","错误","加载中","正在断开连接","在线","初始化中","无法匹配"]
stageThreshold={3:2e-11}

windows_pot = (0,0)
 

def main():
    global preStage_1
    global preStage_2
    global nowStage
    while 1:
        # input("请单击回车进行状态监测...")
        findFixToolsWindows()
        captureScreen()
        cutScreenShotFitPrgm()
        tmp, result = whichStage()



        if(tmp==preStage_1 and tmp==preStage_2 and tmp!=nowStage):
        	nowStage = tmp

        preStage_2 = preStage_1
        preStage_1 = tmp

        if(tmp==1):
            matchLogin()
        elif(tmp==5):
            matchDisconnectButton()

        acc = "N/A"
        if(result!=None):
            acc = result[2]

        print("当前状态为:"+getStageText(nowStage)+" 当前检测到的状态为:"+getStageText(tmp)+str(tmp)+" 精度:"+str(acc))

        time.sleep(0.5)










#win32gui.FindWindow(类名,标题或路径)
hwnd = win32gui.FindWindow(None, '校园客户端')

client_pid = win32process.GetWindowThreadProcessId(hwnd)

if(hwnd==0):
    print("校园客户端程序没有启动, 请检查程序是否启动?")
    exit()

# showWindow(hwnd)
app = QApplication(sys.argv)
screen = QApplication.primaryScreen()
global img
def captureScreen():
    global img
    img = screen.grabWindow(QApplication.desktop().winId()).toImage()
    img.save("screenshot.jpg")



# #设置窗口位置
# def reset_window_pos(targetTitle): 
#  hWndList = [] 
#  win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList) 
#  for hwnd in hWndList:
#   clsname = win32gui.GetClassName(hwnd)
#   title = win32gui.GetWindowText(hwnd)
#   if (title.find(targetTitle) >= 0): #调整目标窗口到坐标(600,300),大小设置为(600,600)
#    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,330,559, win32con.SWP_SHOWWINDOW)#设置窗口位置
    
# reset_window_pos("校园客户端")


#获取窗口大小 (不包括边框)  
#返回: (1503, 223, 1833, 782)  元组 (x0,y0,x1,y1)
def get_window_rect(targetTitle): 
 hWndList = [] 
 win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList) 
 for hwnd in hWndList:
  clsname = win32gui.GetClassName(hwnd)
  title = win32gui.GetWindowText(hwnd)
  if (title.find(targetTitle) >= 0):
    return win32gui.GetWindowRect(hwnd)

   # win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,,, win32con.SWP_SHOWWINDOW)#设置窗口位置
    

global cropped


# 裁剪图片获得程序截图
def cutScreenShotFitPrgm():
    global cropped
    img = cv2.imread("screenshot.jpg")

    pot=get_window_rect("校园客户端")

    print("截图左上角坐标:"+str(pot[0])+","+str(pot[1]))

    cropped = img[pot[1]:pot[3],pot[0]:pot[2]]#img[y0:y1,x0:x1]

    cv2.imwrite("screenshot_crop.jpg", cropped)



# 利用opencv 判断A在B中的位置

# 参数说明
# target：cv2.imread(“图片B”)
# template：cv2.imread(“图片A”)
def find_picture(target,template,displayWindow=True):

    #获得模板图片的高宽尺寸
    theight, twidth = template.shape[:2]
    #执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(target,template,cv2.TM_SQDIFF_NORMED)
    #归一化处理m,             
    cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )
    #寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #匹配值转换为字符串
    #对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
    #对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
    strmin_val = str(min_val)
    #绘制矩形边框，将匹配区域标注出来
    #min_loc：矩形定点
    #(min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    #(0,0,225)：矩形的边框颜色；2：矩形边框宽度
    cv2.rectangle(target,min_loc,(min_loc[0]+twidth,min_loc[1]+theight),(0,0,225),2)
    #显示结果,并将匹配值显示在标题栏上

    x=min_loc[0]
    y=min_loc[1]
    x1=min_loc[0]+twidth
    y1=min_loc[1]+theight

    if(displayWindow):
        if(isTrustResult((x,y,min_val,x1,y1))):
            cv2.imshow("MatchResult----MatchingValue="+strmin_val,target)
            cv2.waitKey()
            cv2.destroyAllWindows()
    #x,y max_val 匹配度
    return x,y,min_val,x1,y1


# 是否有红色的玩意
# src cv2.imread("D:\\myCode\\picture\\cards.png")
# Return  bool 
def hasRedColor(src):
    # cv2.namedWindow("input", cv2.WINDOW_AUTOSIZE)
    # cv2.imshow("input", src)
    """
    提取图中的红色部分
    """
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    low_hsv = numpy.array([0,43,46])
    high_hsv = numpy.array([10,255,255])
    mask = cv2.inRange(hsv,lowerb=low_hsv,upperb=high_hsv)

    redBlocks = 0
    for i in mask:
        for i1 in i:
            if(i1==255):
                redBlocks=redBlocks+1
    if(redBlocks>10):
        return True
    else:
        return False

#传入匹配结果 判断是否可信
def isTrustResult(matchResult):
    #当结果的相似度绝对值小于 1e-10 可以视为可信的结果
    if(matchResult[2]==0):
    	return False
    # if(abs(matchResult[2])<5e-11):
    if(abs(matchResult[2])<5e-11):
        # print("可信的结果")
        return True
    else:
        # print("不可信的结果")
        return False


#阈值可能不确定 要确定颜色,可能需要对比两种的相似度



def getStageText(index):
    global stageTexts
    if(index==None):
        return "未知状态"
    print ("当前状态的状态"+str(index))
    return stageTexts[index]

#判断程序处于什么状态
def whichStage():
    allStage = [matchNoticBar,matchLoginNotic,matchWarning,matchLoading,matchDisconnecting,matchOnline]

    matchResult=None
    matchIndex=-1
    for i in range(0,len(allStage)):
        rs, result = allStage[i]()
        if(rs):
          # print("界面索引"+str(i)+" True")
            
            matchResult=result
            matchIndex=i
            break
        else:
            pass
            # print("界面索引"+str(i)+" False")
    return matchIndex, matchResult
    # if(matchResult==None):
    #     print("程序未知状态,无法匹配状态")
    # else:
    #     print("目标位于 准确度:"+str(matchResult)+" 当前状态为:"+getStageText(matchIndex))



def findFixToolsWindows():
	fhwnd = win32gui.FindWindow(None, '自助排障工具')
	if(fhwnd!=0):
		print ("发现自助排障工具窗口, 窗口句柄:"+str(fhwnd))
		_,PID = win32process.GetWindowThreadProcessId(fhwnd)
		p = psutil.Process(PID)
		p.terminate()
		print ("已经向排障工具发送结束进程指令")
		time.sleep(1)
	# else:
	# 	print("找不到自助排障工具")









def matchOnline():
    #cropped = cv2.imread("screenshot_crop.jpg")
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/disconnect.jpg"))#判断断开连接的按钮是否存在
    disconnJpg = cropped[matchResult[1]:matchResult[4],matchResult[0]:matchResult[3]]
    return isTrustResult(matchResult) and hasRedColor(disconnJpg) , matchResult

def matchDisconnectButton():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/disconnectButton.jpg"))#判断断开连接的按钮是否存在
    disconnJpg = cropped[matchResult[1]:matchResult[4],matchResult[0]:matchResult[3]]
    return isTrustResult(matchResult) and hasRedColor(disconnJpg) , matchResult
    
def matchDisconnecting():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/disconnectGrey.jpg"))#判断断开连接的按钮是否存在
    disconnJpg = cropped[matchResult[1]:matchResult[4],matchResult[0]:matchResult[3]]
    return isTrustResult(matchResult) and (hasRedColor(disconnJpg)==False) , matchResult

def matchLogin():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/loginButton.jpg"))#判断登录按钮是否存在
    return isTrustResult(matchResult) , matchResult

def matchLoginNotic():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/loginNotic.jpg"))#判断登录通知
    return isTrustResult(matchResult) , matchResult

def matchWarning():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/warning.jpg"))#判断是否出错
    print(matchResult)
    return isTrustResult(matchResult) , matchResult

def matchLoading():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/loadingTop.jpg"))#判断是否正在加载中
    return isTrustResult(matchResult) , matchResult

def matchRetry():
    matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/retry.jpg"))#判断重试按钮的位置
    return isTrustResult(matchResult) , matchResult

def matchNoticBar():
    matchResult = find_picture(cv2.imread("screenshot.jpg"),cv2.imread("./template/noticBar.jpg"))#判断是否有错误提示
    return isTrustResult(matchResult) , matchResult

def matchNoticConfirm():
    matchResult = find_picture(cv2.imread("screenshot.jpg"),cv2.imread("./template/noticConfirm.jpg"))#判断通知的确认按钮
    return isTrustResult(matchResult) , matchResult
if __name__ == '__main__':
    main()
    


