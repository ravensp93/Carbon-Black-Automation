from cb_th_api import cb_th_api
import yaml
import time 
import sys
import os

class cb_live_session:

    def __init__(self, ip_addr, cb_api_token):
        self.cb_api = cb_th_api(ip_addr,cb_api_token)
        self.session_id = 0
        self.username = ""
        self.hostname = None
        self.command_ids = []
        self.command_results = []
        self.host_sid = None
        self.APP_ROOT_DIR=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
         
    def get_SID(self):
        ##try deleting file
        self.cb_api.send_command(self.session_id, "delete file", r"C:\Windows\Temp\myscript_results.txt")
        self.cb_api.send_command(self.session_id, "delete file", r"C:\Windows\Temp\myscript.cmd")  
        ## begin
        upload_res = self.cb_api.upload_file_to_server(self.session_id, r"myscript.cmd")
        if upload_res:
            #extract file id from upload, put the file onto server
            putfile_res = self.cb_api.send_command(self.session_id,"put file",r"C:\Windows\Temp\myscript.cmd",upload_res["id"])
            command_wait_res = self.wait_for_command_complete(self.session_id, putfile_res["id"])
            if command_wait_res:
                #create file process
                run_process_res = self.cb_api.send_command(self.session_id,"create process",command_object=r"C:\Windows\Temp\myscript.cmd",output_file_path=r"C:\Windows\Temp\myscript_results.txt")
                command_wait_res = self.wait_for_command_complete(self.session_id, run_process_res["id"])
                if command_wait_res:
                    if command_wait_res == "timeout":
                        print("Create Process Command Timeout")
                        return False
                    #create process success
                    getfile_res = self.cb_api.send_command(self.session_id, "get file","C:\\Windows\\Temp\\myscript_results.txt")
                    command_wait_res = self.wait_for_command_complete(self.session_id, getfile_res["id"])
                    if command_wait_res:
                        if command_wait_res == "timeout":
                            print("Get File Command Timeout")
                            return False
                        #get_file success
                        download_res = self.cb_api.download_file_from_server(self.session_id, getfile_res["file_id"])
                        found = False
                        for i in str(download_res).replace("\\r","").split("\\n"):
                            if "S-" in i:
                                self.host_sid = i.split(r"\\")[-1]
                            if self.username in i:
                                found = True
                                break
                        if not found:
                            print("Cannot find username's SID")
                            return False
                        print(f"Retrieved {self.username}'s SID: {self.host_sid}")
                        #deleting files
                        self.cb_api.send_command(self.session_id, "delete file", r"C:\Windows\Temp\myscript_results.txt")
                        self.cb_api.send_command(self.session_id, "delete file", r"C:\Windows\Temp\myscript.cmd")
                        return True
                    else:
                        print("Get File Failed to execute")
                        return False
                else:
                    print("Create Process Failed to execute")
                    return False
            else:
                print("Put File failed")
                return False
        else:
            print("File Upload failed")
            return False
        
    def quick_reg_key_retrieval_by_list(self, hostname, username):
        self.username = username
        self.hostname = hostname
        self.start_session()
        if self.get_SID():
            self.retrieve_reg_keys()
        self.close_session()
        
    #returns false if session cant be started    
    def start_session(self):
        print(self.APP_ROOT_DIR)
        sensor_res = self.cb_api.check_sensor_details(self.hostname)
        if sensor_res:
            sensor_id = sensor_res[0]["id"]
            #if session can't be start we will treat as offline. Offline host will be requeued later
            if sensor_res[0]["status"] != "Online":
                print(f"{self.hostname} is offline")
                sys.exit()
            ##host is confirmed online here
            print(f"{self.hostname} is online!")
            session_res = self.cb_api.create_session(sensor_id)
            if session_res:
                self.session_id = session_res["id"]
                #session created, wait for session startup and handle errors(timeouts,session startup failure)
                session_startup_res = self.wait_for_session_startup(self.session_id, self.hostname)
                if session_startup_res:
                    if session_startup_res == "Timeout":
                        #timeout while waiting for session to start, retry later
                        print(f"Timeout session for {self.hostname} closed")
                        self.cb_api.close_session(self.session_id)                        
                        sys.exit()
                else:
                    #Error in starting up session
                    print(f"Error in starting session for {self.hostname}")
                    sys.exit()
                self.cb_api.keep_alive_session(self.session_id)
                #session has started successfully, begin doing stuff here
                print("successfully started session!")
            else:
                #session cant be started or an existing session already exist, skip.
                print(f"Error in starting a session for {self.hostname} or existing session already running")
                sys.exit()          
        else:
            ##host confirmed to be not in CBR records.
            print(f"sensor not found for hostname: {self.hostname}")
            sys.exit()
            
    def retrieve_reg_keys(self):
        try:
            with open(r'reg_scan_list.yml') as file:
                documents = yaml.full_load(file)
        except:
            print("reg_scan_list.yml does not exist in yml folder.")
            
        for reg_key in documents["reg_keys"]:
            final_key = reg_key           
            try:
                if "HKEY_CURRENT_USER" in reg_key or "HKCU" in reg_key:
                    reg_dict = reg_key.split("\\")
                    final_key = f"HKEY_USERS\\{self.host_sid }" 
                    for i in reg_dict[1:]:
                        final_key =  final_key + f"\\{i}"
                print(f"sending command to retrieve registry key: {final_key}")
                res = self.cb_api.send_command(self.session_id,"reg enum key", final_key)
                #print(type(res))
                self.command_ids.append(int(res["id"])) 
            except:
                print(f"Retrying command to retrieve registry key: {reg_key}")
            time.sleep(1.5)

        print(f"\nCommand IDs to wait for completion {self.command_ids} for session {self.session_id}\n")
        for command_id in self.command_ids:
            command_wait_res = self.wait_for_command_complete(self.session_id, command_id)
            if command_wait_res:
                if command_wait_res == "timeout":
                    self.command_results.append("Timeout in retrieval")
                    continue
                command_res = self.cb_api.check_commands_details(self.session_id, command_id)
                if 'values' in command_res:
                    self.command_results.append(command_res['values'])
                else:
                    self.command_results.append("clean")
            else:
                self.command_results.append("Error in retrieval, command failed or registry key does not exists")
        
        filepathname = f"reg_key_retrieval_results-{self.hostname}.txt"
        
        f= open(filepathname,"w+")
        i = 0
        for reg_key in documents["reg_keys"]:
            f.write(f"{i+1}) Registry Key:\n{reg_key}\n\nKey_Value:\n{self.command_results[i]}\n\n")
            i = i+1
        f.close() 
        
        print("\nRegistry Key Retrieval Results saved to reg_key_retrieval_results.txt in results folder")
        
    def close_session(self):
        print("Closing session soon...")
        time.sleep(1)
        self.cb_api.close_session(self.session_id)
        print(f"Live Response Session {self.session_id} for {self.hostname} is closed. Exiting..")
        
    def wait_for_session_startup(self,session_id, hostname):
        print(f"Awaiting {hostname} session {session_id} to start up...")
        seconds = 0
        while seconds != 200:
            res = self.cb_api.check_session_details(session_id)
            if res:
                if res["status"] == "active":
                    return True
                time.sleep(1)
                seconds = seconds + 1
            else:
                return False
        return "Timeout"
       
    def wait_for_command_complete(self,session_id, cmd_id):
        seconds = 0
        while seconds != 30: 
                res = self.cb_api.check_commands_details(session_id, cmd_id)
                if res:
                    if res["status"] == "complete":
                        return True
                    if res["status"] == "error":
                        return False
                    time.sleep(1)
                    seconds = seconds + 1
                else:
                    return False
        return "Timeout"
        
if __name__ == "__main__":
    cb_session = cb_live_session("<Carbon Black IP:PORT>","Carbon Black Access Key")
    # cb_session.session_id = 33619
    # cb_session.command_ids.append(2)
    # print(cb_session.cb_api.send_command(cb_session.session_id,"reg enum key",r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce"))
    # cb_session.wait_for_session_startup()
    # cb_session.retrieve_reg_keys()
    # cb_session.wait_for_command(cb_session.command_ids)
    #cb_session.get_SID()


    
    
            