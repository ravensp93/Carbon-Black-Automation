# Carbon-Black-Automation
Automated Registry Key Value Retrieval for both HKCU/HKLM keys

cb_th_api.py - contains singular API Call functions

cb_live_session.py - automation logic leveraging on API Call functions defined in cb_th_api.py

cb_live_resp.py - front-end class for calling the business logics

Edit reg_scan_list.yml to define the reg key you wish to retrieve from target endpoint

To use,

In cb_live_resp.py,
- edit the EDR IP:PORT and Accesskey variable
- edit the hostname and username parameter

Upon execution, script will generate a file containing the values of the reg keys
