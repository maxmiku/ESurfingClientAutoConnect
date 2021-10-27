#coding=utf-8


#qt 截图
import win32gui, win32con, win32api, win32process, cv2, time
import numpy, psutil
from autoWinCtrl import *
from utils import *

#QT5 全屏截图部分
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import sys, os, traceback, logging



# #获取所有窗口的句柄

# hwnd_title = dict()
# def get_all_hwnd(hwnd,mouse):
#   if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
#     hwnd_title.update({hwnd:win32gui.GetWindowText(hwnd)})

# win32gui.EnumWindows(get_all_hwnd, 0)
 
# for h,t in hwnd_title.items()
#   if t is not "":
#     print(h, t)


if(not os.path.exists("./log/"+time.strftime('%Y%m',time.localtime(time.time()))+"/")):
	os.mkdir("./log/"+time.strftime('%Y%m',time.localtime(time.time()))+"/")


# 获取logger对象,取名mylog
logger = logging.getLogger("autoReconnect")
# 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
logger.setLevel(level=logging.DEBUG)

# 获取文件日志句柄并设置日志级别，第二层过滤
handler = logging.FileHandler("./log/"+time.strftime('%Y%m',time.localtime(time.time()))+"/log_"+time.strftime('%Y%m%d',time.localtime(time.time()))+".txt")
handler.setLevel(logging.INFO)  

# 生成并设置文件日志格式，其中name为上面设置的mylog
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 获取流句柄并设置日志级别，第二层过滤
console = logging.StreamHandler()
console.setLevel(logging.WARNING)

# 为logger对象添加句柄
logger.addHandler(handler)
logger.addHandler(console)


# 记录日志
# logger.info("show info")
# logger.debug("show debug")
# logger.warning("show warning")


# 检查窗口是否最小化，如果是最大化
def showWindow(hwnd):

	try:
		#下方两句显示最小化窗口并前置窗口
		win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
		try:
			win32gui.SetForegroundWindow(hwnd)
		except Exception as e:
			log("win32gui前置方式错误,正在尝试使用ctypes方式前置窗口")
			ctypes.windll.user32.SwitchToThisWindow(hwnd,True)

		

		# win32gui.ShowWindow(hwnd, 1)
		time.sleep(0.5)
		return True
		# if(win32gui.IsIconic(hwnd)):
		# #   win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
		#     win32gui.ShowWindow(hwnd, 1)
		#     time.sleep(0.5)
	except Exception as e:
		print ("将窗口置于前台失败:"+str(e))
		return False
	




client_path = r'"C:\Program Files (x86)\Chinatelecom_JSPortal\ESurfingClient.exe"'

nowStage = 5 #当前状态 详细见下表
preStage_1 = 5 #上次检测的状态 防止某次的识别失灵
preStage_2 = 5
#				0 		1 	  2        3      4        5         6
stageTexts=["待登录","错误","加载中","断开中","在线","初始化中","无法匹配"]
stageChanging = True #状态正在变化

STATUS_WAITLOGIN = 0
STATUS_ERROR = 1
STATUS_LOADING = 2
STATUS_DISCONNECTING = 3
STATUS_ONLINE = 4
STATUS_INIT = 5
STATUS_NOTMATCH = -1

pre_control = -1 #上一个操作的时间 防止重复操作

windows_pot = None

lazy_mode = False #低能模式

count_net_error = 0 #网络错误次数

count_client_error = 0 #客户端出现错误次数

last_online = time.time() #上一次在线的时间
disconnect_timeout = 120 #掉线超过120s 将会重启客户端

stage_timeout = 60 #卡在一个界面中超过60秒将重启客户端
stage_start_time = -1 #当前状态持续时间 防止客户端卡死 (加载中 错误 断开中)

# control_client = True #是否需要不断截图控制客户端的标志


#用于测试各种出状态监测的结果
def TestJudgement():
	allStage = [matchLoginNotic,matchWarning,matchLoading,matchDisconnecting,matchOnline]
	print("\n\n\n")
	# os.system('cls')
	matchResult=None
	matchIndex=-1
	print("阶段名称\t匹配度")
	for i in range(0,len(allStage)):
		rs, result = allStage[i]()
		print(getStageText(i)+"\t"+str(result[2])+"\t"+str(isTrustResult(result)))
		

