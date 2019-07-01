from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# private include
from UI.fusioncharts import FusionCharts
from UI.models import Traffic
from collections import OrderedDict
from datetime import datetime
import operator
import time

# it is a default view.
# please go to the samples folder for others view

#def catalogue(request):
#    return  render(request, 'catalogue.html')

# private code : service usage

SNI = [['amazon', ['amazon']], ['apple', ['apple.com']], ['bank', ['bank']], ['bing', ['bing']],
       ['mail', ['mail', 'imap', 'pop', 'smtp']], ['blog', ['blog', 'tistory']],
       ['credit card', ['card']], ['daum', ['daum']], ['dropbox', ['dropbox']],
       ['e-commerce', ['auction', 'akmall', 'interpark', 'gmarket', 'shopping.naver', 'tmon', 'wemakeprice', '11st', 'kyobobook']],
       ['facebook', ['facebook', 'fbc']], ['gist', ['gist']], ['github', ['github']],
       ['google drive', ['drive.google']], ['google play', ['play.google']],
       ['google talk', ['mtalk']], ['google', ['google', 'ggpht']], ['icloud', ['icloud']],
       ['instagram', ['instagram']], ['kakao', ['kakao']], ['microsoft', ['microsoft', 'msn', 'login.live', 'd.docs.live.net', 'office']],
       ['naver', ['naver', 'pstatic.net']], ['netflix', ['netflix', 'nflx']],
       ['samsung', ['samsung']], ['sktelecom', ['sktelecom', 'skplanet']],
       ['skype', ['skype']], ['skyscanner', ['skyscanner']], ['twitch', ['twitch']],
       ['twiter', ['twiter']], ['wikipedia', ['wiki']], ['yahoo', ['yahoo']], ['youtube', ['youtube']]]

countConfig = OrderedDict()
protoConfig = OrderedDict()
ipConfig = OrderedDict()
portConfig = OrderedDict()
serviceConfig = OrderedDict()

countSource = OrderedDict()
protoSource = OrderedDict()
ipSource = OrderedDict()
portSource = OrderedDict()
serviceSource = OrderedDict()

numpkts = []

def init_chart(request):
    
    countConfig["caption"] = "Packet amount"
    countConfig["subCaption"] = "per 60 seconds"
    countConfig["yaxisname"] = "Number of packet"
    countConfig["xaxisname"] = "Time"
    countConfig["numdisplaysets"] = "30"
    countConfig["theme"] = "fusion"
    
    protoConfig["caption"] = "Protocol Share"
    protoConfig["subCaption"] = "For a recent 10s"
    protoConfig["showValues"] = "1"
    protoConfig["showPercentInTooltip"] = "0"
    protoConfig["enableMultiSlicing"] = "1"
    
    ipConfig["caption"] = "Top 10 IP usage"
    ipConfig["yAxisName"] = "Number of packet"
    ipConfig["theme"] = "fusion"
    
    portConfig["caption"] = "Top 10 Port usage"
    portConfig["yAxisName"] = "Number of packet"
    portConfig["theme"] = "fusion"
    
    serviceConfig["caption"] = "Application Traffics"
    serviceConfig["yaxisname"] = "number of session"
    serviceConfig["aligncaptionwithcanvas"] = "0"
    serviceConfig["plottooltext"] = "<b>$dataValue</b> les Trafficads received"
    serviceConfig["theme"] = "fusion"
    
    countSource["chart"] = countConfig
    protoSource["chart"] = protoConfig
    ipSource["chart"] = ipConfig
    portSource["chart"] = portConfig
    serviceSource["chart"] = serviceConfig
    
    countSource["data"] = []
    protoSource["data"] = []
    ipSource["data"] = []
    portSource["data"] = []
    serviceSource["data"] = []
        
    count_chart = FusionCharts("line", "ex1" , "600", "400", "chart-1", "json", countSource)
    protocol_chart = FusionCharts("pie3d", "ex2" , "600", "400", "chart-2", "json", protoSource)
    ip_chart = FusionCharts("bar2d", "ex3" , "600", "400", "chart-3", "json", ipSource)
    port_chart = FusionCharts("bar2d", "ex4" , "600", "400", "chart-4", "json", portSource)
    service_chart = FusionCharts("bar2d", "ex5" , "1200", "2000", "chart-5", "json", serviceSource)
    
    charts = {'c1': count_chart.render(), 'c2': protocol_chart.render(),
                  'c3': ip_chart.render(), 'c4': port_chart.render(),
                   'c5': service_chart.render()}
    return render(request, 'index_test.html', charts)

