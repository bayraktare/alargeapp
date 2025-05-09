import sys
import os
import platform
import sqlite3
import re
import glob
import paramiko



# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%
# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None



# from src.customWidgets import *


class WidgetCache:
    def __init__(self):
        self.cache = {}
        
    def save(self, tab_widget, db_id):
        widgets = [tab_widget.widget(index) for index in range(tab_widget.count())]
        self.cache[db_id] = widgets

    def restore(self, tab_widget, db_id):
        if db_id in self.cache:
            tab_widget.clear()
            widgets = self.cache[db_id]
            for widget in widgets:
                tab_widget.addTab(widget, widget.windowTitle())
    def returnCache(self):
        return self.cache
    
class FileListWidgetItem(QWidget):
    """
    A custom widget for displaying file list items in the database explorer.

    Attributes:
    -----------#+
    layout : QVBoxLayout#+
        The vertical layout for arranging the widgets.#+
#+
    Methods:#+
    --------#+
    __init__(self, file_path: str, parent: QWidget = None)#+
        Initializes the FileListWidgetItem with the given file path and parent widget.#+
        Creates and adds necessary widgets to the layout.#+
    """#+
#+
    def __init__(self, file_path: str, parent: QWidget = None):#+
        """#+
        Initializes the FileListWidgetItem with the given file path and parent widget.#+
        Creates and adds necessary widgets to the layout.#+
#+
        Parameters:#+
        -----------#+
        file_path : str#+
            The path of the file to be displayed.#+
        parent : QWidget, optional#+
            The parent widget for this item. The default is None.#+
        """#+
        super().__init__(parent)#+
#+
        self.layout = QVBoxLayout()#+
#+
        file_name = os.path.basename(file_path)#+
        file_icon = QIcon(file_path)#+
#+
        file_label = QLabel(file_name)#+
        file_label.setAlignment(Qt.AlignLeft)#+
        file_label.setPixmap(file_icon.pixmap(32, 32))#+
#+
        self.layout.addWidget(file_label)#+
        self.setLayout(self.layout)#+
#>>>>>>> Tabnine >>>>>>># {"conversationId":"8addb83f-cf46-46ec-a3bf-a69e3e40cbe0","source":"instruct"}
    def __init__(self, file_path):
        super().__init__()
        
        self.filePath = file_path
        self.fileName = os.path.basename(file_path)
        self.fileBaseName = os.path.splitext(self.fileName)[0]
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()  
        
        self.nameLabel = QLabel(self.formatString(self.fileBaseName))
        self.nameLabel.setFixedHeight(30)
        self.nameLabel.setAlignment(Qt.AlignCenter)
            
        layout.addWidget(self.nameLabel)
        layout.setAlignment(Qt.AlignCenter)        
        self.setLayout(layout)
        
    @staticmethod
    def formatString(string):
        formattedString = string.replace('_', ' ')
        formattedString = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', formattedString)
        
        return formattedString
    

    




class CustomFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_id = ""
        self.selected_date = ""

    def setTestID(self, test_id):
        self.test_id = test_id
        self.invalidateFilter()

    def setSelectedDate(self, selected_date):
        self.selected_date = selected_date
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        test_id_index = model.index(source_row, 0, source_parent)
        date_index = model.index(source_row, 1, source_parent)

        test_id_matches = self.test_id in model.data(test_id_index)
        date_matches = self.selected_date in model.data(date_index)

        return test_id_matches and date_matches

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # super(MainWindow, self).__init__()

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.lastSelectedRow = None
        self.widgetCache = WidgetCache()
        global widgets
        widgets = self.ui

        self.initUI()

        self.addDataBaseFromDir("./databases")
        self.add_component_row()

        self.ui.addDatabaseButton.clicked.connect(self.addDatabase)
        self.ui.createReportButton.clicked.connect(self.createReport)
        self.ui.getDetailsButton.clicked.connect(self.getTestDetails)
        self.ui.visualizeDataButton.clicked.connect(self.visualizeData)
        # self.ui.newButton.clicked.connect(self.ssh_connect)
        self.ui.listWidget.selectionModel().selectionChanged.connect(self.updateTabs)

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "ALARAGE Lab."
        description = "ALARGE Lab. Test Equipments Reporting Tool"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = True
        themeFile = "themes\py_dracula_dark.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.new_page)
        widgets.btn_new.setStyleSheet(UIFunctions.selectMenu(widgets.btn_new.styleSheet()))

        
        # VAR

        # self.ip_address = None
        # self.username = None
        # self.password = None
        # self.data_path = None
        # self.local_path = './databases/MFI.db'

        self.ip_address = None
        self.username = None
        self.password = None
        self.data_path = r'C:\Users\krkrt\Desktop\db\MFI.db'
        self.local_path = './databases/MFI.db'


        

        self.setupComboBox()

        widgets.btn_add_component.clicked.connect(self.add_component_row)
        widgets.btn_remove_component.clicked.connect(self.remove_component_row)

        widgets.btn_save.clicked.connect(self.newRecord)

        widgets.add_connection.clicked.connect(self.sftp)

        widgets.btn_connect.clicked.connect(self.sftp_with_combobox)
        widgets.btn_save_txt_1.clicked.connect(self.save_to_txt)
        widgets.btn_generate_pdf_1.clicked.connect(self.make_pdf)
        widgets.btn_generate_qr_1.clicked.connect(self.make_qrcode)

        





        

    def initUI(self):
        self.ui.home.setStyleSheet(""" 
            QFrame {
                background-color: rgb(40, 44, 52);  /* Updated to match the dark theme */
            }
            QPushButton {
                background-color: rgb(52, 59, 72);  /* Updated to match the dark theme */
                color: rgb(221, 221, 221);          /* Updated text color */
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
                border: 2px solid rgb(44, 49, 58);  /* Updated border color */
            }
            QPushButton:hover {
                background-color: rgb(40, 44, 52);  /* Updated hover color */
            }
            QPushButton:selected {
                background-color: rgb(189, 147, 249); /* Updated selected color */
            }
            QLabel {
                color: rgb(221, 221, 221);          /* Updated text color */
                font-weight: bold;
            }
            """)
        self.ui.reportWidget.setStyleSheet("""
            QFrame {
                background-color: rgb(44, 49, 58);  /* Updated to match the dark theme */
            }
            """)
        self.ui.tabWidget.setStyleSheet("""
            QFrame {
                background-color: rgb(33, 37, 43);  /* Updated to match the dark theme */
            }
            """)
        # self.ui.dbLabel.setStyleSheet("""
        #         background-color: rgb(44, 49, 58);  /* Updated to match the dark theme */
        #         border-radius: 5px;
        #         border: 2px solid rgb(44, 49, 58);   /* Updated border color */
        #     """)
        self.ui.listWidget.setStyleSheet("""
                QListWidget {
                    background-color: rgb(44, 49, 58);  /* Updated to match the dark theme */
                }
                QListWidget::item {
                    background-color: rgb(52, 59, 72);  /* Updated to match the dark theme */
                    margin: 1px;
                    border-radius: 5px;
                    border: solid rgb(44, 49, 58) 1px;  /* Updated border color */
                }
                QListWidget::item:hover {
                    background-color: rgb(40, 44, 52);  /* Updated hover color */
                    border-radius: 5px;
                    border: solid rgb(44, 49, 58) 1px;  /* Updated border color */
                }
                QListWidget::item:selected {
                    background-color: rgb(189, 147, 249); /* Updated selected color */
                    border-radius: 5px;
                    border: solid rgb(44, 49, 58) 1px;  /* Updated border color */
                }
                QLabel {
                    background: transparent;
                    border: 1px solid transparent;
                }
            """)

        self.setupSearchFunctionality()

    def setupSearchFunctionality(self):
        self.ui.filtersearch.clicked.connect(self.filterByTestID)
        self.ui.resetFilterButton.clicked.connect(self.resetFilter)

    def filterByTestID(self):
        test_id = self.ui.testID.text()  # Get the text from the QLineEdit
        selected_date = self.ui.testdate.date().toString("yyyy-MM-dd")  # Get the date from QDateEdit

        if not test_id and not selected_date:
            return  # If both inputs are empty, do nothing

        # Assuming you have a reference to the QTableView
        current_tab = self.ui.tabWidget.currentWidget()
        if current_tab:
            table_view = current_tab.findChild(QTableView)  # Find the QTableView in the current tab
            if table_view:
                # Use the custom proxy model
                proxy_model = CustomFilterProxyModel()
                proxy_model.setSourceModel(table_view.model())
                table_view.setModel(proxy_model)

                # Set filters
                proxy_model.setTestID(test_id)
                proxy_model.setSelectedDate(selected_date)

    def resetFilter(self):
        current_tab = self.ui.tabWidget.currentWidget()
        if current_tab:
            table_view = current_tab.findChild(QTableView)
            if table_view:
                proxy_model = table_view.model()
                if isinstance(proxy_model, CustomFilterProxyModel):
                    # Clear the filters
                    proxy_model.setTestID("")
                    proxy_model.setSelectedDate("")
                    # Reset the view to show all data
                    table_view.setModel(proxy_model.sourceModel())

    def addDataBaseFromDir(self, path):
        if not os.path.isdir(path):
            raise ValueError(f"The provided path '{path}' is not a valid directory.")
            
        path = glob.glob(os.path.join(path, '*.db'))
        
        for file_path in path:
            item_widget = FileListWidgetItem(file_path)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, file_path)
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, item_widget)

    def addDatabase(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileNames(self, 'Select Database Files', '', 'Database Files (*.db);;All Files (*)', options=options)
        
        if fileName:
            fileName = fileName[0]
            existingPaths = [self.ui.listWidget.item(i).data(Qt.UserRole) for i in range(self.ui.listWidget.count())]
            for file in existingPaths:
                if self.comparePaths(fileName, file, home=os.getcwd()):
                    print(f"File '{fileName}' is already in the list.")
                    return
            item_widget = FileListWidgetItem(fileName)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, fileName)
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, item_widget)

    def populateTabs(self, file_path):
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        regExp = re.compile(re.escape("TestAna"), re.IGNORECASE)
        
        for table_name, in tables:
            pattern = r'[_\-\\p{P}\s]'
            s = re.sub(pattern, '', table_name)
            if regExp.search(s):
                tab = QWidget()
                tab_layout = QVBoxLayout()  
                tableWidget = QTableWidget()
                
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                formattedColums = [self.formatString(column) for column in columns]

                tableWidget.setColumnCount(len(columns))
                tableWidget.setHorizontalHeaderLabels(formattedColums)
                tableWidget.setRowCount(len(rows))

                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        tableWidget.setItem(row_idx, col_idx, item)
                        
                # Create a QSortFilterProxyModel
                proxy_model = QSortFilterProxyModel()
                proxy_model.setSourceModel(tableWidget.model())  # Set the source model
                
                # Set the proxy model to the table view
                tableView = QTableView()
                tableView.setModel(proxy_model)
                
                # Set the selection behavior to select entire rows
                tableView.setSelectionBehavior(QTableView.SelectRows)
                
                # Add this line to set the stylesheet for the selected row
                tableView.setStyleSheet("""
                    QTableView::item:selected {
                        background-color: rgb(189, 147, 249); /* Change this color to your preference */
                    }
                """)
                
                tab_layout.addWidget(tableView)  # Add the table view to the tab layout
                
                # Hide the QTableWidget
                tableWidget.setVisible(False)
                
                tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
                tableWidget.setSelectionMode(QTableWidget.SingleSelection)
                tableWidget.itemSelectionChanged.connect(self.selectRow)

                tab_layout.addWidget(tableWidget)
                tab.setLayout(tab_layout)
                tab.setWindowTitle(self.formatString(table_name))
                self.ui.tabWidget.addTab(tab, self.formatString(table_name))
                
        self.widgetCache.save(self.ui.tabWidget, file_path)
        conn.close()

    def searchtest(self):
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        testid = self.ui.lineEdit.text()  

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        regExp = re.compile(re.escape("TestAna"), re.IGNORECASE)
        
        for table_name, in tables:
            pattern = r'[_\-\\p{P}\s]'
            s = re.sub(pattern, '', table_name)
            if regExp.search(s):
                tab = QWidget()
                tab_layout = QVBoxLayout()  
                tableWidget = QTableWidget()
                
                
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                formattedColums = [self.formatString(column) for column in columns]

                tableWidget.setColumnCount(len(columns))
                tableWidget.setHorizontalHeaderLabels(formattedColums)
                tableWidget.setRowCount(len(rows))
    
                for row_idx, row in enumerate(rows):
                    for col_idx, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        tableWidget.setItem(row_idx, col_idx, item)
                        
                tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
                tableWidget.setSelectionMode(QTableWidget.SingleSelection)
                tableWidget.itemSelectionChanged.connect(self.selectRow)
    
                tab_layout.addWidget(tableWidget)
                tab.setLayout(tab_layout)
                tab.setWindowTitle(self.formatString(table_name))
                self.ui.tabWidget.addTab(tab, self.formatString(table_name))
                
        self.widgetCache.save(self.ui.tabWidget, file_path)
        conn.close()

    
        
        


        
    def selectRow(self):
        tableWidget = self.sender()
        selected_items = tableWidget.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            tableWidget.selectRow(row)
            columns = []
            for column in range(tableWidget.columnCount()):
                item = tableWidget.horizontalHeaderItem(column)
                if item:
                    columns.append(item.text())
            self.lastSelectedRow = [columns, selected_items]
            
    def getTestDetails(self):
        if self.lastSelectedRow is None:
            return
        
        try:
            file_path, testType, testId, hatId = self.findSelectedTest()
        except:
            return

        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        regExp = re.compile(re.escape("TestDetay"), re.IGNORECASE)
        regExp2 = re.compile(re.escape("TestId"), re.IGNORECASE)
        pattern = r'[_\-\\p{P}\s]'
            
        for table_name, in tables:
            s = re.sub(pattern, '', table_name)
            if regExp.search(s):
                try:
                    tab = QWidget()
                    tab_layout = QVBoxLayout()  
                    tableWidget = QTableWidget()
                    
                    cursor.execute(f"SELECT * FROM {table_name};")
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    i = next((column_idx for column_idx, column in enumerate(columns) if regExp2.search(re.sub(pattern, '', column)) is not None), None)

                    filteredRows = [row for row in rows if row[i] == int(testId)]
                    
                    formattedColums = [self.formatString(column) for column in columns]
                                        
                    tableWidget.setColumnCount(len(columns))
                    tableWidget.setHorizontalHeaderLabels(formattedColums)
                    tableWidget.setRowCount(len(filteredRows))
                    
                    for row_idx, row in enumerate(filteredRows):
                        for col_idx, value in enumerate(row):
                            item = QTableWidgetItem(str(value))
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            item.setFlags(Qt.ItemIsEnabled)
                            tableWidget.setItem(row_idx, col_idx, item)
                            
                    tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
                    tableWidget.setSelectionMode(QTableWidget.SingleSelection)
                    tableWidget.itemSelectionChanged.connect(self.selectRow)
                    
                    tab_name = f'Test Id: {testId}, Hat No: {hatId}' if hatId is not None else f'Test Id: {testId}'
                    tab_layout.addWidget(tableWidget)
                    tab.setLayout(tab_layout)
                    tab.setWindowTitle(tab_name)
                    
                    self.ui.tabWidget.addTab(tab, tab_name)
                    self.widgetCache.save(self.ui.tabWidget, file_path)
                except:
                    pass
                
    def findSelectedTest(self):
        selected_items = self.ui.listWidget.selectedItems()
        
        if selected_items and self.lastSelectedRow:
            remPunct = r'[_\-\\p{P}\s]'
            patterns = [
                (re.compile(re.escape("DSCOIT"), re.IGNORECASE), 'DSC-OIT'),
                (re.compile(re.escape("MFI"), re.IGNORECASE), 'MFI'),
                (re.compile(re.escape("VICAT"), re.IGNORECASE), 'VICAT')
            ]
            
            selected_item = selected_items[0]
            file_path = selected_item.data(Qt.UserRole)
            
            testType = None

            if file_path:
                for pattern, test_type in patterns:
                    if pattern.search(re.sub(remPunct, '', file_path)) is not None:
                        testType = test_type
                
                regExp = re.compile(re.escape("TestId"), re.IGNORECASE)
                regExp2 = re.compile(re.escape("Hat"), re.IGNORECASE)
                
                if testType == 'VICAT':
                    if regExp2.search(re.sub(remPunct, '', self.lastSelectedRow[0][1])) is None:
                        print("00")
                        return

                # Iterate through the column names and find the column id belonging to 'TestId' and 'HatNum'
                i = next((column_idx for column_idx, column in enumerate(self.lastSelectedRow[0]) if regExp.search(re.sub(remPunct, '', column)) is not None), None)
                j = next((column_idx for column_idx, column in enumerate(self.lastSelectedRow[0]) if regExp2.search(re.sub(remPunct, '', column)) is not None), None)
                
                try:
                    testId = int(self.lastSelectedRow[1][i].data(0))
                    lineNum = int(self.lastSelectedRow[1][j].data(0))
                except:
                    lineNum = None
            return file_path, testType, testId, lineNum

    def createReport(self):
        try:
            file_path, testType, testId, lineNum = self.findSelectedTest()
        except:
            return
                
        print(file_path)
        print(testType)
        print(testId)
        print(lineNum)
        filename = f'{testType}_{testId}_{lineNum}_Report.pdf' if lineNum is not None else f'{testType}_{testId}_Report.pdf'
        ReportCreator(filename=filename, testType=testType, test_db=file_path, test_ID=testId, line_num=lineNum)
    
    def visualizeData(self):
        try:
            file_path, testType, testId, lineNum = self.findSelectedTest()
        except:
            return
        tab = QWidget()
        tab_name = 'Test'
        tab_layout = QGridLayout()
        tab.setLayout(tab_layout)
        tab.setWindowTitle(tab_name)
        
        data = self.getTestData(testType)
        dataset = []
        titles = []
        xAxises = []
        yAxises = []
        
        if testType != 'MFI':
            for sublist in data:
                dataset.append(sublist[0])
                titles.append(sublist[1])
                xAxises.append(sublist[2])
                yAxises.append(sublist[3])
            
            for index in range(len(dataset)):
                graphImage = self.createGraph(dataset[index], title=titles[index], xAxis=xAxises[index], yAxis=yAxises[index])
                graphPixmap = QPixmap.fromImage(graphImage)
                
                graphLabel = QLabel()
                graphLabel.setPixmap(graphPixmap)
                graphLabel.setAlignment(Qt.AlignCenter)
                
                if (len(dataset) % 2 != 0 and index == len(dataset) - 1):
                    tab_layout.addWidget(graphLabel, index // 2, 0, 1, 2)
                else:
                    tab_layout.addWidget(graphLabel, index // 2, index % 2)
                    
                tab_layout.setAlignment(Qt.AlignCenter)
        else:
            tab_layout.addWidget(data)
        
        
        self.ui.tabWidget.addTab(tab, tab_name)
        self.widgetCache.save(self.ui.tabWidget, file_path)
        
        def getTestData(self, testType):
            remPunct = r'[_\-\\p{P}\s]'

        tabExp = re.compile(re.escape("TestId"), re.IGNORECASE)
        
        tab = None
        
        for index in range(self.ui.tabWidget.count()):
            if tabExp.search(re.sub(remPunct, '', self.ui.tabWidget.tabText(index))):
                tab = self.ui.tabWidget.widget(index)
        
        if tab is not None:
            if tab.layout() and tab.layout().count() > 0:
                table = tab.layout().itemAt(0).widget()
        else: return
            
        data = []
        
        if testType == 'DSC-OIT':
            patterns = [
                [re.compile(re.escape("Numune"), re.IGNORECASE), []],
                [re.compile(re.escape("Referans"), re.IGNORECASE), []],
                [re.compile(re.escape("Watt"), re.IGNORECASE), []],
                [re.compile(re.escape("TestSure"), re.IGNORECASE), []]
            ]
        elif testType == 'MFI':
            patterns = [
                [re.compile(re.escape("Agirlik"), re.IGNORECASE), []],
                [re.compile(re.escape("Zaman"), re.IGNORECASE), []],
                [re.compile(re.escape("MVR"), re.IGNORECASE), []],
                [re.compile(re.escape("MFR"), re.IGNORECASE), []]
            ]
        elif testType == 'VICAT':
            patterns = [
                [re.compile(re.escape("Sicaklik"), re.IGNORECASE), []],
                [re.compile(re.escape("Batma"), re.IGNORECASE), []]
            ]
        else: return

        for column in range(table.columnCount()):
            item = table.horizontalHeaderItem(column)
            for pattern, columnData in patterns:
                if pattern.search(re.sub(remPunct, '', item.text())):
                    columnData.extend(self.getColumnData(table, column))
        
        columns = [sublist[1] for sublist in patterns]
        
        if testType == 'DSC-OIT':
            data.append([[['Numune Sıcaklığı', columns[3], columns[0]], ['Referans Sıcaklığı', columns[3], columns[1]]], 'Sıcaklık Zaman Grafiği', 'Test Süresi', 'Sıcaklık'])
            data.append([[['Watt', columns[3], columns[2]]], 'Isı Zaman Grafiği', 'Test Süresi', 'Watt'])
            data.append([[['Isı', columns[0], columns[2]]], 'Isı Sıcaklık Grafiği', 'Sıcaklık', 'Isı'])
        elif testType == 'MFI':
            data = QTableWidget()
            
            columnHeaders = [' Agirlik (gr)', ' Kesme Zam. (sn)', ' MVR (mm³/10dk)', ' MFR (gr/10dk)']
    
            num_cols = len(columns)
            num_rows = len(columns[0]) if num_cols > 0 else 0
            
            data.setRowCount(num_rows)
            data.setColumnCount(num_cols)
            data.setHorizontalHeaderLabels(columnHeaders)
            
            for col_index in range(num_cols):
                data.setColumnWidth(col_index, 100)
            data.setColumnWidth(3, 150)
            
            for row_index, row_data in enumerate(columns):
                for col_index, item in enumerate(row_data):
                    cell = QTableWidgetItem(item if isinstance(item, str) and bool(item) else '-')
                    cell.setTextAlignment(Qt.AlignCenter)
                    data.setItem(col_index, row_index, cell)
        elif testType == 'VICAT':
            data.append([[['Batma', columns[1], columns[0]]], 'Sıcaklık Batma Grafiği', 'Sıcaklık', 'Batma'])
        return data
    
    @staticmethod
    def getColumnData(table, index):
        column_data = []
        
        row_count = table.rowCount()
        
        for row in range(row_count):
            item = table.item(row, index)
            if item:
                column_data.append(item.text())
        
        return column_data

    @staticmethod
    def comparePaths(path1, path2, home=None):
        
        def normalizePath(path, home=None):
            if home:
                path = os.path.join(home, path)
            return os.path.realpath(path)
        
        abs_path1 = normalizePath(path1, home)
        abs_path2 = normalizePath(path2, home)
        return abs_path1 == abs_path2

    @staticmethod
    def formatString(string):
        formattedString = string.replace('_', ' ')
        formattedString = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', formattedString)
        
        return formattedString

    @staticmethod
    def createGraph(data, title='Title', xAxis='xAxisLabel', yAxis='yAxisLabel'):
        
        def smooth_data(x, y, window_length=11, polyorder=2):
            return savgol_filter(y, window_length=window_length, polyorder=polyorder)
        
        def prepareData(x, y):
            valid_indices = [i for i in range(len(x)) if x[i] not in (None, 'None') and y[i] not in (None, 'None')]
            
            x_cleaned = [x[i] for i in valid_indices]
            y_cleaned = [y[i] for i in valid_indices]
            return x_cleaned, y_cleaned

        buf = BytesIO()
        
        plt.figure(figsize=(8, 6))
        
        for dataset in data:
            label, x, y = dataset
            x, y = prepareData(x, y)
            y = smooth_data(x, y, window_length=11 if len(x) > 11 else len(x) // 2)
            plt.plot(x, y, label=label)
        
        plt.gca().xaxis.set_major_locator(AutoLocator())
        plt.gca().yaxis.set_major_locator(AutoLocator())
            
        plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d' if isinstance(x[0], int) else '%.2f'))
        plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        
        plt.title(title)
        plt.xlabel(xAxis)
        plt.ylabel(yAxis)
        plt.grid(color='gray', linestyle='dashdot', linewidth=1)
        plt.legend()
        
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        
        plot_image = QImage()
        plot_image.loadFromData(buf.getvalue())
        
        return plot_image

    def updateTabs(self):
        self.ui.tabWidget.clear()
        self.lastSelectedRow = None
        
        selected_items = self.ui.listWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            file_path = selected_item.data(Qt.UserRole)
            
            if file_path:
                if file_path in self.widgetCache.returnCache():
                    self.widgetCache.restore(self.ui.tabWidget, file_path)
                else:
                    self.populateTabs(file_path)
                
    

    def setupComboBox(self):
        # Clear existing items
        self.ui.connection_combo_box.clear()

        # Read saved user data and populate the combo box
        try:
            with open('saved_user', 'r') as file:
                for line in file:
                    ip_address, username, password = line.strip().split(',')
                    self.ui.connection_combo_box.addItem(ip_address)
        except FileNotFoundError:
            print("No saved user file found.")

        self.ui.connection_combo_box.currentIndexChanged.connect(self.onComboBoxChange)

    def onComboBoxChange(self, index):
        # Read the saved_user file again to get the selected details
        try:
            with open('saved_user', 'r') as file:
                lines = file.readlines()
                if 0 <= index < len(lines):
                    ip_address, username, password = lines[index].strip().split(',')
                    self.ip_address = ip_address
                    self.username = username
                    self.password = password
                    print(f"Selected IP: {self.ip_address}, Username: {self.username}")
        except FileNotFoundError:
            print("No saved user file found.")

    # ssh_connect('192.168.1.1', 'krkrt', '78963', r'C:\Users\krkrt\Desktop\db\MFI.db', 'local_file.db')

    def sftp(self):
        
        ip_address, ok = QInputDialog.getText(self, "Connection Details", "Enter IPv4 Address:")
        print(type(ip_address))
        print(ip_address)
        print(type(self.ip_address))
        print(self.ip_address)
        if not ok:
            return
        
        username, ok = QInputDialog.getText(self, "Connection Details", "Enter Username:")
        print(type(username))
        print(username)
        print(type(self.username))
        print(self.username)
        if not ok:
            return
        password, ok = QInputDialog.getText(self, "Connection Details", "Enter Password:")
        print(type(password))
        print(password)
        print(type(self.password))
        print(self.password)
        if not ok:
            return
        
        QMessageBox.information(self, "Success", "")

        #eğer bağlantı başarılı ise kaydet yapılcak ama bağlantıyı deneyemiyorum
        with open('saved_user', 'a') as file:
            file.write(f"{ip_address},{username},{password}\n")

        self.setupComboBox()





        try:
        # Create an SSH client
            client = paramiko.SSHClient()
        # Automatically add the server's host key (this is insecure, consider using a known_hosts file)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the server
            client.connect(ip_address, username=username, password=password)
            print(f"Successfully connected to {ip_address}")

            remote_file = r'C:\Users\krkrt\Desktop\db\MFI.db'
            local_path = './databases/MFI.db'

        # Create an SFTP session
            sftp = client.open_sftp()
        # Transfer the file from remote to local
            sftp.get(remote_file, local_path)
            print(f"Successfully transferred {remote_file} to {local_path}")



            item_widget = FileListWidgetItem(local_path)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, local_path)
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, item_widget)

        # Close the SFTP session
            sftp.close()
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
        except FileNotFoundError:
            print(f"File not found: {remote_file}")
        finally:
            client.close()


    def sftp_with_combobox(self):

        print(self.ip_address)
        print(self.username)
        print(self.password)

        try:
        # Create an SSH client
            client = paramiko.SSHClient()
        # Automatically add the server's host key (this is insecure, consider using a known_hosts file)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the server
            client.connect(self.ip_address, username=self.username, password=self.password)
            print(f"Successfully connected to {self.ip_address}")

            remote_file = r'C:\Users\krkrt\Desktop\db\MFI.db' #düzeltilcek
            local_path = './databases/MFI.db'# düzeltilcek

        # Create an SFTP session
            sftp = client.open_sftp()
        # Transfer the file from remote to local
            sftp.get(remote_file, local_path)
            print(f"Successfully transferred {remote_file} to {local_path}")



            item_widget = FileListWidgetItem(local_path)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.UserRole, local_path)
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, item_widget)

        # Close the SFTP session
            sftp.close()
        except paramiko.SSHException as e:
            print(f"SSH connection failed: {e}")
        except FileNotFoundError:
            print(f"File not found: {remote_file}")
        finally:
            client.close()



    def addComboBoxItem(self, item_text):
        if item_text:
            self.ui.comboBox_2.addItem(item_text)
            print(f"Added item: {item_text} to comboBox")

