import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtWidgets import QInputDialog
import datetime
from PyQt5.QtGui import QPixmap

# создание главного окна с каталогом
class Main_Window(QMainWindow):
    # создание главного окна в котором происходит подгрузка всех позиций из базы данных
    def __init__(self):
        super().__init__()
        uic.loadUi('my_mainwindow.ui', self)

        self.setWindowTitle("Каталог")

        self.pixmap = QPixmap('vkusno.png')
        self.image = QLabel(self)
        self.image.move(5, 200)
        self.image.resize(90, 80)
        self.image.setPixmap(self.pixmap)

        self.check = {}
        self.spisok = []
        self.fin_cost = 0

        self.admin_btn.clicked.connect(self.open_widget)
        self.comboBox.currentTextChanged.connect(self.table)
        self.radioButton.clicked.connect(self.input_flag)
        self.radioButton_2.clicked.connect(self.input_flag)
        self.show_check.clicked.connect(self.open_check)

    """ создание текстового файла в котором записаны все выбранные позиции. Формат вывода:
        name: "название" count: "колличество" price: "цена за колличество товара" 

        финальная стоимость "сумма цен всех позиций" 
        """
    def check_in_csv(self):
        f = open("check.txt", "w", encoding="utf8")
        for key, n in self.check.items():
            string = "name: " + key.split("\n\n")[0] + " count: " + str(n) + " price: " + str(
                float(key.split("\n\n")[1]) * int(n)) + "\n"
            f.write(string)
        f.write("\n" + "финальная стоимость: " + str(self.fin_cost))
        f.close()
        pass

    def table(self):
        # удаление старых виджетов
        for i in self.spisok:
            i.close()
        self.spisok.clear()

        name = "projectproject.db"
        con = sqlite3.connect(name)
        cur = con.cursor()

        # создание списка кортежей в котором есть все назавния типов которые мы хотим вывести
        if self.comboBox.currentText() == "всё":
            types = cur.execute("""SELECT title FROM types""").fetchall()
        else:
            types = [(str(self.comboBox.currentText()),)]

        konec = 0
        # перебор каждого типа
        for i in range(len(types)):
            # создание названия
            name = types[i][0]
            self.label = QLabel(name, self)
            self.label.move(100, 5 + 120 * i + 100 * konec)
            self.label.show()
            self.spisok.append(self.label)

            # создание кортежа из позиций
            if len(types) == 1:
                id = cur.execute(f"""SELECT id FROM types WHERE title = '{types[0][0]}'""").fetchone()
                katalog = cur.execute(f"""SELECT title FROM katalog WHERE type = {id[0]}""").fetchall()
            else:
                katalog = cur.execute(f"""SELECT title FROM katalog WHERE type = {i + 1}""").fetchall()

            x = self.size().width() - 150

            n = 0
            m = 0
            s = 0
            # перебор каждой позиции в типе
            for j in range(len(katalog)):
                x -= 94
                if x < 0:
                    m += 1
                    s += n
                    n = 0
                    x = self.size().width() - 150 - 94
                price = cur.execute(f"""SELECT price FROM katalog WHERE title = '{katalog[j][0]}'""").fetchall()[0][0]
                qwe = katalog[j][0] + "\n" + "\n" + str(price)
                self.btn = QPushButton(qwe, self)
                self.btn.resize(100, 100)
                self.btn.move(100 + (j - s) * 100, 30 + 120 * i + 100 * m + 100 * konec)
                self.spisok.append(self.btn)
                self.btn.clicked.connect(self.fin_price)
                self.btn.show()
                n += 1
            konec += m

    # переключение флажка с удалением/добавлением
    def input_flag(self):
        self.radioButton.setChecked(0)
        self.radioButton_2.setChecked(0)
        self.sender().setChecked(1)

    # создание словаря с позициями
    def fin_price(self):
        stroka = self.sender().text()
        if self.radioButton.isChecked():
            if stroka in self.check:
                self.check[stroka] += 1
            else:
                self.check[stroka] = 1
            self.fin_cost += float(stroka.split("\n\n")[1])
        else:
            if stroka in self.check:
                self.check[stroka] -= 1
                if self.check[stroka] == 0:
                    self.check.pop(stroka)
                self.fin_cost -= float(stroka.split("\n\n")[1])
        self.label_price.setText(str(self.fin_cost))

    # диалоговое окно для ввода пароля
    def open_widget(self):
        otvet, ok_pressed = QInputDialog.getText(self, "Вход только для администраторов", "Напишите парроль")
        if otvet == "512354" and ok_pressed == True:
            self.widget = Main_Widget()
            self.widget.show()
            self.hide()
        else:
            pass

    # открытие окна с оплатой
    def open_check(self):
        self.check_in_csv()
        self.check_wi = Check_Widget()
        self.check_wi.show()
        self.hide()

    # перерисовка таблицы при изменении размера экрана
    def resizeEvent(self, event):
        self.table()

