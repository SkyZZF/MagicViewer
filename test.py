#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import QApplication
from MagicViewer import ImageViewer

app = QApplication(sys.argv)
viewer = ImageViewer()
viewer.openfile('C:\test.jpg') #这里改为你的图片路径
sys.exit(app.exec_())
