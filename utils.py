import os, shutil, psutil, win32con, win32gui, requests

def mymovefile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        print ("move %s -> %s"%( srcfile,dstfile))

def mycopyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print ("copy %s -> %s"%( srcfile,dstfile))

def killProgram(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        return True
    except Exception as e:
        print("killProgram Error"+str(e))
        return False
    
def closeWindow(hwnd):
    win32gui.PostMessage(hwnd,win32con.WM_CLOSE,0,0)

def killProgramByName(name):
    try:
        cmd = 'taskkill /F /IM '+name
        os.system(cmd)
        return True
    except Exception as e:
        print("killProgramByName Error"+str(e))
        return False


        

if __name__ == '__main__':
    print(checkInternetConnection())