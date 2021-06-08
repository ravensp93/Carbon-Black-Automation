from cb_live_session import cb_live_session
import time

CB_IP_ADDR = "<CBR_IP_PORT>"
CB_API_TOKEN = "<CBR_ACCESS_KEY>"

start_time = time.time()

cb_session = cb_live_session(CB_IP_ADDR, CB_API_TOKEN)
cb_session.quick_reg_key_retrieval_by_list("<Hostname>", "<username e.g Administrator ")
print("\n--- Time taken for execution %s seconds ---" % (time.time() - start_time))
