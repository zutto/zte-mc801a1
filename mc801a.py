import os
import hashlib
import requests
import time

class MC801A:
    def __init__(self, password, device_ip):
        self.password = password
        self.device_ip = device_ip
        self.stok = None  # Initialize stok to None

    def get_ld_value(self):
        timestamp = int(time.time())
        headers = self._get_headers()
        response = requests.get(f"http://{self.device_ip}/goform/goform_get_cmd_process?isTest=false&cmd=LD&_={timestamp}", headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            ld_value = response_json.get("LD")
            return ld_value
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def perform_backdoor(self):
        ld_value = self.get_ld_value()
        go_hash = self._calculate_hash(ld_value, self.password)
        headers = self._get_headers()
        payload = {"isTest": "false", "goformId": "LOGIN", "password": go_hash}
        response = requests.post(f"http://{self.device_ip}/goform/goform_set_cmd_process", headers=headers, data=payload)
        
        if response.status_code == 200:
            # Update stok value
            self.stok = response.cookies.get("stok")
            return response
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def get_rd(self):
        headers = self._get_headers()
        headers["Cookie"] = f"stok={self.stok}"
        timestamp = int(time.time())
        url = f"http://{self.device_ip}/goform/goform_get_cmd_process?isTest=false&cmd=RD&_=1691603993142"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("RD")
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def get_version(self):
        headers = self._get_headers()
        headers["Cookie"] = f"stok={self.stok}"
        timestamp = int(time.time())
        url = f"http://{self.device_ip}/goform/goform_get_cmd_process?isTest=false&cmd=Language%2Ccr_version%2Cwa_inner_version&multi_data=1&_={timestamp}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            wa_inner_version = response_json.get("wa_inner_version")
            return wa_inner_version
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def change_mode(self, BearerPreference, AD):
        headers = self._get_headers()
        headers["Cookie"] = f"stok={self.stok}"
        payload = {
            "isTest": "false",
            "goformId": "SET_BEARER_PREFERENCE",
            "BearerPreference": BearerPreference,
            "AD": AD
        }
        response = requests.post(f"http://{self.device_ip}/goform/goform_set_cmd_process", headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()["result"]
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def _get_headers(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": f"http://{self.device_ip}/",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        return headers

    def _calculate_hash(self, ld_value, password):
        ld_upper = ld_value.upper()
        go_hash = hashlib.sha256(password.encode()).hexdigest().upper()
        go_hash = hashlib.sha256((go_hash + ld_upper).encode()).hexdigest().upper()
        return go_hash

if __name__ == "__main__":
    from zte_crypto import hex_md5
    mc = MC801A(password=os.environ.get("ZTE_PASSWORD"), device_ip="192.168.32.1")
    response = mc.perform_backdoor()
    mc.change_mode(BearerPreference="WL_AND_5G", AD=hex_md5(hex_md5(mc.get_version())+mc.get_rd()))
    #LTE_AND_5G
