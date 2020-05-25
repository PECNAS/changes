import sys  # sys нужен для передачи argv в QApplication
import json # для хранения настроек в файле config.json
import vk # для получения информации о группе
import thread6 # для многопоточности программы
import pymysql # для работы с субд

from PyQt5 import Qt, QtGui, QtWidgets # работа с интерфейсом
from PyQt5.QtWidgets import QMainWindow, QApplication
from packages.main_interface import Ui_MainWindow as main_window # Это наш конвертированный файл дизайна
from packages.settings import Ui_MainWindow as settings_window # Это наш конвертированный файл дизайна
from packages import database_append as db # это файл, который работает с базой данных

class MainWindow(QMainWindow, main_window):
	def __init__(self):
		super().__init__()
		self.setupUi(self)  # Это нужно для инициализации нашего дизайна
		self.toolButton.clicked.connect(lambda: settings.show()) # для показа окна настроек

		self.vk_settings() # вызываем функцию, которая настраивает vkAPI
		self.write_changes = False # ставим запись в базу по умолчанию на False

		self.check_box.stateChanged.connect(self.set_mode) # если измениться состояние чекбокса, означающего запись в бд, то измениться состояние других чекбоксов
		self.start_button.clicked.connect(self.get_members) # запускает парсер
		self.comparison_button.clicked.connect(self.compare_groups) # запускает сравнение (ТРЕБУЕТСЯ ПОДКЛЮЧЕНИЕ К СУБД)

		self.w = self.size().width()     # "определение ширины"
		self.h = self.size().height()    # "определение высоты"


	def vk_settings(self): # объяявляем вк настройки
		self.token = "" # объявляем пустой токен. Потом мы его просто переназначаем(объявляем, что бы не было ошибки)
		try:
			config = open("packages\\config.json", 'x') # создаём файл
			config.close()

			self.block_widgets() # блокируем главный экран
			settings.set_closable(False) # запрещаем закрытие окна
			settings.show() # показываем окно настроек

		except FileExistsError: # если таковой уже существует
			try:
				config = open("packages\\config.json", 'r') # читаем содержимое файла
				self.token = json.load(config)['token']
				config.close()
			except json.decoder.JSONDecodeError: # если файл пустой
				self.block_widgets() # блокируем главный экран
				settings.set_closable(False) # запрещаем закрытие окна
				settings.show() # показываем окно настроек

		self.session = vk.Session(access_token=self.token)  # Авторизация
		self.vk_api = vk.API(self.session)


	def set_mode(self, state): # разрешаем или запрещаем запись опираясь на чекбокс
		if state == 2:
			self.write_changes = True
		else:
			self.write_changes = False

	@thread6.threaded() # потоки
	def get_members(self, group_name: list=None, compare=False, *args): # парсим количество участников
		if compare == False: # если режим сравнения выключен
			ids = set(self.url_box.text().split(';')) # берём id групп из поля ввода
		else:
			ids = group_name # берём список id

		self.url_box.clear() # убираем ссылки
		self.block_widgets() # блокируем виджеты

		for row in ids:
			group_id = self.url_clear_fix(row) # вызываем функцию "очищения" id
			if group_id != "Invalid url!": # если функция не вернула ошибку
				try: # ловим ошибки
					first = self.vk_api.groups.getMembers(group_id=group_id, v=5.92)  # Первое выполнение метода
					data = first['items']  # Присваиваем переменной первую тысячу id'шников
					count = first['count'] // 1000  # Присваиваем переменной количество тысяч участников

					for i in range(1, count + 1):  
						data = data + self.vk_api.groups.getMembers(group_id=group_id, v=5.92, offset=(i * 1000))['items'] # делаем так, что бы был не двухмерный массив, а одномерный

					result = {'ids': data, 'count': first['count'], 'title': group_id} # формируем переменную для компоновки всех значение
					self.url_box.clear() # очищаем поле ввода для ссылки
					
					if compare == False: # если сравнение выключено
						self.information_box.append(f"(Id-шник: {result['title']}) Подписчики: {result['count']}\n") # добавляем текст
					else:
						self.unblock_widgets()
						return result # не добавляем, а возвращаем результат

					if self.write_changes == True: # если стоит запись
						cursor, connection = db.connect() # подключаемся к базе данных
						db.insert(cursor, connection, group_name=result['title'], users=result['ids']) # добавляем в базу данных или обновляем значение
						db.close_connection(connection) # закрываем сосединение

				except pymysql.err.OperationalError: # если не удалось подключиться к базе данных
					self.information_box.append("Connection Error")

					configs = settings.get_settings() # Получаем настройки с файла
					if configs['ip'] == "" or configs['ip'] == " ": # если ip пустой 
						self.information_box.append("Empty database ip")
					if configs['login'] == "" or configs['login'] == " ": # если логин пустой
						self.information_box.append("Empty database login")
					if configs['password'] == "" or configs['password'] == " ": # если пароль пустой
						self.information_box.append("Empty database password")

				except vk.exceptions.VkAPIError: # если неверный токен или неправильная ссылка на группу
					self.information_box.append("Invalid url or application token!")
			else: # если выдал ошибку о том, что неверный url
				self.information_box.append("Invalid url!") # выводим ошибку

		self.information_box.append("Complete!\n----------------------------------------------------------------\n\n") # завершнеие
		self.unblock_widgets() # разблокируем все виджеты

	def block_widgets(self): # блокировка виджетов
		self.url_box.setReadOnly(True)
		self.check_box.setCheckable(False)
		self.comparison_button.setEnabled(False)
		self.start_button.setEnabled(False)
		self.toolButton.setEnabled(False)

	def unblock_widgets(self): # разблокировака виджетов
		self.url_box.setReadOnly(False)
		self.check_box.setCheckable(True)
		self.comparison_button.setEnabled(True)
		self.start_button.setEnabled(True)
		self.toolButton.setEnabled(True)

	def url_clear_fix(self, url): # "чистка" ссылок
		if url != "" and url != " ":
			url = url.replace("?from=top", "")
			url = url.replace("public", "")
			url = url.replace("club", "")
			url = url.split('/')[-1]

			return url
		else:
			return "Invalid url!"

	@thread6.threaded() # поток
	def compare_groups(self, *args): # функция сравнения 
		group_name = self.comparison_name.text() # получаем название 
		group_name = self.url_clear_fix(group_name) # "чистка" ссылки
		self.comparison_name.clear() # очищаем поле для ввода ссылок для очистки
		real_members = self.get_members(group_name=[group_name], compare=True).await_output()['ids'] # берём только идентификаторы

		cursor, connection = db.connect() # подключаемся к базе данных
		come, departed = db.compare(cursor, connection, group_name, real_members) # получаем два списка: кто пришёл и кто ушёл
		db.close_connection(connection) # закрываем соединение
		self.append_after_compaire(come, departed) # добавляем всех, кто пришёл и всех, кто ушел


	def append_after_compaire(self, come, departed): # функция добавления пользователей
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
		width =  self.size().width() # находим ширину
		height = self.size().height() # находим высоту

		koefW = width / self.w # коэффициент широты 
		koefH = height / self.h # коэффициент высоты

		self.information_box.setGeometry(20 * koefW, 10 * koefH, 421 * koefW, 301 * koefH) # 20, 10, 421, 301
		self.url_box.setGeometry(470 * koefW, 20 * koefH, 261 * koefW, 31 * koefH) # 470, 20, 261, 31
		self.check_box.setGeometry(470 * koefW, 90 * koefH, 151 * koefW, 41 * koefH) # 470, 90, 151, 41
		self.start_button.setGeometry(620 * koefW, 220 * koefH, 141 * koefW, 61 * koefH) # 620, 220, 141, 61
		self.toolButton.setGeometry(770 * koefW, 0 * koefH, 25 * koefW, 19 * koefH) # 770, 0, 25, 19
		self.comparison_button.setGeometry(460 * koefW, 220 * koefH, 141 * koefW, 61 * koefH) # 460, 220, 141, 61
		self.comparison_name.setGeometry(470 * koefW, 140 * koefH, 261 * koefW, 31 * koefH) # 470, 140, 261, 31


