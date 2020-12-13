# Electric Load Viewer

Clone the repository and install the required python packages, for example via pip with 
`pip install -r requirements.txt`. Afterwards, the program can be started by running the following commands (assuming
the repo was cloned into the home directory and navigated into). The current uWSGI settings assume a Raspberry Pi with
Raspberry Pi OS is used as the server.

```shell script
# Python
python wsgi.py -d

# uWSGI
sudo uwsgi uwsgi.ini

# Docker
sudo docker run  --rm --name elv -v "$(pwd)"/itp.db:/app/itp.db:z -p 80:80 -d elv
```

_Hint: When using a Raspberry Pi, the package `libatlas-base-dev` has to be installed additionally for NumPy to work._