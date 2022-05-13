######################################################################
# استيراد المكاتب
######################################################################

from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QToolBar, QVBoxLayout, QTabWidget, \
    QDockWidget, QFileDialog, QMessageBox, QStatusBar, QLabel, QTreeView
from PyQt6.QtGui import QIcon, QFont, QAction, QFontDatabase, QFileSystemModel
from PyQt6.QtCore import Qt, QProcess, QTimer, QObject, pyqtSignal, pyqtSlot, QThread, QDir
from tempfile import gettempdir
import CodeEditor
from Console import Consol, InputLine
import sys
import os

try:
    from ctypes import windll

    appID = 'com.Shad7ows.SpectrumIDE.V2'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)
except ImportError:
    print('Can\'t import ctypes lib')


######################################################################
# الصنف الرئيسي
######################################################################

class MainWin(QMainWindow):
    def __init__(self):
        super(MainWin, self).__init__()
        self.resize(1280, 720)
        self.setWindowTitle("طيف")
        self.setWindowIcon(QIcon('./icons/TaifLogo.svg'))
        self.version = '0.4.2'
        self.set_fonts_database()

        self.centerWidget = QWidget(self)

        # self.setStyleSheet('QMenu::item::selected {background-color: red; color: yellow}')

        self.codeLay = QVBoxLayout(self.centerWidget)
        self.codeLay.setContentsMargins(0, 0, 0, 0)

        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath(QDir.currentPath())
        self.fileView = QTreeView()
        self.fileView.doubleClicked.connect(lambda idx: self.open_selected_file(idx))
        self.fileView.setModel(self.fileModel)
        # self.fileView.setRootIndex(self.fileModel.index((QDir.currentPath())))

        self.fileWidget = QDockWidget('مسار المشروع')
        self.fileWidget.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.fileWidget)
        self.fileWidget.setWidget(self.fileView)

        self.codeWin = CodeEditor.CodeEditor()

        self.tabWin = QTabWidget()
        self.tabWin.setTabsClosable(True)
        self.tabWin.setMovable(True)
        self.tabWin.tabCloseRequested.connect(lambda idx: self.close_tab(idx))
        self.new_file(False)

        self.consoleWidget = QWidget()
        self.consoleLayout = QVBoxLayout()
        self.consoleLayout.setContentsMargins(0, 0, 0, 0)
        self.resultWin = Consol()
        self.inputLine = InputLine()

        self.dockWin = QDockWidget('الطرفية')
        self.dockWin.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dockWin)
        self.dockWin.setWidget(self.consoleWidget)
        self.consoleWidget.setLayout(self.consoleLayout)
        self.consoleLayout.addWidget(self.resultWin)
        self.consoleLayout.addWidget(self.inputLine)

        self.charCount = CharCont(self)
        self.alif_version()

        self.setCentralWidget(self.centerWidget)
        self.codeLay.addWidget(self.tabWin)

        self._Actions()
        self._menu_bar()
        self._tool_bar()
        self._status_bar()

        ######################################################################
        # المتغيرات
        ######################################################################

        self.tempFile = gettempdir()
        self.filePath = ''
        self.tabName = []
        self.compileResult = 1

        ######################################################################
        # الدوال
        ######################################################################

    def set_fonts_database(self):
        fontsDir = 'fonts'
        for font in os.listdir(fontsDir):
            QFontDatabase.addApplicationFont(os.path.join(fontsDir, font))

    def _menu_bar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&ملف')
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)

        examplesMenu = menuBar.addMenu('أمثلة')
        examplesMenu.addAction(self.addExampleAction)
        examplesMenu.addAction(self.WebuiExampleAction)

        helpMenu = menuBar.addMenu('مساعدة')

    def _tool_bar(self):
        runToolBar = QToolBar('تشغيل')
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, runToolBar)
        runToolBar.setMovable(False)
        runToolBar.addAction(self.compileAction)
        runToolBar.addAction(self.runAction)

    def _Actions(self):
        self.newAction = QAction(QIcon('./icons/add_black.svg'), '&جديد', self)
        self.newAction.setShortcut('Ctrl+N')
        self.newAction.setStatusTip('فتح تبويب جديد... ')
        self.newAction.triggered.connect(lambda clear: self.new_file(True))

        self.openAction = QAction(QIcon('./icons/folder_open_black.svg'), '&فتح', self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip('فتح ملف... ')
        self.openAction.triggered.connect(self.open_file)
        self.saveAction = QAction(QIcon('./icons/save_black.svg'), '&حفظ', self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip('حفظ شفرة التبويب الحالي... ')
        self.saveAction.triggered.connect(self.save_file)

        self.compileAction = QAction(QIcon('./icons/compile_black.svg'), 'ترجمة', self)
        self.compileAction.setShortcut('Ctrl+f2')
        self.compileAction.setStatusTip('بناء شفرة التبويب الحالي... ')
        self.compileAction.triggered.connect(self.compile_thread_task)
        self.runAction = QAction(QIcon('./icons/run_arrow.svg'), 'تشغيل', self)
        self.runAction.setShortcut('Ctrl+f10')
        self.runAction.setStatusTip('تنفيذ الشفرة التي تم بناؤها... ')
        self.runAction.triggered.connect(self.run_thread_task)

        self.addExampleAction = QAction('جمع عددين', self)
        self.addExampleAction.setStatusTip('فتح مثال "جمع.alif"')
        self.addExampleAction.triggered.connect(self.open_add_example)

        self.WebuiExampleAction = QAction('واجهة ويب', self)
        self.WebuiExampleAction.setStatusTip('فتح مثال "تطبيق واجهة ويب.alif"')
        self.WebuiExampleAction.triggered.connect(self.open_webui_example)

    def _status_bar(self):
        self.stateBar = QStatusBar()
        self.setStatusBar(self.stateBar)
        self.stateBar.addPermanentWidget(self.charCount.charCountLable)

    def close_tab(self, idx):
        if self.is_saved(idx):
            self.tabWin.removeTab(idx)
        if self.tabWin.tabText(idx) in self.tabName:
            self.tabName.remove(self.tabWin.tabText(idx))

    def open_selected_file(self, idx):
        filePath = self.fileModel.filePath(idx)
        fileExtention = filePath.split('.')[-1]
        if fileExtention == 'alif':
            if filePath in self.tabName:
                self.set_tab_by_name(filePath)
                idx = self.tabWin.currentIndex()
                self.is_saved(idx)
            else:
                self.new_file(True)
                with open(filePath, "r", encoding="utf-8") as openFile:
                    fileCode = openFile.read()
                    self.tabWin.currentWidget().setPlainText(fileCode)
                    openFile.close()
                self.tabWin.setTabText(self.tabWin.currentIndex(), filePath)
                self.tabName.append(filePath)

    def new_file(self, clear):
        codeWin = CodeEditor.CodeEditor()
        if clear:
            codeWin.clear()
        if self.tabWin.count() <= 4:
            self.tabWin.addTab(codeWin, 'غير معنون')
            self.tabWin.setCurrentWidget(codeWin)

    def open_file(self):
        self.filePath, _ = QFileDialog.getOpenFileName(self, "فتح ملف ألف", "", "كل الملفات (*.alif)")
        if self.filePath:
            if self.filePath in self.tabName:
                self.set_tab_by_name(self.filePath)
                idx = self.tabWin.currentIndex()
                self.is_saved(idx)
            else:
                self.new_file(True)
                with open(self.filePath, "r", encoding="utf-8") as openFile:
                    fileCode = openFile.read()
                    self.tabWin.currentWidget().setPlainText(fileCode)
                    openFile.close()
                self.tabWin.setTabText(self.tabWin.currentIndex(), self.filePath)
                self.tabName.append(self.filePath)

    def set_tab_by_name(self, pathName):
        for indx in range(self.tabWin.count()):
            tabName = self.tabWin.tabText(indx)
            if pathName == tabName:
                return self.tabWin.setCurrentIndex(indx)

    def save_file(self, idx):
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

    def is_saved(self, idx):
        if self.tabWin.widget(idx).document().isModified():
            result = self.msgBox("حفظ الملف", "هل تريد حفظ الملف؟", "حفظ", "عدم الحفظ", "إلغاء")
            if result == 0:
                self.save_file(idx)
                if not self.filePath:
                    return False
            elif result == 2:
                return False
        return True

    def msg_box(self, title, text, firstBtn, secondBtn, therdBtn):
        msgBox = QMessageBox()
        msgBox.addButton(firstBtn, QMessageBox.ButtonRole.YesRole)
        msgBox.addButton(secondBtn, QMessageBox.ButtonRole.NoRole)
        msgBox.addButton(therdBtn, QMessageBox.ButtonRole.RejectRole)
        msgBox.setWindowTitle(title)
        msgBox.setWindowIcon(QIcon("./Icons/TaifLogo.svg"))
        msgBox.setText(text)
        msgBox.exec()
        return msgBox.result()

    def compile_thread_task(self):
        self.compileThread = CompileThread()
        self.thread = QThread()
        self.compileThread.moveToThread(self.thread)
        self.thread.started.connect(self.compileThread.run)
        self.compileThread.resultSignal.connect(self.code_compile)
        self.thread.start()
        self.compileAction.setEnabled(False)
        self.runAction.setEnabled(False)
        self.thread.finished.connect(lambda: self.compileAction.setEnabled(True))
        self.thread.finished.connect(lambda: self.runAction.setEnabled(True))

    def run_thread_task(self):
        self.runThread = RunThread()
        self.thread = QThread()
        self.runThread.moveToThread(self.thread)
        self.thread.started.connect(self.runThread.run)
        self.runThread.readDataSignal.connect(self.run_code)
        self.thread.start()
        self.compileAction.setEnabled(False)
        self.runAction.setEnabled(False)
        self.thread.finished.connect(lambda: self.compileAction.setEnabled(True))
        self.thread.finished.connect(lambda: self.runAction.setEnabled(True))

    @pyqtSlot(int, float)
    def code_compile(self, compileResult: int, build_time: float):
        self.compileResult = compileResult

        if compileResult == 0:
            self.resultWin.setPlainText(f"[انتهى البناء خلال: {build_time} ثانية]")
        elif compileResult == 1:
            log = os.path.join(self.tempFile, "temp.alif.log")
            logOpen = open(log, "r", encoding="utf-8")
            self.resultWin.setPlainText(logOpen.read())
            logOpen.close()
        elif compileResult == -2:
            self.resultWin.setPlainText("تحقق من أن لغة ألف 3 مثبتة بشكل صحيح")

    @pyqtSlot(str)
    def run_code(self, data: str):
        self.resultWin.appendPlainText(data)

    def open_add_example(self):
        plain_text_example = CodeEditor.CodeEditor()
        self.tabWin.addTab(plain_text_example, 'جمع.alif')
        self.tabWin.setCurrentWidget(plain_text_example)
        with open("./example/جمع.alif", "r", encoding="utf-8") as example:
            exampleRead = example.read()
            self.tabWin.currentWidget().setPlainText(exampleRead)
            example.close()

    def open_webui_example(self):
        plainTextExample = CodeEditor.CodeEditor()
        self.tabWin.addTab(plainTextExample, 'تطبيق واجهة ويب.alif')
        self.tabWin.setCurrentWidget(plainTextExample)
        with open("./example/تطبيق واجهة ويب.alif", "r", encoding="utf-8") as example:
            exampleRead = example.read()
            self.tabWin.currentWidget().setPlainText(exampleRead)
            example.close()

    def alif_version(self):
        alifVersion = '--v'
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.alif_version_statusbar)
        self.process.start("alif", [alifVersion])

    def alif_version_statusbar(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        stdout = stdout.split(' ')
        stdout = stdout[2].strip('v')
        stdout = f'ألف {stdout}'
        versionLable = QLabel(stdout)
        versionLable.setFont(QFont('Alusus Mono Medium'))
        self.stateBar.addPermanentWidget(versionLable)


######################################################################
# مسلك الترجمة
######################################################################

class CompileThread(QObject):
    resultSignal = pyqtSignal(int, float)

    def __init__(self):
        super(CompileThread, self).__init__()

    def run(self):
        timer = QTimer()
        timer.start(60000)

        code = mainWin.tabWin.currentWidget().toPlainText()
        tempFile = mainWin.tempFile

        with open(os.path.join(tempFile, "temp.alif"), "w", encoding="utf-8") as temporaryFile:
            temporaryFile.write(code)
            temporaryFile.close()

        process = QProcess()
        alifCodeCompile = os.path.join(tempFile, "temp.alif")
        compileResult = process.execute("alif", [alifCodeCompile])
        process.kill()

        remineTime = timer.remainingTime()
        buildTime = (60000 - remineTime) / 1000
        timer.stop()

        self.resultSignal.emit(compileResult, buildTime)
        mainWin.thread.quit()


######################################################################
# مسلك التشغيل
######################################################################

class RunThread(QObject):
    readDataSignal = pyqtSignal(str)

    def __init__(self):
        super(RunThread, self).__init__()
        mainWin.inputLine.returnPressed.connect(self.wait_input)
        self.process = None

    def run(self):
        compileResult = mainWin.compileResult
        tempFile = mainWin.tempFile

        if compileResult == 0:
            if sys.platform == "linux":
                self.process = QProcess()
                self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                self.process.readyRead.connect(self.ifReadReady)
                self.process.start(os.path.join(tempFile, "./temp"))
            else:
                self.process = QProcess()
                self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
                self.process.readyRead.connect(self.ifReadReady)
                self.process.start(os.path.join(tempFile, "temp.exe"))
        else:
            mainWin.resultWin.appendPlainText("قم ببناء الشفرة أولاً")
            mainWin.thread.quit()

    def ifReadReady(self):
        data = self.process.readAll()
        data = bytes(data).decode('utf8')
        self.readDataSignal.emit(data)
        self.process.finished.connect(mainWin.thread.quit)

    def wait_input(self):
        if self.process != None:
            dataWrite = mainWin.inputLine.text() + '\n'
            dataWriteByte = dataWrite.encode()
            self.process.write(dataWriteByte)

######################################################################
# عداد الحروف
######################################################################

class CharCont:
    def __init__(self, MainWin):
        super(CharCont, self).__init__()
        self.mainWin = MainWin
        self.charCountLable = QLabel(f'{self.char_count()} حرف   ')
        self.charCountLable.setFont(QFont("Alusus Mono Medium"))
        self.mainWin.tabWin.widget(0).textChanged.connect(self.charCount)
        self.mainWin.tabWin.currentChanged.connect(lambda idx: self.changeCharCount(idx))

    def changeCharCount(self, idx):
        self.charCountTab = len(self.mainWin.tabWin.widget(idx).toPlainText())
        self.charCountLable.setText(f'{self.charCountTab} حرف   ')
        self.mainWin.tabWin.widget(idx).textChanged.connect(self.charCount)

    def charCount(self):
        self.charCountLable.setText(f'{self.char_count()} حرف   ')

    def char_count(self):
        return len(self.mainWin.tabWin.currentWidget().toPlainText())


######################################################################
# تشغيل التطبيق
######################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setFont(QFont('Tajawal', 10))
    mainWin = MainWin()
    mainWin.show()
    sys.exit(app.exec())
