#!/usr/bin/python3
import requests
import platform
import subprocess
import base64
import requests.utils
import urllib3
import argparse
import textwrap
import sys
from requests import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)