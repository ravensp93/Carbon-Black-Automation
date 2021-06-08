#!/usr/bin/python3.8
import requests,json
requests.packages.urllib3.disable_warnings()

class cb_th_api:

    def __init__(self, ip_addr, cb_api_token):
        self.cb_ip_addr = ip_addr
        self.headers = { 'X-Auth-Token': cb_api_token }
    
    #res = requests.get(url, headers=self.headers , auth=auth , files=files)
    def query_binary(self, binary_md5=None):
        
        url = "https://" + self.cb_ip_addr +"/api/v1/binary/" + binary_md5 +"/summary"
        # print(url)
        res = requests.get(url, headers=self.headers, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False
            
    #/api/v1/sensor/(id)?hostname=(hostname)&ip=(ipaddr)&groupid=(groupid)&inactive_filter_days=(int)
            
    def check_sensor_details(self, hostname):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/sensor"
        
        #use param ?active_only=true
        params = {'hostname':hostname}
    
        # print(url)
        res = requests.get(url, headers=self.headers, params=params, verify=False)
    
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False

    #Live Response Methods
    
    def create_session(self, sensor_id):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session"
        
        request_body = {'sensor_id': sensor_id}
    
        # print(url)
        res = requests.post(url, headers=self.headers, json=request_body, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False
            
    def close_session(self,session_id):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id) 
        
        request_body = {'status' : "close"}
    
        # print(url)
        res = requests.put(url, headers=self.headers, json=request_body, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False
            
    def view_current_sessions(self, active_only=False):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session"
        
        #use param ?active_only=true
        params = {'active_only':active_only}
    
        # print(url)
        res = requests.get(url, headers=self.headers, params=params, verify=False)
    
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False
    
    def keep_alive_session(self, session_id):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id) + "/keepalive"
    
        # print(url)
        res = requests.get(url, headers=self.headers, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False        
    
    def check_session_details(self, session_id):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id)
    
        # print(url)
        res = requests.get(url, headers=self.headers, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False
            
            
    def check_commands_details(self, session_id, command_id):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id) + "/command/" + str(command_id)
    
        # print(url)
        res = requests.get(url, headers=self.headers, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False   
        
    #Send Commands
    
    def send_command(self, session_id, command_type, command_object=None, file_id=None, output_file_path=None):

        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id) + "/command" 
    
        if command_type == "reg enum key" or command_type == "reg query value" or command_type == "reg delete value" or command_type == "delete file" or command_type == "get file":
            request_body = {"name": command_type, "object": command_object}
        elif command_type == "put file":
            request_body = {"name": command_type, "object": command_object, "file_id": file_id}
        elif command_type == "create process" and output_file_path == None:
            request_body = {"name": command_type, "object": command_object, "wait": True}
        elif command_type == "create process" and output_file_path != None:
            request_body = {"name": command_type, "object": command_object, "wait": True, "output_file" : output_file_path}
        # print(url)
        res = requests.post(url, headers=self.headers, data=json.dumps(request_body), verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False
        
#################Live Response Files Section #############
    
    def upload_file_to_server(self, session_id, file_path):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id) + "/file"
    
        files = {'file': open(str(file_path),'rb')}
    
        # print(url)
        res = requests.post(url, headers=self.headers, files=files, verify=False)
    
        if res.status_code == 200:
            return res.json()
        else:
            print(res.text)
            return False

    def download_file_from_server(self, session_id, file_id):
        #retrieve a list of currently active or recently closed sessions
        url = "https://" + self.cb_ip_addr + "/api/v1/cblr/session/" + str(session_id) + "/file/" + str(file_id) + "/content"
    
        # print(url)
        res = requests.get(url, headers=self.headers, verify=False)
    
        if res.status_code == 200:
            return res.content
        else:
            print(res.text)
            return False
        

if __name__ == "__main__":
    #session_id = "15141"
    cb_api = cb_th_api("<Carbon Black IP:PORT>","Carbon Black Access Key")
    #print(cb_api.view_current_sessions())
    # print(cb_api.check_session_details(6635)["status"] == "active")
    #cb_api.create_session(20516))
    
    # query_binary("6D778E0F95447E6546553EEEA709D03C")
    # view_current_sessions(True)
    # check_session_details(6610)
    # print(cb_api.check_commands_details(6663, 2)["status"])
    #print(cb_api.send_command("33596","put file",r"C:\Windows\Temp\myscript.cmd",1))
    # print(cb_api.close_session(6678))
    #print(cb_api.upload_file_to_server(33597, r"C:\Users\t.chin\Desktop\myscript.cmd"))
    #print(cb_api.send_command("33597","put file",r"C:\Windows\Temp\myscript.cmd",1))
    #print(cb_api.send_command("33597","create process",command_object=r"C:\Windows\Temp\myscript.cmd",output_file_path=r"C:\Windows\Temp\myscript_results.txt"))
    #print(cb_api.send_command(33597, "get file","C:\\Windows\\Temp\\myscript_results.txt"))
    #print(cb_api.download_file_from_server(33597, 2))