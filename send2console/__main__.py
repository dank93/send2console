import sys
from .send2console import get_kernel_and_run_in_console
from .send2console import command_server

if sys.argv[1] == '-s':
    command_server(sys.argv[2])
elif sys.argv[1] == '-f':
    with open(sys.argv[2], mode='r') as f:
        cmd = f.read()
    get_kernel_and_run_in_console(cmd)
else:
    cmd = sys.argv[1]
    get_kernel_and_run_in_console(cmd)
