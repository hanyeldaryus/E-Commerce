import http.client
import json
conn = http.client.HTTPSConnection("api.rajaongkir.com")



headers = {
    'key': "49caf46c70492b45611c78584849acea",
    'content-type': "application/x-www-form-urlencoded"
    }

def cekOngkir(origin, destination,  courier, weight=1000):
    payload = f"origin={origin}&destination={destination}&weight={weight}&courier={courier}"
    try:
        conn.request("POST", "/starter/cost", payload, headers)
        res = conn.getresponse()
    except:
        conn.request("POST", "/starter/cost", payload, headers)
        res = conn.getresponse()
        
    #res = conn.getresponse()
    return json.load(res)

if __name__ == "__main__":
    print(cekOngkir(origin=501, destination=114, courier="jne")['rajaongkir']['results'][0]['costs'][0]['cost'][0]['value'])
