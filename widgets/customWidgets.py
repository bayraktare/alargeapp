from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QRegExpValidator, QRegularExpressionValidator
from PyQt6.QtCore import QRegExp, QRegularExpression


class DateLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText('YYYY/MM/DD')
        self.setMaxLength(10)

        regEx = QRegExp(
            r'^(?:19|20)\d\d/(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])$'
        )
        
        self.validator = QRegExpValidator(regEx, self)
        self.setValidator(self.validator)

        self.textChanged.connect(self.onTextChanged)

    def onTextChanged(self):
        text = self.text()
        
        digits = ''.join(c for c in text if c.isdigit())
        
        if len(digits) >= 8:
            formatted_text = f'{digits[:4]}/{digits[4:6]}/{digits[6:8]}'
        elif len(digits) >= 6:
            formatted_text = f'{digits[:4]}/{digits[4:6]}/{digits[6:]}'
        elif len(digits) >= 4:
            formatted_text = f'{digits[:4]}/{digits[4:]}'
        else:
            formatted_text = digits
        
        if self.text() != formatted_text:
            self.blockSignals(True)
            self.setText(formatted_text)
            self.setCursorPosition(len(formatted_text))
            self.blockSignals(False)

class PercentageLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Percentage")
        self.setMaxLength(7)
        
        self.regEx = QRegularExpression(r'^(?:100|[0-9]|[1-9][0-9])(\.[0-9]{1,2})?$')
        self.validator = QRegularExpressionValidator(self.regEx, self)
        self.setValidator(self.validator)
        
        self.editingFinished.connect(self.onEditingFinished)
    
    def onEditingFinished(self):
        text = self.text()
        
        if text.endswith('%'):
            text = text[:-1]
        
        match = self.regEx.match(text)
        
        if match.hasMatch():
            try:
                number = float(text)
                if 0.0 <= number <= 100.0:
                    formatted_text = f"{number:.2f}%"
                    self.blockSignals(True)
                    self.setText(formatted_text)
                    self.blockSignals(False)
                    self.setCursorPosition(len(formatted_text))
            except ValueError:
                pass        
            
class PhoneNumLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
        regEx = QRegExp(r'^\+\d{1,4}\s\d{7,15}$')
        validator = QRegExpValidator(regEx, self)
        
        self.setValidator(validator)
        self.setPlaceholderText("+ (CountryCode) phone number")

class IPAddressLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        regex_pattern = (
            r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        
        regEx = QRegExp(regex_pattern)
        validator = QRegExpValidator(regEx, self)
        
        self.setValidator(validator)
