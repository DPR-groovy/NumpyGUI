# NumpyGUI3
Table GUI for numpy 2-D structured array

# Dependencies
Python Ver. 3.6 +
PyQt5, matplotlib, numpy, math, sys, os

# Sample GUI running
    python example.py

# NumpyTableModel Docstring
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
