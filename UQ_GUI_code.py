# GUI Application Code

import sys
import cv2
from PyQt5 import uic, QtWidgets, QtGui
import UQ_functions as UQF

qtCreatorFile = "uq_gui.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.all_img_paths = []
        self.plant_el_dict = {}
        self.TB_imagefolder.clicked.connect(self.select_images)
        self.PB_clearimgs.clicked.connect(self.clear_images)
        self.PB_showimage.clicked.connect(self.show_image)
        self.PB_showmask.clicked.connect(self.show_mask)
    
    def select_images(self):
        img_paths, ext = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select Images', '', "Images (*.tif)")
        self.LW_imgpaths.addItems(img_paths)
        self.all_img_paths.extend(img_paths)
        names, self.plant_el_dict = UQF.names_dict_from_filenames(img_paths, self.plant_el_dict)
        self.CB_selectimage.addItems(names)
        #self.CB_selectthreshold.addItems(els)
        
    def clear_images(self):
        self.LW_imgpaths.clear()
        self.CB_selectimage.clear()
        self.CB_selectthreshold.clear()
        self.CB_selectthreshold.addItem('Manual')
        self.all_img_paths = []
        self.plant_el_dict = {}
        
    def show_image(self):
        cur_path = self.all_img_paths[self.CB_selectimage.currentIndex()]
        plant, el = UQF.plantname_from_filename(cur_path)
        self.CB_selectthreshold.clear()
        self.CB_selectthreshold.addItem('Manual')
        self.CB_selectthreshold.addItems(self.plant_el_dict[plant])
        self.cur_plant = plant
        pixmap = QtGui.QPixmap(cur_path)
        item = QtWidgets.QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(item)
        self.GV_image.setScene(scene)
        self.GV_image.fitInView(item)
    
    def show_mask(self):
        th_mode = self.CB_selectthreshold.currentText()
        th_manual = self.SB_selectmanualth.value()
        cur_path = self.all_img_paths[self.CB_selectimage.currentIndex()]
        mask = UQF.get_single_mask(th_mode, th_manual, cur_path)
        qImg = QtGui.QImage(mask.data, mask.shape[1], mask.shape[0], QtGui.QImage.Format_Grayscale8)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        item = QtWidgets.QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixmap)
        self.GV_mask.setScene(scene)
        self.GV_image.fitInView(item)


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