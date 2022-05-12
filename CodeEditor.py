from PyQt6.QtWidgets import QPlainTextEdit, QFrame
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtCore import Qt, QRect
import AlifSyntax


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super(CodeEditor, self).__init__()
        self.setFont(QFont("Alusus Mono Medium", 12))
        self.lineNumberArea = NumsBar(self)
        self.highlight = AlifSyntax.AlifHighlighter(self.document())
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        editorDoc = self.document().defaultTextOption()
        editorDoc.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.document().setDefaultTextOption(editorDoc)
        self.setTabStopDistance(32)
        self.openExample()

    def openExample(self):
        with open("./example/مرحبا بالعالم.alif", "r", encoding="utf-8") as example:
            exampleRead = example.read()
            self.setPlainText(exampleRead)
            example.close()

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.document().blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(0, 0, self.lineNumberAreaWidth() + 5, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberAreaWidth(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.right() - self.lineNumberAreaWidth() - 5, cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def PaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QColor("#252525"))
                painter.setFont(QFont("Alusus Mono Medium"))
                painter.drawText(0, int(top), self.lineNumberArea.width(), height, Qt.AlignmentFlag.AlignLeft, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


class NumsBar(QFrame):
    def __init__(self, editor):
        super(NumsBar, self).__init__(editor)
        self.editor = editor

    def paintEvent(self, event):
        self.editor.PaintEvent(event)
