import os
import sys
import json
from PyQt5.QtWidgets import (QFileDialog, QApplication,
                             QMessageBox, QPushButton,QWidget,QLineEdit,QGridLayout)
class QConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.config1 = QPushButton('常用1')
        self.config2 = QPushButton('常用2')
        self.config3 = QPushButton('常用3')
        self.save_button = QPushButton('保存')
        self.Edit1 = QLineEdit()
        self.Edit2 = QLineEdit()
        self.Edit3 = QLineEdit()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.config1, 1, 0)
        grid.addWidget(self.Edit1, 1, 1)

        grid.addWidget(self.config2, 2, 0)
        grid.addWidget(self.Edit2, 2, 1)

        grid.addWidget(self.config3, 3, 0)
        grid.addWidget(self.Edit3, 3, 1)
        grid.addWidget(self.save_button, 4, 0, 1, 2)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('配置')

        self.config1.clicked.connect(lambda :self.choose_dir1(self.config1))
        self.config2.clicked.connect(lambda :self.choose_dir1(self.config2))
        self.config3.clicked.connect(lambda :self.choose_dir1(self.config3))
        self.save_button.clicked.connect(self.save_config)
        self.init_json()
    def choose_dir1(self,text):

        get_directory_path = QFileDialog.getExistingDirectory(self,"选取指定文件夹","C:/")
        if text == self.config1:
            self.Edit1.setText(str(get_directory_path))
        elif text == self.config2:
            self.Edit2.setText(str(get_directory_path))
        elif text == self.config3:
            self.Edit3.setText(str(get_directory_path))

    def init_json(self):
        filename = 'config.json'
        if os.path.exists(filename):
            path1,path2,path3=self.read_config()
            self.Edit1.setText(path1)
            self.Edit2.setText(path2)

            self.Edit3.setText(path3)
        else:
            dict = {'config': ['选择常用的图片文件夹', '选择常用的图片文件夹', '选择常用的图片文件夹']}
            with open('config.json', 'w') as f:
                json.dump(dict, f)
            f.close()

    def read_config(self):

        with open('config.json', 'r') as f:
            dict = json.load(f)
        return dict['config'][0],dict['config'][1],dict['config'][2]

    def save_config(self):

        dict = {'config': [self.Edit1.text(), self.Edit2.text(), self.Edit3.text()]}
        with open('config.json', 'w') as f:
            json.dump(dict, f)
        f.close()
        QMessageBox.information(self, "保存", "配置保存成功",QMessageBox.Ok)

if __name__ == "__main__":
        app = QApplication(sys.argv)
        form = QConfig()
        form.show()
        sys.exit(app.exec_())