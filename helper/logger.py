def log(data, txt, color=None, *args, **kwargs):
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'

    color = GREEN if color == "GREEN" else RED if color == "RED" else RESET

    dt = data.datetime.date(0)
    # Format the main message with *args
    formatted_txt = txt % args

    # Log the message with additional keyword arguments if any
    extra_info = ', '.join(f'{k}={v}' for k, v in kwargs.items())

    if extra_info:
        print(f'{color}{dt}, {formatted_txt}, {extra_info}{RESET}')
    else:
        print(f'{color}{dt}, {formatted_txt}{RESET}')
