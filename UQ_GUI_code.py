# GUI Application Code
# zoom function
# csv = ppm
# txt = counts
import sys
import cv2
from PyQt5 import uic, QtWidgets, QtGui, QtCore
import UQ_functions as UQF

qtCreatorFile = "uq_gui.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        '''Runs on start of application: Initialization of program
        
        Opens the GUI application
        Initializes variables
        Initializes clickable buttons
        '''
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        
        self.all_img_paths = []
        self.plant_el_dict = {}
        self.plant_path_dict = {}
        self.nr_img = 0
        self.TB_imagefolder.clicked.connect(self.select_images)
        self.PB_clearimgs.clicked.connect(self.clear_images)
        self.CB_selectplant.currentIndexChanged.connect(self.select_plant)
        self.PB_showmask.clicked.connect(self.show_mask)
        self.PB_applymask.clicked.connect(self.apply_mask)
    
    def select_images(self):
        '''Runs when TB_imagefolder is clicked: selects images
        
        Opens a QFileDialog screen to select images (.tif or .txt)
        Checks if the filenames are valid
        Saves the loaded image paths in a list
        Extracts a list with the names and a dict with the elements per plant
        Adds the plant names to a selection box
        Runs the select_plant() function
        '''
        #img_paths, ext = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select Images', '', "Images (*.tif; *.txt)")
        img_paths, ext = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select Images', '')
        for img_path in img_paths:
            if UQF.is_valid_filename(img_path) == False:
                print(img_path, 'is not a valid filename and is therefore removed')
                img_paths.remove(img_path)
        self.nr_img += len(img_paths)
        self.LW_imgpaths.addItem(str(self.nr_img) + ' images loaded')
        self.all_img_paths.extend(img_paths)
        names, self.plant_el_dict = UQF.names_dict_from_filenames(img_paths, self.plant_el_dict)
        self.CB_selectplant.clear()
        self.CB_selectplant.addItems(self.plant_el_dict.keys())
        self.select_plant()
        
    def clear_images(self):
        '''Runs when PB_clearimgs is clicked: clears images
        
        Clears every trace of the selected images
        '''
        self.nr_img = 0
        self.LW_imgpaths.clear()
        self.CB_selectplant.clear()
        self.CB_selectel.clear()
        self.all_img_paths = []
        self.plant_el_dict = {}
        
    def select_plant(self):
        ''''Runs after select_images and when CB_selectplant index is changed
        '''
        self.CB_selectel.clear()
        self.ImgTabs.clear()
        self.cur_plant = self.CB_selectplant.currentText()
        els = self.plant_el_dict[self.cur_plant]
        self.CB_selectel.addItems(els)
        self.plant_path_dict = UQF.group_plants_files(self.all_img_paths)
        self.plant_path_dict = self.plant_path_dict[self.cur_plant]
        for el in els:
            tab = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout()
            label = QtWidgets.QLabel()
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHeightForWidth(True)
            label.setSizePolicy(sizePolicy)
            label.setMinimumSize(1, 1)
            layout.addWidget(label)
            path = UQF.get_el_file_from_working_files(self.plant_path_dict, el)
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
        cur_path = UQF.get_el_file_from_working_files(self.plant_path_dict, th_el)
        mask, con = UQF.get_mask(th_mode, th_manual, cur_path, self.all_img_paths)
        qImg = QtGui.QImage(mask.data, mask.shape[1], mask.shape[0], QtGui.QImage.Format_Grayscale8)
        self.mask = mask
        self.con = con
        pixmap = QtGui.QPixmap.fromImage(qImg)
        item = QtWidgets.QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(item)
        self.GV_mask.setScene(scene)
        self.GV_mask.fitInView(item)
        
    def apply_mask(self):
        # TODO: check if mask and con are not empty
        els = self.plant_el_dict[self.cur_plant]
        self.Table.setRowCount(len(els))
        self.Table.setVerticalHeaderLabels(els)
        self.Table.setColumnCount(len(self.con))
        self.Table.setHorizontalHeaderLabels(['Total Counts'])
        UQF.area_contours(self.con, self.plant_path_dict)
        for i, el in enumerate(els):
            counts = 1
            self.Table.setItem(i,0, QtWidgets.QTableWidgetItem(str(counts)))


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
