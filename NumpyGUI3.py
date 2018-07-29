import numpy as np
from matplotlib import pyplot as plt
import math
from PyQt5 import Qt

def rangeNormalize(array, minval, maxval, roundup=False):
    """Transform a N-D numpy array / numpy structured array into a range-normalized N-D numpy array.

        :param array: N-D numpy array / N-D numpy structured array (int/float)
        :param minval: Minimum value after normalization
        :param maxval: Maximum value after normalization
        :param roundup: Boolean value indicating whether to apply element-wise roundup to the each element of
        a transformed array
        :return: N-D numpy array (float)

        >>> float_array = np.random.rand(100,100)
        >>> float_array
        array([[0.99842849, 0.7335879 , 0.45241696, ..., 0.78776639, 0.2122709 ,
                0.53029906],
               [0.03119923, 0.98444669, 0.70326038, ..., 0.41407126, 0.3634376 ,
                0.0843546 ],
               [0.81968529, 0.84791423, 0.54861544, ..., 0.49453236, 0.13844598,
                0.11945915],
               ...,
               [0.00582142, 0.59930892, 0.35842354, ..., 0.07554911, 0.24260212,
                0.52219156],
               [0.12665493, 0.74025658, 0.04250501, ..., 0.8702505 , 0.22234428,
                0.28757176],
               [0.51968882, 0.9900433 , 0.46353337, ..., 0.45834456, 0.00472072,
                0.6826813 ]])
        >>> rangeNormalize(float_array, 0, 100, roundup=True)
        array([[100.,  73.,  45., ...,  79.,  21.,  53.],
               [  3.,  98.,  70., ...,  41.,  36.,   8.],
               [ 82.,  85.,  55., ...,  49.,  14.,  12.],
               ...,
               [  1.,  60.,  36., ...,   8.,  24.,  52.],
               [ 13.,  74.,   4., ...,  87.,  22.,  29.],
               [ 52.,  99.,  46., ...,  46.,   0.,  68.]])

    """
    dtype_arr = array.dtype
    if dtype_arr.names is None:
        array = array.astype('f8')
        shape = array.shape
        array = array.flatten()
        minval = float(minval)
        maxval = float(maxval)
        array_std = (array - array.min(axis=0)) / (array.max(axis=0) - array.min(axis=0))
        array_scaled = array_std * (maxval - minval) + minval
        if roundup:
            return np.round(array_scaled.reshape(shape))
        return array_scaled.reshape(shape)
    else:
        temp_list = []
        for colname in dtype_arr.names:
            temp_list.append(array[colname].astype('f8').reshape(1, -1))
        array = np.concatenate(temp_list).T
        shape = array.shape
        array = array.flatten()
        minval = float(minval)
        maxval = float(maxval)
        array_std = (array - array.min(axis=0)) / (array.max(axis=0) - array.min(axis=0))
        array_scaled = array_std * (maxval - minval) + minval
        if roundup:
            return np.round(array_scaled.reshape(shape))
        return array_scaled.reshape(shape)


