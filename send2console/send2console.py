import atexit
import jupyter_client
import os
import time
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters.terminal256 import Terminal256Formatter

def _print_tty(tty, thing=''):
    # Print to tty
    with open('/dev/tty'+str(tty), mode='w') as out:
        out.write('\n')
        out.write(str(thing))

def _notify(tty, msg):
    # Format notification and print to tty
    _LENGTH = 30
    if msg != '':
        num_pad = int((30 - len(msg) - 2) / 2)
        note = '-' * num_pad + ' ' + msg + ' ' + '-' * num_pad
    else:
        note = '-' * _LENGTH
    _print_tty(tty, '\33[93m' + note + '\n\33[0m')

def _print_code(tty, code):
    # Syntax highlight code and print to tty
    _print_tty(tty, '\033[2J\033[H') # Clear screen and move cursor to top
    _notify(tty, 'Code')
    _print_tty(tty, highlight(code, PythonLexer(), Terminal256Formatter()))

def _get_kernel():
    # Get Jupyter console kernel info. If there is no console,
    # we'll fail here
    cf = jupyter_client.find_connection_file()
    km = jupyter_client.BlockingKernelClient(connection_file=cf)
    km.load_connection_file()
    return km

def _get_tty():
    # Grep processes to find jupyter console tty, so we can print to it
    tty = os.popen("ps ax | grep  'jupyter-console' | grep -v 'grep' | head -1 | awk '{ print $2 }'").read()
    tty = tty.split('\n')[0] # Get rid of trailing newline
    return tty

def run_in_console(km, tty, cmd):
    # Print command in console and send it to kernel to pe run.
    # Then wait for responses and print in console
    _print_code(tty, cmd)
    mid = km.execute(cmd)
    _notify(tty, 'Output')
    while True:

        # Grab response from kernel
        msg = km.get_iopub_msg()

        # Ignore if irrelevant
        if msg['parent_header']['msg_id'] != mid:
            continue

        # Handles
        msg_type = msg['header']['msg_type']
        content = msg['content']

        # If idle state is reached, process if over
        if msg_type == 'status':
            if content['execution_state'] == 'idle':
                _print_tty(tty)
                break

        # Parse and print response
        if msg_type == 'error':
            for tb in content['traceback']: _print_tty(tty, tb)
        elif msg_type == 'stream':
            _print_tty(tty, content['text'][0:-1])
        elif msg_type == 'execute_result':
            _print_tty(tty, content['text']['data'])
        elif msg_type == 'execute_input':
            pass
        elif msg_type == 'status':
            pass
        else:
            _print_tty(tty, msg)
    _notify(tty, '')

def get_kernel_and_run_in_console(cmd):
    km = _get_kernel()
    tty = _get_tty()
    run_in_console(km, tty, cmd)

def command_server(pipe_name):
    # Delete and recreate fifo to make sure we have a clean workspace
    try:
        os.remove(pipe_name)
    except FileNotFoundError:
        pass
    os.mkfifo(pipe_name)

    # Clean up on exit
    atexit.register(lambda: os.remove(pipe_name))

    # Grab kernel and tty
    km = _get_kernel()
    tty = _get_tty()

    # Loop forever
    fifo = open(pipe_name)
    while True:
        cmd = fifo.read()
        if cmd:
            run_in_console(km, tty, cmd)
        time.sleep(0.2)
