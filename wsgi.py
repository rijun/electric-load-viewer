import sys

from elv import index

if '-d' in sys.argv:
    index.app.run_server(debug=True, host='0.0.0.0')
else:
    server = index.app.server
