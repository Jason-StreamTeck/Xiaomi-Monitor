import httpx

class API:
    def __init__(self, url):
        self.url = url

    def post_data(self, timestamp, temp, humid, bat):
        try:
            with httpx.Client() as client:
                client.post(url=self.url, json={
                    "timestamp": timestamp,
                    "temperature": temp,
                    "humidity": humid,
                    "battery": bat
                })
        except Exception as e:
            print(f"Error occurred: {e}")