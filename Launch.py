from lex_analizator_var11 import LexAnalizator
from translator_var11 import Syntax
from interpreter_var11 import Interpreter

if __name__ == '__main__':
	# print("-"*100)
	# print("Начало лексического анализа")
	# print("-"*100)

	lexer = LexAnalizator()
	lexer.read_code('test.inna')
	lexer.lex()
	# print("-"*100)
	# print("Лексический анализ прошел успешно!")
	# print("-"*100)
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

		# print("-"*100)
		# print("Начало синтаксического анализа и трансляции")
		# print("-"*100)
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

			# print("-"*100)
			# print("Начало интерпретации")
			# print("-"*100)
			interpret = Interpreter(syntax.postfixCode, syntax.ident, syntax.const, syntax.labels)
			# print(interpret.idents, interpret.consts)
			interpret.postfixProcessing()

		else:
			print("\nОшибка при синтаксическом анализе или трансляции. Интерпретация невозможна.")
	else:
		print("\nОшибка в лексическом анализе. Синтаксический анализ невозможен.")