###############################################################

    def newRecord(self):
        # Check if the company information file exists
        self.material_window = NewRecordWindow()
        self.material_window.show()




    


    def add_component_row(self):
        hbox = QHBoxLayout()
        input_name = QLineEdit()
        input_name.setPlaceholderText("Component Name")
        input_percent = PercentageLineEdit()
        input_percent.setPlaceholderText("Component Percent")
        supplier_name = QLineEdit()
        supplier_name.setPlaceholderText("Supplier Name")
        hbox.addWidget(input_name)
        hbox.addWidget(input_percent)
        hbox.addWidget(supplier_name)
        self.ui.component_layout_1.addLayout(hbox)
 

    def remove_component_row(self):
        if self.ui.component_layout_1.count() > 0:
            layout_item = self.ui.component_layout_1.takeAt(self.ui.component_layout_1.count() - 1)
            for i in reversed(range(layout_item.count())):
                layout_item.itemAt(i).widget().setParent(None)

    def save_to_sql(self):
        # Create database connection
        conn = sqlite3.connect('material_records.db')
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY,
                raw_material TEXT,
                supplier TEXT,
                manufacturing_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                material_id INTEGER,
                component_name TEXT,
                component_percent TEXT,
                FOREIGN KEY(material_id) REFERENCES materials(id)
            )
        ''')

        # Insert material information
        cursor.execute('''
            INSERT INTO materials (raw_material, supplier, manufacturing_date)
            VALUES (?, ?, ?)
        ''', (self.ui.input_raw_material_1.text(), self.ui.input_supplier.text(), self.ui.input_manufacturing_date_1.text()))

        material_id = cursor.lastrowid

        # Insert component information
        for i in range(self.ui.component_layout_1.count()):
            layout_item = self.ui.component_layout_1.itemAt(i)
            component_name = layout_item.itemAt(0).widget().text()
            component_percent = layout_item.itemAt(1).widget().text()
            cursor.execute('''
                INSERT INTO components (material_id, component_name, component_percent)
                VALUES (?, ?, ?)
            ''', (material_id, component_name, component_percent))

        conn.commit()
        conn.close()

        # Inform the user
        QMessageBox.information(self, "Success", "Record saved to SQL database successfully.")

    def save_to_txt(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save to Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as file:
                file.write(f"Raw Material: {self.ui.input_raw_material_1.text()}\n")
                file.write("Components:\n")
                for i in range(self.ui.component_layout_1.count()):
                    layout_item = self.ui.component_layout_1.itemAt(i)
                    if layout_item is not None:
                        component_name_widget = layout_item.itemAt(0)
                        component_percent_widget = layout_item.itemAt(1)
                        supplier_name_widget = layout_item.itemAt(2)
                        
                        if component_name_widget and component_percent_widget and supplier_name_widget:
                            component_name = component_name_widget.widget().text()
                            component_percent = component_percent_widget.widget().text()
                            supplier_name = supplier_name_widget.widget().text()
                            file.write(f"  - {component_name}: {component_percent}% {supplier_name}\n")
                file.write(f"Manufacturing Date: {self.ui.input_manufacturing_date_1.text()}\n")

            # Inform the user
            QMessageBox.information(self, "Success", "Record saved to text file successfully.")

    def make_qrcode(self):
        if not self.ui.input_raw_material_1.text() or not self.ui.input_manufacturing_date_1.text():
            QMessageBox.warning(self, "Input Error", "Please fill in all the fields before generating a QR code.")
            return
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Files (*.png);;All Files (*)", options=options)
        if file_path:
            text = f"Raw Material: {self.ui.input_raw_material_1.text()}\nComponents:\n"
            for i in range(self.ui.component_layout_1.count()):
                layout_item = self.ui.component_layout_1.itemAt(i)
                if layout_item is not None:
                    component_name_widget = layout_item.itemAt(0)
                    component_percent_widget = layout_item.itemAt(1)
                    supplier_name_widget = layout_item.itemAt(2)
                    
                    if component_name_widget and component_percent_widget and supplier_name_widget:
                        component_name = component_name_widget.widget().text()
                        component_percent = component_percent_widget.widget().text()
                        supplier_name = supplier_name_widget.widget().text()
                        text += f"  - {component_name}: {component_percent}% {supplier_name}\n"
            text += f"Manufacturing Date: {self.ui.input_manufacturing_date_1.text()}"
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(file_path)
        
        QMessageBox.information(self, "Success", "QR Code generated and saved successfully.")

    



    def make_pdf(self):

    
        # if not self.input_raw_material.text() or not self.input_manufacturing_date.text():
        #     QMessageBox.warning(self, "Input Error", "Please fill in all the fields before generating a QR code.")
        #     return
        # else:
            component_name = self.ui.input_raw_material_1.text()
            PDFPSReporte(f'{component_name}.pdf', input_raw_material=self.ui.input_raw_material_1, input_manufacturing_date=self.ui.input_manufacturing_date_1, component_layout=self.ui.component_layout_1)

            QMessageBox.information(self, "Success", "PDF generated and saved successfully.")

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.material_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("alargepng.ico"))
    window = MainWindow()
    sys.exit(app.exec_())
