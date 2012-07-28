import urllib2
import json
from pymongo import *
import mail

def parse(element):
    key = element["propertyCode"]
    return {
            "price" : element["price"],
            "rooms" : element["rooms"],
            "bathroom" : element["bathrooms"],
            "distance" : element["distance"],
            "address" : element["address"],
            "key" : key,
            "tipo" : element["propertyType"],
            "lat" : element["latitude"],
            "lon" : element["longitude"],
            "url" : element["url"]
    }

def print_pis(pis):
    return "\n\nPis a " + pis["address"] + "\n\n"+ "\n".join(map( lambda e: " %s: %s" %( e , pis[e]), pis))

def print_pisos(pisos):
    return "\n".join(map( lambda pis: print_pis(pis), pisos))

KEY="5b85c03c16bbb85d96e232b112ee85dc"
BASE_URL="http://www.idealista.com/labs/api/2/search"
BENET_I_MATEU="41.39521788743978,2.12557554244995"
DISTANCIA="1000" # En metres..
MAX_PRICE=850
MIN_BEDROOMS=3
MIN_SIZE=60
URL="%s?k=%s&t=1&operation=%s&center=%s&distance=%s&maxPrice=%s&maxItems=500&bedrooms=%s&minSize=%s"% \
        (BASE_URL,KEY, "A", BENET_I_MATEU, DISTANCIA, MAX_PRICE, MIN_BEDROOMS,
                MIN_SIZE)

print URL

f = urllib2.urlopen(URL)
data = f.read()
data = json.loads(data)

conn = Connection()
db = conn["idealista"]


pisos_on_db = list(db.pisos.find({}))
pisos_on_response = map( lambda element: parse(element), data["elementList"])

pisos_nous = filter(
        lambda r: not r["key"] in map(
            lambda d: d["key"],    pisos_on_db)
        , pisos_on_response)

pisos_esborrats = filter(
        lambda d: not d["key"] in map(
            lambda r: r["key"],    pisos_on_response)
        , pisos_on_db)

pisos_join = [ (d,r) for d in pisos_on_db for r in pisos_on_response if
        d["key"] == r["key"]]

pisos_diff_preu = filter( lambda(d,r) : d["price"] != r["price"] , pisos_join)

print "nous: ",  len(pisos_nous)
print "esborrats: ",  len(pisos_esborrats)
print "cambiat_preu:" , len(pisos_diff_preu)

subject = "Idealista feed"
message = """
    Pisos rebaixats: 

%s 


    Pisos nous: 

%s

    Pisos esborrats: 

%s



""" % ( "\n".join(map(lambda (d,r): "Abans %s - Ara %s \n %s " % (d["price"] , r["price"]
    , print_pis(r)) , pisos_diff_preu)) , 
        print_pisos(pisos_nous), print_pisos(pisos_esborrats))
to = ["elisabethlo85@gmail.com" , "kozko2001@gmail.com"]

if len(pisos_nous) > 0 or len(pisos_esborrats) > 0 or len(pisos_diff_preu) > 0 : 
    mail.sendMail(to, "idealista feed", message.encode("utf-8"))

if len(pisos_nous) > 0:
    db.pisos.insert(pisos_nous)
if len(pisos_esborrats) > 0:
    keys = map( lambda p: {"key": p["key"]}, pisos_esborrats)
    for key in keys:
        db.pisos.remove( key ) 
if len(pisos_diff_preu) > 0:
    pisos = map( lambda (d,r) : r , pisos_diff_preu)
    for pis in pisos:
        db.pisos.update( {"key": pis["key"] }, pis)
