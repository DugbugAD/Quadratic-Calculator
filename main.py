# coding=utf-8

import sys
from PyQt5 import QtTest
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qt import Qt
from PyQt5 import QtCore
from PyQt5.QtCore import *
from pyqtgraph import *
import numpy as np
from cmath import sqrt as csqrt
from math import sqrt as sqrt

###
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MathTextLabel(QWidget): # Credit to https://stackoverflow.com/questions/14097463/displaying-nicely-an-algebraic-expression-in-pyqt for this class

    def __init__(self, mathText, parent=None, **kwargs):
        super(QWidget, self).__init__(parent, **kwargs)
        l = QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)

        r, g, b, a = self.palette().base().color().getRgbF()

        self._figure = Figure(edgecolor=(r, g, b), facecolor=(r, g, b))
        self._canvas = FigureCanvas(self._figure)
        l.addWidget(self._canvas)
        self._figure.clear()
        text = self._figure.suptitle(
            mathText,
            x=0.0,
            y=1.0,
            horizontalalignment='left',
            verticalalignment='top',
            size=QFont().pointSize() * 2
        )
        self._canvas.draw()

        (x0, y0), (x1, y1) = text.get_window_extent().get_points()
        w = x1 - x0
        h = y1 - y0

        self._figure.set_size_inches(w / 90, h / 90)
        self.setFixedSize(int(w), int(h))

