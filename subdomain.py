#!/usr/bin/env python3

import requests
import argparse
from gevent import socket
from gevent.pool import Pool

requests.packages.urllib3.disable_warnings()

def ana(domain, masscanCikti, urlCikti):
    bulunanAlanlar = {}
    bulunmayanAlanlar = {}
    
    if (not masscanCikti and not urlCikti):
        print("[+]: crt.sh'den alan listesi indiriliyor...")
    
    yanit = yanitTopla(domain)
    
    if (not masscanCikti and not urlCikti):
        print("[+]: Alan listesi indirme tamamlandı.")
    
    alanlar = alanlariTopla(yanit)
    
    if (not masscanCikti and not urlCikti):
        print("[+]: Listedeki %s alan çözümlendi." % len(alanlar))
    
    if len(alanlar) == 0:
        exit(1)
    
    havuz = Pool(15)
    yesillikler = [havuz.spawn(cozun, domain) for domain in alanlar]
    
    havuz.join(timeout=1)
    
    for yesillik in yesillikler:
        sonuc = yesillik.value
        
        if (sonuc):
            for ip in sonuc.values():
                if ip != 'yok':
                    bulunanAlanlar.update(sonuc)
                else:
                    bulunmayanAlanlar.update(sonuc)
    
    if (urlCikti):
        printUrls(sorted(alanlar))
    
    if (masscanCikti):
        printMasscan(bulunanAlanlar)
    
    if (not masscanCikti and not urlCikti):
        print("\n[+]: Bulunan Alanlar:")
        printAlanlar(bulunanAlanlar)
        print("\n[+]: DNS kaydı olmayan Alanlar:")
        printAlanlar(bulunmayanAlanlar)

def cozun(domain):
    try:
        return({domain: socket.gethostbyname(domain)})
    except:
        return({domain: "yok"})

def printAlanlar(alanlar):
    for alan in sorted(alanlar):
        print("%s\t%s" % (alanlar[alan], alan))

def printMasscan(alanlar):
    ipListesi = set()
    
    for alan in alanlar:
        ipListesi.add(alanlar[alan])
    
    for ip in sorted(ipListesi):
        print("%s" % (ip))

def printUrls(alanlar):
    for alan in alanlar:
        print("https://%s" % alan)

def yanitTopla(domain):
    url = 'https://crt.sh/?q=' + domain + '&output=json'
    
    try:
        yanit = requests.get(url, verify=False)
    except:
        print("[!]: Sunucuyla bağlantı kurulamadı.")
        exit(1)
    
    try:
        alanlar = yanit.json()
        return alanlar
    except:
        print("[!]: Sunucu geçerli bir JSON yanıtı vermedi.")
        exit(1)

def alanlariTopla(yanit):
    alanlar = set()
    
    for alan in yanit:
        alanlar.add(alan['common_name'])
        
        if '\n' in alan['name_value']:
            domListesi = alan['name_value'].split()
            
            for dom in domListesi:
                alanlar.add(dom)
        else:
            alanlar.add(alan['name_value'])
    
    return alanlar

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--domain", type=str, required=True,
                        help="CT günlükleri için sorgulanacak alan adı, ör.: domain.com")
    
    parser.add_argument("-u", "--urls", default=0, action="store_true",
                        help="çözümlenen alanlar için https:// ile başlayan URL'leri çıktı olarak verir.")
    
    parser.add_argument("-m", "--masscan", default=0, action="store_true",
                        help="çözümlenen IP adreslerini, her satırda bir IP adresi olacak şekilde çıktı verir. Masscan için \"-iL\" formatında kullanışlıdır.")
    
    args = parser.parse_args()
    ana(args.domain, args.masscan, args.urls)
