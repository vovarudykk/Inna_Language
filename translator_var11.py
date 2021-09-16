import re
import sys

from lex_analizator_var11 import LexAnalizator

class Syntax(object):
	# different_token = 'Ошибка! Неверный токен.\nОжидался  ({0}).'
	len_error = 'Синтаксический анализатор:\nОшибка! Неожиданный конец программы.\nВ таблице символов нет записи с номером ({1}), ожидался ({0}).'
	different_token_error = 'Синтаксический анализатор:\nОшибка! В строке {0} неожиданный элемент ({3},{4}), ожидался ({1},{2}).'
	different_instruction = 'Синтаксический анализатор:\nОшибка! В строке {0} неожиданный элемент ({1},{2}), ожидался ({3}).'
	different_factors_error = 'Синтаксический анализатор:\nОшибка! В строке {0} неожиданный элемент ({1},{2}), ожидался ({3}).'
	inccorect_type_error = 'Синтаксический анализатор:\nОшибка! В строке {0} несуществующий тип данных ({1},{2}).'
	failed_name_id = "Синтаксический анализатор:\nОшибка! \n\t В строке {0} несуществующий идентификатор ({1},{2})."
	len_error_undefined = 'Синтаксический анализатор:\nОшибка! Неожиданный конец программы.\nВ таблице символов нет записи с номером ({0}).'
	undefined_id = 'Транслятор:\nОшибка! В строке {0} использована необьявленная переменная ({1}, {2}).'
	repeat_id = 'Транслятор:\nОшибка! В строке {0} повторное обьявление переменной ({1}, {2}).'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
	def __init__(self, table_symbols, const, ident):
		self.symbols_table = table_symbols
		self.len_symbol_table = len(self.symbols_table)
		self.current_number_word = 1
		self.oper = 0
		self.postfixCode = []
		self.step_translation = 0
		self.const = const
		self.ident = ident
		self.checkError = True
		self.temp_id = []
		self.flag_declaration = False
		self.labels = {}
		self.lastLabelIndex = 0

	def printTranslation(self, num):
		print("Шаг трансляции №" + str(self.step_translation))
		print("symbols_table[" + str(num) + "] = " + str(self.symbols_table[num]))
		print("postfixCode = " + str(self.postfixCode) + "\n")

	def createLabel(self, row_of_program, symbol_name, class_name):
		self.lastLabelIndex += 1
		lexeme = 'm' + str(self.lastLabelIndex)
		val = self.labels.get(lexeme)
		if val is None:
			self.labels[lexeme] = 'val_undef'
			tok = 'label'
		else:
			assert False, \
			'Транслятор:\nОшибка! В строке {0} конфликт меток ({1}{2})'.format(row_of_program, symbol_name, class_name)
		return [0, lexeme, tok]


	def setLabelVal(self, label):
		g, lex, tok = label
		self.labels[lex] = len(self.postfixCode) + 1
		return True

	def check_token(self, name, class_):
		# print("Do check_token")
		# print(self.get_current_symbol())
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if self.current_number_word > len(self.symbols_table): 
			self.checkError = False
			assert self.current_number_word <= len(self.symbols_table), Syntax.len_error.format((name, class_), self.current_number_word)
			sys.exit()
		if name != symbol_name or class_name != class_:
			self.checkError = False
			assert name == symbol_name and class_name == class_, Syntax.different_token_error.format(row_of_program, name, class_, symbol_name, class_name)
			sys.exit()
		self.current_number_word += 1


	def check_end_of_statment(self):
		# print("Do check_end_of_statment")
		# print(self.get_current_symbol())
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if symbol_name != ';':
			self.checkError = False
			assert symbol_name == ';', Syntax.different_instruction.format(row_of_program, symbol_name, class_name, (';', 'punct'))
			sys.exit()
		self.current_number_word += 1


	def check_end(self, name, class_):
		# print("Do check_end")
		# print(self.get_current_symbol())
		if self.current_number_word > len(self.symbols_table):
			self.checkError = False
			assert self.current_number_word <= len(self.symbols_table), Syntax.len_error.format((name, class_), self.current_number_word)
			sys.exit()
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if symbol_name != name or class_name != class_:
			self.checkError = False 
			assert name == symbol_name and class_name == class_, Syntax.different_token_error.format(self.current_number_word, name, class_, symbol_name, class_name)
			sys.exit()


	def get_current_symbol(self):
		if self.current_number_word > len(self.symbols_table):
			self.checkError = False
			assert self.current_number_word <= len(self.symbols_table), Syntax.len_error_undefined.format(self.current_number_word)
			sys.exit()

		return self.symbols_table.get(self.current_number_word)[0], self.symbols_table.get(self.current_number_word)[1], self.symbols_table.get(self.current_number_word)[2]


	def parse(self):
		# print("Do parse")
		try:
			self.check_token('program', 'keyword')
			self.parse_id()
			self.check_token('var', 'keyword')
			self.parse_declaration_list()
			self.flag_declaration = True
			self.check_token('begin', 'keyword')
			self.parse_statment_list()
			self.check_end('end', 'keyword')

			print("-"*100)
			print("Синтаксический анализ и трансляция в ПОЛИС прошли успешно!")
			print("-"*100)
		except Exception as ex:
			print(ex)


	def parse_id(self):
		row_of_program, symbol_name, class_name = self.get_current_symbol()

		if self.flag_declaration:
			self.checkDefinedIdent()


		# print("Do parse_id")
		# print(self.get_current_symbol())
		if self.flag_declaration == False:
			self.checkNonRepeatId(row_of_program, symbol_name, class_name)
		if class_name == "id":
			if re.fullmatch(r"^[^\d\W]\w*\Z", symbol_name):
				self.current_number_word += 1
				return True
			else:
				self.checkError = False
				assert False, Syntax.failed_name_id.format(row_of_program, symbol_name, class_name)
		


	def check_type(self, row_of_program, symbol_name, class_name):
		# print("Do check_type")
		# print(symbol_name)
		if symbol_name != "int" and symbol_name != "double" and symbol_name != "bool" and symbol_name != "real" and symbol_name != 'string':
			self.checkError = False
			assert symbol_name == "int" or symbol_name == "double" or symbol_name == "bool" or symbol_name == "real" or symbol_name == 'string', Syntax.inccorect_type_error.format(row_of_program, symbol_name, class_name)
			sys.exit()
		self.current_number_word += 1


	def parse_declaration_list(self):
		self.current_number_word -=1
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		# print("Do parse_declaration_list")
		# print(self.get_current_symbol())

		if symbol_name == 'var':
			state = 0
			self.current_number_word += 1
			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if symbol_name == "begin":
				self.checkError = False
				assert symbol_name != "begin", "Синтаксический анализатор:\nОшибка! Декларация переменных не может быть пустой."
				sys.exit()

			while True:
				row_of_program, symbol_name, class_name = self.get_current_symbol()
				if class_name == 'id':
					state = 0
					self.temp_id.append(symbol_name)
					self.parse_id()
					row_of_program, symbol_name, class_name = self.get_current_symbol()
					

				elif class_name == 'comma':
					state = 1
					self.current_number_word += 1
				
				elif symbol_name == ':' and state != 1:
					self.current_number_word += 1
					row_of_program, symbol_name, class_name = self.get_current_symbol()

					for i in range(len(self.ident)):
						for t in range(len(self.temp_id)):
							if self.ident[i][0] == self.temp_id[t]:
								self.ident[i][1] = symbol_name

					self.temp_id.clear()
					self.check_type(row_of_program, symbol_name, class_name)
					self.check_end_of_statment()

				elif symbol_name == 'begin':
					break

				elif state == 1:
					row_of_program, symbol_name, class_name = self.get_current_symbol()
					if state == 1:
						self.checkError = False
						assert state != 1, "Синтаксический анализатор:\nОшибка! Ожидался идентификатор вместо ({0} {1}, {2})".format(row_of_program, symbol_name, class_name)
						sys.exit()
				
				else:
					self.checkError = False
					assert False, "Синтаксический анализатор:\nОшибка! Декларация переменных написана неправильно.".format(row_of_program, symbol_name, class_name)
					sys.exit()


	def parse_statment_list(self):
		# print("Do parse_statment_list")
		# print(self.get_current_symbol())

		count = 0

		is_work = True
		while is_work is True:
			count += 1

			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if class_name == "id":
				self.parse_assing()

				# row_of_program, symbol_name, class_name = self.get_current_symbol()
				# self.step_translation += 1
				# self.printTranslation(self.current_number_word)
				# self.postfixCode.append([row_of_program, symbol_name, class_name])
				
				self.check_end_of_statment()
			elif symbol_name == "read":
				self.parse_read()
			elif symbol_name == "write":
				self.parse_write()
			elif symbol_name == "for":
				self.parse_for_statement()
			elif symbol_name == "if":
				self.parse_if_statment()
			elif symbol_name == "rof":
				is_work = False
			elif symbol_name == "fi":
				is_work = False
			elif symbol_name == "end":
				is_work = False
			elif count >= 1000:
				self.checkError = False
				print("Опять попал в бесконечный цикл, дурачек!")
				sys.exit()
				break
			else:
				self.checkError = False
				assert False, 'Синтаксический анализатор:\nОшибка! Строка {0}, лексема ("{1}", {2})  в неправильном месте.'.format(row_of_program, symbol_name, class_name)
				sys.exit()
				break
	

	def checkDefinedIdent(self):
		row_of_program, symbol_name, class_name = self.get_current_symbol()

		status = ""
		for i in self.ident:
			if i[0] == symbol_name:
				status = i[1]

		if status == 'type_undef' and class_name == 'id':
			self.checkError = False
			print(status, "error")
			assert False, Syntax.undefined_id.format(row_of_program, symbol_name, class_name)
			sys.exit()

	def checkNonRepeatId(self, row_of_program, symbol_name, class_name):

		status = ""
		for i in self.ident:
			if i[0] == symbol_name:
				status = i[1]

		if status not in ('type_undef', 'prog_name') and class_name == 'id':
			self.checkError = False
			assert False, Syntax.repeat_id.format(row_of_program, symbol_name, class_name)

	def parse_assing(self):
		# print("Do parse_assign")
		# print(self.get_current_symbol())
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		self.step_translation += 1
		# self.printTranslation(self.current_number_word)
		self.postfixCode.append([row_of_program, symbol_name, class_name])

		self.parse_id()

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if class_name != "assign_op":
			self.checkError = False
			assert class_name == "assign_op", "Синтаксический анализатор:\nОшибка! Ожидался символ '=' вместо {0} {1}, {2}".format(row_of_program, symbol_name, class_name)
			sys.exit()
		temp1, temp2, temp3 = self.get_current_symbol()
		temp = [temp1, temp2, temp3]
		tmp = self.current_number_word

		self.current_number_word += 2
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if class_name == 'rel_op':
			self.current_number_word -= 1
			self.parse_bool_expr()
			# self.step_translation += 1
			# self.printTranslation(self.current_number_word)
			# self.postfixCode.append(temp)
		else:
			self.current_number_word -=1
			self.parse_expression()
			self.step_translation += 1
			# self.printTranslation(tmp)
			self.postfixCode.append(temp)


	def parse_repeat_statement(self):
		# print("Виконується Parse do_statement")
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		while symbol_name != 'rof':
			self.parse_statment_list()
			row_of_program, symbol_name, class_name = self.get_current_symbol()
		self.check_token('rof', 'keyword')


	def parse_expression(self):
		# print("Do parse_expression")
		# print(self.get_current_symbol())
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		temporary = 0

		if symbol_name == '-':
			temporary = [row_of_program, self.current_number_word]
			self.current_number_word += 1

			self.parse_term()

			self.postfixCode.append([temporary[0], 'NEG', 'add_op'])
			# self.printTranslation(temporary[1])
			temporary.clear()
		elif symbol_name == '+':
			self.current_number_word += 1
			self.parse_term()
		else:
			self.parse_term()
		flag = True
		temp = []
		temp_curent_num = 0
		# продовжувати розбирати Доданки (Term)
		# розділені лексемами '+' або '-'
		row_of_program, symbol_name, class_name = self.get_current_symbol()

		while flag:
			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if class_name == 'add_op':

				row_of_program, symbol_name, class_name = self.get_current_symbol()
				temp_curent_num = self.current_number_word
				temp.append(list(self.get_current_symbol()))

				self.current_number_word += 1

				row_of_program, symbol_name, class_name = self.get_current_symbol()
				if(class_name == 'add_op' or class_name == 'mult_op' or class_name == 'right_assoc_op'):
					self.checkError = False
					assert False, \
					"Синтаксический анализатор:\nОшибка! Ожидалась переменная или литерал вместо (строка {0}, {1}, {2})".format(row_of_program, symbol_name, class_name)
					sys.exit()
				else:
					self.parse_term()
					self.step_translation += 1
					# self.printTranslation(temp_curent_num)
					temp_curent_num = 0
					self.postfixCode.append(temp[0])
					temp.clear()
			else:
				flag = False


	def parse_term(self):
		# print("Do parse_term")
		# print(self.get_current_symbol())
		self.parse_power()
		flag = True
		temp = []
		temp_curent_num = 0
		# продовжувати розбирати Множники (Factor)
		# розділені лексемами '*' або '/' або '^'
		while flag:
			# print(self.get_current_symbol())
			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if class_name == 'mult_op':


				row_of_program, symbol_name, class_name = self.get_current_symbol()
				temp_curent_num = self.current_number_word
				temp.append(list(self.get_current_symbol()))


				self.current_number_word += 1

				row_of_program, symbol_name, class_name = self.get_current_symbol()
				if(class_name == 'add_op' or class_name == 'mult_op' or class_name == 'right_assoc_op'):
					self.checkError = False
					assert False, \
					"Синтаксический анализатор:\nОшибка! Ожидалась переменная или литерал вместо (строка {0}, {1}, {2})".format(row_of_program, symbol_name, class_name)
					sys.exit()
				else:
					self.parse_factor()
					self.step_translation += 1
					# self.printTranslation(temp_curent_num)
					temp_curent_num = 0
					self.postfixCode.append(temp[0])
					temp.clear()
			else:
				flag = False


	def parse_power(self):
		# print("Do parse_power")
		# print(self.get_current_symbol())
		self.parse_factor()
		flag = True
		temp = []
		temp_curent_num = 0
		# продовжувати розбирати Множники (Factor)
		# розділені лексемами '^'
		while flag:
			# print(self.get_current_symbol())
			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if class_name == 'right_assoc_op':


				row_of_program, symbol_name, class_name = self.get_current_symbol()
				temp_curent_num = self.current_number_word
				temp.append(list(self.get_current_symbol()))


				self.current_number_word += 1

				row_of_program, symbol_name, class_name = self.get_current_symbol()
				if(class_name == 'add_op' or class_name == 'mult_op' or class_name == 'right_assoc_op'):
					self.checkError = False
					assert False, \
					"Синтаксический анализатор:\nОшибка! Ожидалась переменная или литерал вместо (строка {0}, {1}, {2})".format(row_of_program, symbol_name, class_name)
					sys.exit()
				else:
					self.parse_expression()
					self.step_translation += 1
					# self.printTranslation(temp_curent_num)
					temp_curent_num = 0
					self.postfixCode.append(temp[0])
					temp.clear()

			else:
				flag = False


	def parse_factor(self):
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		# print("Do parse_factor")
		# print(self.get_current_symbol())

		if class_name in ('int', 'double', 'real', 'id', 'bool', 'string'):

			row_of_program, symbol_name, class_name = self.get_current_symbol()
			self.step_translation += 1
			# self.printTranslation(self.current_number_word)
			self.postfixCode.append([row_of_program, symbol_name, class_name])

			self.current_number_word += 1

		elif symbol_name == '(':
			self.current_number_word += 1
			self.parse_expression()
			self.check_token(')', 'brackets_op')

		elif symbol_name == ';':
			self.checkError = False
			assert symbol_name != ';', Syntax.different_instruction.format(row_of_program, symbol_name, class_name, ('int', 'double', 'real', 'id', 'bool', 'string'))
			sys.exit()
		
		else:
			self.checkDefinedIdent()


	def parse_write(self):
		# print("Обработка функции write()")
		# print(self.get_current_symbol())
		self.current_number_word += 1

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if symbol_name == '(':
			self.current_number_word += 1
			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if symbol_name == ")":
				self.checkError = False
				assert symbol_name != ")", "Синтаксический анализатор:\nОшибка! Функция write() не может быть без параметров."
				sys.exit()

			while True:
				row_of_program, symbol_name, class_name = self.get_current_symbol()
				self.postfixCode.append([row_of_program, symbol_name, class_name])
				self.postfixCode.append([0, 'OUT', 'out'])
				self.parse_id()
				row_of_program, symbol_name, class_name = self.get_current_symbol()

				if class_name == 'comma':
					self.current_number_word += 1
				
				elif symbol_name == ')':
					self.current_number_word += 1
					self.check_end_of_statment()
					break
				else:
					self.checkError = False
					assert False, \
					'Синтаксический анализатор:\nОшибка! Функция write() написана неправильно.\nОшибка в строке {0}, лексема ({1}, {2})).'.format(row_of_program, symbol_name, class_name)
					sys.exit()


	def parse_read(self):
		# print("Обработка функции read()")
		# print(self.get_current_symbol())
		self.current_number_word += 1

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if symbol_name == '(':
			self.current_number_word += 1
			row_of_program, symbol_name, class_name = self.get_current_symbol()
			if symbol_name == ")":
				self.checkError = False
				assert symbol_name != ")", "Синтаксический анализатор:\nОшибка! Функция read() не может быть без параметров."
				sys.exit()

			while True:
				row_of_program, symbol_name, class_name = self.get_current_symbol()
				self.postfixCode.append([row_of_program, symbol_name, class_name])
				self.postfixCode.append([0, 'INP', 'inp'])
				self.parse_id()
				row_of_program, symbol_name, class_name = self.get_current_symbol()

				if class_name == 'comma':
					self.current_number_word += 1
				
				elif symbol_name == ')':
					self.current_number_word += 1
					self.check_end_of_statment()
					break
				else:
					self.checkError = False
					assert False, \
					"Синтаксический анализатор:\nОшибка! Функция read() написана неправильно.\nОшибка в строке {0}, лексема ({1}, {2})).".format(row_of_program, symbol_name, class_name)
					sys.exit()


	def parse_for_statement(self):
		# print("Do parse_for_statement")
		# print(self.get_current_symbol())

		self.check_token('for', 'keyword')

		self.parse_assing()

		self.check_token('to', 'keyword')
		row_of_program, symbol_name, class_name = self.get_current_symbol()

		m1 = self.createLabel(row_of_program, symbol_name, class_name)
		self.setLabelVal(m1)

		self.parse_bool_expr()

		# if class_name == 'id':
		# 	m1 = self.createLabel(row_of_program, symbol_name, class_name)
		# 	self.setLabelVal(m1)

		# 	self.parse_id()

		# elif class_name == 'int' or class_name == 'double' or class_name == 'real' or class_name == 'bool' or class_name == 'boolval':
		# 	m1 = self.createLabel(row_of_program, symbol_name, class_name)
		# 	self.setLabelVal(m1)

		# 	self.check_type(row_of_program, class_name, 'keyword')


		self.check_token('by', 'keyword')

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		m2 = self.createLabel(row_of_program, symbol_name, class_name)
		self.postfixCode.append(m2)
		self.postfixCode.append([0, 'JF', 'jf'])

		m5 = self.createLabel(row_of_program, symbol_name, class_name)
		self.postfixCode.append(m5)
		self.postfixCode.append([0, 'JUMP', 'jump'])

		m4 = self.createLabel(row_of_program, symbol_name, class_name)
		self.setLabelVal(m4)

		self.parse_assing()

		self.postfixCode.append(m1)
		self.postfixCode.append([0, 'JUMP', 'jump'])

		self.check_token('while', 'keyword')

		self.setLabelVal(m5)
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if class_name == 'bool':
			self.parse_id()
		else:
			self.parse_bool_expr()

		m3 = self.createLabel(row_of_program, symbol_name, class_name)
		self.postfixCode.append(m2)
		self.postfixCode.append([0, 'JF', 'jf'])
		self.postfixCode.append(m3)
		self.postfixCode.append([0, 'JUMP', 'jump'])
		
		self.setLabelVal(m3)

		self.parse_repeat_statement()

		self.postfixCode.append(m4)
		self.postfixCode.append([0, 'JUMP', 'jump'])
		self.setLabelVal(m2)



	def parse_if_statment(self):
		# print("Do parse_if_statment")
		# print(self.get_current_symbol())

		self.check_token('if', 'keyword')

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		self.parse_bool_expr()

		self.check_token('then', 'keyword')

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		m = self.createLabel(row_of_program, symbol_name, class_name)
		self.postfixCode.append(m)
		self.postfixCode.append([0, 'JF', 'jf'])

		row_of_program, symbol_name, class_name = self.get_current_symbol()
		while symbol_name != 'fi':
			self.parse_statment_list()
			row_of_program, symbol_name, class_name = self.get_current_symbol()
		self.check_token('fi', 'keyword')
		self.setLabelVal(m)


	def parse_bool_expr(self):
		# print("Do parse_bool_expr")
		# print(self.get_current_symbol())
		self.parse_expression()
		row_of_program, symbol_name, class_name = self.get_current_symbol()
		if class_name != 'rel_op':
			self.checkError = False
			assert False, \
			'Синтаксический анализатор:\nОшибка! Логическое выражение написано неверно.\nОшибка в строке {0}, лексема ({1}, {2})'.format(row_of_program, symbol_name, class_name)
			sys.exit()
		else:
			temp = self.get_current_symbol()
			self.current_number_word += 1
		self.parse_expression()
		self.postfixCode.append(list(temp))

	def printPostfixCode(self):
		for lexem in self.postfixCode:
			print(lexem)

if __name__ == '__main__':
	lexer = LexAnalizator()
	lexer.read_code('test.inna')
	lexer.lex()
	if(lexer.checkError()):
		lexer.normalizeTable()
		print("Таблица символов: ")
		print(lexer.table_of_symbols)
		print("Таблица констант после лексического анализа: ")
		for i in range(len(lexer.normal_const)):
			print(lexer.normal_const[i])

		print("Таблица переменных после лексического анализа: ")
		for i in range(len(lexer.normal_ident)):
			print(lexer.normal_ident[i])

		syntax_analizator = Syntax(lexer.table_of_symbols, lexer.normal_const, lexer.normal_ident)
		syntax_analizator.parse()
		syntax_analizator.printPostfixCode()

		print("Таблица констант после синтаксического анализа и трансляции: ")
		for i in range(len(syntax_analizator.const)):
			print(syntax_analizator.const[i])

		print("Таблица переменных после синтаксического анализа и трансляции: ")
		for i in range(len(syntax_analizator.ident)):
			print(syntax_analizator.ident[i])
	else:
		print("Ошибка в лексическом анализе или трансляции. Синтаксический анализ невозможен.")

