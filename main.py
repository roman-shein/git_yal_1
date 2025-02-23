import sqlite3
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from main_ui import Ui_MainWindow as main_window
from addEditCoffeeForm import Ui_MainWindow as add_widget


class Coffee(QMainWindow, main_window):
    def __init__(self):
        super().__init__()
        # uic.loadUi("UI\main.ui", self)
        self.setupUi(self)

        self.addBtn.clicked.connect(self.add_row)
        self.updateBtn.clicked.connect(self.update_row)

        self.add_window = None
        self.update_window = None

        self.con = sqlite3.connect("data/coffee.sqlite")
        self.cur = self.con.cursor()

        self.update_table()

    def add_row(self):
        self.statusBar().showMessage("")
        self.add_window = AddWidget(self)
        self.add_window.show()

    def update_row(self):
        if self.index.text() and self.cur.execute(f"select * from coffee where id = {self.index.text()}").fetchall():
            self.statusBar().showMessage("")
            self.update_window = AddWidget(self, add=False)
            self.update_window.show()
        else:
            self.statusBar().showMessage("Введен неверный индекс")

    def update_table(self):
        res = self.cur.execute("""select * from coffee""").fetchall()
        title = [el[0] for el in self.cur.description]
        self.tableWidget: QTableWidget
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(title)
        self.tableWidget.setRowCount(0)

        for i, row in enumerate(res):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, col in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(col)))

    def closeEvent(self, event):
        self.con.close()


class AddWidget(QMainWindow, add_widget):
    def __init__(self, parent=None, add=True):
        super().__init__(parent)
        # uic.loadUi(r"UI\addEditCoffeeForm.ui", self)
        self.setupUi(self)

        self.cur = self.parent().cur
        self.add = add
        self.widgets = [
            self.id,
            self.title,
            self.roasting,
            self.type,
            self.taste,
            self.coast,
            self.size
        ]
        self.int_widgets = [
            self.coast,
            self.size
        ]

        if self.add:
            self.updateBtn.clicked.connect(self.add_row)
            self.id.hide()
            self.id.setText("1")
            self.label.hide()
        else:
            self.id.hide()
            self.id.setText("1")
            self.label.hide()
            self.updateBtn.clicked.connect(self.update_row)
            self.edit_widgets()

    def add_row(self):
        if self.is_empty() and self.is_correct_cell():
            self.statusBar().showMessage("")
            arr = list(map(lambda x: x.text(), self.widgets))

            text = f"""insert into coffee (title, roasting, type, taste, coast, size)
                        values("{arr[1]}", "{arr[2]}", "{arr[3]}", "{arr[4]}", {arr[5]}, {arr[6]})"""

            self.cur.execute(text)
            self.parent().con.commit()

            self.parent().update_table()

            self.close()
        else:
            self.statusBar().showMessage("Ошибка при заполнении формы")

    def update_row(self):
        if self.is_empty() and self.is_correct_cell():
            self.statusBar().showMessage("")
            arr = list(map(lambda x: x.text(), self.widgets))

            text = f"""update coffee
                        set title = "{arr[1]}", roasting = "{arr[2]}", type = "{arr[3]}", taste = "{arr[4]}", 
                        coast = {arr[5]}, size = {arr[6]}
                        where id = {arr[0]}"""

            self.cur.execute(text)

            self.parent().con.commit()

            self.parent().update_table()

            self.close()
        else:
            self.statusBar().showMessage("Ошибка при заполнении формы")

    def edit_widgets(self):
        row_id = self.parent().index.text()
        res = self.cur.execute(f"select * from coffee where id = {row_id}").fetchall()
        for i, el in enumerate(self.widgets):
            el.setText(str(res[0][i]))

    def is_empty(self):
        if all(map(lambda x: x.text(), self.widgets)):
            return True
        return False

    def is_correct_cell(self):
        try:
            a = list(map(lambda x: int(x.text()), self.int_widgets))
            return True
        except ValueError:
            return False


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
