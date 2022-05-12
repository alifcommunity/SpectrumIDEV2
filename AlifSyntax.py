from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

blue = "#0025FF"
lightBlue = "#4946FF"
darkMagenta = "#D16335"
greenYellow = "#317A17"
fireRed = "#FF0000"
gray = "#636363"
lightPurple = "#7C35D1"

def format(color, style=''):
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'black' in style:
        _format.setFontWeight(QFont.Weight.Black)
    if 'bold' in style:
        _format.setFontWeight(QFont.Weight.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

STYLES = {
    'library': format(lightPurple, 'black'),
    'keyword': format(blue, 'bold'),
    'operator': format(lightBlue),
    'brace': format(gray),
    'string': format(greenYellow),
    'comment': format(gray),
    'numbers': format(fireRed),
    'injlang': format(darkMagenta, 'italic')
}


class AlifHighlighter(QSyntaxHighlighter):
    library = [
        'ألف', 'مكتبة', 'نص'
    ]

    keywords = [
        'صنف', 'كائن', 'دالة', 'إذا', 'أو', 'وإلا', 'و', 'عدد', 'نص', 'اطبع',
        'نافذة', 'كلما', 'نهاية', 'رئيسية', 'إرجاع'
    ]

    operators = [
        '=',

        '==', '!=', '<', '<=', '>', '>=',

        '\+', '-', '\*', '/', '//', '\%', '\*\*',

        '\+=', '-=', '\*=', '/=', '\%=',

        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    injlang = [
        '_ج_', '_ب_', '_س_'
    ]

    def __init__(self, document):
        super(AlifHighlighter, self).__init__(document)

        rules = []


        rules += [('#%s($|[^\u0621-\u064A[^0-9]]*)' % l, 0, STYLES['library'])
                  for l in AlifHighlighter.library]
        rules += [('(?:%s)(?![\w\u0621-\u064A])' % w, 0, STYLES['keyword'])
                  for w in AlifHighlighter.keywords]
        rules += [('%s' % o, 0, STYLES['operator'])
                  for o in AlifHighlighter.operators]
        rules += [('%s' % b, 0, STYLES['brace'])
                  for b in AlifHighlighter.braces]
        rules += [('%s' % i, 0, STYLES['injlang'])
                  for i in AlifHighlighter.injlang]

        rules += [
            (r' [^ء-ي ]*[+-]?[0-9]+|^[+-]?[0-9]+', 0, STYLES['numbers']),
            (r' [^ء-ي ]*[+-]?[٠-٩]+|^[+-]?[٠-٩]+', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+\b', 0, STYLES['numbers']),
        ]

        rules += [
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r'--[^\n]*', 0, STYLES['comment']),
        ]

        self.rules = [(QRegularExpression(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        for expression, nth, format in self.rules:
            match = expression.globalMatch(text, 0)

            while match.hasNext():
                matched = match.next()
                index = matched.capturedStart()
                length = matched.capturedLength()
                self.setFormat(index, length, format)