class NumpyTableModel(Qt.QAbstractTableModel):
    """
            Setting up QAbstractTableModel from a 1-D / 2-D numpy structured array or numpy array.

            :param data: 1-D / 2-D numpy structured array or numpy array
            :param dtypes: User defined format string for each columns
            ex) dtypes={'a':'{:,.0f}', 'b':'{:,d}'}
            :param alignment: User defiend alignment for each columns (valid values : 'left', 'center', 'right')
            ex) alignment={'a':'center', 'b':'left', 'c':'right'}
            :param colormap: User defined colormap for each columns
            ex) colormap={'RdBu':[['a','b','c','d'], 'e', 'f'], 'Jet':['g', 'h']}
            ex) colormap='all'
            :param alpha: Alpha value for colormap
            :param parent: Parent widget
            :param args:
    """
    def __init__(self, data, dtypes=None, alignment=None, colormap=None, alpha=None, parent=None, *args):
        super(NumpyTableModel, self).__init__(parent, *args)
        self._alpha = alpha
        self.preprocessData(data)
        self.getColIndex()
        self.dtypeDefine(dtypes)
        self.alignmentDefine(alignment)
        self.colormapPrep(colormap)

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return len(self._data.dtype)

    def data(self, index, role=Qt.Qt.DisplayRole):
        i = index.row()
        j = index.column()
        dtypes = self._data.dtype
        if role == Qt.Qt.DisplayRole:
            if j == 0:
                return "{}".format(self._data[i][j])
            else:
                if self._dtypes_dict is None:
                    if dtypes[j] in [np.float, np.float16, np.float32, np.float64, np.float_]:
                        return "{:,.4f}".format(self._data[i][j])
                    elif dtypes[j] in [np.int, np.int0, np.int16, np.int8, np.int_, np.int32, np.int64]:
                        return "{:,d}".format(self._data[i][j])
                    return "{}".format(self._data[i][j])
                else:
                    if self._col_index_inverse[j] in self._dtypes_dict:
                        return self._dtypes_dict[self._col_index_inverse[j]].format(self._data[i][j])
                    else:
                        if dtypes[j] in [np.float, np.float16, np.float32, np.float64, np.float_]:
                            return "{:,.4f}".format(self._data[i][j])
                        elif dtypes[j] in [np.int, np.int0, np.int16, np.int8, np.int_, np.int32, np.int64]:
                            return "{:,d}".format(self._data[i][j])
                        return "{}".format(self._data[i][j])
        elif role == Qt.Qt.TextAlignmentRole:
            if self._alignment_dict is None:
                if j == 0:
                    return Qt.Qt.AlignHCenter
            else:
                if j == 0:
                    return Qt.Qt.AlignHCenter
                else:
                    if self._col_index_inverse[j] in self._alignment_dict:
                        return self._alignment_dict[self._col_index_inverse[j]]
                    return Qt.Qt.AlignLeft
        elif role == Qt.Qt.BackgroundRole:
            try:
                for cm, value in self._cmap_data.items():
                    target_cm = self._cmap[cm]
                    for idx, sub_value in value.items():
                        target_data = sub_value['data']
                        target_colidx = sub_value['colidx']
                        target_map = {}
                        for enum_idx, t_col in enumerate(target_colidx):
                            target_map[t_col] = enum_idx

                        if len(target_data.shape) == 2:
                            if j in target_colidx:
                                target_color = Qt.QBrush(Qt.QColor(*target_cm[int(target_data[i, target_map[j]])]))
                                return target_color
                        else:
                            if j in target_colidx:
                                target_color = Qt.QBrush(Qt.QColor(*target_cm[int(target_data[i])]))
                                return target_color
            except:
                raise
        elif role == Qt.Qt.ForegroundRole:
            if dtypes[j] in [np.int, np.int0, np.int16, np.int8, np.int_, np.int32, np.int64, np.float, np.float16, np.float32, np.float64, np.float_]:
                if self._data[i][j] < 0:
                    return Qt.QBrush(Qt.QColor(255, 0, 0))
        else:
            return Qt.QVariant()

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if orientation == Qt.Qt.Horizontal and role == Qt.Qt.DisplayRole:
            return Qt.QVariant(self._data.dtype.names[section])
        elif orientation == Qt.Qt.Vertical and role == Qt.Qt.DisplayRole:
            return Qt.QVariant("{}".format(self._data['Idx'][section]))
        return Qt.QVariant()

    def dtypeDefine(self, dtypes):
        if dtypes is None:
            self._dtypes_dict = None
        else:
            self._dtypes_dict = dtypes

    def alignmentDefine(self, alignment):
        if alignment is None:
            self._alignment_dict = None
        else:
            self._alignment_dict = {}
            for key, item in alignment.items():
                if item == 'left':
                    self._alignment_dict[key] = Qt.Qt.AlignLeft
                elif item == 'right':
                    self._alignment_dict[key] = Qt.Qt.AlignRight
                elif item == 'center':
                    self._alignment_dict[key] = Qt.Qt.AlignHCenter
                else:
                    self._alignment_dict[key] = Qt.Qt.AlignLeft

    def getColIndex(self):
        self._col_index = {}
        self._col_index_inverse = {}
        for i, colname in enumerate(self._data.dtype.names):
            self._col_index[colname] = i
            self._col_index_inverse[i] = colname

    def sortByColIndex(self, col_number):
        self._data = np.sort(self._data, order=self._data.dtype.names[col_number])
        self.reset()

    def sortByColName(self, col_name):
        self._data = np.sort(self._data, order=col_name)
        self.reset()

    def sort(self, col, order=Qt.Qt.AscendingOrder):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self._data = np.sort(self._data, order=self._data.dtype.names[col])
        if order == Qt.Qt.DescendingOrder:
            self._data = self._data[::-1]
        self.layoutChanged.emit()

    def preprocessData(self, data):
        if len(data.shape) == 1:
            dtype_list = []
            dtype_format = data.dtype
            dtype_list.append(("Idx", "i8"))
            for i in range(len(dtype_format)):
                dtype_list.append((dtype_format.names[i], dtype_format[i]))
            self._data = np.zeros(data.shape, dtype=dtype_list)
            self._data['Idx'] = np.arange(data.shape[0])
            for i in range(len(dtype_format)):
                colname = dtype_format.names[i]
                self._data[colname] = data[colname]
        elif len(data.shape) == 2:
            dtype_list = []
            dtype_format = data.dtype
            dtype_list.append(("Idx", "i8"))
            for i in range(data.shape[1]):
                dtype_list.append((str(i), dtype_format))
            self._data = np.zeros((data.shape[0],), dtype=dtype_list)
            self._data['Idx'] = np.arange(data.shape[0])
            for j in range(data.shape[1]):
                self._data[str(j)] = data[:, j]

    def colormapPrep(self, colormap):
        floatTointRGB = np.vectorize(lambda x: 255 if x >= 1.0 else 0 if x <= 0.0 else int(math.floor(x * 256.0)))
        self._cmap = {}
        self._cmap_data = {}
        if colormap is None:
            cm = plt.get_cmap('RdBu')
            cm_array = []
            for i in range(cm.N):
                cm_array.append(cm(i))
            cm_array = np.array(cm_array)
            self._cmap['RdBu'] = floatTointRGB(cm_array)[::-1]
            if self._alpha is not None:
                self._cmap['RdBu'][:, 3] = self._alpha
        else:
            if colormap == 'all':
                colormap = {'RdBu': [list(self._data.dtype.names)[1:]]}
            for key, value in colormap.items():
                cm = plt.get_cmap(key)
                cm_array = []
                for i in range(cm.N):
                    cm_array.append(cm(i))
                cm_array = np.array(cm_array)
                self._cmap[key] = floatTointRGB(cm_array)[::-1]
                if self._alpha is not None:
                    self._cmap[key][:, 3] = self._alpha

                self._cmap_data[key] = {}
                for i, sub_value in enumerate(value):
                    self._cmap_data[key][i] = {}
                    self._cmap_data[key][i]['data'] = rangeNormalize(self._data[sub_value], 0, 255, roundup=True)
                    self._cmap_data[key][i]['colidx'] = []
                    if type(sub_value) == list:
                        for item in sub_value:
                            self._cmap_data[key][i]['colidx'].append(self._col_index[item])
                    else:
                        self._cmap_data[key][i]['colidx'].append(self._col_index[sub_value])
        self._colormap = colormap

    def reDraw(self):
        if self._colormap is not None:
            for key, value in self._colormap.items():
                for i, sub_value in enumerate(value):
                    self._cmap_data[key][i]['data'] = rangeNormalize(self._data[sub_value], 0, 255, roundup=True)

