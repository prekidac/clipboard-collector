#! /usr/bin/env python3
import subprocess
import logging
import time
import os
import psutil
import sys

ENCODING = "utf-8"


FORMAT = "%(filename)s - %(levelname)s -- %(message)s -- line: %(lineno)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

logging.disable(logging.WARNING)


class Collector(object):

    def __init__(self) -> None:
        self.contains = []
        self.status = "OK"
        self.actions = {
            "collect": self.collect,
            "exit": self.exit_
        }

    def copy(self, text) -> None:
        p = subprocess.Popen(["xsel", "-b", "-i"],
                             stdin=subprocess.PIPE, close_fds=True)
        while True:
            try:
                p.communicate(input=text.encode(ENCODING), timeout=1)
                break
            except Exception as exc:
                p.kill()
                logging.error(exc)

    def paste(self) -> str:
        p = subprocess.Popen(["xsel", "-b", "-o"],
                             stdout=subprocess.PIPE, close_fds=True)
        try:
            stdout, stderr = p.communicate(timeout=1)
        except Exception as exc:
            p.kill()
            logging.error(exc)
            return ""
        return stdout.decode(ENCODING)

    def backup(self) -> None:
        with open("/tmp/clipboard", "a") as f:
            f.write(self.current + "\n")

    def exit_(self) -> None:
        self.collect()
        self.status = "EXIT"

    def collect(self) -> None:
        logging.debug(f"Collected: {' '.join(self.contains[1:])}")
        # prevent multiple copy of "collect" to erase collected
        if len(self.contains) == 1:
            self.copy(self.contains[0])
        else:
            self.copy("\n".join(self.contains[1:]))
        self.contains = []
        self.status = "COLLECTED"

    def check(self) -> None:
        self.current = self.paste()
        if len(self.contains) == 0:
            self.contains.append(self.current)
            logging.debug(f"On clipboard: {self.contains[0]}")
        elif self.current and self.contains[-1] != self.current:
            if self.current in self.actions:
                self.actions[self.current]()
            else:
                logging.debug(self.current)
                self.contains.append(self.current)
                self.backup()
    
    def loop(self) -> None:
        while self.status != "EXIT":
            self.check()
            time.sleep(0.1)



if __name__ == "__main__":
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
    c = Collector()
    c.loop()