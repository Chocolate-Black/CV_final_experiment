import final

from sys import argv,exit
from PyQt5.QtWidgets import QApplication,QMainWindow,\
    QHBoxLayout,QWidget,QComboBox,QLabel,\
    QListWidgetItem,QMessageBox,QFrame,QFileDialog,QHeaderView,QInputDialog,QLineEdit
from PyQt5.QtGui import QStandardItemModel,QStandardItem
import os
import exifread
from pathlib import Path
from sfm import OpenMVG
from pmvs import CMVS_PMVS
import time
import datetime
from all import mvg_mvs

CAMERA_SENSOR_WIDTH_DIRECTORY = "F:/openMVG2/openMVG/src/openMVG/exif/sensor_width_database"


class MainWindow(QMainWindow,final.Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.input_dir = ""
        self.output_dir = ""
        self.mvg = None
        self.mvs = None
        self.actionimport_images.triggered.connect(self.import_images)
        self.model = QStandardItemModel(0, 0)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.actionclear.triggered.connect(self.clear)
        self.actionIntrinsics_analysis.triggered.connect(self.Intrinsics_analysis)
        self.actionCompute_features.triggered.connect(self.Compute_features)
        self.actionCompute_matches.triggered.connect(self.Compute_matches)
        self.actionincreased_sfm.triggered.connect(self.Incremental_sfm)
        self.actionglobal_sfm.triggered.connect(self.Global_sfm)
        self.actionconvert_to_PMVS.triggered.connect(self.convert_to_PMVS)
        self.actionCMVS.triggered.connect(self.CMVS)
        self.actionPMVS.triggered.connect(self.PMVS)
        self.actionstart.triggered.connect(self.quick_reconstruct)
        self.actionadd_camera_name.triggered.connect(self.add_camera_dialog)


    def import_images(self):
        dir_choose = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      self.cwd)  # 起始路径
        if dir_choose == "":
            print("cancel")
            return
        else:
            self.output_dir = dir_choose
            self.input_dir = dir_choose+'/'+'images'
            if Path(self.input_dir).is_dir():
                mystr = "图片文件夹路径:" + self.input_dir
                self.log(mystr)
                output_str = "输出文件夹路径:"+self.output_dir
                self.log(output_str)
            else:
                self.log("路径不存在！请检查本目录下是否新建了images文件夹。")
                return

        self.log("读取图片...")
        image_num = 0
        self.model.setHorizontalHeaderLabels(['文件名称', '所在文件夹', '图片相机型号'])
        for filename in os.listdir(self.input_dir):
            if filename.endswith(('.jpg','.jpeg')):
                image_num += 1
                file_path = self.input_dir+'/'+filename
                info = self.get_image_exif(file_path)
                self.model.appendRow([
                    QStandardItem(filename),
                    QStandardItem(dir_choose),
                    QStandardItem(info['Image Model'])
                ])
            else:
                continue
        self.log("读取图片完成！总计{0}张图片。".format(image_num))

    def log(self,mystr):
        self.textBrowser.append(mystr)  # 在指定的区域显示提示信息
        self.cursor = self.textBrowser.textCursor()
        self.textBrowser.moveCursor(self.cursor.End)  # 光标移到最后，这样就会自动显示出来
        QApplication.processEvents()  # 一定加上这个功能，不然有卡顿

    def get_image_exif(self,path):
        f = open(path, 'rb')
        tags = exifread.process_file(f)
        info={
            'Image Model':tags.get('Image Model', '0').values
        }
        f.close()
        return info

    def clear(self):
        self.model.clear()
        self.input_dir = ""
        self.output_dir = ""
        self.mvg = None
    
    def Intrinsics_analysis(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return 
        self.log("初始化...")
        time_start = time.time()
        self.mvg = OpenMVG(self.input_dir, self.output_dir)
        self.log("初始化完成！")
        self.log("Intrinsics analysis...")
        self.mvg.Intrinsics_analysis()
        self.log("Intrinsics analysis completed!")
        time_end = time.time()
        cost = time_end-time_start
        cost_time = datetime.time(second=int(cost))
        self.log("重建完成！共计耗时：{0}:{1}:{2}".format(cost_time.hour,cost_time.minute,cost_time.second))


    def Compute_features(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvg == None:
            self.mvg = OpenMVG(self.input_dir,self.output_dir)

        filepath = self.mvg.matches_dir + '/sfm_data.json'
        filepath = Path(filepath)
        if filepath.is_file():
            self.log("Compute features...")
            self.mvg.Compute_features()
            self.log("Compute features completed!")

        else:
            mystr = self.mvg.matches_dir + '/sfm_data.json 不存在！'
            self.log(mystr)

    def Compute_matches(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvg == None:
            self.mvg = OpenMVG(self.input_dir,self.output_dir)

        filepath_1 = self.mvg.matches_dir + '/sfm_data.json'
        filepath_1 = Path(filepath_1)
        filepath_2 = self.mvg.matches_dir + '/image_describer.json'
        filepath_2 = Path(filepath_2)
        if filepath_1.is_file() and filepath_2.is_file():
            self.log("Compute matches...")
            self.mvg.Compute_matches()
            self.log("Compute matches completed!")
        else:
            if filepath_1.is_file() == False:
                mystr = self.mvg.matches_dir + '/sfm_data.json 不存在！'
                self.log(mystr)
            if filepath_2.is_file() == False:
                mystr = self.mvg.matches_dir + '/image_describer.json 不存在！'
                self.log(mystr)

    def Incremental_sfm(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvg == None:
            self.mvg = OpenMVG(self.input_dir,self.output_dir)

        filepath_1 = self.mvg.matches_dir + '/matches.f.bin'
        filepath_1 = Path(filepath_1)
        filepath_2 = self.mvg.matches_dir + '/matches.putative.bin'
        filepath_2 = Path(filepath_2)
        if filepath_1.is_file() and filepath_2.is_file():
            self.log("Incremental reconstruction...")
            self.mvg.Incremental_sfm()
            self.log("Incremental reconstruction completed!")
        else:
            if filepath_1.is_file() == False:
                mystr = self.mvg.matches_dir + '/matches.f.bin 不存在！'
                self.log(mystr)
            if filepath_2.is_file() == False:
                mystr = self.mvg.matches_dir + '/matches.putative.bin 不存在！'
                self.log(mystr)

    def Global_sfm(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvg == None:
            self.mvg = OpenMVG(self.input_dir,self.output_dir)

        filepath_1 = self.mvg.matches_dir + '/matches.f.bin'
        filepath_1 = Path(filepath_1)
        filepath_2 = self.mvg.matches_dir + '/matches.putative.bin'
        filepath_2 = Path(filepath_2)
        if filepath_1.is_file() and filepath_2.is_file():
            self.log("Global reconstruction...")
            self.mvg.global_sfm()
            self.log("Global reconstruction completed!")
        else:
            if filepath_1.is_file() == False:
                mystr = self.mvg.matches_dir + '/matches.f.bin 不存在！'
                self.log(mystr)
            if filepath_2.is_file() == False:
                mystr = self.mvg.matches_dir + '/matches.putative.bin 不存在！'
                self.log(mystr)

    def convert_to_PMVS(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvg == None:
            self.mvg = OpenMVG(self.input_dir,self.output_dir)

        filepath_1 = self.mvg.reconstruction_dir + '/sfm_data.bin'
        filepath_1 = Path(filepath_1)

        if filepath_1.is_file():
            self.log("convert to PMVS...")
            self.mvg.convert_to_PMVS()
            self.log("convert to PMVS completed!")
        else:
            mystr = self.mvg.reconstruction_dir + '/sfm_data.bin 不存在！'
            self.log(mystr)

    def CMVS(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvs == None:
            self.mvs = CMVS_PMVS(self.input_dir,self.output_dir)

        dir_path = self.mvs.reconstruction_dir + '/PMVS'
        dir_path = Path(dir_path)
        if dir_path.is_dir():
            self.log("CMVS processing...")
            self.mvs.CMVS()
            self.log("CMVS completed!")
        else:
            mystr = self.mvs.reconstruction_dir + '/PMVS 不存在！'
            self.log(mystr)

    def PMVS(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return
        if self.mvs == None:
            self.mvs = CMVS_PMVS(self.input_dir,self.output_dir)

        file_path = self.mvs.reconstruction_dir + '/PMVS/option-0000'
        file_path = Path(file_path)

        if file_path.is_file():
            self.log("PMVS processing...")
            self.mvs.PMVS()
            self.log("PMVS completed!")
        else:
            mystr = self.mvs.reconstruction_dir + '/PMVS/option-0000 不存在！'
            self.log(mystr)

    def quick_reconstruct(self):
        if self.input_dir == "" or self.output_dir == "":
            self.log("请先导入图片！")
            return

        self.log("重建开始...")
        time_start = time.time()
        my_model = mvg_mvs(self.input_dir,self.output_dir)
        my_model.recon()
        time_end = time.time()
        cost = time_end-time_start
        self.log("重建完成！共计耗时：{0}s".format(cost))

    def add_camera_dialog(self):
        name, ok = QInputDialog.getText(self,'添加相机型号','添加相机型号及传感器宽度（用分号隔开）：',QLineEdit.Normal,"")
        if ok:
            self.add_camera_name(name)

    def add_camera_name(self,name):
        file_path = CAMERA_SENSOR_WIDTH_DIRECTORY + '/sensor_width_camera_database.txt'
        file_path2 = Path(file_path)
        if file_path2.is_file():
            f = open(file_path,'a')
            f.write('\n'+name)
            f.close()
            self.log("相机型号添加成功！")
        else:
            self.log("文件不存在！")



if __name__ == '__main__':
    app = QApplication(argv)
    ui = MainWindow()
    ui.show()
    exit(app.exec_())