###


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quadratic Solver")
        self.setStyleSheet('''
        background-color: #121212;
        QLabel {
            color: #FFFFFF;
            font-family: Courier New;
            font-dize: 16pt;
            font-weight: bold;
        }
        ''')
        self.setFixedSize(800, 600)

        lbl = QLabel(self, text="<span style='color: #BB86FC';>a</span>x<sup>2</sup> + <span style='color: #BB86FC';>b</span>x + <span style='color: #BB86FC';>c</span> = 0")
        lbl.setStyleSheet('''
            background-color: #272727;
            color: #FFFFFF;
            font-size: 56pt;
            font-family: Courier New;
            font-weight: Bold;
        ''')
        lbl.setFixedSize(800, 80)
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.move(0, 30)

        frm = QFrame(self)
        frm.move(30, 150)
        frm.setFixedSize(200, 200)
        frm.setStyleSheet('''
        QFrame {
            background-color: #343434;
            border-radius: 10px;
        }

        QLabel {
            color: #FFFFFF;
            font-family: Courier New;
            font-size: 24pt;
            font-weight: bold;
        }

        QDoubleSpinBox {
            background-color: #343434;
            color: #FFFFFF;
            font-family: Courier New;
            font-size: 24pt;
            font-weight: bold;
            border-color: rgb(28, 30, 38);
            border: 13pt;
        }
        ''')
        layout = QGridLayout()
        self.n1 = QDoubleSpinBox(decimals=2, minimum=-1000000, maximum=1000000)
        self.n2 = QDoubleSpinBox(decimals=2, minimum=-1000000, maximum=1000000)
        self.n3 = QDoubleSpinBox(decimals=2, minimum=-1000000, maximum=1000000)

        layout.addWidget(QLabel(text="a = "), 0, 0)
        layout.addWidget(QLabel(text="b = "), 1, 0)
        layout.addWidget(QLabel(text="c = "), 2, 0)

        layout.addWidget(self.n1, 0, 1)
        layout.addWidget(self.n2, 1, 1)
        layout.addWidget(self.n3, 2, 1)
        frm.setLayout(layout)

        self.go_btn = QPushButton(self, text='SOLVE')
        self.go_btn.setStyleSheet('''
            background-color: #03DAC6;
            color: #000000;
            font-family: Courier New;
            font-size: 24pt;
            font-weight: bold;
            border-radius: 10px;
            ''')
        self.go_btn.move(130, 365)
        self.go_btn.setFixedSize(100, 40)
        self.go_btn.clicked.connect(self.GO)

        self.answer_lbl = QLabel(self, text='')
        self.answer_lbl.setStyleSheet('''
            color: #FFFFFF;
            font-family: Courier New;
            font-size: 32pt;
            font-weight: bold;
        ''')
        self.answer_lbl.setFixedSize(800, 50)
        self.answer_lbl.move(30, 475)

        self.sumandproduct_lbl = QLabel(self, text='')
        self.sumandproduct_lbl.setStyleSheet('''
            color: #FFFFFF;
            font-family: Courier New;
            font-size: 18pt;
            font-weight: bold;
        ''')
        self.sumandproduct_lbl.setFixedSize(800, 50)
        self.sumandproduct_lbl.move(30, 535)

        self.show_work_btn = QPushButton(self)
        self.show_work_btn.setStyleSheet('''
            background-color: #121212;
            color: white;
            font-family: Courier New;
            font-weight: bold;
            font-size: 18pt;
        ''')
        self.show_work_btn.setFixedSize(190, 50)
        self.show_work_btn.move(0, 430)

        self.MAKE_GRAPH()

    def MAKE_GRAPH(self):
        self.graph = PlotWidget(self)
        self.graph.setBackground('#121212')
        self.graph.setFixedSize(485, 300)
        self.graph.showGrid(x=True, y=True)
        self.graph.setAspectLocked(1)
        self.graph.addItem(InfiniteLine(
            angle=0, pen=mkPen(color=(90, 90, 94), width=7)))
        self.graph.addItem(InfiniteLine(
            angle=90, pen=mkPen(color=(90, 90, 94), width=7)))

        self.graph.setRange(xRange=[0, 0], yRange=[0, 0])
        self.graph.move(275, 150)

    def GO(self):
        if self.n1.value() == 0:
            QMessageBox(icon=QMessageBox.Warning,
                        text="Coefficient 'a' must not be equal to 0").exec()
            return

        def GRAPH_EQUATION(a, b, c):
            self.CLEAR()
            x = np.linspace(-1000, 1000, 100000)
            y = (a * (x**2)) + (b * x) + c

            pen = mkPen('#BB86FC', width=3)
            self.line = self.graph.plot(x, y, pen=pen)

            realorcomplex, p, q = self.SOLVE(a, b, c)
            if realorcomplex == "real":
                self.intercept1 = self.graph.plot([p], [0], symbol='o', symbolPen='#03DAC5',
                                                  symbolBrush='#03DAC5', symbolSize=10)
                self.i1 = TextItem(
                    text=f'({p}, 0)', anchor=(1, 0), color='#03DAC5')
                self.i1.setPos(p, 0)
                self.i1.setFont(QFont("Courier New", 20))

                self.intercept2 = self.graph.plot([q], [0], symbol='o', symbolPen='#03DAC5',
                                                  symbolBrush='#03DAC5', symbolSize=10)
                self.i2 = TextItem(
                    text=f'({q}, 0)', anchor=(0, 0), color='#03DAC5')
                self.i2.setPos(q, 0)
                self.i2.setFont(QFont("Courier New", 20))

                self.graph.addItem(self.i1)
                self.graph.addItem(self.i2)

            sum_ = str(round(-b / a, 2))
            product = str(round(c / a, 2))

            s = f'x = {p}, {q}'
            s = s.replace('j', 'i')
            self.answer_lbl.setText(s)
            self.sumandproduct_lbl.setText(
                "Sum of Roots: " + sum_ + '\n' + "Product of Roots: " + product)
            self.show_work_btn.setText('Show Work ⓘ')
            self.show_work_btn.clicked.connect(lambda: self.SHOW_WORK(
                self.n1.value(), self.n2.value(), self.n3.value(), p, q, realorcomplex))

        GRAPH_EQUATION(self.n1.value(), self.n2.value(), self.n3.value())

    def SOLVE(self, a, b, c):
        d = b**2 - (4 * a * c)
        if d >= 0:
            p = round(((-1 * b) + sqrt((b**2 - (4 * a * c)))) / (2 * a), 2)
            q = round(((-1 * b) - sqrt((b**2 - (4 * a * c)))) / (2 * a), 2)

            if p <= q:
                return "real", p, q
            elif p > q:
                return "real", q, p

        elif d < 0:
            p = ((-1 * b) + csqrt((b**2 - (4 * a * c)))) / (2 * a)
            q = ((-1 * b) - csqrt((b**2 - (4 * a * c)))) / (2 * a)
            p = complex(round(p.real, 2), round(p.imag, 2))
            q = complex(round(q.real, 2), round(q.imag, 2))

            return "complex", p, q

    def CLEAR(self):
        try:
            self.line.clear()
            self.intercept1.clear()
            self.intercept2.clear()
            self.graph.removeItem(self.i1)
            self.graph.removeItem(self.i2)
        except:
            pass

    def SHOW_WORK(self, a, b, c, p, q, realorcomplex):
        self.GO()

        dlg = QDialog(self)
        dlg.setWindowTitle('Quadratic Formula')
        dlg.setStyleSheet("""
            background-color: white;
        """)
        dlg.setFixedSize(700, 600)
        mathText = r'$X_k = \sum_{n=0}^{N-1} x_n . e^{\frac{-i2\pi kn}{N}}$'
        mathText = r'$x = \frac{-b  ±  \sqrt{b^2 - 4ac}}{2a}$'
        lbl1 = MathTextLabel(mathText, dlg)
        lbl1.move(20, 25)

        MathTextLabel(
            rf'$x = \frac{{-({b})  ±  \sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}$', dlg).move(20, 125)
        MathTextLabel(
            rf'$x = \frac{{{-1*b}  ±  \sqrt{{{b**2} - {4*a*c}}}}}{{{2*a}}}$', dlg).move(20, 225)
        MathTextLabel(
            rf'$x = \frac{{{-1*b}  ±  \sqrt{{{b**2 - 4*a*c}}}}}{{{2*a}}}$', dlg).move(20, 325)
        if realorcomplex == 'real':
            MathTextLabel(
                rf'$x = \frac{{{-1*b}  ±  {round(sqrt(b**2 - 4*a*c), 2)}}}{{{2*a}}}$', dlg).move(20, 425)
        else:
            x = csqrt(b**2 - 4 * a * c)
            x = complex(round(x.real, 2), round(x.imag, 2))
            x = str(x).replace('j', 'i')
            MathTextLabel(
                rf'$x = \frac{{{-1*b}  ±  {x}}}{{{2*a}}}$', dlg).move(20, 425)

        MathTextLabel(
            rf'$x = {p}, {q}$'.replace("j", "i"), dlg).move(20, 525)

        dlg.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyle('Fusion')
    window = HomeScreen()
    window.show()
    sys.exit(app.exec())
