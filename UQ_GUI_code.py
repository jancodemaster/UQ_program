# GUI Application Code

import sys
import cv2
from PyQt5 import uic, QtWidgets, QtGui, QtCore
import UQ_functions as UQF

qtCreatorFile = "uq_gui.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        
        self.all_img_paths = []
        self.plant_el_dict = {}
        self.TB_imagefolder.clicked.connect(self.select_images)
        self.PB_clearimgs.clicked.connect(self.clear_images)
        self.PB_showmask.clicked.connect(self.show_mask)
        self.CB_selectplant.currentIndexChanged.connect(self.select_plant)
    
    def select_images(self):
        img_paths, ext = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select Images', '', "Images (*.tif)")
        self.LW_imgpaths.addItems(img_paths)
        self.all_img_paths.extend(img_paths)
        names, self.plant_el_dict = UQF.names_dict_from_filenames(img_paths, self.plant_el_dict)
        self.CB_selectplant.clear()
        self.CB_selectplant.addItems(self.plant_el_dict.keys())
        self.select_plant()
        
    def clear_images(self):
        self.LW_imgpaths.clear()
        self.CB_selectplant.clear()
        self.CB_selectel.clear()
        self.all_img_paths = []
        self.plant_el_dict = {}
        
    def select_plant(self):
        self.cur_plant = self.CB_selectplant.currentText()
        self.CB_selectel.clear()
        self.CB_selectel.addItems(self.plant_el_dict[self.cur_plant])
        
        self.ImgTabs.clear()
        els = self.plant_el_dict[self.cur_plant]
        self.plantdict = UQF.group_plants_files(self.all_img_paths)
        self.plantdict = self.plantdict[self.cur_plant]
        for el in els:
            tab = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout()
            label = QtWidgets.QLabel()
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHeightForWidth(True)
            label.setSizePolicy(sizePolicy)
            label.setMinimumSize(1, 1)
            layout.addWidget(label)
            path = UQF.get_el_file_from_working_files(self.plantdict, el)
            pixmap = QtGui.QPixmap(path)
            #label.setPixmap(pixmap.scaled(label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            label.setScaledContents(True)
            label.setPixmap(pixmap)
            tab.setLayout(layout)
            self.ImgTabs.addTab(tab, el)
    
    def show_mask(self):
        th_mode = self.CB_selectthreshold.currentText()
        th_el = self.CB_selectel.currentText()
        if th_mode == 'Auto':
            th_mode = th_el
        th_manual = self.SB_selectmanualth.value()
        cur_path = UQF.get_el_file_from_working_files(self.plantdict, th_el)
        mask = UQF.get_mask(th_mode, th_manual, cur_path, self.all_img_paths)
        qImg = QtGui.QImage(mask.data, mask.shape[1], mask.shape[0], QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        item = QtWidgets.QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(item)
        self.GV_mask.setScene(scene)
        self.GV_mask.fitInView(item)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())




#for img in img_paths:
#    item = QtWidgets.QTreeWidgetItem(self.Table)
#    item.setText(0, img)
#    el = img.split(' - ')[-1]
#    el = el.split('.')[0]