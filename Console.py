from PyQt6.QtWidgets import QPlainTextEdit, QLineEdit
from PyQt6.QtCore import Qt


class Consol(QPlainTextEdit):
    def __init__(self):
        super(Consol, self).__init__()

        self.resultDoc = self.document().defaultTextOption()
        self.resultDoc.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.document().setDefaultTextOption(self.resultDoc)
        self.setFrameStyle(0)
        self.setReadOnly(True)


class InputLine(QLineEdit):
    def __init__(self):
        super(InputLine, self).__init__()

        self.setPlaceholderText('المدخلات')
        self.setFrame(False)