#运行主函数
def main():
	global nowStage,preStage_1,preStage_2
	global pre_control
	global lazy_mode,count_net_error,count_client_error,stage_start_time,last_online

	os.system('title autoReconnect')


	showWindow(hwnd)
	reset_window_pos()

	# while 1:
	# 	if(findFixToolsWindows()):
	# 		print ("Stop fixTools Success")
	# 	if(findNoticWindow()):
	# 		print ("Close notic window Success")

	# 	if(not isClientWindowShot()):
	# 		print("当前截图不属于客户端,正在将客户端调前...")
	# 		if(not showWindow(hwnd)):
	# 			print("重试中...")
	# 			continue

	# 	captureScreen()
	# 	if(cutScreenShotFitPrgm()):
	# 		TestJudgement()
	# 	else:
	# 		print("Error 窗口应该是被隐藏了")
	# 		showWindow(hwnd)
	# 		reset_window_pos()
	# return

	
	

	while 1:
		try:
			# input("请单击回车进行状态监测...")
			if(findFixToolsWindows()):
				log ("Stop fixTools Success")
				lazy_mode=False

			if(findNoticWindow()):
				log ("Close notic window Success")
				lazy_mode=False
			
			if(lazy_mode):
				if(checkInternetConnection()):
					log("lazy_mode 网络连接正常 "+time.strftime('%H:%M:%S',time.localtime(time.time())),-1)
					time.sleep(5)
					continue
				else:
					if(checkInternetConnection()):
						log("lazy_mode 网络连接正常 "+time.strftime('%H:%M:%S',time.localtime(time.time())),-1)
						time.sleep(5)
						continue
					else:
						log("网络异常,已切出lazyMode",1)
						lazy_mode=False


			iscws,rs_client = isClientWindowShot()
			if(not iscws):
				log("当前截图不属于客户端,正在将客户端调前... 精度:"+str(rs_client[2]),1)
				if(not showWindow(hwnd)):
					log("客户端窗口前置失败,即将尝试将启动程序...",2)
					time.sleep(1)
					continue

			captureScreen()
			if(not cutScreenShotFitPrgm()):
				log("客户端窗口应该是被隐藏了,窗口位置不正确",1)
				if(not showWindow(hwnd)):
					log("客户端窗口前置失败,重试中...",1)
					time.sleep(1)
					continue
				reset_window_pos()
				continue


			tmp, result = whichStage()

			#在线时判断是否正在断线
			if(tmp==4):
				if(isDisconnecting()):
					tmp=3


			if(tmp==preStage_1 and tmp==preStage_2 and tmp!=nowStage):
				nowStage = tmp

			preStage_2 = preStage_1
			preStage_1 = tmp

			stageChanging = not (tmp==nowStage==preStage_1==preStage_2)

			acc = "N/A"
			if(result!=None):
				acc = result[2]

			if(stageChanging):
				log("当前状态:"+getStageText(nowStage)+" 当前检测状态:"+getStageText(tmp)+str(tmp)+" 精度:{:.5}".format(acc)+" 变化中",-1)
			else:
				log("当前状态:"+getStageText(nowStage)+str(tmp)+" 精度:{:.5}".format(acc)+" 稳定 "+time.strftime('%H:%M:%S',time.localtime(time.time())),-1)
				
			#实现自动代码的部分
			if(not stageChanging):
				# if(nowStage==STATUS_ONLINE):
				# 	print("即将断开连接")
				# 	fun_click_disconnect()
				
				if(not nowStage==STATUS_ONLINE and lazy_mode):
					log("非在线状态,lazyMode将关闭",-1)
					lazy_mode=False
				



				if(nowStage==STATUS_WAITLOGIN):
					count_client_error=0
					if(pre_control<time.time()-20):
						pre_control=time.time()
						log("即将操作客户端即将登陆")
						if(not fun_click_login()):
							pre_control=-1
					else:
						log("正在等待操作完成或超时",-1)
				elif(nowStage==STATUS_ERROR):
					if(count_client_error>4):
						log("客户端错误次数过多,正在尝试重置客户端及服务",2)
						fun_killClientService()
						fun_restartClient()
						count_client_error=0
						continue
					if(pre_control<time.time()-20):
						pre_control=time.time()
						log("客户端遇到错误,即将重试")	
						mycopyfile("screenshot_crop.jpg","./log/error/"+time.strftime('%Y%m%d %H%M%S',time.localtime(pre_control))+".jpg")
						count_client_error=count_client_error+1
						if(not fun_click_retry()):
							pre_control=-1
					else:
						log("正在等待操作完成或超时",-1)
				elif(nowStage==STATUS_NOTMATCH):
					log("无法匹配窗口,出现错误,尝试重设窗口位置",1)
					# TestJudgement()
					fun_fixNotmatchError()
				elif(nowStage==STATUS_ONLINE):
					count_client_error=0
					if(not checkInternetConnection()):
						log("网络连接不通,累计:"+str(count_net_error),1)
						count_net_error=count_net_error+1
						preStage_1=STATUS_DISCONNECTING
						lazy_mode=False
						if(count_net_error>2):
							log("网络连接不通>2,正在尝试断线重连",1)
							nowStage=preStage_2=STATUS_DISCONNECTING
							preStage_1=STATUS_ONLINE
							lazy_mode=False
							if(pre_control<time.time()-20):
								pre_control=time.time()
								if(not fun_click_disconnect()):
									pre_control=-1
							else:
								log("正在等待操作完成或超时",-1)
					else:
						count_net_error=0 #复位网络错误计数器
						if(nowStage==preStage_1==preStage_2==STATUS_ONLINE and not lazy_mode):
							log("在线状态稳定,lazyMode将启动,你现在可以切出应用了",-1)
							lazy_mode=True
							win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
				elif(nowStage==STATUS_DISCONNECTING):
					if(not checkInternetConnection()):
						if stage_start_time==-1:
							stage_start_time = time.time();
						
						#超时将杀掉进程重启客户端
						if(stage_start_time<time.time()-stage_timeout):
							log("卡在断开中时间超过"+str(stage_timeout)+"s 将重启客户端",1)
							fun_restartClient()
							stage_start_time=time.time()
						elif(stage_start_time<time.time()-stage_timeout*0.6):
							log("卡在断开中 "+str(int(stage_start_time+stage_timeout-time.time()))+"s 后将重启客户端",-1)
					else:
						stage_start_time=time.time()
			else:
				if(tmp==STATUS_LOADING and nowStage==preStage_2==STATUS_ERROR):
					#点击重试成功
					log("点击重试成功")
					pre_control=-1
				elif(not tmp==STATUS_WAITLOGIN and nowStage==preStage_2==STATUS_WAITLOGIN):
					#点击登录按钮成功
					log("点击登录按钮成功")
					pre_control=-1
				elif(nowStage==STATUS_DISCONNECTING and pre_control!=-1):
					#点击登录按钮成功
					log("点击断开按钮成功")
					pre_control=-1
				elif(preStage_1==preStage_2==STATUS_ONLINE and not nowStage==STATUS_ONLINE):
					#上线成功
					log("上线成功")
					# log("lazyMode将启动,检测频率将调整为:5s",-1)
					# lazy_mode = True
				elif(lazy_mode and not (preStage_1==preStage_2==STATUS_ONLINE) and nowStage==STATUS_ONLINE):
					log("在线状态发生改变")
					log("lazyMode将关闭,检测频率将调整为:None",-1)
					lazy_mode = False


			#断线超时检测
			if(last_online<time.time()-disconnect_timeout):
				log("掉线超过"+str(disconnect_timeout)+"s 即将重启客户端",2)
				fun_restartClient()
				last_online=time.time()
			elif(last_online<time.time()-disconnect_timeout*0.6):
				log("掉线超时 "+str(int(last_online+disconnect_timeout-time.time()))+"s 后将重启客户端",-1)

			if(lazy_mode):
				time.sleep(5)
		except Exception as e:
			log(traceback.format_exc(),2)
			try:
				fun_fixNotmatchError()
				captureScreen()
				cutScreenShotFitPrgm()
			except Exception as e:
				log(traceback.format_exc(),2)


