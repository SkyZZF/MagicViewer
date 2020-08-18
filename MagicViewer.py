#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
图片浏览器
'''
__version__ = 0.4
import os
import sys
import image_qr
from config_window import QConfig
from functools import partial
from PyQt5.QtGui import QPixmap, QTransform, QIcon, QFont, QCursor
from PyQt5.QtWidgets import (QFileDialog, QMainWindow, QApplication, QGraphicsScene,
                             QGraphicsView, QMenu, QMessageBox, QPushButton)
from PyQt5.QtCore import QDir, QFileInfo, Qt ,QTimer
class ImageViewer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp',
                        '.pbm', '.pgm', '.ppm', '.xbm', '.xpm')
        self.rotval = 0     # 旋转方向
        self.rotvals = (0, -90, -180, -270)
        self.file_path = QDir.currentPath()     # 获取当前文件路径

        self.resize(1000, 800)
        self.setFixedSize(self.width(),self.height())
        self.setWindowTitle("Magic Viewer")
        self.setWindowIcon(QIcon(':/image/Icon.png'))

        self.btn = QPushButton("打开图片", self)
        self.btn.resize(200, 80)
        self.btn.move((self.width() - self.btn.width()) / 2, (self.height() - self.btn.height()) / 2)
        self.btn.setFont(QFont("", 20, QFont.Bold))
        self.btn.clicked.connect(self.btnClicked)

        #菜单栏
        # 将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 创建QMenu信号事件
        self.customContextMenuRequested.connect(self.showMenu)
        self.menu = QMenu(self)
        self.function_menu=QMenu(self.menu)
        self.function_menu.setTitle('功能')
        self.open_menu = self.menu.addAction(QIcon(':/image/open.png'),'打开          O')
        self.file_path_menu = self.menu.addAction(QIcon(':/image/openfolder.png'),'打开文件所在位置')

        self.menu.addSeparator()
        self.menu.addMenu(self.function_menu)
        self.zoom_in_menu = self.function_menu.addAction(QIcon(':/image/zoom_in.png'), '放大          Scorll Up, W',)
        self.zoom_out_menu = self.function_menu.addAction(QIcon(':/image/zoom_out.png'), '缩小          Scroll Down, S')
        self.rotate_right_menu = self.function_menu.addAction(QIcon(':/image/rotate_right.png'), '顺转90°     R')
        self.rotate_left_menu = self.function_menu.addAction(QIcon(':/image/rotate_left.png'), '逆转90°     E')
        self.fitsize_menu = self.function_menu.addAction(QIcon(':/image/fitsize.png'),'适合屏幕    F')
        self.relsize_menu = self.function_menu.addAction(QIcon(':/image/relsize.png'),'实际尺寸    1')
        self.loop_menu = self.function_menu.addAction(QIcon(':/image/loop.png'), '幻灯片       L')
        self.about_menu = self.function_menu.addAction(QIcon(':/image/about.png'),'关于Magic Viewer')
        self.menu.addSeparator()
        self.next_menu = self.menu.addAction(QIcon(':/image/next.png'), '下一张       Right, SPACE')
        self.previous_menu = self.menu.addAction(QIcon(':/image/previous.png'), '上一张       Left, B')
        self.full_menu = self.menu.addAction(QIcon(':/image/full.png'), '全屏          F11')
        self.menu.addSeparator()
        self.close_menu=self.menu.addAction(QIcon(':/image/exit.png'),'退出')

       # 事件绑定
        self.zoom_in_menu.triggered.connect(self.zoomIn)
        self.zoom_out_menu.triggered.connect(self.zoomOut)
        self.full_menu.triggered.connect(self.toggleFullscreen)
        self.rotate_right_menu.triggered.connect(lambda: self.rotateImg(-1))
        self.rotate_left_menu.triggered.connect(lambda: self.rotateImg(1))
        self.next_menu.triggered.connect(lambda: self.dirBrowse(1))
        self.previous_menu.triggered.connect(lambda: self.dirBrowse(-1))
        self.fitsize_menu.triggered.connect(self.fitView)
        self.relsize_menu.triggered.connect(self.zoomReset)
        self.open_menu.triggered.connect(lambda: self.openfile(None))
        self.close_menu.triggered.connect(self.closeMainWindow)
        self.file_path_menu.triggered.connect(self.openfile_path)
        self.about_menu.triggered.connect(self.about)
        self.loop_menu.triggered.connect(self.loop_start)
        # 判断是否是幻灯片模式
        self.isLoop = False

    def btnClicked(self):

        self.openfile()

    def openfile(self, file=None):
        if file is None:
            self.chooseFile()
        else:
            self.key = file.replace("\\", "/")
        # 获取图像列表
        if self.key:
            self.btn.setEnabled(False)      # 选择了文件按钮消失
            self.imgfiles = []  # 如果选择了文件则则重新获取图像列表
            self.file_path = os.path.dirname(self.key)      # 获取文件路径
            try:
                for file in os.listdir(self.file_path):
                    if os.path.splitext(file)[1].lower() in self.formats:
                        self.imgfiles.append(self.file_path + "/" + file)
                self.count = len(self.imgfiles)     # 图像列表总数量
                self.index = self.imgfiles.index(self.key)  # 当前图像在图像列表中位置
            except FileNotFoundError:
                print("文件目录不存在！")

        self.showImage()

    def chooseFile(self):
        # 选择图片文件
        self.key, _ = QFileDialog.getOpenFileName(self,
                                                  "选择文件", self.file_path,
                                                  "图片文件 (*.bmp *.jpg *.jpeg *.png *.gif)")
    def common_file(self,path):
        self.key, _ = QFileDialog.getOpenFileName(self,
                                                  "选择文件", path,
                                                  "图片文件 (*.bmp *.jpg *.jpeg *.png *.gif)")
        self.openfile(file=self.key)
    def openfile_path(self):
        #获得当前路径
        try:
            os.startfile(self.file_path)
        except FileNotFoundError:
            print("文件目录不存在！")

    def showImage(self):

        if self.key:
            self.img = QPixmap(self.key)
            if self.img.isNull():
                QMessageBox.information(
                    self, "Magic Viewer", "不能打开文件：%s！" % self.key)
                return

            self.scene = QGraphicsScene()
            self.view = QGraphicsView(self.scene)
            self.view.setDragMode(QGraphicsView.ScrollHandDrag)
            # self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            # self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

            self.scene.clear()
            self.view.resetTransform()
            self.scene.addPixmap(self.img)


            self.zoom = 1   # 缩放系数
            self.rotate = 0  # 旋转系数

            # 如果图片尺寸＞窗口尺寸，计算缩放系数进行缩放
            if self.img.width() > self.width() or self.img.height() > self.height():
                self.zoom = min(self.width() / self.img.width(),
                                self.height() / self.img.height()) * 0.995

            width = self.img.width()
            height = self.img.height()

            # self.scene.setSceneRect(0, 0, width - 2, height - 2)
            self.view.resize(width, height)
            self.setCentralWidget(self.view)
            self.updateView()
            self.show()

    # 获取文件大小
    def fileSize(self, file):
        size = QFileInfo(file).size()

        if size < 1024:
            return str(size), "B"
        elif 1024 <= size < 1024 * 1024:
            return str(round(size / 1024, 2)), "KB"
        else:
            return str(round(size / 1024 / 1024, 2)), "MB"

    def closeMainWindow(self):

        self.close()

    def toggleFullscreen(self):
        # 全屏
        if self.isFullScreen():
            if self.isLoop:
                self.loop_end()
            else:
                self.showNormal()
        elif self.btn.isEnabled():#未全屏状态下如果任处启动界面，pass
            pass
        else:
            self.showFullScreen()

    def keyPressEvent(self, event):
        if self.isLoop:
            self.loop_end()
            return
        elif event.key() == Qt.Key_F11:
            self.toggleFullscreen()
        elif event.key() == Qt.Key_Up or event.key() == Qt.Key_W:
            self.zoomIn()
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_S:
            self.zoomOut()
        elif event.key() == Qt.Key_1:
            self.zoomReset()
        elif event.key() == Qt.Key_E:
            self.rotateImg(1)
        elif event.key() == Qt.Key_R:
            self.rotateImg(-1)
        elif event.key() == Qt.Key_F:
            self.fitView()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Space:
            self.dirBrowse(1)
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_B:
            self.dirBrowse(-1)
        elif event.key() == Qt.Key_O:
            self.btnClicked()
        elif event.key()==Qt.Key_L:
            self.loop_start()
        elif event.key() == Qt.Key_Escape:
            self.showNormal()

    def mouseDoubleClickEvent(self, event):
        #定义左键双击鼠标事件
        self.toggleFullscreen()

    def zoomIn(self):

        self.zoom *= 1.05
        self.updateView()

    def zoomOut(self):

        self.zoom /= 1.05
        self.updateView()

    def zoomReset(self,):

        self.zoom = 1
        self.updateView()

    def rotateImg(self, clock):

        self.rotval += clock
        if self.rotval == 4:
            self.rotval = 0
        elif self.rotval < 0:
            self.rotval = 3
        self.rotate = self.rotvals[self.rotval]
        self.updateView()

    def fitView(self):

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        if self.rotate == 0:
            self.zoom = self.view.transform().m11()
        elif self.rotate == -90:
            self.zoom = (self.view.transform().m12()) * -1
        elif self.rotate == -180:
            self.zoom = (self.view.transform().m11()) * -1
        else:
            self.zoom = self.view.transform().m12()

    def updateView(self):

        self.view.setTransform(QTransform().scale(
            self.zoom, self.zoom).rotate(self.rotate))
        # 更新标题信息
        self.title = os.path.basename(self.key)
        size = self.fileSize(self.key)
        self.setWindowTitle("%s(%sx%s,%s %s) - 第%s/%s张 %.2f%%" % (
            self.title, self.img.width(), self.img.height(), size[0], size[1],
            self.index + 1, self.count, self.zoom * 100))

    def dirBrowse(self, direc):

        if self.count > 1:
            self.index += direc
            # 最后一张后跳到第一张，第一张前跳到最后一张
            if self.index > self.count - 1:
                self.index = 0
            elif self.index < 0:
                self.index = self.count - 1

            self.key = self.imgfiles[self.index]

            self.showImage()
    def setBackground(self,color):
        #改变背景颜色
        # self.color = QColor(0, 0, 0)
        self.setStyleSheet('QWidget{background-color:%s}'%color)

    def loop_end(self):
        #关闭幻灯片
        if self.isLoop:

            self.timer.stop()
            self.setBackground('')#样式恢复默认效果
            self.isLoop = False
            self.showNormal()

    def loop_start(self):
        #开启幻灯片
        self.isLoop=True
        self.timer = QTimer()
        if self.isLoop:

            self.showFullScreen()
            self.setBackground('black')
            self.timer.start(5000)  # 每过5秒，定时器到期，产生timeout的信号
            self.timer.timeout.connect(partial(self.dirBrowse, 1))

    def wheelEvent(self, event):
        # 鼠标滚动
        moose = event.angleDelta().y() / 120
        if moose > 0:
            self.zoomIn()
        elif moose < 0:
            self.zoomOut()

    def showMenu(self):
        # 右键菜单
        if self.btn.isEnabled():
            common_menu = QMenu()
            qconfig = QConfig()
            common_menu.addAction(QIcon(':/image/config.png'), '配置', qconfig.show)
            path1,path2,path3=qconfig.read_config()
            if os.path.isdir(path1):
                common_menu.addAction(QIcon(':/image/common.png'), os.path.basename(path1), lambda :self.common_file(path1))
            if os.path.isdir(path2):
                common_menu.addAction(QIcon(':/image/common.png'), os.path.basename(path2), lambda :self.common_file(path2))
            if os.path.isdir(path3):
                common_menu.addAction(QIcon(':/image/common.png'), os.path.basename(path3), lambda :self.common_file(path3))
            common_menu.exec_(QCursor.pos())
        elif self.isLoop:
            self.loop_end()
            return
        else:
            self.menu.exec_(QCursor.pos())  # 在鼠标位置显示


    def about(self):
        QMessageBox.about(self, "关于Magic Viewer",
                          "<b>Magic Viewer</b>是一个基于PyQt5的开源图片浏览器<br>"
                          "二次作者 : SkyZZF<br>"
                          "原作者 : Youth Lee<br>"
                          "版本 : Ver 0.4<br>"
                          "网址 : <a href='https://github.com/SkyZZF/MagicViewer'>https://github.com/SkyZZF/MagicViewer</a>")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    # viewer.open(sys.argv[1])
    sys.exit(app.exec_())
