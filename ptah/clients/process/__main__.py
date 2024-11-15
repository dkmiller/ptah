import signal
import sys

from . import Process, _sigterm_handler

# https://stackoverflow.com/a/45070583
pc = Process()
decoded = pc.decode(sys.argv[-1])
signal.signal(signal.SIGTERM, _sigterm_handler)
pc.run(decoded)
