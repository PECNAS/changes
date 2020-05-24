import sys  # sys нужен для передачи argv в QApplication
import json
import vk
import time
import thread6

from PyQt5 import Qt, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from packages.main_interface import Ui_MainWindow as main_window # Это наш конвертированный файл дизайна
from packages.settings import Ui_MainWindow as settings_window # Это наш конвертированный файл дизайна
from packages import database_append as db

class MainWindow(QMainWindow, main_window):
	def __init__(self):
		super().__init__()
		self.setupUi(self)  # Это нужно для инициализации нашего дизайна
		self.toolButton.clicked.connect(lambda: settings.show())

		config = open("packages/config.json", 'r')
		self.token = json.load(config)['token'] # получаем токен
		config.close()

		self.session = vk.Session(access_token=self.token)  # Авторизация
		self.vk_api = vk.API(self.session)
		self.write_changes = False

		self.check_box.stateChanged.connect(self.set_mode)
		self.start_button.clicked.connect(self.get_members)
		self.comparison_button.clicked.connect(self.compare_groups)

		self.w = self.size().width()     # "определение ширины"
		self.h = self.size().height()    # "определение высоты"


	def set_mode(self, state):
		if state == 2:
			self.write_changes = True
		else:
			self.write_changes = False

	@thread6.threaded()
	def get_members(self, group_name=None, compare=False, *args):
		if compare == False:
			ids = set(self.url_box.text().split(';'))
		else:
			ids = group_name

		self.url_box.clear()
		self.block_widgets()

		for row in ids:
			group_id = self.url_clear_fix(row)
			if group_id != "Invalid url!":
				try:
					first = self.vk_api.groups.getMembers(group_id= group_id, v=5.92)  # Первое выполнение метода
					data = first['items']  # Присваиваем переменной первую тысячу id'шников
					count = first['count'] // 1000  # Присваиваем переменной количество тысяч участников

					for i in range(1, count + 1):  
						data = data + self.vk_api.groups.getMembers(group_id=group_id, v=5.92, offset=(i * 1000))['items'] # делаем так, что бы был не двухмерный массив, а одномерный

					result = {'ids': data, 'count': first['count'], 'title': group_id} # формируем переменную для компоновки всех значение
					self.url_box.clear() # очищаем поле ввода для ссылки
					if compare == False:
						self.information_box.append(f"(Id-шник: {result['title']}) Подписчики: {result['count']}\n") # добавляем текст
					else:
						self.unblock_widgets()
						return result

					if self.write_changes == True: # если стоит запись
						cursor, connection = db.connect() # подключаемся к базе данных
						db.insert(cursor, connection, group_name=result['title'], users=result['ids']) # добавляем в базу данных или обновляем значение
						db.close_connection(connection)

				except:  
					self.information_box.append("Invalid url!")
			else:
				self.information_box.append(group_id)

		self.information_box.append("Complete!\n----------------------------------------------------------------\n\n")
		self.unblock_widgets()

	def block_widgets(self):
		self.url_box.setReadOnly(True)
		self.check_box.setCheckable(False)
		self.comparison_button.setEnabled(False)
		self.start_button.setEnabled(False)
		self.toolButton.setEnabled(False)

	def unblock_widgets(self):
		self.url_box.setReadOnly(False)
		self.check_box.setCheckable(True)
		self.comparison_button.setEnabled(True)
		self.start_button.setEnabled(True)
		self.toolButton.setEnabled(True)

	def url_clear_fix(self, url):
		if url != "" and url != " ":
			url = url.replace("?from=top", "")
			url = url.replace("public", "")
			url = url.replace("club", "")
			url = url.split('/')[-1]

			return url
		else:
			return "Invalid url!"

	@thread6.threaded()
	def compare_groups(self, *args):
		try:
			group_name = self.comparison_name.text() # получаем название 
			group_name = self.url_clear_fix(group_name)
			self.comparison_name.clear()
			real_members = self.get_members(group_name=[group_name], compare=True).await_output()['ids'] # берём только идентификаторы

			cursor, connection = db.connect() # подключаемся к базе данных
			come, departed = db.compare(cursor, connection, group_name, real_members)
			db.close_connection(connection)
			self.append_after_compaire(come, departed)

		except:
			self.information_box.append("Invalid url for compare")

	def append_after_compaire(self, come, departed):
		if come == []:
			self.information_box.append("Никто не пришёл")
		else:
			self.information_box.append(f"Всего пришли: {len(come)} ||| Идентификаторы: \n")
			for row in come:
				self.information_box.append(f"{row}")

		if departed == []:
			self.information_box.append("Никто не ушёл")
		else:
			self.information_box.append(f"Всего ушли: {len(departed)} ||| Идентификаторы: \n")
			for row in departed:
				self.information_box.append(f"{row}")

		self.information_box.append("Complete!\n----------------------------------------------------------------\n\n")

	def resizeEvent(self, event): # вызывается автоматически при изменении размера окна
		width =  self.size().width()
		height = self.size().height()

		koefW = width / self.w 
		koefH = height / self.h 

		self.information_box.setGeometry(20 * koefW, 10 * koefH, 421 * koefW, 301 * koefH) # 20, 10, 421, 301
		self.url_box.setGeometry(470 * koefW, 20 * koefH, 261 * koefW, 31 * koefH) # 470, 20, 261, 31
		self.check_box.setGeometry(470 * koefW, 90 * koefH, 151 * koefW, 41 * koefH) # 470, 90, 151, 41
		self.start_button.setGeometry(620 * koefW, 220 * koefH, 141 * koefW, 61 * koefH) # 620, 220, 141, 61
		self.toolButton.setGeometry(770 * koefW, 0 * koefH, 25 * koefW, 19 * koefH) # 770, 0, 25, 19
		self.comparison_button.setGeometry(460 * koefW, 220 * koefH, 141 * koefW, 61 * koefH) # 460, 220, 141, 61
		self.comparison_name.setGeometry(470 * koefW, 140 * koefH, 261 * koefW, 31 * koefH) # 470, 140, 261, 31



class Settings(QMainWindow, settings_window):
	def __init__(self):
		super().__init__() # вызываем у родительского элемента
		self.setupUi(self) # вызываем из файла interface
		self.pushButton.clicked.connect(self.write_config)

	def write_config(self):
		if self.lineEdit.text() != "":
			dictionary = {
				'token': self.lineEdit.text(),
				'ip': self.db_ip.text(),
				'login': self.db_login.text(),
				'password': self.db_password.text()

			}
			with open("packages/config.json", 'w') as config:
				json.dump(dictionary, config, indent=4)
			config.close() # закрыли файл
			settings.close() # закрыли окно
		else:
			self.lineEdit.setText("Invalid token...")

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
	app = QApplication(sys.argv)  # Новый экземпляр QApplication
	window = MainWindow()  # Создаём объект класса MainWindow
	settings = Settings() # создаём объект класса Settings
	
	window.show()  # Показываем окно
	app.exec_()  # и запускаем приложение