from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4, inch
from reportlab.graphics.shapes import Line, LineShape, Drawing
from reportlab.lib.colors import Color, HexColor
import os

HOME = os.getcwd()

class FooterCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.width, self.height = A4

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if (self._pageNumber >= 1):
                # self.setFillColor(HexColor('#861a22'))
                # self.setStrokeColor(HexColor('#861a22'))
                # self.rect(0, 751, self.width, self.height, fill=1)
                
                
                self.draw_header(os.path.join(HOME, 'resources/headerInfo.txt'))

            canvas.Canvas.showPage(self)
            
        canvas.Canvas.save(self)



    def draw_header(self, path):
        img = Image(os.path.join(HOME, 'resources/redlogo.png')) ###### conpany infodan logo
        width, height = img.wrap(0, 0)
        aspect_ratio = width / height
        
        img.drawHeight = self.height * 0.09
        img.drawWidth = self.height * 0.09 * aspect_ratio
        
        headerFormat = ParagraphStyle('Helvetica', fontSize=9, leading=10, justifyBreaks=1, alignment=TA_RIGHT, justifyLastLine=1)
        headerInfo = self.getHeaderInfo(path)
        singles, labels, info = headerInfo

        textBuffer = []
        singlesBuffer = []
        for single in singles:
            text = f"""<font color="#ffffff">{single}<br/>"""
            singlesBuffer.append(Paragraph(single, headerFormat))
        
        for label, info in zip(labels, info):
            text = f"""<font color="#000000">{label}</font>{info}<br/>"""
            textBuffer.append(text)
        
        result = []
        for i in range(0, len(textBuffer), 2):
            if i + 2 <= len(textBuffer):
                result.append([Paragraph(textBuffer[i], headerFormat), Paragraph(textBuffer[i + 1], headerFormat)])
        
        infoTable = Table(result, colWidths=[self.width * 0.30, self.width * 0.30])
        infoTable.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 1)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('HALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        content = [singlesBuffer, infoTable]
        
        header = [
            [img, content]
        ]
        
        headerTable = Table(header, colWidths=[(self.width - 1.3 * inch) / 3, (self.width - 1.3 * inch) / 3 * 2])
        
        headerTable.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), (0, 0, 1)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('HALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        headerTable.wrapOn(self, width, height)
        headerTable.drawOn(self, inch / 2, self.height - inch * 1.2)

    @staticmethod
    def getHeaderInfo(path):
        try:
            headerInfoPath = path
            info = []
            labels = []
            singles = []
            with open(headerInfoPath, 'r') as file: 
                lines = file.readlines()
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if i == 0:
                        singles.append(line)
                        continue
                    
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        before_colon, after_colon = parts
                        info.append(after_colon)
                        labels.append(before_colon + ":")
                    else:
                        singles.append(parts)
            
            return singles, labels, info
        except FileNotFoundError:
            print(f"Error: The file {headerInfoPath} does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

class PDFPSReporte:

    def __init__(self, path, input_raw_material, input_manufacturing_date, component_layout):
        
        self.path = path

        self.styleSheet = getSampleStyleSheet()
        self.elements = []

        # colors - Azul turkeza 367AB3
        self.colorOhkaGreen0 = Color((45.0 / 255), (166.0 / 255), (153.0 / 255), 1)
        self.colorOhkaGreen1 = Color((182.0 / 255), (227.0 / 255), (166.0 / 255), 1)
        self.colorOhkaGreen2 = Color((140.0 / 255), (222.0 / 255), (192.0 / 255), 1)
        self.colorOhkaBlue0 = Color((54.0 / 255), (122.0 / 255), (179.0 / 255), 1)
        self.colorOhkaBlue1 = Color((122.0 / 255), (180.0 / 255), (225.0 / 255), 1)
        self.colorOhkaGreenLineas = Color((50.0 / 255), (140.0 / 255), (140.0 / 255), 1)
        self.colorAlargeDarkRed = Color((134.0 / 255), (26.0 / 255), (34.0 / 255), 1)
        self.colorBlack = Color(0, 0, 0, 1)  # Define black color

        self.raw_material= input_raw_material.text()
        self.manufacturing_date = input_manufacturing_date.text()
        self.component_layout = component_layout
        

        self.nextPagesHeader(True)
        self.remoteSessionTableMaker()
        self.doc = SimpleDocTemplate(path, pagesize=A4)
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    def nextPagesHeader(self, isSecondPage):
        if isSecondPage:
            spacer = Spacer(10, 30)
            self.elements.append(spacer)
            psHeaderText = ParagraphStyle('Helvetica', fontSize=25, alignment=TA_LEFT, borderWidth=3, textColor=self.colorBlack)
            text = self.raw_material
            paragraphReportHeader = Paragraph(text, psHeaderText)
            self.elements.append(paragraphReportHeader)
            
            
            

            spacer = Spacer(10, 20)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-52, 0, 492, 0)
            line.strokeColor = self.colorAlargeDarkRed
            line.strokeWidth = 2
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 1)
            self.elements.append(spacer)

            d = Drawing(500, 1)
            line = Line(-50, 0, 490, 0)
            line.strokeColor = self.colorAlargeDarkRed
            line.strokeWidth = 0.5
            d.add(line)
            self.elements.append(d)

            spacer = Spacer(10, 10)
            self.elements.append(spacer)

    def remoteSessionTableMaker(self):        

        """
        Create the line items
        """
        d = []
        textData = ["Component Name", "Percent", "Supplier Name"]
        fontSize = 8
        leftside = ParagraphStyle(name="leftside", alignment=TA_LEFT)
        rightside = ParagraphStyle(name="rightside", alignment=TA_RIGHT)
        for text in textData:
            ptext = "<font size='%s'><b>%s</b></font>" % (fontSize+1, text)
            titlesTable = Paragraph(ptext, leftside)
            d.append(titlesTable)        

        data = [d]
        formattedLineData = []

        alignStyle = [ParagraphStyle(name="01", alignment=TA_LEFT),
                      ParagraphStyle(name="02", alignment=TA_LEFT),
                      ParagraphStyle(name="03", alignment=TA_LEFT)]

        
        for i in range(self.component_layout.count()):
            layout_item = self.component_layout.itemAt(i)
            if layout_item is not None:
                component_name_widget = layout_item.itemAt(0)
                component_percent_widget = layout_item.itemAt(1)
                supplier_name_widget = layout_item.itemAt(2)

                if component_name_widget is not None and component_percent_widget is not None and supplier_name_widget is not None:
                    component_name = component_name_widget.widget().text()
                    component_percent = component_percent_widget.widget().text()
                    supplier_name = supplier_name_widget.widget().text()
                    lineData = [component_name, component_percent, supplier_name]
                    columnNumber = 0
                    for item in lineData:
                        ptext = "<font size='%s'>%s</font>" % (fontSize - 1, item)
                        p = Paragraph(ptext, alignStyle[columnNumber])
                        formattedLineData.append(p)
                        columnNumber += 1
                    data.append(formattedLineData)
                    formattedLineData = []

        # Row for total
        totalRow = ["Manufacturing Date:", "", self.manufacturing_date]
        for item in totalRow:
            ptext = "<font size='%s'>%s</font>" % (fontSize, item)
            p = Paragraph(ptext, leftside)
            formattedLineData.append(p)
        data.append(formattedLineData)


        
        table = Table(data, colWidths=[180, 180, 180, 80, 80])
        tStyle = TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ("ALIGN", (1, 0), (1, -1), 'LEFT'),
                ('LINEABOVE', (0, 0), (-1, -1), 1, self.colorAlargeDarkRed),
                ('BACKGROUND', (0, 0), (-1, 0), self.colorAlargeDarkRed),
                ('BACKGROUND', (0, -1), (-1, -1), self.colorAlargeDarkRed),
                ('SPAN', (0, -1), (-2, -1))
                ])
        table.setStyle(tStyle)
        self.elements.append(table)

if __name__ == '__main__':
    report = PDFPSReporte('psreport.pdf')