class NumpyTableView(Qt.QTableView):
    def __init__(self, numpytablemodel, parent=None):
        super(NumpyTableView, self).__init__(parent)
        self._table_model = numpytablemodel
        self.setModel(self._table_model)

        cornerButton = self.findChild(Qt.QAbstractButton)
        cornerButton.clicked.connect(self.cornerEvent)
        self._cornerOrder = 0

        self._table_model.dataChanged.connect(self.resizeColFunction)

        font = Qt.QFont("Arial", 10)
        self.setFont(font)
        self.horizontalHeader().hideSection(0)

        self.setSortingEnabled(True)

        self.resizeColumnsToContents()
        self.getColumnsWidth()

        self.verticalHeader().setDefaultSectionSize(self.fontMetrics().height())
        self.horizontalHeader().sortIndicatorChanged.connect(self.resizeColFunction)

        self.fitTableToWindow()

        self.verticalHeader().setFont(Qt.QFont("Calbri", 8))

        self._table_model.sort(0)
        self.resizeColFunction()

    def cornerEvent(self):
        self.clearSelection()
        if self._cornerOrder == 0:
            self._cornerOrder += 1
        else:
            self._cornerOrder -= 1
        self._table_model.sort(0, self._cornerOrder)
        self.resizeColFunction()

    def getColumnsWidth(self):
        self._columns_width = []
        for i in range(self._table_model.columnCount()):
            self._columns_width.append(self.columnWidth(i))

    def resizeColFunction(self):
        self._table_model.reDraw()
        for i, width in enumerate(self._columns_width):
            self.setColumnWidth(i, width)

    def fitTableToWindow(self):
        total_rows_width = self.fontMetrics().height() * 50
        total_cols_width = 0
        for width in self._columns_width:
            total_cols_width += width * 1.3
        self.setMinimumSize(min(total_cols_width, 1500), total_rows_width)
        self._geo_x, self._geo_y, self._geo_w, self._geo_h = 100, 100, min(total_cols_width, 1200), total_rows_width

