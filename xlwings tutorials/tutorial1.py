from xlwings import Workbook, Sheet, Range, Chart

def main():
	wb = Workbook()  # Creates a connection with a new workbook
	Range('A1').value = 'Foo 1'
	print Range('A1').value
	# 'Foo 1'
	Range('A1').value = [['Foo 1', 'Foo 2', 'Foo 3'], [10.0, 20.0, 30.0]]
	print Range('A1').table.value  # or: Range('A1:C2').value
	# [['Foo 1', 'Foo 2', 'Foo 3'], [10.0, 20.0, 30.0]]
	print Sheet(1).name
	# 'Sheet1'
	chart = Chart.add(source_data=Range('A1').table)	


if __name__ == '__main__':
	main()

