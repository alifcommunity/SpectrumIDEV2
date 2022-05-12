from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtCore import Qt


class Consol(QPlainTextEdit):
    def __init__(self):
        super(Consol, self).__init__()

        self.resultDoc = self.document().defaultTextOption()
        self.resultDoc.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.document().setDefaultTextOption(self.resultDoc)
        self.setReadOnly(True)

    # def Lexer(self):
    #     if len(self.toPlainText()) < 3:
    #         self.insertPlainText('>')
    #
    #
    # def keyPressEvent(self, event):
    #     super(Consol, self).keyPressEvent(event)
    #     if event.key() == Qt.Key.Key_Backspace:
    #         self.Lexer()
    #     if event.key() == Qt.Key.Key_Return:
    #         self.insertPlainText('>>>')
    #     event.accept()
