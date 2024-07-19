import matplotlib.pyplot as plt
import sys
import os
import cv2
import numpy as np

#使用命令行
#命令参考1：python thx.py D:\\0Project\\Crack\\in D:\\0Project\\Crack\\out
#命令参考2：python thx.py ./in ./out
#命令参考3：python D:\0Project\Crack\thx.py ./in D:\\0Project\\Crack\\out

def nothing():pass
#获取孔隙体积
def get_spot_VE_VT(img, rx):
    hist = cv2.calcHist([img], [0], None, [255], [0, 255]) #灰度直方图
    rn = float(img.size) #总像素尺寸=长*宽
    ve = 0.0
    vt = 0.0
    for i in range(0, rx):
        ri = hist[i]
        if ri[0]<0.0:continue
        hri = ri[0]/rn #计算该像素的实际深度体积
        ve += (rx-i)*hri #累积深度体积
        vt += hri
    return ve,vt

def img_process(img_input):
    src = cv2.imread(img_input)
    #cv2.imshow('src', src)
    gray8 = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    #gray8 = cv2.GaussianBlur(gray8,(3,3),1)
    gray8 = cv2.medianBlur(gray8,3)
    # 将8位灰度值映射到16位
    #gray16 = ((gray8/256.0)*65535).astype('uint16')
    #cv2.imwrite(img_path, gray16)
    #cv2.imshow('gray16', gray16)
    X_BEST = VE = VT = gray8.max() #X_BEST-最优参考点 VE-孔隙体积 VT-理想体积
    ET = 1.0 #ET-孔隙率

    # # -------------------------------X手动调节-------------------------------------
    # def img_process(pos):
    #     X = cv2.getTrackbarPos('X', 'dsc')   
    #     VE,VT = get_spot_VE_VT(gray8, X)
    #     print("参考点X %f 对应深度体积[VE]=%f, 对应孔隙率[VE/VT]=%f" % (X, VE, VE/VT))
    #     _,dsc = cv2.threshold(gray8, X, 255, cv2.THRESH_BINARY_INV)
    #     cv2.imshow('dsc', dsc)

    # cv2.namedWindow('dsc', cv2.WINDOW_GUI_EXPANDED)
    # cv2.createTrackbar('X', 'dsc', gray8.max(), gray8.max(), img_process)

    # while True:
    #     if 32 == (cv2.waitKey(0)&0xFF):break
    # cv2.destroyAllWindows()

    # # -------------------------------X最优解-------------------------------------
    lx = np.linspace(gray8.min(), gray8.max(), gray8.max()-gray8.min())
    ly = []
    isfind=False
    vex,vtx = get_spot_VE_VT(gray8, gray8.max())
    for X in reversed(range(gray8.min(), gray8.max())):
        vex,vtx = get_spot_VE_VT(gray8, X)
        vtx *= X #(X-gray8.min()) #计算理想体积所用高度是否为相对最小值的差而不是绝对值呢？
        # vex = vex*0.95+ve*0.05 #一阶平滑VE曲线，针对不同来源图像请调优此一阶平滑参数,否则部分区域会出现黑晕
        # vtx = vtx*0.95+vt*0.05 #一阶平滑VT曲线，针对不同来源图像请调优此一阶平滑参数
        etx = vex/vtx
        #et = ET*0.95 + (ve/vt)*0.05 #一阶平滑VT曲线，针对不同来源图像请调优此一阶平滑参数
        ly.insert(0,etx)
        if isfind : continue
        if etx > ET: 
            X_BEST = X-20 #X最优解需针对不同图片做一定的偏置调整才能达到比较好的效果，或者采用上面一阶滤波
            VE = vex
            VT = vtx
            isfind=True
            continue
        ET = etx
    line = "%s,%f,%f,%f,%f\n"%(img_input, X_BEST, X_BEST*256, VE, ET)
    log = "%s 最优X_8bit %f X_16bit %f 对应深度体积[VE]=%f, 对应孔隙率[VE/VT]=%f" % (img_input, X_BEST, X_BEST*256, VE, ET)
    print(log)
    #-------------------孔隙度曲线--------------------
    #---------------------------------------
    _,dsc = cv2.threshold(gray8, X_BEST, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow('dsc', dsc)
    # cv2.waitKey(0)
    return dsc,line


img_in = sys.argv[1] #"d:\\0Project\\Crack\\test.jpg"
img_out = sys.argv[2] #"d:\\0Project\\Crack\\test.png"
with open(img_out+'\log.csv','w') as csv:
    csv.write("file,X8,X16,VE,ET\n")
    for file in os.listdir(img_in):
        dsc,line = img_process(img_in+"/"+file)
        cv2.imwrite(img_out+"/"+file, dsc)
        csv.write(line) #输出csv
# cv2.imshow('dsc', dsc)
# cv2.waitKey(0)
    