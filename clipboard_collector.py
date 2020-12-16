#! /usr/bin/env python3
import argparse
import subprocess
import logging
import time
import os
import psutil
import sys

ENCODING = "utf-8"


FORMAT = "%(filename)s - %(levelname)s -- %(message)s -- line: %(lineno)s"
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
            logging.disable(logging.WARNING)

    def copy(self, text):
        p = subprocess.Popen(["xsel", "-b", "-i"],
                             stdin=subprocess.PIPE, close_fds=True)
        try:
            p.communicate(input=text.encode(ENCODING), timeout=1)
        except Exception as exc:
            p.kill()
            logging.error(exc)
            raise

    def paste(self):
        p = subprocess.Popen(["xsel", "-b", "-o"],
                             stdout=subprocess.PIPE, close_fds=True)
        try:
            stdout, stderr = p.communicate(timeout=1)
        except Exception as exc:
            p.kill()
            logging.error(exc)
            raise
        return stdout.decode(ENCODING)

    def backup(self) -> None:
        with open("/tmp/clipboard", "a") as f:
            f.write(self.current + "\n")

    def exit_(self) -> str:
        self.collect()
        return "EXIT"

    def collect(self) -> str:
        logging.info("Collected")
        logging.debug(" ".join(self.contains[1:]))
        # prevent multiple copy of "collect" to erase collected
        while True:
            try:
                if len(self.contains) == 1:
                    self.copy(self.contains[0])
                    break
                else:
                    self.copy("\n".join(self.contains[1:]))
                    break
            except Exception as exc:
                logging.error(exc)
        self.contains = []
        return "COLLECTED"

    def check(self) -> str:
        """
        Check for changes
        Returns: status
        """
        try:
            self.current = self.paste()
        except:
            pass
        if len(self.contains) == 0:
            logging.info("On clipboard")
            self.contains.append(self.current)
            logging.debug(self.contains[-1].replace("\n", " "))
            logging.info("Collector ready")
        if self.contains[-1] != self.current:
            if self.current in self.actions.keys():
                return self.actions[self.current]()
            logging.debug(self.current)
            self.contains.append(self.current)
            self.backup()
        return "OK"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clipboard collecting deamon")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="display log messages")
    args = parser.parse_args()
    old_pid = None
    try:
        file = "/tmp/.clip_daemon_pid"
        with open(file, "r") as f:
            old_pid = f.read().strip()
    except:
        pass
    if old_pid and psutil.pid_exists(int(old_pid)):
        exit("Already running!")
    else:
        with open(file, "w") as f:
            f.write(str(os.getpid()))
    c = Collector(verbose=args.verbose)
    while c.check() != "EXIT":
        time.sleep(0.1)
