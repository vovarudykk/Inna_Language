from lex_analizator_var11 import LexAnalizator
from translator_var11 import Syntax
from stack import Stack


class Interpreter():

	def __init__(self, postfixCode, ident, const, labels):
		self.stack = Stack()
		self.postfixCode = self.correctPostfixCode(postfixCode)
		self.labels = labels
		self.normal_ident = ident
		self.normal_const = const
		self.idents = self.correctTable(self.normal_ident)
		self.consts = self.correctTable(self.normal_const)
		self.commandTrack = []
		self.instrNum = 1


	def correctPostfixCode(self, postfixCode):
		lst = []
		for i in range(len(postfixCode)):
			lst.append((postfixCode[i][1], postfixCode[i][2]))
		return lst

	def correctTable(self, table):
		dic = {}

		for i in range(1, len(table)+1):
			dic[table[i-1][0]] = (i, table[i-1][1], table[i-1][2])

		return dic 

	def configToPrint(self, step, lex, tok, maxN):

		print('\nШаг интерпретации №{0}'.format(step))
		if tok in ('int', 'double', 'bool', 'real', 'string'):
			print('Лексема: {0} в таблице констант: {1}'.format((lex, tok), lex + ':' + str(self.consts[lex])))
		elif tok == 'id':
			print('Лексема: {0} в таблице переменных: {1}'.format((lex, tok), lex + ':' + str(self.idents[lex])))
		elif tok == 'label':
			print('Лексема: {0} в таблице меток: {1}'.format((lex, tok), lex + ':' + str(self.labels[lex])))
		else:
			print('Лексема: {0}'.format((lex, tok)))

		print('postfixCode={0}'.format(self.postfixCode)) 
		self.stack.print()

		return True

	def identsToPrint(self):
		print("\nТаблица переменных после интерпретации: ")
		s1 = '{0:<20s} {1:<20s} {2:<20s} {3:<20s} '
		print(s1.format("Ident", "Type", "Value", "Index"))
		s2 = '{0:<20s} {2:<20s} {3:<20s} {1:<20d} '
		for id in self.idents: 
			index, type, val = self.idents[id]
			print(s2.format(id, index, type, str(val)))


	def constsToPrint(self):
		print("\nТаблица констант после интерпретации: ")
		s1 = '{0:<20s} {1:<20s} {2:<20s} {3:<20s} '
		print(s1.format("Const", "Type", "Value", "Index"))
		s2 = '{0:<20s} {2:<20s} {3:<20} {1:<20d} '
		for cnst in self.consts: 
			index, type, val = self.consts[cnst]
			print(s2.format(str(cnst), index, type, val))

	def tableToPrint(self, Tbl):
		if Tbl == "Id":
			self.identsToPrint()
		elif Tbl == "Const":
			self.constsToPrint()
		else:
			self.identsToPrint()
			self.constsToPrint()
		return True

	def postfixProcessing(self):
		cyclesNumb = 0
		maxNumb = len(self.postfixCode) + 1

		while self.instrNum < maxNumb and cyclesNumb < 5000:
			cyclesNumb += 1
			lex, tok = self.postfixCode[self.instrNum - 1]
			self.commandTrack.append((self.instrNum, lex, tok))
			if tok in ('id', 'int', 'double', 'bool', 'real', 'label', 'string'):
				self.stack.push((lex, tok))
				nextInstr = self.instrNum + 1
			elif tok in ('jf', 'jump'):
				nextInstr = self.doJumps(tok)
			else:
				self.doIt(lex, tok)
				nextInstr = self.instrNum + 1
			# self.configToPrint(self.instrNum, lex, tok, maxNumb)
			self.instrNum = nextInstr

		print('\nПостфіксний код:')
		s = ''
		for code in self.postfixCode: 
			s += code[0] + ' '
		print(s)
		# s = ''
		# for code in self.commandTrack: 
		# 	s += code[1] + ' '
		# print('\nПослідовність команд:')
		# print(s)
		# print('\nЗагальна кiлькiсть крокiв: {0}'.format(cyclesNumb))

		self.tableToPrint('All')

		return self.commandTrack


	def doIt(self, lex, tok):
		if (lex, tok) == ('=', 'assign_op'):
			# зняти з вершини стека запис (правий операнд = число)
			(lexR, tokR) = self.stack.pop()
			# зняти з вершини стека ідентифікатор (лівий операнд)
			(lexL, tokL) = self.stack.pop()

			if self.idents[lexL][1] == 'type_undef':
				self.failRunTime('неоголошена змінна', (lexL, self.idents[lexL], (lexL, tokL), lex, (lexR, tokR)))
			if tokR == 'id':
				if self.idents[lexR][1] == 'type_undef':
					self.failRunTime('неоголошена змінна', (lexR, self.idents[lexR], (lexL, tokL), lex, (lexR, tokR)))
				elif self.idents[lexR][2] == 'val_undef':
					self.failRunTime('неініціалізована змінна', (lexR, self.idents[lexR], (lexL, tokL), lex, (lexR, tokR)))
				else:
					valR, tokR = (self.idents[lexR][2], self.idents[lexR][1])
			else:
				valR, tokR = (self.consts[lexR][2], self.consts[lexR][1])

			# виконати операцію:
			# оновлюємо запис у таблиці ідентифікаторів
			# ідентифікатор/змінна  
			# (index не змінюється, 
			# тип - як у ідентифікатора,  
			# значення - як у константи, приводитися до типу ідентифікатора, якщо не співпадає з ним)
			if tokR == self.idents[lexL][1]:
				self.idents[lexL] = (self.idents[lexL][0], self.idents[lexL][1], valR)
			else:
				value = self.cast(valR, tokR, self.idents[lexL][1])
				if value == 'wrong type':
					self.failRunTime('недопустиме приведення типів', ((lexL, tokL), lex, (lexR, tokR)))
				self.idents[lexL] = (self.idents[lexL][0], self.idents[lexL][1], value)
				self.toConsts(value, self.idents[lexL][1])
		elif lex == 'NEG':
			# зняти з вершини стека запис (операнд)
			lex, tok = self.stack.pop()
			self.processing_neg(lex, tok)
		elif tok in ('add_op', 'mult_op', 'right_assoc_op', 'rel_op'):
			# зняти з вершини стека запис (правий операнд)
			(lexR, tokR) = self.stack.pop()
			# зняти з вершини стека запис (лівий операнд)
			(lexL, tokL) = self.stack.pop()

			self.processing_binary_op((lexL, tokL), lex, (lexR, tokR))

		elif tok == 'inp':
			self.processing_inp()
		elif tok == 'out':
			self.processing_out()
		return True

	def processing_neg(self, lex, tok):
		if tok == 'id':
			if self.idents[lex][1] == 'type_undef':
				self.failRunTime('неініціалізована змінна', (lex, self.idents[lex], (lex, tok), lex, (lex, tok)))
			else:
				(val, tok) = (self.idents[lex][2], self.idents[lex][1])
		else:
			val = self.consts[lex][2]

		self.stack.push(('-' + str(val), tok))
		if tok == 'int':
			self.toConsts(-int(val), tok)
		elif tok == 'double':
			self.toConsts(-float(val), tok)
		elif tok == 'real':
			self.toConsts('-' + str(val), tok)

	def processing_binary_op(self, ltL, lex, ltR):
		lexL,tokL = ltL
		lexR,tokR = ltR
		if tokL == 'id':
			if self.idents[lexL][1] == 'type_undef':
				self.failRunTime('неоголошена змінна', (lexL, self.idents[lexL], (lexL, tokL), lex, (lexR, tokR)))
			elif self.idents[lexL][2] == 'val_undef':
				self.failRunTime('неініціалізована змінна', (lexL, self.idents[lexL], (lexL, tokL), lex, (lexR, tokR)))
			else:
				valL, tokL = (self.idents[lexL][2], self.idents[lexL][1])
		else:
			valL = self.consts[lexL][2]
		if tokR == 'id':
			if self.idents[lexR][1] == 'type_undef':
				self.failRunTime('неоголошена змінна', (lexR, self.idents[lexR], (lexL, tokL), lex, (lexR, tokR)))
			elif self.idents[lexR][2] == 'val_undef':
				self.failRunTime('неініціалізована змінна', (lexR, self.idents[lexR], (lexL, tokL), lex, (lexR, tokR)))
			else:
				valR,tokR = (self.idents[lexR][2], self.idents[lexR][1])
		else:
			valR = self.consts[lexR][2]
		self.getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))


	def getValue(self, vtL, lex, vtR):
		valL, lexL, tokL = vtL
		valR, lexR, tokR = vtR
		value = None

		if tokL == 'string' or tokR == 'string':
			self.failRunTime('строка', ((lexL, tokL), lex, (lexR, tokR)))

		elif tokL == 'double' or tokR == 'double':
			if lex == '+':
				value = float(valL) + float(valR)
			elif lex == '-':
				value = float(valL) - float(valR)
			elif lex == '*':
				value = float(valL) * float(valR)
			elif (lex == '/' and valR == '0') or (lex == '/' and valR == 0):
				self.failRunTime('деление на ноль', ((lexL, tokL), lex, (lexR, tokR)))
			elif lex == '/':
				value = float(valL) / float(valR)
			elif lex == '^':
				value = float(valL) ** float(valR)
			elif lex in ('==', '<=', '<', '>', '>=', '!='):
				value = self.boolOperand(valL, valR, lex)
			else:
				pass
			if value in ('true', 'false'):
				self.stack.push((value, 'bool'))
				self.toConsts(value, 'bool')
			else:
				self.stack.push((str(value), 'double'))
				self.toConsts(value, 'double')
		
		elif tokL == 'int' and tokR == 'int':
			if lex == '+':
				value = int(valL) + int(valR)
			elif lex == '-':
				value = int(valL) - int(valR)
			elif lex == '*':
				value = int(int(valL) * int(valR))
			elif (lex == '/' and valR == '0') or (lex == '/' and valR == 0):
				self.failRunTime('деление на ноль', ((lexL, tokL), lex, (lexR, tokR)))
			elif lex == '/':
				value = int(int(valL) / int(valR))
			elif lex == '^':
				value = int(int(valL) ** int(valR))
			elif lex in ('==', '<=', '<', '>', '>=', '!='):
				value = self.boolOperand(valL, valR, lex)
			else:
				pass
			if value in ('true', 'false'):
				self.stack.push((value, 'bool'))
				self.toConsts(value, 'bool')
			else:
				self.stack.push((str(value), 'int'))
				self.toConsts(value, 'int')

		elif tokL == 'real' or tokR == 'real':
			if lex == '+':
				value = float(valL) + float(valR)
			elif lex == '-':
				value = float(valL) - float(valR)
			elif lex == '*':
				value = float(int(valL) * float(valR))
			elif (lex == '/' and valR == '0') or (lex == '/' and valR == 0):
				self.failRunTime('деление на ноль', ((lexL, tokL), lex, (lexR, tokR)))
			elif lex == '/':
				value = float(int(valL) / float(valR))
			elif lex == '^':
				value = float(int(valL) ** float(valR))
			elif lex in ('==', '<=', '<', '>', '>=', '!='):
				value = self.boolOperand(valL, valR, lex)
			else:
				pass
			if value in ('true', 'false'):
				self.stack.push((value, 'bool'))
				self.toConsts(value, 'bool')
			else:
				self.stack.push((str(format(value, '.4e')), 'real'))
				self.toConsts(format(value, '.4e'), 'real')
		elif tokL == 'bool' and tokR == 'bool':
			value = self.boolOperand(valL, valR, lex)
			self.stack.push((value, 'bool'))
			self.toConsts(value, 'bool')



	def boolOperand(self, valL, valR, lex):
		if(str(valL) in ('true', 'false') and str(valR) in ('true', 'false')):
			if lex == '==':
				value = str(valL == valR).lower()
			elif lex == '!=':
				value = str(valL != valR).lower()
			else:
				assert False, "Интерпретатор: Ошибка!\nОшибка в выражении {0} {1} {2}".format(valL, lex, valR)
			return value
		else:
			if lex == '==':
				value = str(float(valL) == float(valR)).lower()
			elif lex == '<=':
				value = str(float(valL) <= float(valR)).lower()
			elif lex == '<':
				value = str(float(valL) < float(valR)).lower()
			elif lex == '>':
				value = str(float(valL) > float(valR)).lower()
			elif lex == '>=':
				value = str(float(valL) >= float(valR)).lower()
			elif lex == '!=':
				value = str(float(valL) != float(valR)).lower()
			return value

	def toConsts(self, val, tok):
		lexeme = str(val)
		index1 = self.consts.get(lexeme)   
		if index1 is None:
			index = len(self.consts) + 1 
			self.consts[lexeme] = (index, tok, val)


	def cast(self, value, origType, newType):
		if newType == 'int':
			if origType in ('bool'):
				return 'wrong type'
			return int(value)
		elif newType == 'double':
			if origType in ('bool'):
				return 'wrong type'
			return float(value)
		elif newType == 'real':
			if origType in ('bool'):
				return 'wrong type'
			return float(value)
		elif newType == 'bool':
			if value in ('0', '0.0', '""', 'false'):
				return 'false'
			else:
				return 'true'
		elif newType == 'string':
			return '"' + str(value) + '"'


	def doJumps(self, tok):
		if tok == 'jump':
			next = self.processing_jump()
		elif tok == 'jf':
			next = self.processing_jf()
		return next


	def processing_jump(self):
		lex, tok = self.stack.pop()
		return self.labels[lex]


	def processing_jf(self):
		lexL, tokL = self.stack.pop()
		lexB, tokB = self.stack.pop()
		if lexB == 'false':
			return self.labels[lexL]
		else:
			return self.instrNum + 1


	def processing_inp(self):
		lex, tok = self.stack.pop()

		if self.idents[lex][1] == 'type_undef':
			self.failRunTime('неоголошена змінна', (lex, self.idents[lex], (lex, tok), '', ('INP', 'inp')))

		while True:
			try:
				inp = list(map(str, input().split()))[0]

				identType = self.idents[lex][1]

				if identType == 'int':
					value = int(inp)
				elif identType == 'double':
					value = float(inp)
				elif identType == 'real':
					value = float(inp)
				elif identType == 'bool':
					value = cast(inp, 'string', 'bool')
				elif identType == 'string':
					value = '"' + inp + '"'
			except:
				print("Интерпретатор:\nОшибка! Введенное значение не соответствует типу переменной. Повторите ввод.")
				continue
			else:
				break

		self.idents[lex] = (self.idents[lex][0], self.idents[lex][1], value)
		self.toConsts(value, self.idents[lex][1])

	def processing_out(self):
		lex, tok = self.stack.pop()

		if tok == 'id':
			if self.idents[lex][1] == 'type_undef':
				self.failRunTime('неоголошена змінна', (lex, self.idents[lex], (lex, tok), '', ('OUT', 'out')))
			elif self.idents[lex][2] == 'val_undef':
				self.failRunTime('неініціалізована змінна', (lex, self.idents[lex], (lex, tok), '', ('OUT', 'out')))
			else:
				(val, tok) = (self.idents[lex][2], self.idents[lex][1])
		else:
			val = self.consts[lex][2]

		if tok == 'string':
			val = val[1:len(val) - 1]

		print(val)

	def failRunTime(self, str, tuple):
		if str == 'невідповідність типів':
			((lexL, tokL), lex, (lexR, tokR)) = tuple
			print('Интерпретатор:\nОшибка! Несоответсвие типов. Типы операндов отличаются ({0}) {1} ({2})'.format((lexL, tokL), lex, (lexR, tokR)))
			exit(1)
		elif str == 'неініціалізована змінна':
			(lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
			print('Интерпретатор:\nОшибка! Значение переменной {0}:{1} не определено. Встретилось в {2} {3} {4}'.format(lx, rec, (lexL, tokL), lex, (lexR, tokR)))
			exit(2)
		elif str == 'деление на ноль':
			((lexL, tokL), lex, (lexR, tokR)) = tuple
			print('Интерпретатор:\nОшибка! Деление на ноль в ({0}) {1} ({2}). '.format((lexL, tokL), lex, (lexR, tokR)))
			exit(3)
		elif str == 'невідповідність типу':
			((lexL, tokL), lex) = tuple
			print('Интерпретатор:\nОшибка! Несоответсвие типа. Тип операнда не подходит для {0} {1}'.format((lexL, tokL), lex))
			exit(4)
		elif str == 'недопустиме приведення типів':
			((lexL, tokL), lex, (lexR, tokR)) = tuple
			print('Интерпретатор:\nОшибка! Недопустимое приведение типов. Тип данных отличается в {0} {1} {2}'.format((lexL, tokL), lex, (lexR, tokR)))
			exit(5)
		elif str == 'строка':
			((lexL, tokL), lex, (lexR, tokR)) = tuple
			print('Интерпретатор:\nОшибка! Над строками нельзя проводить арифметические операции {0} {1} {2}.'.format((lexL, tokL), lex, (lexR, tokR)))
			exit(4)
		elif str == 'неоголошена змінна':
			(lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
			print('Интерпретатор:\nОшибка! Переменная {0}:{1} не была обьявлена. Встретилось в {2} {3} {4}'.format(lx, rec, (lexL, tokL), lex, (lexR, tokR)))
			exit(2)


if __name__ == '__main__':
	print("-"*100)
	print("Начало лексического анализа")
	print("-"*100)

	lexer = LexAnalizator()
	lexer.read_code('test.inna')
	lexer.lex()
	print("-"*100)
	print("Лексический анализ прошел успешно!")
	print("-"*100)
	if(lexer.checkError()):
		lexer.normalizeTable()
		# print("Таблица символов: ")
		# print(lexer.table_of_symbols)
		# print("Таблица констант после лексического разбора: ")
		# for i in range(len(lexer.normal_const)):
		# 	print(lexer.normal_const[i])

		# print("Таблица переменных после лексического разбора: ")
		# for i in range(len(lexer.normal_ident)):
		# 	print(lexer.normal_ident[i])

		print("-"*100)
		print("Начало синтаксического анализа и трансляции")
		print("-"*100)
		syntax = Syntax(lexer.table_of_symbols, lexer.normal_const, lexer.normal_ident)
		syntax.parse()

		if syntax.checkError:
			# print("PostfixCode: ")
			# syntax.printPostfixCode()
			# print("Таблица констант после синтаксического разбора и трансляции: ")
			# for i in range(len(syntax.const)):
			# 	print(syntax.const[i])

			# print("Таблица переменных после синтаксического разбора и трансляции: ")
			# for i in range(len(syntax.ident)):
			# 	print(syntax.ident[i])

			print("-"*100)
			print("Начало интерпретации")
			print("-"*100)
			interpret = Interpreter(syntax.postfixCode, syntax.ident, syntax.const, syntax.labels)
			# print(interpret.idents, interpret.consts)
			interpret.postfixProcessing()

		else:
			print("\nОшибка при синтаксическом анализе или трансляции. Интерпретация невозможна.")
	else:
		print("\nОшибка в лексическом анализе. Синтаксический анализ невозможен.")
