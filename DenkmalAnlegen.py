import json, pywikibot as pwb
from pywikibot import pagegenerators as pg

def getTarget(clmtp:str,tgt:str,tgt2:str="de",prc:str="9"):
    if clmtp == "item":
        target = pwb.ItemPage(repo, tgt)
    elif clmtp == "date":
        if prc == "":
            p = 9
        else:
            p = int(prc[0])
        if tgt.isnumeric():
            target  = pwb.WbTime(year=int(tgt), precision=p)
    elif clmtp == "file":
        site1 = pwb.Site("commons", "commons")
        target = pwb.FilePage(site1, tgt)
    elif clmtp == "str":
        target = tgt
    elif clmtp == "text":
        target = pwb.WbMonolingualText(tgt,tgt2)
    elif clmtp == "koord":
        target = pwb.Coordinate(lat=float(tgt2), lon=float(tgt), alt=0, precision=0.000001, site=site) 
    else:
        target = None
    return(target)
        
def setClaim(item, d:dict, clmnm:str, clmtp: str, tgt:str, tgt2:str="de", prc:str="9", overwrite:bool=False) -> None:
    claim = pwb.Claim(repo, clmnm) 
    # print("clmnm:", clmnm, "tgt:", tgt)
    fd = False
    target = getTarget(clmtp,tgt,tgt2,prc)
    if clmnm in d['claims'] and target:
        clms = d['claims'][clmnm]
        # print(clms, len(clms))
        for c in clms:
            if clmtp == "koord":
                d = c.toJSON()["mainsnak"]["datavalue"]["value"]
                lat = d["latitude"]
                lon = d["longitude"]
                fd = lat == float(tgt2) and lon == float(tgt)
#                print(fd,lat,tgt2,lon,tgt)
            else:
                fd = c.target_equals(target)
            if fd: 
                break
        if fd:
            print(f"Claim {clmnm} has already target {str(target)} - skipping")
        else:
            print(f"Claim {clmnm} has other target {str(target)} ")
            if overwrite:
                print("overwriting")
                c.changeTarget(target)
    if target and not fd and not overwrite:
#        print("Claim " + clmnm + " has not yet target " + str(target) )
        claim.setTarget(target) 
        item.addClaim(claim, summary=u'Adding claim')

def setSource(item, clmnm, srcnm, val):
    if item.claims[clmnm]:
        for claim in item.claims[clmnm]: # Loop through claims
            already = False
            try:
                srcs = claim.getSources() # Gets all of the source on the claim
            except:
                continue
            for src in srcs: # Loop through sources
                if srcnm in src:
                    already = True
            if already: # If True skip this claim
                print(f"Claim {clmnm} has already {srcnm} as source - skipping")
                continue
            # add source
            source = pwb.Claim(repo, srcnm, is_reference=True) 
            source.setTarget(val) # Inserting value
            claim.addSource(source, summary=u'Adding source')
    
def setQualifier(item, clmnm:str, qualnm:str, qualtp: str, tgt:str, tgt2:str="de", prc:str="9"):
    target = getTarget(qualtp,tgt,tgt2,prc)
    claim = item.claims[clmnm][0]
    if qualnm in claim.qualifiers: #If not already exists
        print(f"Claim {clmnm} has already {qualnm} as qualifier - skipping")
    else:
        qualifier = pwb.Claim(repo, qualnm)
        qualifier.setTarget(target)
        claim.addQualifier(qualifier, summary=u'Adding qualifier.') #Adding qualifier 

def openJSONfile(fn: str) -> dict:
    with open("./public/data/" + fn + ".json", 'r') as f:
        s = json.load(f)
        f.close()
        return(s)

user = "Reinhard Kraasch"
site = pwb.Site("wikidata", "wikidata")
site.login()
repo = site.data_repository()  # this is a DataSite object

st =         openJSONfile("Stadtteile")
bz =         openJSONfile("Bezirke")
artikel =    openJSONfile("Artikel")
entwurf =    openJSONfile("Entwurf")
datierung =  openJSONfile("Daten")
dsh =        openJSONfile("Denkmalliste")
bilder =     openJSONfile("Bilder")
commonscat = openJSONfile("Commonscat")
typtowd =    openJSONfile("TypToWikidata")
idtowd =     openJSONfile("Wikidata")
ensembles =  openJSONfile("Ensembles")
    
