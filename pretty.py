from datetime import datetime

def show_msg(username: str, message: str, newlinefirst=False):
    time = datetime.now()
    str = f"[{time.hour}:{time.minute}] {username}@: {message}"
    if newlinefirst:
        str = "\n" + str
    else:
        str = str + "\n"
    print(str, end="")

def prompt(username: str):
    print(f"{username}$: ", end="")