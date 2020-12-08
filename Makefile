.PHONY: all install

PREFIX=/usr/local
DIR=${PREFIX}/share/clipboard-collector

all:
	@echo "To install type 'sudo make install'"

install:
	sudo apt install xclip xsel
	pip3 install pyperclip
	sudo mkdir -p ${DIR}
	cp clipboard_collector.py ${DIR}
	ln -sf ${DIR}/clipboard_collector.py ${PREFIX}/bin/clipboard_collector
	chmod +x ${PREFIX}/bin/clipboard_collector
