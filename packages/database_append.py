import pymysql.cursors
import json

def connect():
	with open("D:\\программы\\Python\\интерфейс\\changes\\packages\\config.json", 'r') as config:
		dictionary = json.load(config)
	config.close()

	ip = dictionary['ip']
	login = dictionary['login']
	password = dictionary['password']


	connection = pymysql.connect(host=ip,
								 user=login,
								 password=password,
								 db="groups_compare")
	cursor = connection.cursor()

	return cursor, connection


def update_members(cursor, connection, group_name, users):
	cursor.execute("UPDATE `groups` SET `members` = '" + str(users) + "' WHERE `title` = '" + str(group_name) + "'")
	cursor.execute("UPDATE `groups` SET `count` = '" + str(len(users)) + "' WHERE `title` = '" + str(group_name) + "'")
	connection.commit()


def get_members(cursor, connection, group_name):
	cursor.execute("SELECT `id`, `members` FROM `groups` WHERE `title` = '" + group_name + "'")
	group_id = cursor.fetchone()
	members = group_id[1]
	members = [int(i) for i in members.replace("[", "").replace("]", "").split(',')] # генератором из строки в список
	group_id = group_id[0]

	return group_id, members


def insert(cursor, connection, group_name, users):
	try:
		cursor.execute("SELECT MAX(`id`) FROM `groups`") # выполняем команлу 
		max_id = cursor.fetchall()[0][0]

		if max_id == None:
			max_id = 0

		cursor.execute("""INSERT INTO `groups`(`id`, `count`, `title`, `members`) VALUES(""" + str(max_id + 1) + """, '""" + str(len(users)) + """', '""" + group_name + """', '""" + str(users) + """')""")
		connection.commit()

	except pymysql.IntegrityError as e:
		update_members(cursor, connection, group_name, users)


def compare(cursor, connection, group_name, real_members):
	cursor.execute("SELECT `members` FROM `groups` WHERE `title` = '" + group_name + "'")
	pre_members = cursor.fetchone()[0] # вытягиваем всё из полученного
	pre_members = [int(i) for i in pre_members.replace("[", "").replace("]", "").split(',')] # генератором из строки в список

	come = list(set(real_members) - set(pre_members))
	departed = list(set(pre_members) - set(real_members))

	return come, departed

def close_connection(connection):
	connection.close()

if __name__ == "__main__":
	cursor, connection = connect()
	group_name, users = get_members(cursor, connection, "howdyho_net")
	compare(cursor, connection, "howdyho_net", users)
	close_connection(connection)