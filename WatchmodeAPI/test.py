# For test main.py has been temporarily from  
from main import WatchmodeAPI



def api():
    return WatchmodeAPI()

print(api().get_actor_id("Ryan Reynolds"))
