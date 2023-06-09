import sys

class TestStdouts:
	def test_myoutput(self, capsys):  # or use "capfd" for fd-level
		print("hello")
		sys.stderr.write("world\n")
		captured = capsys.readouterr()
		assert captured.out == "hello\n"
		assert captured.err == "world\n"
		print("next")
		captured = capsys.readouterr()
		assert captured.out == "next\n"