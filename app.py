import urllib
import logging
import json
import heapq
from datetime import datetime
from datetime import time as ti
from spyne import Application, srpc, ServiceBase, Integer, String
from spyne import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication

class CrimeReport(ServiceBase):
    @srpc(String, String, String, _returns=Iterable(String))
    def checkcrime(lat, lon, radius):
        res = urllib.urlopen('https://api.spotcrime.com/crimes.json?lat='+lat+'&lon='+lon+'&radius='+radius+'&key=.')
        #res = urlib.urlopen('https://api.spotcrime.com/crimes.json?lat=37.334164&lon=-121.884301&radius=0.02&key=.')
        crimedata = json.loads(res.read())
        address_dict = {}
        dict = {
                "total_crime" : 0,
                "the_most_dangerous_streets" : 0,
                "crime_type_count" : {
                "Assault" : 0,
                "Arrest" : 0,
                "Burglary" : 0,
                "Robbery" : 0,
                "Theft" : 0,
                "Other" : 0
                },
                "event_time_count" : {
                "12:01am-3am" : 0,
                "3:01am-6am" : 0,
                "6:01am-9am" : 0,
                "9:01am-12noon" : 0,
                "12:01pm-3pm" : 0,
                "3:01pm-6pm" : 0,
                "6:01pm-9pm" : 0,
                "9:01pm-12midnight" : 0
                } 
            }
        dict["total_crime"] = len(crimedata['crimes']) 

        for each in crimedata['crimes']:
            if each.get('type') == "Assault":
                dict["crime_type_count"]["Assault"]+=1
            elif each.get('type') == "Arrest":
                dict["crime_type_count"]["Arrest"]+=1
            elif each.get('type') == "Burglary":
                dict["crime_type_count"]["Burglary"]+=1
            elif each.get('type') == "Robbery":
                dict["crime_type_count"]["Robbery"]+=1
            elif each.get('type') == "Theft":
                dict["crime_type_count"]["Theft"]+=1
            elif each.get('type') == "Other":
                dict["crime_type_count"]["Other"]+=1


            timedate = each.get('date')[9:]
            t1 = datetime.strptime(timedate,"%I:%M %p")
            crimet = t1.time()
            if crimet >= ti(00,01,00) and crimet <= ti(03,00,00):
                dict["event_time_count"]["12:01am-3am"]+=1
            elif crimet >= ti(03,01,00) and crimet <= ti(06,00,00):
                dict["event_time_count"]["3:01am-6am"]+=1
            elif crimet >= ti(06,01,00) and crimet <= ti(9,00,00):
                dict["event_time_count"]["6:01am-9am"]+=1
            elif crimet >= ti(9,01,00) and crimet <= ti(12,00,00):
                dict["event_time_count"]["9:01am-12noon"]+=1
            elif crimet >= ti(12,01,00) and crimet <= ti(15,00,00): 
                dict["event_time_count"]["12:01pm-3pm"]+=1 
            elif crimet >= ti(15,01,00) and crimet <= ti(18,00,00): 
                dict["event_time_count"]["3:01pm-6pm"]+=1  
            elif crimet >= ti(18,01,00) and crimet <= ti(21,00,00):
                dict["event_time_count"]["6:01pm-9pm"]+=1
            elif crimet >= ti(21,01,00) and crimet < ti(00,00,00) or crimet == ti(00,00,00):
                dict["event_time_count"]["9:01pm-12midnight"]+=1

    
      
            address = each.get('address')
            ad = ''
            if 'OF' in address:
                ad = address.split('OF')
                for obj in ad:
                    obj=obj.strip()
                    if 'ST' in obj:
                        if address_dict.has_key(obj):
                            address_dict[obj]+=1
                        else:
                            address_dict.update({obj:1})
                    if 'RD' in obj:
                        if address_dict.has_key(obj):
                            address_dict[obj]+=1
                        else:
                            address_dict.update({obj:1})
                    if 'AV' in obj:
                        if address_dict.has_key(obj):
                            address_dict[obj]+=1
                        else:
                            address_dict.update({obj:1})  

            if '&' in address:
                ad = address.split('&')
                for obj in ad:
                    obj=obj.strip()
                    if 'ST' in obj:
                        if address_dict.has_key(obj):
                            address_dict[obj]+= 1
                        else:
                            address_dict.update({obj:1})
                    elif 'AV' in obj:
                        if address_dict.has_key(obj):
                            address_dict[obj]+= 1
                        else:
                            address_dict.update({obj:1})
        dict["the_most_dangerous_streets"] = heapq.nlargest(3,address_dict, key=address_dict.get)
        yield dict
        

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    logging.basicConfig(level=logging.DEBUG)
    application = Application([CrimeReport], 'checkcrime.',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument(ignore_wrappers=True)
)

    # Now that we have our application, we must wrap it inside a transport.
    # In this case, we use Spyne's standard Wsgi wrapper. Spyne supports
    # popular Http wrappers like Twisted, Django, Pyramid, etc. as well as
    # a ZeroMQ (REQ/REP) wrapper.
    wsgi_application = WsgiApplication(application)

    # More daemon boilerplate
    server = make_server('127.0.0.1', 8000, wsgi_application)

    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")

    server.serve_forever()
            
