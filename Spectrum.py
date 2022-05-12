from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QToolBar, QVBoxLayout, QTabWidget, \
    QDockWidget, QFileDialog, QMessageBox, QStatusBar, QLabel, QTreeView
from PyQt6.QtGui import QIcon, QFont, QAction, QFontDatabase, QFileSystemModel
from PyQt6.QtCore import Qt, QProcess, QTimer, QObject, pyqtSignal, pyqtSlot, QThread, QDir
from tempfile import gettempdir
import CodeEditor
import Console
import sys
import os

try:
    from ctypes import windll

    myappid = 'com.Shad7ows.SpectrumIDE.V2'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    print('Can\'t import ctypes lib')


class MainWin(QMainWindow):
    def __init__(self):
        super(MainWin, self).__init__()
        self.resize(1280, 720)
        self.setWindowTitle("طيف")
        self.setWindowIcon(QIcon('./icons/TaifLogo.svg'))
        self.version = '0.4.1'
        self.setFontsDataBase()

        self.centerWidget = QWidget(self)

        # self.setStyleSheet('QMenu::item::selected {background-color: red; color: yellow}')

        self.codeLay = QVBoxLayout(self.centerWidget)
        self.codeLay.setContentsMargins(0, 0, 0, 0)

        # self.file_sys_model = QFileSystemModel()
        # self.file_sys_model.setRootPath(QDir.currentPath())
        # self.tree_file_view = QTreeView()
        # self.tree_file_view.setModel(self.file_sys_model)
        # self.tree_file_view.setRootIndex(self.file_sys_model.index((QDir.currentPath())))
        # self.tree_file_view.currentChanged.connect(lambda current, previos: self.openChosenFile(current, previos))
        #
        # self.file_sys_widget = QDockWidget('مسار المشروع')
        # self.file_sys_widget.setFeatures(
        #     QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        # self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.file_sys_widget)
        # self.file_sys_widget.setWidget(self.tree_file_view)

        self.codeWin = CodeEditor.CodeEditor()

        self.resultWin = Console.Consol()

        self.tabWin = QTabWidget()
        self.tabWin.setTabsClosable(True)
        self.tabWin.setMovable(True)
        self.tabWin.tabCloseRequested.connect(lambda idx: self.closeTab(idx))
        self.newFile(False)

        self.dockWin = QDockWidget('الطرفية')
        self.dockWin.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dockWin)
        self.dockWin.setWidget(self.resultWin)

        self.charCount = CharCont(self)
        self.alifVersion()

        self.setCentralWidget(self.centerWidget)
        self.codeLay.addWidget(self.tabWin)

        self._Actions()
        self._MenuBar()
        self._toolBar()
        self.staBar()

        ########################################المتغيرات########################################

        self.temp_file = gettempdir()
        self.filePath = ''
        self.tabName = []
        self.res = 1

        #########################################################################################

    def setFontsDataBase(self):
        fonts_dir = 'fonts'
        for font in os.listdir(fonts_dir):
            QFontDatabase.addApplicationFont(os.path.join(fonts_dir, font))

    def _MenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&ملف')
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)

        examplesMenu = menuBar.addMenu('أمثلة')
        examplesMenu.addAction(self.addExampleAction)
        examplesMenu.addAction(self.WebuiExampleAction)

        helpMenu = menuBar.addMenu('مساعدة')

    def _toolBar(self):
        runToolBar = QToolBar('تشغيل')
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, runToolBar)
        runToolBar.setMovable(False)
        runToolBar.addAction(self.compileAction)
        runToolBar.addAction(self.runAction)

    def _Actions(self):
        self.newAction = QAction(QIcon('./icons/add_black.svg'), '&جديد', self)
        self.newAction.setShortcut('Ctrl+N')
        self.newAction.setStatusTip('فتح تبويب جديد... ')
        self.newAction.triggered.connect(lambda clear: self.newFile(True))

        self.openAction = QAction(QIcon('./icons/folder_open_black.svg'), '&فتح', self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip('فتح ملف... ')
        self.openAction.triggered.connect(self.openFile)
        self.saveAction = QAction(QIcon('./icons/save_black.svg'), '&حفظ', self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip('حفظ شفرة التبويب الحالي... ')
        self.saveAction.triggered.connect(self.saveFile)

        self.compileAction = QAction(QIcon('./icons/compile_black.svg'), 'ترجمة', self)
        self.compileAction.setShortcut('Ctrl+f2')
        self.compileAction.setStatusTip('بناء شفرة التبويب الحالي... ')
        self.compileAction.triggered.connect(self.compileThreadTask)
        self.runAction = QAction(QIcon('./icons/run_arrow.svg'), 'تشغيل', self)
        self.runAction.setShortcut('Ctrl+f10')
        self.runAction.setStatusTip('تنفيذ الشفرة التي تم بناؤها... ')
        self.runAction.triggered.connect(self.runThreadTask)

        self.addExampleAction = QAction('جمع عددين', self)
        self.addExampleAction.setStatusTip('فتح مثال "جمع.alif"')
        self.addExampleAction.triggered.connect(self.openAddExample)

        self.WebuiExampleAction = QAction('واجهة ويب', self)
        self.WebuiExampleAction.setStatusTip('فتح مثال "تطبيق واجهة ويب.alif"')
        self.WebuiExampleAction.triggered.connect(self.openWebuiExample)

    def staBar(self):
        self.stateBar = QStatusBar()
        self.setStatusBar(self.stateBar)
        self.stateBar.addPermanentWidget(self.charCount.char_count_lable)

    def closeTab(self, idx):
        if self.isSaved(idx):
            self.tabWin.removeTab(idx)
        if self.tabWin.tabText(idx) in self.tabName:
            self.tabName.remove(self.tabWin.tabText(idx))

    # def openChosenFile(self, current, previos):
    #     print(self.file_sys_model.filePath(current))

    def newFile(self, clear):
        codeWin = CodeEditor.CodeEditor()
        if clear:
            codeWin.clear()
        if self.tabWin.count() <= 4:
            self.tabWin.addTab(codeWin, 'غير معنون')
            self.tabWin.setCurrentWidget(codeWin)

    def openFile(self):
        self.filePath, _ = QFileDialog.getOpenFileName(self, "فتح ملف ألف", "", "كل الملفات (*.alif)")
        if self.filePath:
            if self.filePath in self.tabName:
                self.setTabByName(self.filePath)
                idx = self.tabWin.currentIndex()
                self.isSaved(idx)
            else:
                self.newFile(True)
                with open(self.filePath, "r", encoding="utf-8") as openFile:
                    fileCode = openFile.read()
                    self.tabWin.currentWidget().setPlainText(fileCode)
                    openFile.close()
                self.tabWin.setTabText(self.tabWin.currentIndex(), self.filePath)
                self.tabName.append(self.filePath)

    def setTabByName(self, pathName):
        for indx in range(self.tabWin.count()):
            tabName = self.tabWin.tabText(indx)
            if pathName == tabName:
                return self.tabWin.setCurrentIndex(indx)

    def saveFile(self, idx):
        tabChild = self.tabWin.widget(idx)
        alifCode = tabChild.toPlainText()

        if self.tabWin.tabText(idx) != 'غير معنون':
            with open(self.tabWin.tabText(idx), "w", encoding="utf-8") as saveFile:
                saveFile.write(alifCode)
                saveFile.close()
        else:
            self.filePath, _ = QFileDialog.getSaveFileName(self, "حفظ ملف ألف", "غير معنون.alif", "ملف ألف (*.alif)")
            if self.filePath:
                with open(self.filePath, "w", encoding="utf-8") as saveFile:
                    saveFile.write(alifCode)
                    saveFile.close()
                self.tabWin.setTabText(idx, self.filePath)
                self.tabName.append(self.filePath)
            else:
                return ''

    def isSaved(self, idx):
        if self.tabWin.widget(idx).document().isModified():
            result = self.msgBox("حفظ الملف", "هل تريد حفظ الملف؟", "حفظ", "عدم الحفظ", "إلغاء")
            if result == 0:
                self.saveFile(idx)
                if not self.filePath:
                    return False
            elif result == 2:
                return False
        return True

    def msgBox(self, title, text, frstBtn, scndBtn, thrdBtn):
        msgBox = QMessageBox()
        msgBox.addButton(frstBtn, QMessageBox.ButtonRole.YesRole)
        msgBox.addButton(scndBtn, QMessageBox.ButtonRole.NoRole)
        msgBox.addButton(thrdBtn, QMessageBox.ButtonRole.RejectRole)
        msgBox.setWindowTitle(title)
        msgBox.setWindowIcon(QIcon("./Icons/TaifLogo.svg"))
        msgBox.setText(text)
        msgBox.exec()
        return msgBox.result()

    def compileThreadTask(self):
        self.compile_thread = CompileThread()
        self.thread = QThread()
        self.compile_thread.moveToThread(self.thread)
        self.thread.started.connect(self.compile_thread.run)
        self.compile_thread.result_signal.connect(self.codeCompile)
        self.thread.start()
        self.compileAction.setEnabled(False)
        self.runAction.setEnabled(False)
        self.thread.finished.connect(lambda: self.compileAction.setEnabled(True))
        self.thread.finished.connect(lambda: self.runAction.setEnabled(True))

    def runThreadTask(self):
        self.run_thread = RunThread()
        self.thread = QThread()
        self.run_thread.moveToThread(self.thread)
        self.thread.started.connect(self.run_thread.run)
        self.run_thread.read_data_signal.connect(self.runCode)
        self.thread.start()
        self.compileAction.setEnabled(False)
        self.runAction.setEnabled(False)
        self.thread.finished.connect(lambda: self.compileAction.setEnabled(True))
        self.thread.finished.connect(lambda: self.runAction.setEnabled(True))

    @pyqtSlot(int, float)
    def codeCompile(self, res: int, build_time: float):
        self.temp_file = gettempdir()
        self.res = res

        if res == 0:
            self.resultWin.setPlainText(f"[انتهى البناء خلال: {build_time} ثانية]")
        elif res == 1:
            log = os.path.join(self.temp_file, "temp.alif.log")
            logOpen = open(log, "r", encoding="utf-8")
            self.resultWin.setPlainText(logOpen.read())
            logOpen.close()
        elif res == -2:
            self.resultWin.setPlainText("تحقق من أن لغة ألف 3 مثبتة بشكل صحيح")

    @pyqtSlot(str)
    def runCode(self, data: str):
        self.resultWin.appendPlainText(data)

    # def runCode(self):
    #     if self.res == 0:
    #         if sys.platform == "linux":
    #             self.process = QProcess()
    #             self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
    #             self.process.readyRead.connect(self.ifReadReady)
    #             self.process.start(os.path.join(self.temp_file, "./temp"))
    #         else:
    #             self.process = QProcess()
    #             self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
    #             self.process.readyRead.connect(self.ifReadReady)
    #             self.process.start(os.path.join(self.temp_file, "temp.exe"))
    #     else:
    #         self.resultWin.appendPlainText("قم ببناء الشفرة أولاً")
    #
    # def ifReadReady(self):
    #     # self.resultWin.setReadOnly(False)
    #     self.resultWin.appendPlainText(str(self.process.readAll(), "utf8"))

    def openAddExample(self):
        plain_text_example = CodeEditor.CodeEditor()
        self.tabWin.addTab(plain_text_example, 'جمع.alif')
        self.tabWin.setCurrentWidget(plain_text_example)
        with open("./example/جمع.alif", "r", encoding="utf-8") as example:
            exampleRead = example.read()
            self.tabWin.currentWidget().setPlainText(exampleRead)
            example.close()

    def openWebuiExample(self):
        plain_text_example = CodeEditor.CodeEditor()
        self.tabWin.addTab(plain_text_example, 'تطبيق واجهة ويب.alif')
        self.tabWin.setCurrentWidget(plain_text_example)
        with open("./example/تطبيق واجهة ويب.alif", "r", encoding="utf-8") as example:
            exampleRead = example.read()
            self.tabWin.currentWidget().setPlainText(exampleRead)
            example.close()

    def alifVersion(self):
        alif_version = '--v'
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.alifVersionStatusBar)
        self.process.start("alif", [alif_version])

    def alifVersionStatusBar(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        stdout = stdout.split(' ')
        stdout = stdout[2].strip('v')
        stdout = f'ألف {stdout}'
        version_lable = QLabel(stdout)
        version_lable.setFont(QFont('Alusus Mono Medium'))
        self.stateBar.addPermanentWidget(version_lable)


class CompileThread(QObject):
    result_signal = pyqtSignal(int, float)

    def __init__(self):
        super(CompileThread, self).__init__()

    def run(self):
        timer = QTimer()
        timer.start(60000)

        code = mainWin.tabWin.currentWidget().toPlainText()
        temp_file = gettempdir()

        with open(os.path.join(temp_file, "temp.alif"), "w", encoding="utf-8") as temporaryFile:
            temporaryFile.write(code)
            temporaryFile.close()

        process = QProcess()
        alifCodeCompile = os.path.join(temp_file, "temp.alif")
        res = process.execute("alif", [alifCodeCompile])
        process.kill()

        remine_time = timer.remainingTime()
        build_time = (60000 - remine_time) / 1000
        timer.stop()

        self.result_signal.emit(res, build_time)
        mainWin.thread.quit()


class RunThread(QObject):
    read_data_signal = pyqtSignal(str)

    def __init__(self):
        super(RunThread, self).__init__()

    def run(self):
        res = mainWin.res
        temp_file = mainWin.temp_file
        if res == 0:
            if sys.platform == "linux":
                self.process = QProcess()
                self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                self.process.readyRead.connect(self.ifReadReady)
                self.process.start(os.path.join(temp_file, "./temp"))
            else:
                self.process = QProcess()
                self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                self.process.readyRead.connect(self.ifReadReady)
                self.process.start(os.path.join(temp_file, "temp.exe"))
        else:
            mainWin.resultWin.appendPlainText("قم ببناء الشفرة أولاً")
            mainWin.thread.quit()

    def ifReadReady(self):
        data = self.process.readAll()
        data = bytes(data).decode('utf8')
        print(data, type(data))
        self.read_data_signal.emit(data)
        mainWin.thread.quit()


class CharCont:
    def __init__(self, MainWin):
        super(CharCont, self).__init__()
        self.mainWin = MainWin
        self.char_count_lable = QLabel(f'{self.char_count()} حرف   ')
        self.char_count_lable.setFont(QFont("Alusus Mono Medium"))
        self.mainWin.tabWin.widget(0).textChanged.connect(self.charCount)
        self.mainWin.tabWin.currentChanged.connect(lambda idx: self.changeCharCount(idx))

    def changeCharCount(self, idx):
        self.char_count_tab = len(self.mainWin.tabWin.widget(idx).toPlainText())
        self.char_count_lable.setText(f'{self.char_count_tab} حرف   ')
        self.mainWin.tabWin.widget(idx).textChanged.connect(self.charCount)

    def charCount(self):
        self.char_count_lable.setText(f'{self.char_count()} حرف   ')

    def char_count(self):
        return len(self.mainWin.tabWin.currentWidget().toPlainText())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setFont(QFont('Tajawal', 10))
    mainWin = MainWin()
    mainWin.show()
    sys.exit(app.exec())
