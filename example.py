import NumpyGUI3
from NumpyGUI3 import *
import sys, os

class TableWindow(Qt.QWidget):
    def __init__(self, tableview, parent=None):
        super(TableWindow, self).__init__(parent)
        self._table_view = tableview
        self._npz_address = None
        self._prev_npz_address = None
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Numpy GUI")
        self.setGeometry(self._table_view._geo_x, self._table_view._geo_y, self._table_view._geo_w, self._table_view._geo_h)
        self.pshBtn_populate = Qt.QPushButton("Populate")
        self.pshBtn_populate.clicked.connect(self.loadNpz)

        valid_data_lists = [item for item in os.listdir('./data/') if item.endswith('.npz')]
        self.cb_npzlist = Qt.QComboBox()
        self.cb_npzlist.addItems(valid_data_lists)
        self.cb_npzlist.activated.connect(self.cbHandleActivated)

        layout = Qt.QVBoxLayout()
        layout.addWidget(self._table_view)
        layout_lower_part = Qt.QHBoxLayout()
        layout_lower_part.addWidget(self.cb_npzlist)
        layout_lower_part.addWidget(self.pshBtn_populate)
        layout.addLayout(layout_lower_part)
        self.setLayout(layout)

    def cbHandleActivated(self, index):
        self._npz_address = './data/' + self.cb_npzlist.itemText(index)

    def loadNpz(self):
        if self._npz_address != self._prev_npz_address:
            self._table_view._table_model = NumpyTableModel(np.load(self._npz_address)['data'],
                                             dtypes={'Open': "{:,.2f}", 'High': "{:,.2f}", 'Low': "{:,.2f}",
                                                     "Close": "{:,.2f}", "Volume": "{:,.0f}"},
                                             alignment={'Date': 'center', 'Code': 'center', 'Open': 'center',
                                                        'High': 'center', 'Low': 'center', 'Close': 'center'},
                                             colormap={
                                                 'RdBu': [['Open', 'High', 'Low', 'Close'], 'Volume']},
                                             alpha=255)

            self._table_view._table_model.dataChanged.connect(self._table_view.resizeColFunction)
            self._table_view.setModel(self._table_view._table_model)
            #self._table_view.setSortingEnabled(True)
            self._table_view.resizeColumnsToContents()
            self._table_view.getColumnsWidth()
            self._table_view.resizeColFunction()
            self._prev_npz_address = self._npz_address

    def run(self):
        self.show()

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    nptm = NumpyTableModel(np.load("./data/AMZN.npz")['data'],
                                             dtypes={'Open': "{:,.2f}", 'High': "{:,.2f}", 'Low': "{:,.2f}",
                                                     "Close": "{:,.2f}", "Volume": "{:,.0f}"},
                                             alignment={'Date': 'center', 'Code': 'center', 'Open': 'center',
                                                        'High': 'center', 'Low': 'center', 'Close': 'center'},
                                             colormap={'RdBu': [['Open', 'High', 'Low', 'Close'], 'Volume']},
                                             alpha=255)
    nptv = NumpyTableView(nptm)
    tablewindow = TableWindow(nptv)
    tablewindow.run()
    app.exec_()