i = 0
for id in dsh:
    v = dsh[id]
    if id in idtowd:
        it = idtowd[id]
    else:
        it = "Q115484575"
#    if id != "11763" :
#    if id != "11753" :
    if id != "11760" :
        continue
    print(id, v, it)
    if it == "":
        item = pwb.ItemPage(site)
        label_dict = { "de": v["Bezeichnung"], "en": v["Bezeichnung"],  "fr": v["Bezeichnung"]}
        item.editLabels(labels = label_dict, summary="Setting labels")
        description_dict = {"de": v["Typ"]}
        item.editDescriptions(descriptions = description_dict, summary="Setting descriptions")
        # alias_dict = {"en":[], "de":[]}
        #item.editAliases(aliases = alias_dict, summary="Setting aliases")
        it = item.getID()
    item = pwb.ItemPage(site,it)        
    dict = item.get()
#    print(*dict)
    tp = v["Typ"]
    tpset = False
    if tp in typtowd:
        typ = typtowd[tp]
        for ttyp in typ:
#            print(ttyp)
            setClaim(item, dict,u'P31',"item",ttyp)
        tpset = True
    if not tpset:
        setClaim(item, dict,u'P31',"item",u'Q28661501')
    setClaim(item, dict, u'P1435',"item",u'Q28661501')
    StadtTeile = v["Stadtteil"].split(",")
    for StadtTeil in StadtTeile: 
        setClaim(item, dict,u'P276',"item",st[StadtTeil.strip()])
    Bezirke = v["Bezirk"].split(",")
    for Bezirk in Bezirke:
        setClaim(item, dict,u'P131',"item",bz[Bezirk.strip()])
    setClaim(item, dict,u'P17',"item",u'Q183')
    if "Datierung" in v:
        d = v["Datierung"] 
        if d.isnumeric():
            setClaim(item, dict, u'P571', "date", d,'year')
        else:
            dd = datierung[d]
            print(dd)
            if dd:
                for d in dd:
                    setClaim(item, dict,u'P571',"date",d[0],d[2])
                    if d[1] and d[1].isnumeric():
                        setQualifier(item, u'P571',u'P580', "date",d[0],d[2])
                        setQualifier(item, u'P571',u'P582', "date",d[1],d[2])
                    
    setClaim(item, dict,u'P625',"koord",v["XCenter"],v["YCenter"],True)
    Adressen = v["Belegenheit"].split("|")
    for Adresse in Adressen:
        setClaim(item, dict,u'P6375',"text",Adresse.strip() + ", " + v["PLZ"] + " Hamburg","de")

    setClaim(item, dict,u'P1822',"str",id)
    setQualifier(item, u'P1822',u'P1932',"str",str(v))
    setSource(item, u'P1435',u'P854',u'http://static.hamburg.de/fhh/opendata/kb/DenkmallisteHamburg.xml')
    setSource(item, u'P1822',u'P854',u'http://static.hamburg.de/fhh/opendata/kb/DenkmallisteHamburg.xml')
    if "Entwurf" in v:
        if v["Entwurf"] in entwurf:
            ll = entwurf[v["Entwurf"]]
            for l in ll[1:]:
                if len(l) > 1:
                    setClaim(item, dict, u'P84',"item", l[1])
    if id in bilder:
        setClaim(item, dict,u'P18',"file",bilder[id] )
    if id in commonscat:
        setClaim(item, dict,u'P373',"str",commonscat[id])
        try:
            sl = item.getSitelink("commonswiki")
        except:
            sl = ""
        if sl != 'Category:' + commonscat[id]:
            sitedict = {'site':'commonswiki', 'title': 'Category:' + commonscat[id]}
            item.setSitelink(sitedict, summary=u'Setting sitelink.')
        else:
            print(f"item {it} has already commonswiki sitelink Category:{commonscat[id]}")
    if id in artikel:
        try:
            sl = item.getSitelink("dewiki")
        except:
            sl = ""
        if sl != artikel[id]:
            sitedict = {'site':'dewiki', 'title': artikel[id]}
            item.setSitelink(sitedict, summary=u'Setting sitelink.')
        else:
            print(f"item {it} has already dewiki sitelink {artikel[id]}")
    break
    
#print(dict)
