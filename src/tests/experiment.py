from pprint import pprint as pp
from jupyter_client.manager import start_new_kernel
from IPython.utils.capture import capture_output


TIMEOUT = 30

km, kc = start_new_kernel()
code = """
import pandas as pd
df = pd.read_csv('target/example.csv')
df
"""

with capture_output() as io:
    reply = kc.execute_interactive(code, timeout=TIMEOUT)

assert reply['content']['status'] == 'ok'

io.show()

# Result:
# - can only communicate with ipykernel using strings.
#   - input code as string is not too much of a problem.
#   - but output dataframe as only string is ... inconvenient.

#km.shutdown_kernel()
#kc.stop_channels()