def log(msg,level=0):
	# logger.info("show info")
	# logger.debug("show debug")
	# logger.warning("show warning")
	if(level==0):
		print("[提示] "+str(msg))
		logger.info(msg)
	elif(level==1):
		print("[警告] "+str(msg))
		logger.warning(msg)
	elif(level==2):
		print("[错误] "+str(msg))
		logger.error(msg)
	else:
		print("       "+str(msg))


def logFile(msg):
	time.strftime('%Y%m%d %H%M%S',time.localtime(time.time()))



def fun_click_disconnect():
	global windows_pot
	if(nowStage==STATUS_ONLINE or nowStage==STATUS_DISCONNECTING):
		hasTarget ,rs = matchDisconnectButton()
		if(hasTarget):
			log("找到断开连接按钮")
			if(windows_pot==None):
				windows_pot = win32gui.GetWindowRect(hwnd)
				if(windows_pot==None):
					log("We can't find the client window. Return!(fun_click_disconnect)",2)
					return False
			return dclickButton(rs,windows_pot)
		else:
			log("找不到断开连接按钮,精度:"+str(rs[2])+" 正在重试",2)
	else:
		log("点击断开失败,当前程序状态不正确"+str(nowStage)+"!="+str(STATUS_ONLINE),1)
	return False
