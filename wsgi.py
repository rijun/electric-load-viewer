import sys

from elv import index

if '-d' in sys.argv:
    index.app.run_server(debug=True, host='0.0.0.0')
if '-h' in sys.argv:
    print("Usage: python wsgi.py [options]")
    print("Provides the server instance of the electric load viewer dash app.")
    print("Alternatively the Flask development server can be used.\n")
    print("Options:")
    print("  -d start the integrated Flask development server")
    print("  -h display this help and exit")
else:
    server = index.app.server
