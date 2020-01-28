
log_switch = False


def set_log_switch(value):
    global log_switch
    log_switch = value


def log(name, value):
    """
        Only switched on for development
    """
    if log_switch:
        print("LOG {}={}".format(name, str(value)))


def exit_on_rc_error(message, value):
    exit_on_error("{}: {}".format(message, value))


def exit_on_login_error(message, file_name):
    exit_on_error(("{}: {}\n"
                   "Make shure you have created this file in your home directory and it has read access.\n "
                   "Please go to https://app.velohero.com/sso and get yourself a private single sign-on key. "
                   "That's the long string.\n"
                   "Then create a file '{}' containing\n\n"
                   "----- snip -------------------------------------------------------------\n"
                   "VELOHERO_SSO_KEY=[insert your own]\n"
                   "----- snap -------------------------------------------------------------\n"
                   ).format(message, file_name, file_name))


def exit_on_error(message):
    print(message)
    exit(1)



