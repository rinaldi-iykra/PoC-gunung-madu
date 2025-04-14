from app import app
import requests

class ApiBMKGHelper:
    base_url = ''
    
    def __init__(self):
        self.base_url = app.config["BASE_BMKG_API"]

    def info(self, datas=dict()):
        return datas

    def weather(self, datas=list()):
        temperatures = list()
        for data in datas:
            for i in data:
                temperatures.append(i['t'])

        avg_temperatures = (sum(temperatures) / len(temperatures))
        return {
            "avg": avg_temperatures
        }


    def get_weather(self, code=''):
        url = '/'.join((
            self.base_url, 
            'prakiraan-cuaca?adm4={}'.format(code)
        ))
        payload = {}
        headers = {}

        response = requests.request(
            "GET", 
            url, 
            headers=headers, 
            data=payload
        )

        if response.status_code == 200:
            result_json = response.json()
            self.weather(result_json['data'][0]['cuaca'])
            self.info(result_json['lokasi'])

        else:
            print("Error")


