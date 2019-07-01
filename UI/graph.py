from django.shortcuts import render

# Include the `fusioncharts.py` file which has required functions to embed the charts in html page
from .fusioncharts import FusionCharts

# private include
from .fusioncharts import FusionTable
from .fusioncharts import TimeSeries
from .models import Traffic
from collections import OrderedDict
from django.db.models import Count
from datetime import datetime
import operator

# private code : service usage

SNI = [['amazon', ['amazon']], ['apple', ['apple.com']], ['bank', ['bank']], ['bing', ['bing']],
       ['mail', ['mail', 'imap', 'pop', 'smtp']], ['blog', ['blog', 'tistory']],
       ['credit card', ['card']], ['daum', ['daum']], ['dropbox', ['dropbox']],
       ['e-commerce', ['auction', 'akmall', 'interpark', 'gmarket', 'shopping.naver', 'tmon', 'wemakeprice', '11st', 'kyobobook']],
       ['facebook', ['facebook', 'fbc']], ['gist', ['gist']], ['github', ['github']],
       ['google drive', ['drive.google']], ['google play', ['play.google']],
       ['google talk', ['mtalk']], ['google', ['google', 'ggpht']], ['icloud', ['icloud']],
       ['instagram', ['instagram']], ['kakao', ['kakao']], ['microsoft', ['microsoft', 'msn', 'login.live', 'd.docs.live.net', 'office']],
       ['nate', ['nate']], ['naver', ['naver', 'pstatic.net']], ['netflix', ['netflix', 'nflx']],
       ['samsung', ['samsung']],  ['sktelecom', ['sktelecom', 'skplanet']],
       ['skype', ['skype']], ['skyscanner', ['skyscanner']], ['twitch', ['twitch']],
       ['twiter', ['twiter']], ['wikipedia', ['wiki']], ['yahoo', ['yahoo']], ['youtube', ['youtube']]]

serviceConfig = OrderedDict()
serviceConfig["caption"] = "Application Traffics"
serviceConfig["yaxisname"] = "number of session"
serviceConfig["aligncaptionwithcanvas"] = "0"
serviceConfig["plottooltext"] = "<b>$dataValue</b> leads received"
serviceConfig["theme"] = "fusion"

serviceData = OrderedDict()
for app in SNI :
    serviceData[app[0]] = 0

def show_chart(request):
    charts = {'c1': count_chart().render(), 'c2': protocol_chart().render(),
                  'c3': ip_chart().render(), 'c4': port_chart().render(),
                   'c5': service_chart().render()}
    return render(request, 'index.html', charts) 
    
def count_chart():
    data=[]
    duplicates = Traffic.objects.values('unixtime').annotate(time_count=Count('unixtime')).filter(time_count__gt=0)
    data = [[datetime.fromtimestamp(D.get('unixtime')).strftime("%S-%M-%H-%d-%b-%y"),D.get('time_count')] for D in duplicates]

    schema = [{
        "name": "Time",
        "type": "date",
        "format": "%S-%M-%H-%d-%b-%y"
        }, {
        "name": "Packet count",
        "type": "number"
        }]
    
    fusionTable = FusionTable(schema, data)
    timeSeries = TimeSeries(fusionTable)

    timeSeries.AddAttribute("caption", """{ 
                                        text: 'Packet amont Analysis'
                                        }""")

    timeSeries.AddAttribute("subcaption", """{ 
                                    text: ''
                                    }""") 
    timeSeries.AddAttribute("yAxis", """[{
                                            plot: {
                                            value: 'Packet Amount Value',
                                            type: 'line'
                                            },
                                            format: {
                                            prefix: ''
                                            },
                                            title: ' Value'
                                        }]""")

    # Create an object for the chart using the FusionCharts class constructor
    return FusionCharts("timeseries", "ex1", "600", "400", "chart-1", "json", timeSeries)
    
def protocol_chart():
    # Create an object for the pie3d chart using the FusionCharts class constructor
    dataSource = OrderedDict()

    # The `chartConfig` dict contains key-value pairs data for chart attribute
    chartConfig = OrderedDict()
    chartConfig["caption"] = "Protocol Share"
    chartConfig["subCaption"] = "For a recent 10s"
    chartConfig["showValues"] = "1"
    chartConfig["showPercentInTooltip"] = "0"
    chartConfig["enableMultiSlicing"] = "1"

    # The `chartData` dict contains key-value pairs data
    chartData = OrderedDict()
    traffic = Traffic.objects.all()
    for pkt in traffic :
        proto = pkt.protocol
        if proto in chartData :
            chartData[proto] = chartData[proto] + 1
        else :
            chartData[proto] = 1

    dataSource["chart"] = chartConfig
    dataSource["data"] = []

    for key, value in chartData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)

    return FusionCharts("pie3d", "ex2" , "600", "400", "chart-2", "json", dataSource)