def fun_click_retry():
	global windows_pot
	if(nowStage==STATUS_ERROR):
		hasTarget ,rs = matchRetry()
		if(hasTarget):
			log("找到重试按钮")
			if(windows_pot==None):
				windows_pot = win32gui.GetWindowRect(hwnd)
				if(windows_pot==None):
					log("We can't find the client window. Return!(fun_click_retry)",2)
					return False
			return dclickButton(rs,windows_pot)
		else:
			log("找不到重试按钮,精度:"+str(rs[2])+" 正在重试",2)
	else:
		log("点击重试失败,当前程序状态不正确"+str(nowStage)+"!="+str(STATUS_ERROR),1)
	return False
def fun_click_login():
	global windows_pot
	if(nowStage==STATUS_WAITLOGIN):
		hasTarget ,rs = matchLoginButton()
		if(hasTarget):
			log("找到登录连接按钮")
			if(windows_pot==None):
				windows_pot = win32gui.GetWindowRect(hwnd)
				if(windows_pot==None):
					log("We can't find the client window. Return!(fun_click_login)",2)
					return False
			return dclickButton(rs,windows_pot)
		else:
			log("找不到登录按钮,精度:"+str(rs[2])+" 正在重试",2)
	else:
		log("点击登录失败,当前程序状态不正确"+str(nowStage)+"!="+str(STATUS_WAITLOGIN),1)
	return False
def clickButton(rs,basePot=None):
	if(basePot==None):
		return False
	targetx = int(basePot[0] + (rs[0] + rs[3])/2)
	targety = int(basePot[1] + (rs[1] + rs[4])/2)
	# print(targetx,targety)
	mouse_click(targetx,targety)
	log("鼠标单击成功,pot"+str(targetx)+","+str(targety))
	mouse_move(0,0)
	return True

def dclickButton(rs,basePot=None):
	if(basePot==None):
		return False
	targetx = int(basePot[0] + (rs[0] + rs[3])/2)
	targety = int(basePot[1] + (rs[1] + rs[4])/2)
	# print(targetx,targety)
	mouse_dclick(targetx,targety)
	log("鼠标双击成功,pot"+str(targetx)+","+str(targety))
	mouse_move(0,0)
	return True

#修复找不到客户端的错误
def fun_fixNotmatchError():
	global hwnd,client_pid
	log("正在尝试修复找不到窗口的错误",1)
	hwnd = win32gui.FindWindow("#32770", '校园客户端')
	log("更新窗口句柄:"+str(hwnd),-1)
	client_pid = win32process.GetWindowThreadProcessId(hwnd)
	if(hwnd==0):
		log("校园客户端程序没有启动, 正在尝试重启客户端",2)
		fun_restartClient()
		time.sleep(3)
		fun_fixNotmatchError()
		return
	log("更新程序pid:"+str(client_pid),-1)
	log("正在显示窗口",-1)
	showWindow(hwnd)
	log("正在调节窗口位置",-1)
	reset_window_pos()

def fun_restartClient():
	if(not killProgramByName("ESurfingClient.exe")):
		log("结束进程失败 ESurfingClient.exe",2)
	fun_startClient()
	# if(not killProgramByName("ESurfingSvr.exe")):
	# 	log("结束进程失败 ESurfingSvr.exe",2)

def fun_killClientService():
	if(not killProgramByName("ESurfingSvr.exe")):
		log("结束进程失败 ESurfingSvr.exe",2)

def fun_startClient():
	os.popen(client_path)

hwnd = 0
client_pid = None

while hwnd==0:
	#win32gui.FindWindow(类名,标题或路径)
	hwnd = win32gui.FindWindow("#32770", '校园客户端')
	log("窗口句柄:"+str(hwnd),-1)

	if(hwnd==0):
		log("找不到客户端窗口,正在尝试打开客户端...")
		fun_startClient()
		time.sleep(3)
	

