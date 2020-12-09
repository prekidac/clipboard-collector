#! /usr/bin/env python3
import argparse
import pyperclip
import logging
import time

FORMAT = "%(levelname)s -- %(message)s -- line: %(lineno)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


class Collector(object):

    def __init__(self, verbose: bool = False) -> None:
        self.contains = []
        self.verbose = verbose
        self.actions = {
            "collect": self.collect,
            "exit": self.exit_
        }
        if not self.verbose:
            logging.disable(logging.CRITICAL)

    def exit_(self) -> bool:
        self.collect()
        return "END"

    def collect(self) -> None:
        pyperclip.copy("\n".join(self.contains[1:]))
        logging.debug(" ".join(self.contains[1:]))
        logging.info("Collected")
        self.contains = []
        return "OK"

    def check(self) -> str:
        """
        Check for changes
        Returns: OK or END
        """
        self.current = pyperclip.paste()
        if len(self.contains) == 0:
            logging.info("Old")
            self.contains.append(self.current)
            logging.debug(self.contains[-1].replace("\n", " "))
            logging.info("Collector ready")
        if self.contains[-1] != self.current:
            if self.current in self.actions.keys():
                return self.actions[self.current]()
            logging.debug(self.current)
            self.contains.append(self.current)
        return "OK"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clipboard collecting deamon")
    parser.add_argument("-v", "--verbose", action="store_true", help="display log messages")
    args = parser.parse_args()
    c = Collector(verbose=args.verbose)
    while c.check() == "OK":
        time.sleep(1)