class Settings(QMainWindow, settings_window): # окно настроек
	def __init__(self):
		super().__init__() # вызываем у родительского элемента
		self.setupUi(self) # вызываем из файла interface
		self.pushButton.clicked.connect(self.write_config)
		self._closable = True


		self.w = self.size().width()     # "определение ширины"
		self.h = self.size().height()    # "определение высоты"

	def set_closable(self, state): # функция меняет возможность закрытия окна
		self._closable = state

	def write_config(self): # записываем настройки в config файл
		if self.lineEdit.text() != "" and self.lineEdit.text() != "Invalid token...":
			self.set_closable(True)
			window.unblock_widgets() # разблокируем виджеты
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

			window.vk_settings() # меняем токен на новый
		else:
			self.set_closable(False) # запрещаем закрытие окна
			self.lineEdit.setText("Invalid token...") # выдаём ошибку

	def closeEvent(self, evnt): # функция, игнорируюшая акрытие окна в момент ввода токена, когда он еще не введён
		if self._closable:
			super(Settings, self).closeEvent(evnt) # закрываем
		else:
			evnt.ignore() # запрещаем закрытие

	def get_settings(self):
		with open("packages\\config.json", 'r') as config:
			dictionary = json.load(config)
			return dictionary

	def resizeEvent(self, event): # вызывается автоматически при изменении размера окна
		width =  self.size().width()
		height = self.size().height()

		koefW = width / self.w 
		koefH = height / self.h 

		self.pushButton.setGeometry(290 * koefW, 140 * koefH, 201 * koefW, 61 * koefH) # 290, 140, 201, 61
		self.lineEdit.setGeometry(10 * koefW, 10 * koefH, 511 * koefW, 41 * koefH) # 10, 10, 511, 41
		self.db_ip.setGeometry(10 * koefW, 60 * koefH, 251 * koefW, 31 * koefH) # 10, 60, 251, 31
		self.db_login.setGeometry(280 * koefW, 60 * koefH, 241 * koefW, 31 * koefH) # 280, 60, 241, 31
		self.db_password.setGeometry(10 * koefW, 140 * koefH, 251 * koefW, 31 * koefH) # 10, 140, 251, 31


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
	app = QApplication(sys.argv)  # Новый экземпляр QApplication
	settings = Settings() # создаём объект класса Settings
	window = MainWindow()  # Создаём объект класса MainWindow
	
	window.show()  # Показываем окно
	app.exec_()  # и запускаем приложение