client_pid = win32process.GetWindowThreadProcessId(hwnd)




app = QApplication(sys.argv)
screen = QApplication.primaryScreen()
global img
def captureScreen():
	global img
	img = screen.grabWindow(QApplication.desktop().winId()).toImage()
	img.save("screenshot.jpg")

#设置窗口位置
def reset_window_pos(): 
	# hWndList = [] 
	# win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWndList) 
	# for hwnd in hWndList:
		# clsname = win32gui.GetClassName(hwnd)
		# title = win32gui.GetWindowText(hwnd)
		# if (title.find(targetTitle) >= 0): #调整目标窗口到坐标(600,300),大小设置为(600,600)
	#win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 10,0,330,559, win32con.SWP_SHOWWINDOW)#设置窗口位置
	pot=get_window_rect("校园客户端")
	height=pot[3]-pot[1]
	width=pot[2]-pot[0]
	# print(pot)
	# print(height ,width)
	time.sleep(1)
	win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 10,0,width,height, win32con.SWP_SHOWWINDOW)#设置窗口位置
	
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
			windows_pot = win32gui.GetWindowRect(hwnd)
			return windows_pot

		# win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,,, win32con.SWP_SHOWWINDOW)#设置窗口位置

global cropped

# 裁剪图片获得程序截图
def cutScreenShotFitPrgm():
	global cropped
	img = cv2.imread("screenshot.jpg")

	pot=get_window_rect("校园客户端")

	

	if(pot[0]<0 or pot[1]<0):
		try:
			os.remove("screenshot_crop.jpg")
		except:
			pass
		return False

	# print("截图左上角坐标:"+str(pot[0])+","+str(pot[1]))

	cropped = img[pot[1]:pot[3],pot[0]:pot[2]]#img[y0:y1,x0:x1]

	cv2.imwrite("screenshot_crop.jpg", cropped)

	return True


# 利用opencv 判断A在B中的位置

# 参数说明
# target：cv2.imread(“图片B”)
# template：cv2.imread(“图片A”)
def find_picture(target,template,displayWindow=False):

	#获得模板图片的高宽尺寸
	theight, twidth = template.shape[:2]

	# print(theight,twidth)

	#执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
	# result = cv2.matchTemplate(target,template,cv2.TM_SQDIFF_NORMED)
	result = cv2.matchTemplate(target,template,cv2.TM_CCORR_NORMED)
	


	#归一化处理m,     屏蔽掉 好像对结果有影响 导致结果都为1.0   !!!!!!!!!!!!!!!!!!!!      
	# cv2.normalize( result, result, 0, 1, cv2.NORM_MINMAX, -1 )


	#寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
	#匹配值转换为字符串
	#对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
	#对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
	strmax_val = str(max_val)
	#绘制矩形边框，将匹配区域标注出来
	#min_loc：矩形定点
	#(min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
	#(0,0,225)：矩形的边框颜色；2：矩形边框宽度
	cv2.rectangle(target,max_loc,(max_loc[0]+twidth,max_loc[1]+theight),(0,0,225),2)
	#显示结果,并将匹配值显示在标题栏上

	x=max_loc[0]
	y=max_loc[1]
	x1=max_loc[0]+twidth
	y1=max_loc[1]+theight

	if(displayWindow):
		if(True):
			if(isTrustResult((x,y,max_val,x1,y1))):
				cv2.imshow("MatchResult----MatchingValue="+strmax_val,target)
				cv2.waitKey()
				cv2.destroyAllWindows()
	# print("最大值:"+str(max_val))
	#x,y max_val 匹配度
	return x,y,max_val,x1,y1

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
	if(matchResult[2]==1.0):
		# print("不可信的结果")
		return False
	# if(abs(matchResult[2])<5e-11):
	if(matchResult[2]>0.997):
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
	# print ("当前状态的状态"+str(index))
	return stageTexts[index]

