import copy
from string import ascii_letters

class LexAnalizator(object):

	def __init__(self):
		self.normal_const = []
		self.normal_ident = []
		self.error = 0
		self.table_of_language_tokens = {'int': 'keyword'     , 'double': 'keyword', 'bool': 'keyword',
										 'read': 'keyword'    , 'write': 'keyword' , 'for': 'keyword' ,
										 'rof': 'keyword'     , 'to': 'keyword'    , 'by': 'keyword',
										 'while': 'keyword'   , 'if': 'keyword'    , 'then': 'keyword',
										 'fi': 'keyword'      , 'begin': 'keyword' , 'end': 'keyword',
										 'program': 'keyword' , '=': 'assign_op'   , '+': 'add_op',
										 '-': 'add_op'        , '*': 'mult_op'     , '/': 'mult_op',
										 '^': 'right_assoc_op', '<': 'rel_op'      , '<=': 'rel_op',
										 '==': 'rel_op'       , '!=': 'rel_op'     , '>=': 'rel_op',
										 '>': 'rel_op'        , '(': 'brackets_op' , ')': 'brackets_op',
										 '.': 'dot'           , ',': 'comma'       , ':': 'punct', 
										 ';': 'punct'         , '\32': 'ws'        , '\n': 'nl',
										 '\0': 'eof'          , 'true': 'bool'  , 'false': 'bool', '"': 'quote',
										 'var': 'keyword'     , 'real': 'keyword', 'string': 'keyword', ' \t': 'ws',
										 '#': 'comment_sting'}

		self.table_ident_double_int = {2: 'id', 7: 'double', 8: 'int', 18: 'real', 40: 'string'}

		self.stf = {(0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,
					(0, 'e'): 1, (1, 'e'): 1,

					(0, 'quote'): 35, (35, 'other'): 106,
									  (35, 'Letter'): 36, (36, 'Letter'): 36, (36, 'Digit'): 36, (36, 'ws'): 36, (36, 'quote'): 38, (38, 'other'): 40, 
									  (35, 'e'):36, (36, 'e'):36,
									  										  (36, 'other'): 107,

					(0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'other'): 8,
													  (3, 'dot'): 4, (4, 'Digit'): 5, (5, 'Digit'): 5, (5, 'other'): 7,
																	 (4, 'other'): 105, #hz
													  (3, 'e'): 9, (9, '+'): 14, (9, '-'): 14, (14, 'Digit'): 15, (15, 'Digit'): 15, (15, 'other'): 18,
																   (9, 'other'): 102, 
																							   (14, 'other'): 101,
					
					(0, '+'): 31, (0, '-'): 31, (0, '*'): 31, (0, '/'): 31, (0, '('): 31, (0, ')'): 31, (0, '^'): 31, (0, ';'): 31, (0, ':'): 31,

					(0, '#'): 41, (41, 'other'): 42, (42, 'other'): 42, (42, 'nl'): 43, (43, 'other'): 44,   

					(0, 'other'): 103,

					(0, 'comma'):31,

					(0, 'ws'): 0,

					(0, 'nl'): 32,

					(0, '<'): 20, (20, '='): 22, (22, 'other'): 23,
								  (20, 'other'): 21,

					(0, '>'): 10, (10, '='): 11, (11, 'other'): 13,
								  (10, 'other'): 12,

					(0, '='): 19, (19, '='): 25, (25, 'other'): 26,
								  (19, 'other'): 24,

					(0, '!'): 27, (27, '='): 28, (28, 'other'): 29,
								  (27, 'other'): 104,	

		}

		self.f = {2, 6, 7, 8, 12, 13, 18, 21, 23, 24, 26, 29, 31, 32, 101, 102, 103, 104, 105, 106, 107, 34, 40, 44}

		self.f_star = {2, 7, 8, 32, 18, 21, 12, 24, 26, 29, 13, 23, 34, 40}  # зірочка

		self.f_error = {101, 102, 103, 104, 106, 107, 105}  # обробка помилок

		self.table_of_vars = {}  # Таблиця ідентифікаторів

		self.table_of_const = {}  # Таблиць констант

		self.table_of_symbols = {}  # Таблиця символів програми (таблиця розбору)

		self.state = 0  # поточний стан

		self.source_code = ""

		self.len_code = 0

		self.num_char = -1  # number of first symbol will take with next_char function

		self.num_line = 1

		self.char = ''

		self.lexeme = ''

	def read_code(self, file_name):
		with open(file_name) as file:
			self.source_code = file.read()
		self.len_code = len(self.source_code) - 1

	def lex(self):
		while self.num_char < self.len_code:
			self.char = self.next_char()
			class_char_ = self.class_of_char(self.char)
			self.state = self.next_state(self.state, class_char_)

			if self.is_final(self.state):
				self.processing()
				if self.state in self.f_error:
					break
			elif self.state == 0:
					self.lexeme = ''
			else:
				self.lexeme += self.char

	def processing(self):
		if self.state == 32:
			self.num_line += 1
			self.state = 0
		elif self.state in self.f_star:
			token_ = self.get_token(self.state, self.lexeme)
			if token_ != 'keyword':
				index = self.index_var_const(self.state, self.lexeme)
				# self.output_not_keyword(self.num_line, self.lexeme, token_, index)
				self.table_of_symbols[len(self.table_of_symbols) + 1] = (self.num_line, self.lexeme, token_, index)
			else:
				# self.output_keyword(self.num_line, self.lexeme, token_)
				self.table_of_symbols[len(self.table_of_symbols) + 1] = (self.num_line, self.lexeme, token_, '')

			self.lexeme = ''
			self.num_char = self.put_char_back(self.num_char)  # зірочка
			self.state = 0
		elif self.state in (31, 22, 11, 25, 28):
			self.lexeme += self.char
			token_ = self.get_token(self.state, self.lexeme)
			# self.output_keyword(self.num_line, self.lexeme, token_)

			self.table_of_symbols[len(self.table_of_symbols) + 1] = (self.num_line, self.lexeme, token_, '')
			self.lexeme = ''
			self.state = 0
		elif self.state == 44:
			self.lexeme = ''
			self.state = 0

		elif self.state in (101, 102, 103, 104, 105, 106, 107):  # ERROR

			self.fail()

	@staticmethod
	def output_not_keyword(num_line, lexeme, token, index):
		print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(num_line, lexeme, token, index))

	@staticmethod
	def output_keyword(num_line, lexeme, token):
		print('{0:<3d} {1:<10s} {2:<10s}'.format(num_line, lexeme, token))

	def fail(self):
		if self.state == 101 or self.state == 105:
			self.error += 1
			print('Лексический анализатор:\nОшибка! В строке №', self.num_line, ' ожидался Digit, а не ' + self.char)

		if self.state == 102:
			self.error += 1
			print('Лексический анализатор:\nОшибка! В строке №', self.num_line, ' ожидался + или -, а не ' + self.char)
		
		if self.state == 103:
			self.error += 1
			print('Лексический анализатор:\nОшибка! В строке №', self.num_line, ' неожиданный символ ' + self.char)

		if self.state == 104:
			self.error += 1
			print('Лексический анализатор:\nОшибка! В строке №', self.num_line, ' ожидался символ =, а не ' + self.char)

		if self.state == 106:
			self.error += 1
			print('Лексический анализатор:\nОшибка! В строке №', self.num_line, ' ожидался Letter, а не "' + self.char + "\"")

		if self.state == 107:
			self.error += 1
			print('Лексический анализатор:\nОшибка! В строке №', self.num_line, ' ожидался символ \", а не "' + self.char + "\"")

	def is_final(self, state):
		if (state in self.f):
			return True
		else:
			return False

	def next_state(self, state, class_of_char):
		try:
			return self.stf[(state, class_of_char)]
		except KeyError:
			return self.stf[(state, 'other')]

	def next_char(self):
		self.num_char += 1
		return self.source_code[self.num_char]

	@staticmethod
	def put_char_back(num_char):
		return num_char - 1

	@staticmethod
	def class_of_char(char):
		if char in '.':
			res = "dot"
		elif char in ascii_letters and char != 'e':
			res = "Letter"
		elif char in "0123456789":
			res = "Digit"
		elif char in ',':
			res = "comma"
		elif char in " \t":
			res = "ws"
		elif char in "\n":
			res = "nl"
		elif char in "\"":
			res = "quote"
		elif char in '+-*/<>!=()^;:e#':
			res = char
		else:
			raise Exception("Ошибка! Несуществующая лексема '" + str(char) + "'")
		return res

	def get_token(self, state, lexeme):
		try:
			return self.table_of_language_tokens[lexeme]
		except KeyError:
			return self.table_ident_double_int[state]

	def index_var_const(self, state, lexeme):
		indx = 0

		if state == 2:
			indx = self.table_of_vars.get(lexeme)

			if indx is None:
				indx = len(self.table_of_vars) + 1

				self.table_of_vars[lexeme] = indx
		
		elif state == 7:

			indx = self.table_of_const.get(lexeme)

			if indx is None:
				indx = len(self.table_of_const) + 1

				self.table_of_const[lexeme] = indx

		elif state == 8:

			indx = self.table_of_const.get(lexeme)

			if indx is None:
				indx = len(self.table_of_const) + 1

				self.table_of_const[lexeme] = indx

		elif state == 18:

			indx = self.table_of_const.get(lexeme)

			if indx is None:
				indx = len(self.table_of_const) + 1

				self.table_of_const[lexeme] = indx

		elif state == 40:

			indx = self.table_of_const.get(lexeme)

			if indx is None:
				indx = len(self.table_of_const) + 1

				self.table_of_const[lexeme] = indx

		return indx

	def checkError(self):
		if(self.error == 0):
			self.correctTrueFalse()
			return True
		else:
			return False

	def getTableOfVars(self):
		return self.table_of_vars

	def get_key(self, d, value):
		for k, v in d.items():
			if v == value:
				return k

	def correctTrueFalse(self):
		temp_const = copy.deepcopy(self.table_of_const)
		temp_vars = copy.deepcopy(self.table_of_vars)

		for i in range(1, len(temp_vars)+1):
			if self.get_key(temp_vars, i) == 'true' or self.get_key(temp_vars, i) == 'false':
				boool = self.get_key(temp_vars, i)
				del temp_vars[boool]
				tmp = {boool:len(temp_const)+1}
				temp_const = dict(list(temp_const.items()) + list(tmp.items()))

		lst = list(temp_vars.keys())
		lst1 = [i for i in range(1, len(lst)+1)]

		self.table_of_const = copy.deepcopy(temp_const)
		self.table_of_vars = dict(zip(lst, lst1))

	def normalizeTable(self):
		temp_const = copy.deepcopy(self.table_of_const)
		temp_vars = copy.deepcopy(self.table_of_vars)

		self.normal_const = []
		self.normal_ident = []

		for i in range(1, len(temp_const)+1):
			self.normal_const.append([self.get_key(temp_const, i), "type_undef", self.get_key(temp_const, i)])

		l = [self.normal_const[i][0] for i in range(len(self.normal_const))]

		tbfs = list(self.table_of_symbols.values())

		for i in range(len(tbfs)):
			if tbfs[i][1] in l:
				for j in range(len(self.normal_const)):
					if tbfs[i][1] == self.normal_const[j][0]:
						self.normal_const[j][1] = tbfs[i][2]



		for i in range(1, len(temp_vars)+1):
			if i == 1:
				self.normal_ident.append([self.get_key(temp_vars, i), "prog_name", "val_undef"])
			else:
				self.normal_ident.append([self.get_key(temp_vars, i), "type_undef", "val_undef"])





if __name__ == '__main__':
	print("Лексический анализатор языка Inna")
	lexer = LexAnalizator()
	lexer.read_code('test.inna')
	print("Код программы: ")
	print(lexer.source_code)
	lexer.lex()
	lexer.checkError()
	print("Таблица символов: ")
	print(lexer.table_of_symbols)
	lexer.normalizeTable()

	print("Таблица констант: ")
	for i in range(len(lexer.normal_const)):
		print(lexer.normal_const[i])

	print("Таблица переменных: ")
	for i in range(len(lexer.normal_ident)):
		print(lexer.normal_ident[i])