# Electric Load Viewer

## Setup

Clone the repository and install the required python packages, for example via pip with 
`pip3 install -r requirements.txt`. Afterwards, the program can be started by running the following commands (assuming
the repo was cloned into the home directory and navigated into):

```shell script
python3 wsgi.py -d

# Docker alternative
sudo docker run --name elv -v "$(pwd)"/itp.db:/app/itp.db:z -p 80:8015 -d elv
```

_Hint: When using a Raspberry Pi, the package `libatlas-base-dev` has to be installed additionally for NumPy to work._