#判断程序处于什么状态
def whichStage():
	allStage = [matchLoginNotic,matchWarning,matchLoading,matchDisconnecting,matchOnline]
	
	

	matchResult=None
	matchIndex=-1
	matchVal = -1.0
	for i in range(0,len(allStage)):
		rs, result = allStage[i]()
		# print(getStageText(i)+"\t"+str(result[2])+"\t"+str(isTrustResult(result)))
		if(rs):
			# print("界面索引"+str(i)+" True")
			if(matchVal<result[2]):
				matchVal=result[2]
				matchResult=result
				matchIndex=i
		else:
			pass
			# print("界面索引"+str(i)+" False")
	# print("匹配结果:"+str(matchIndex))
	return matchIndex, matchResult
	# if(matchResult==None):
	#     print("程序未知状态,无法匹配状态")
	# else:
	#     print("目标位于 准确度:"+str(matchResult)+" 当前状态为:"+getStageText(matchIndex))



def findFixToolsWindows():
	fhwnd = win32gui.FindWindow(None, '自助排障工具')
	if(fhwnd!=0):
		log ("发现自助排障工具窗口, 窗口句柄:"+str(fhwnd))
		_,PID = win32process.GetWindowThreadProcessId(fhwnd)
		
		log ("已经向排障工具发送结束进程指令 "+str(killProgram(PID)))
		time.sleep(1)
		return True
	return False
	# else:
	# 	print("找不到自助排障工具")

#查找提示窗口并关闭
def findNoticWindow():
	notice_hwnd = win32gui.FindWindow("#32770", '提示')
	

	if(notice_hwnd!=0):
		log("发现提示窗口,窗口句柄:"+str(notice_hwnd))
		if(checkIsClientWindow(notice_hwnd)):
			log("这个提示窗口来自客户端,正在尝试关闭窗口")
			#往后自动在这个窗口中找到确定按钮或者关闭按钮关闭这个提示窗口（可以保留个错误截图）
			closeWindow(notice_hwnd)
			return True
		# else:
		# 	print("This window isn't from Esuring client")
	return False


#检查是否为客户端程序的窗口
def checkIsClientWindow(hwnd):
	_,PID = win32process.GetWindowThreadProcessId(hwnd)
	log("checking 是否为客户端窗口: 当前弹窗pid:"+str(PID)+" 客户端pid:"+str(client_pid),-1)
	found = False

	for h2 in client_pid:
		if(PID==h2):
			found = True
	return found

#检测当前局部截图是否为校园客户端
def isClientWindowShot():
	return matchClientWindow()

#在在线的时候判断是否正在断开连接
def isDisconnecting():
	_,rs_no=matchDisconnectButton()
	_,rs_ing=matchDisconnecting()
	if(rs_no[2]<rs_ing[2]):
		#正在断开连接
		return True
	return False


#检查网络连通性
def checkInternetConnection():
    global last_online
    try:
        response = requests.get("http://www.baidu.com/",timeout=2)
        if(response.text.find("bdstatic")!=-1):
        	last_online=time.time()
        	return True
        else:
        	return False
    except Exception as e:
        return False


##匹配状态与按钮开始
def matchOnline():
	#cropped = cv2.imread("screenshot_crop.jpg")
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/online.jpg"))#判断断开连接的按钮是否存在
	disconnJpg = cropped[matchResult[1]:matchResult[4],matchResult[0]:matchResult[3]]
	return isTrustResult(matchResult) , matchResult

def matchDisconnectButton():
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/disconnectButton.jpg"))#判断断开连接的按钮是否存在
	disconnJpg = cropped[matchResult[1]:matchResult[4],matchResult[0]:matchResult[3]]

	return isTrustResult(matchResult) and hasRedColor(disconnJpg) , matchResult

def matchDisconnecting():
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/disconnectGrey.jpg"))#判断断开连接的按钮是否存在
	disconnJpg = cropped[matchResult[1]:matchResult[4],matchResult[0]:matchResult[3]]
	return isTrustResult(matchResult) and (hasRedColor(disconnJpg)==False) , matchResult

def matchLoginButton():
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/loginButton.jpg"))#判断登录按钮是否存在
	return isTrustResult(matchResult) , matchResult

#判断当前截图是否是客户端
def matchClientWindow():
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/window_top.jpg"))#判断登录通知
	return isTrustResult(matchResult) , matchResult

def matchLoginNotic():
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/loginNotic.jpg"))#判断登录通知
	return isTrustResult(matchResult) , matchResult

def matchWarning():
	matchResult = find_picture(cv2.imread("screenshot_crop.jpg"),cv2.imread("./template/warning.jpg"))#判断是否出错
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
##匹配状态与按钮结束

if __name__ == '__main__':
	main()

	