def ip_chart():

    # Chart data is passed to the `dataSource` parameter, as dictionary in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `chartConfig` dict contains key-value pairs data for chart attribute
    chartConfig = OrderedDict()
    chartConfig["caption"] = "Top 10 IP usage"
    chartConfig["xAxisName"] = "IP address"
    chartConfig["yAxisName"] = "Count time"
    chartConfig["theme"] = "fusion"

    # The `chartData` dict contains key-value pairs data
    data=[]
    duplicates1 = Traffic.objects.values('src_ip').annotate(ip_count=Count('src_ip')).filter(src_ip__gt=0)
    duplicates2 = Traffic.objects.values('src_ip').annotate(ip_count=Count('dst_ip')).filter(dst_ip__gt=0)

    duplicates=duplicates1.union(duplicates2)
    data=[[d.get('src_ip'),d.get('ip_count')] for d in duplicates]
    data.sort(key=operator.itemgetter(1),reverse=True)
    # The `chartData` dict contains key-value pairs data
    print(data[:10])
    chartData = OrderedDict()
    i=0
    for D in data:
        if (i>10):
            break
        countvalue=int(D[1])
        chartData[D[0]]=countvalue
        i=i+1


    dataSource["chart"] = chartConfig
    dataSource["data"] = []
    
    # Convert the data in the `chartData` array into a format that can be consumed by FusionCharts. 
    # The data for the chart should be in an array wherein each element of the array is a JSON object
    # having the `label` and `value` as keys.

    # Iterate through the data in `chartData` and insert in to the `dataSource['data']` list.
    for key, value in chartData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)

    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `dataSource` parameter.
    return FusionCharts("column2d", "ex3" , "600", "400", "chart-3", "json", dataSource)

def port_chart():

    # Chart data is passed to the `dataSource` parameter, as dictionary in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `chartConfig` dict contains key-value pairs data for chart attribute
    chartConfig = OrderedDict()
    chartConfig["caption"] = "Top 10 port Number Usage"
    chartConfig["xAxisName"] = "Port Number"
    chartConfig["yAxisName"] = "Count"
    chartConfig["numberSuffix"] = "K"
    chartConfig["theme"] = "fusion"
    
    data=[]
    duplicates1 = Traffic.objects.values('src_port').annotate(port_count=Count('src_port')).filter(src_port__gt=0)
    duplicates2 = Traffic.objects.values('src_port').annotate(port_count=Count('dst_port')).filter(dst_port__gt=0)

    duplicates=duplicates1.union(duplicates2)
    data=[[d.get('src_port'),d.get('port_count')] for d in duplicates]
    data.sort(key=operator.itemgetter(1),reverse=True)
    # The `chartData` dict contains key-value pairs data
    print(data[:10])
    chartData = OrderedDict()
    i=0
    for D in data:
        if (i>10):
            break
        name=str(D[0])
        chartData[name]=D[1]
        i=i+1

    dataSource["chart"] = chartConfig
    dataSource["data"] = []
    
    # Convert the data in the `chartData` array into a format that can be consumed by FusionCharts. 
    # The data for the chart should be in an array wherein each element of the array is a JSON object
    # having the `label` and `value` as keys.

    # Iterate through the data in `chartData` and insert in to the `dataSource['data']` list.
    for key, value in chartData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)


    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `dataSource` parameter.
    return FusionCharts("column2d", "ex4" , "600", "400", "chart-4", "json", dataSource)
    
    
def service_chart():
    # Create an object for the pie3d chart using the FusionCharts class constructor
    dataSource = OrderedDict()
    traffic = Traffic.objects.exclude(sni=' \'NULL\'')

    for pkt in traffic :
        for app in SNI :
            f = 0
            for ptn in app[1] :
                if ptn in pkt.sni :
                    serviceData[app[0]] = serviceData[app[0]] + 1
                    f = 1
                    break
            if f == 1 :
                break

    dataSource["chart"] = serviceConfig
    dataSource["data"] = []

    for key, value in serviceData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)

    return FusionCharts("bar2d", "ex5" , "1200", "2000", "chart-5", "json", dataSource)
