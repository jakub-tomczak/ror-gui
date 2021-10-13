import datetime


def get_log_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("%H-%M-%S %d-%m-%Y")