def update_data(source, dic):
    source["data"] = []

    for key, value in dic.items():
        data = {}
        data["label"] = key
        data["value"] = value
        source["data"].append(data)

def update_chart(request):
    start_time = int(time.time()) - 65
    end_time = start_time + 60
    #start_time = 1557884580
    #end_time = 1557884588
    traffics = Traffic.objects.filter(unixtime__gte = start_time, unixtime__lt = end_time)
    L = len(traffics)
     
    numpkts.append([end_time, L])
    if len(numpkts) == 30 :
        numpkts.pop()

    counts = OrderedDict()
    for ct in numpkts :
        t = datetime.utcfromtimestamp(ct[0]).strftime('%Y-%m-%d %H:%M')
        counts[t] = ct[1]

    protocols_tp = OrderedDict()
    for pkt in traffics :
        proto = pkt.protocol
        if proto in protocols_tp :
            protocols_tp[proto] = protocols_tp[proto] + 1
        else :
            protocols_tp[proto] = 1
    
    oth = 0
    protocols = OrderedDict()
    for key, value in protocols_tp.items():
        if value < L/100 :
            oth = oth + value            
        else :
            protocols[key] = value
    protocols["others"] = oth
    
    ips = OrderedDict()
    
    for pkt in traffics :
        sip = pkt.src_ip
        dip = pkt.dst_ip
        if sip in ips :
            ips[sip] = ips[sip] + 1
        else :
            ips[sip] = 1
        if dip in ips :
            ips[dip] = ips[dip] + 1
        else :
            ips[dip] = 1

    ips_top10 = sorted(ips.items(), key=operator.itemgetter(1), reverse=True)
    ips = OrderedDict()
    
    for i in range(10) :
        ips[ips_top10[i][0]] = ips_top10[i][1]
            
    ports = OrderedDict()
    
    for pkt in traffics :
        sport = str(pkt.src_port)
        dport = str(pkt.dst_port)
        if sport in ports :
            ports[sport] = ports[sport] + 1
        else :
            ports[sport] = 1
        if dport in ports :
            ports[dport] = ports[dport] + 1
        else :
            ports[dport] = 1    
    
    ports_top10 = sorted(ports.items(), key=operator.itemgetter(1), reverse=True)
    ports = OrderedDict()
    
    for i in range(10) :
        ports[ports_top10[i][0]] = ports_top10[i][1]    
    
    services = OrderedDict()
    for app in SNI :
        services[app[0]] = 0    
    
    for pkt in traffics :
        if pkt.sni == ' \'NULL\'' :
            continue
        for app in SNI :
            f = 0
            for ptn in app[1] :
                if ptn in pkt.sni :
                    services[app[0]] = services[app[0]] + 1
                    f = 1
                    break
            if f == 1 :
                break
    
    update_data(countSource, counts)
    update_data(protoSource, protocols)
    update_data(ipSource, ips)
    update_data(portSource, ports)
    update_data(serviceSource, services)
    
    datasets = OrderedDict()
    datasets["count"] = countSource
    datasets["proto"] = protoSource
    datasets["ip"] = ipSource
    datasets["port"] = portSource
    datasets["service"] = serviceSource
    
    #countSource["data"].append({"label": "1557884588", "value": '{}'.format(len(traffics))})
    #return HttpResponse(request.GET.get('message', None))
    return JsonResponse(datasets)
  
