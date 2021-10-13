import datetime


def get_log_time() -> str:
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")
