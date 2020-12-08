#! /usr/bin/env python3
import pyperclip
import logging
import time

FORMAT = "%(levelname)s -- %(message)s -- line: %(lineno)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


class Collector(object):

    def __init__(self) -> None:
        self.contains = []
        self.end_word = "exit"

    def is_end(self) -> bool:
        if self.current == self.end_word:
            return True
        return False

    def end_collecting(self) -> None:
        pyperclip.copy("\n".join(self.contains[1:]))
        logging.debug(" ".join(self.contains[1:]))

    def check(self) -> str:
        """
        Check for changes
        Returns: OK or END
        """
        self.current = pyperclip.paste()
        if len(self.contains) == 0:
            self.contains.append(self.current)
            logging.debug(self.contains[-1])
            logging.info("New clipboard")

        if self.contains[-1] != self.current:
            if self.is_end():
                self.end_collecting()
                return "END"
            logging.debug(self.current)
            self.contains.append(self.current)
        return "OK"


if __name__ == "__main__":
    c = Collector()
    while c.check() == "OK":
        time.sleep(1)
