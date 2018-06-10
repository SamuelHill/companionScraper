import difflib

with open("diff_test_1.txt") as file1, open("diff_test_2.txt") as file2:
	d = difflib.Differ()
	diff = d.compare(file1.read().splitlines(), file2.read().splitlines())
	print('\n'.join(diff))