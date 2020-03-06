# send2console

Python package that sends python code from stdin or file to active
Jupyter kernel, where it is displayed and run in the kernel's global
scope. Can additionally set up a server that polls a fifo buffer for
input that is sent to Jupyter.

Ex:

`$ python3 -m send2console "print(123)"`
`$ python3 -m send2console -f thing.py`

