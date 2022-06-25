import threading
import os
import sys
import time
import random
import string
from colorama import Fore, init; init(autoreset=True)

# Thread lock, while running tasks
thread_lock = threading.Lock()

class Console:
    @staticmethod
    def _time():
        return time.strftime("%H:%M:%S", time.gmtime())

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def sprint(content: str, status: bool) -> None:
        thread_lock.acquire()
        sys.stdout.write(f'[{Fore.LIGHTBLUE_EX}{Console()._time()}{Fore.RESET}] {Fore.GREEN if status else Fore.RED}{content}' + '\n')
        thread_lock.release()

class Utils:
    @staticmethod
    def get_proxies():
        try:
            proxies = open('proxies.txt','r').read().splitlines()
            return proxies
        except:
            return False

    @staticmethod
    def get_usernames(custom_username: bool):
        if custom_username:
            try:
                usernames = open('usernames.txt','r').read().splitlines()
                return random.choice(usernames)
            except:
                return False
        else:
            return ''.join(random.choice(string.ascii_letters + string.digits)for _ in range(10))

    @staticmethod
    def get_password():
        return ''.join(random.choice(string.ascii_letters + string.digits)for _ in range(10))