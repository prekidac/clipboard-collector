.PHONY: all install

BIN=~/.local/bin

all:
	@echo "To install type 'make install'"

install:
	sudo apt install xsel
	pip3 install psutil
	cp clipboard_collector.py ${BIN}/clipboard_collector