# панель администратора для изменения базы данных
class Main_Widget(QWidget):
    # создание панели администратора в которой можно изменять, добавлять и удалять позиции
    def __init__(self):
        super().__init__()
        uic.loadUi("my_widget.ui", self)

        self.setWindowTitle("Настройка меню")

        self.pixmap = QPixmap('vkusno.png')
        self.image = QLabel(self)
        self.image.move(200, 200)
        self.image.resize(90, 80)
        self.image.setPixmap(self.pixmap)

        self.load_table()

        self.add_btn.clicked.connect(self.add_stroka)
        self.back_btn.clicked.connect(self.close_widget)
        self.update_btn.clicked.connect(self.update_stroka)
        self.delete_idd.clicked.connect(self.delete_id)
        self.delite_title.clicked.connect(self.delete_name)

    # подгрузка таблицы
    def load_table(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('projectproject.db')
        db.open()
        model = QSqlTableModel(self, db)
        model.setTable('katalog')
        model.select()
        self.tableView.setModel(model)
        self.tableView.show()

        model_2 = QSqlTableModel(self, db)
        model_2.setTable('types')
        model_2.select()
        self.tableView_2.setModel(model_2)
        self.tableView_2.show()
        # -----------------------

        self.con = sqlite3.connect('projectproject.db')
        self.cur = self.con.cursor()

    # добавление строки
    def add_stroka(self):
        self.label_5.setText("")
        a = self.add_title.text()
        b = self.add_type.currentText()
        c = float(self.doubleSpinBox.value())
        if a == "":
            self.label_5.setText("имя не может быть пустой строкой")
        else:
            if len(self.cur.execute(f"""SELECT * FROM katalog WHERE title = '{a}'""").fetchall()) != 0:
                self.label_5.setText("такое имя уже существует")
            else:
                otvet, ok_pressed = QInputDialog.getText(self, "Подтвердите",
                                                         "Вы точно хотите добавить новую строчку?\n Напишите  ПОДВЕРДИТЬ  если вы согласны.")
                if otvet == "ПОДТВЕРДИТЬ" and ok_pressed:
                    self.cur.execute(f"""INSERT INTO katalog(title,type,price) VALUES ('{a}',{b},{c})""")
                    self.con.commit()
                    self.load_table()
                else:
                    self.label_5.setText("Вы не подтвердили изменения")

    # обновление строки
    def update_stroka(self):
        self.label_5.setText("")
        a = self.update_title.text()
        b = self.update_type.currentText()
        c = float(self.doubleSpinBox_2.value())
        id = self.update_id.text()
        if a == "":
            self.label_5.setText("имя не может быть пустой строкой")
        elif id == "":
            self.label_5.setText("id не может быть пустой строкой")
        else:
            try:
                id = int(id)
                if len(self.cur.execute(f"""SELECT * FROM katalog 
                WHERE title = '{a}' AND type = {b} AND price = {c}""").fetchall()) != 0:
                    self.label_5.setText("такая позиция уже существует")
                else:
                    otvet, ok_pressed = QInputDialog.getText(self, "Подтвердите",
                                                             f"Вы точно хотите обновить строку с id = {id}?\n Напишите  ПОДВЕРДИТЬ  если вы согласны.")
                    if otvet == "ПОДТВЕРДИТЬ" and ok_pressed:
                        self.cur.execute(f"""UPDATE katalog SET title = '{a}' WHERE id = {id}""")
                        self.cur.execute(f"""UPDATE katalog SET type = {b} WHERE id = {id}""")
                        self.cur.execute(f"""UPDATE katalog SET price = {c} WHERE id = {id}""")
                        self.con.commit()
                        self.load_table()
                    else:
                        self.label_5.setText("Вы не подтвердили изменения")

            except:
                self.label_5.setText("введите коректный id")

    # удаление строки по id
    def delete_id(self):
        self.label_5.setText("")
        a = self.delete_edit_1.text()
        if a != "":
            try:
                if len(self.cur.execute(f"""SELECT * FROM katalog WHERE id = {a}""").fetchall()) != 0:
                    otvet, ok_pressed = QInputDialog.getText(self, "Подтвердите",
                                                             f"Вы точно хотите удалить строку с id = {a}?\n Напишите  ПОДВЕРДИТЬ  если вы согласны.")
                    if otvet == "ПОДТВЕРДИТЬ" and ok_pressed:
                        self.cur.execute(f"""DELETE FROM katalog WHERE id = {a}""")
                        self.con.commit()
                        self.load_table()
                    else:
                        self.label_5.setText("Вы не подтвердили изменения")

                else:
                    self.label_5.setText("такого id не существует")
            except:
                self.label_5.setText("введите коректный айди")
        else:
            self.label_5.setText("id не может быть пустым")

    # удаление строки по id
    def delete_name(self):
        self.label_5.setText("")
        a = self.lineEdit_6.text()
        if a != "":
            try:
                if len(self.cur.execute(f"""SELECT * FROM katalog WHERE title = '{a}'""").fetchall()) != 0:
                    otvet, ok_pressed = QInputDialog.getText(self, "Подтвердите",
                                                             f"Вы точно хотите удалить строку с названием = {a}?\n Напишите  ПОДВЕРДИТЬ  если вы согласны.")
                    if otvet == "ПОДТВЕРДИТЬ" and ok_pressed:
                        self.cur.execute(f"""DELETE FROM katalog WHERE title = '{a}'""")
                        self.con.commit()
                        self.load_table()
                    else:
                        self.label_5.setText("Вы не подтвердили изменения")

                else:
                    self.label_5.setText("такой позиции не существует")
            except:
                self.label_5.setText("введите коректное имя")
        else:
            self.label_5.setText("пустых имён в этой таблице нет!!!")

    # правильное закрытие окна с изменением мейн виндоу для того чтобы оно обновилось
    def close_widget(self):
        self.con.commit()
        self.con.close()
        self.close()
        x = ex.size().width()
        y = ex.size().height()
        ex.resize(x + 1, y + 1)
        ex.show()

    # конвертация окна при изменение размера окна
    def resizeEvent(self, event):
        x = self.size().width()
        y = self.size().height()
        self.scrollArea.resize(x, y - 280)
        self.scrollArea.move(0, 280)


class Check_Widget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('my_check.ui', self)

        self.setWindowTitle("Оплата")

        self.pixmap = QPixmap('vkusno.png')
        self.image = QLabel(self)
        self.image.move(5, 100)
        self.image.resize(90, 80)
        self.image.setPixmap(self.pixmap)

        self.open_txt()

        self.pushButton.clicked.connect(self.process_data)
        self.close_widget.clicked.connect(self.close_check)

    # открытие текстового файла в listWidget
    def open_txt(self):
        f = open("check.txt", "r", encoding="utf8")
        self.textBrowser.setText(f.read())

    # закрытие окна
    def close_check(self):
        self.close()
        x = ex.size().width()
        y = ex.size().height()
        ex.resize(x + 1, y + 1)
        ex.show()

    # получение и проверка номера карты
    def get_card_number(self):
        card_num = self.card_data.text()
        card_num = ''.join(card_num.split())
        if card_num.isdigit() and len(card_num) == 16:
            return card_num
        else:
            return 404

    # получение и проверка кода карты
    def get_card_kod(self):
        card_kod = self.kod_data.text()
        card_kod = ''.join(card_kod.split())
        if card_kod.isdigit() and len(card_kod) == 3:
            return card_kod
        else:
            return 404

    # получение и проверка срока действия карты
    def get_card_srok(self):
        card_srok = self.srok_data.text()
        card_srok = ''.join(''.join(card_srok.split()).split("/"))
        if card_srok.isdigit() and len(card_srok) == 4:
            now = datetime.datetime.now()
            if int(str(now.year)[2:4]) < int(card_srok[2:4]):
                return card_srok
            elif int(str(now.year)[2:4]) == int(card_srok[2:4]) and now.month <= int(card_srok[:2]):
                return card_srok
            else:
                return 400
        else:
            return 404

    # проверка Луна
    def double(self, x):
        res = x * 2
        if res > 9:
            res = res - 9
        return res

    # продолжение проверки Луна
    def luhn_algorithm(self, card):
        odd = map(lambda x: self.double(int(x)), card[::2])
        even = map(int, card[1::2])
        return (sum(odd) + sum(even)) % 10 == 0

    # проверка всех условий и вывод состояния
    def process_data(self):
        number = self.get_card_number()
        srok = self.get_card_srok()
        kod = self.get_card_kod()
        if number == 404:
            self.errorLabel.setText(
                "Введите только 16 цифр. Допускаются пробелы")
        elif self.luhn_algorithm(number):
            if srok == 404:
                self.errorLabel.setText("Введите коректный срок")
            elif srok == 400:
                self.errorLabel.setText("Срок действия карты истёк")
            else:
                if kod == 404:
                    self.errorLabel.setText("Введите коректный код")
                else:
                    self.errorLabel.setText("оплата прошла успешно")
        else:
            self.errorLabel.setText("Номер недействителен. Попробуйте снова.")

# вывод ошибки в компилятор
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_Window()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())