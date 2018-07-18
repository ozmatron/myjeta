from django.db import connection # useful for viewing django sql using print(connection.queries)
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Coefficients, Lines, Linked, Routes, Stops
from .destinations import Destinations
from .route_result import Route_result

from datetime import datetime, timedelta
import json
from more_itertools import unique_everseen
import pandas as pd
from pytz import timezone
import time

def index(request):
    return render(request, 'index.html')


def lines(request):
    """
    Arguments: source bus stop, destination bus stop
    Returns json of bus lines which have routes that use these two bus stops.  
    Note: does not check that source stop is before the destination stop.
        - Logically this will always be the case since routes are one way.
    """
    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')

    routes = Routes.objects.filter(stopids__contains=[source, destination]).values_list('routeid', flat=True)
    lines = Lines.objects.filter(routes__overlap=list(routes)).values_list('lineid', flat=True)

    return HttpResponse(json.dumps(list(lines)), content_type='application/json')


def journeytime(request):
    """
    Arguments: source & destination bus stops, lineid (e.g. 39A), time (unixtime)
    Returns json showing model prediction:
        - Arrival time at destination
        - Total travel time
        - Travel time for each segment of the journey (distance between each bus stop)
    """

    source = request.GET.get('source', '')
    destination = request.GET.get('destination', '')
    lineid = request.GET.get('lineid', '')
    start_time = request.GET.get('time', '')

    rain = 0.5 # Should come from table or API query

    # Get Irish timezone (utc + daylight saving time (DST))
    irish_time = timezone('Europe/Dublin')

    # Get start_time (unixtime) as datetime object
    dt_time = datetime.fromtimestamp(int(start_time), irish_time)

    # Create list with desired weekday filled.
    weekday = dt_time.weekday() # Mon: 0, Sun: 6
    week_dummies = [0] * 7
    week_dummies[weekday] = 1
    del week_dummies[2] # Delete wednesday - not included in model due to dummy var trap

    # Get arrivaltime in seconds
    date = dt_time.date()
    date_unixtime = time.mktime(date.timetuple())
    seconds_since_midnight = int(time.mktime((dt_time - timedelta(seconds = date_unixtime)).timetuple()))
    
    # Group model inputs into single list
    model_inputs = [seconds_since_midnight, rain] + week_dummies

    # Get stop lists associated with query lineid, start stop and end stop
    lineids = Lines.objects.filter(lineid=lineid).values_list('routes', flat=True)
    routes = Routes.objects.filter(routeid__in=(list(lineids)[0]), stopids__contains=[source, destination]).values()
    routes = pd.DataFrame.from_records(routes)

    if routes.shape[0] > 1:
        print("Error: multiple possible routes.")
        print(routes)

    # Convert pandas list of stopids to list. If multiple possible routes, take first row.
    stop_list = routes['stopids'].tolist()[0]

    # Slice list by source and destination stop
    journey_stops = stop_list[stop_list.index(int(source)):(stop_list.index(int(destination))+1)]

    # Change each stopid into string
    stringified = list(map(str, journey_stops))

    # Make stopids into segments
    journey_segments = [ '_'.join(x) for x in zip(stringified[0:], stringified[1:])]

    # Select coefficient rows with these segment ids, and load into pd dataframe.
    coefficients_qs = Coefficients.objects.filter(pk__in=journey_segments).values()
    coefficients = pd.DataFrame.from_records(coefficients_qs)

    # Sort values by journey_segment segmentid
    coefficients['segment'] = coefficients['segment'].astype("category")
    coefficients['segment'].cat.set_categories(journey_segments, inplace=True)
    coefficients = coefficients.sort_values(["segment"])

    # Rearrange columns and set segment id as index
    coefficients = coefficients[["segment", "intercept", "arrivaltime", "rain", 
    "mon", "tue", "thu", "fri", "sat", "sun"]]    
    coefficients = coefficients.set_index('segment')

    # Loop through rows of coefficients df, calculating segment travel time
    arrivaltime = model_inputs[0]
    totaltraveltime = 0
    segment_times = []

    for i, rows in coefficients.iterrows():
        traveltime = (rows['intercept']
                    +(rows['arrivaltime']*arrivaltime)
                    +(rows['rain']*model_inputs[1])
                    +(rows['mon']*model_inputs[2])
                    +(rows['tue']*model_inputs[3])
                    +(rows['thu']*model_inputs[4])
                    +(rows['fri']*model_inputs[5])
                    +(rows['sat']*model_inputs[6])
                    +(rows['sun']*model_inputs[7]))
        segment_times.append((i, round(traveltime)))
        totaltraveltime += traveltime

        # arrivaltime = initial start time + sum of previous segment times
        arrivaltime = model_inputs[0] + totaltraveltime

    # Construct json
    json_dict = {}
    json_dict['arrivaltime'] = str(timedelta(seconds=round(int(arrivaltime))))
    json_dict['totaltraveltime'] = str(timedelta(seconds=round(int(totaltraveltime))))
    json_dict['segment_times'] = {i[0]:i[1] for i in segment_times}

    return HttpResponse(json.dumps(json_dict), content_type='application/json')


def get_address(request):
    if not request.is_ajax():
        error_json = json.dumps({"error": {"code": 400,"message": "Not Ajax request."}})
        return HttpResponse(error_json, content_type='application/json')

    term = request.GET.get('term', '')
    bus_adds = Stops.objects.filter(Q(stopid__startswith=term) | Q(address__icontains=term))[:20]
    results = []
    for badd in bus_adds:
        badd_json = {}
        badd_json['label'] = badd.address +", "+ str(badd.stopid)
        results.append(badd_json)
    data = results

    return HttpResponse(json.dumps(data), content_type='application/json')


def routes(request):
    routes = Routes.objects.all().values()
    routesJson = [dict(i) for i in routes]

    return JsonResponse(routesJson, safe=False)


def linked(request):
    linked = Linked.objects.all().values()
    linkedJson = [dict(i) for i in linked]

    return JsonResponse(linkedJson, safe=False)


def destinations(request):
    start = 15
    dest1 = Destinations(start).destinations_json()
    return JsonResponse(dest1, safe=False)


def route_result(request):
    start = 1165
    destination = 7564
    route1 = Route_result(start, destination).route_json()
    return JsonResponse(route1, safe=False)


def stops(request):
    """
    Query Terms: source stop id, destination stop id, bus line id.
        - source and destination must be ints
        - Either all or none of these terms can be added.
    Returns json showing stop information:
        - If source stopid is given, returns stopids that can be reached from this location.
        - If source & destination stopid are given, returns stopids that connect these two via any route.
        - If source, destination & lineid are given, returns stopids that connect these two via only this route
    Stop information:
        - stop_id
        - stop_name = address of stop
        - lineid = dictionary or form {lineid: order of stop on route}. E.g. {"46A":14,"46E":13,"7B":13}
        - coord = list of coordinations [lat, lng].
    """

    if not request.is_ajax():
        error_json = json.dumps({"error": {"code": 400,"message": "Not Ajax request."}})
        return HttpResponse(error_json, content_type='application/json')

    source = request.GET.get("source")
    destination = request.GET.get("destination")
    lineid = request.GET.get("lineid")

    routes_qs = Routes.objects.all()
        
    if source:
        source = int(source)
        routes_qs = routes_qs.filter(stopids__contains=[source])

    if destination:
        destination = int(destination)
        routes_qs = routes_qs.filter(stopids__contains=[destination])

    if lineid:
        routes_qs = routes_qs.filter(lineid=lineid)

    routes = pd.DataFrame.from_records(routes_qs.values('lineid', 'stopids'))

    if routes.empty:
        error_json = json.dumps({"error": {"code": 404,"message": "No data fits these criteria."}})
        return HttpResponse(error_json, content_type='application/json')

    # Slice stopids to left of start_stop to remove stops previous to the start stop
    if source:
        routes['stopids'] = routes['stopids'].apply(lambda x: x[x.index(source):])

    # Slice stopids by destination if it was given.
    if destination:
        routes['stopids'] = routes['stopids'].apply(lambda x: x[:(x.index(destination)+1)])

    # Remove duplicate stopids within routes, while maintaining stop order.
    routes['stopids'] = routes['stopids'].apply(lambda x: list(unique_everseen(x)))

    # Remove routes with identical lineids. Favour routes with more stops.
    routes['stopids_len'] = routes['stopids'].apply(lambda x: len(x))
    routes = routes.sort_values('stopids_len').groupby('lineid').last()
    routes = pd.DataFrame(routes).reset_index()
    routes = routes[['lineid', 'stopids']]

    # Unstack stopids column.
    routes_unstacked = routes.set_index('lineid').stopids.apply(pd.Series).stack().reset_index(level=-1, drop=True).astype(int).reset_index()
    routes_unstacked = routes_unstacked.rename(columns={0:'stopid'})

    # Create a column indicating the order (program number) of each stop in each route.
    routes_unstacked['program'] = routes_unstacked.groupby('lineid').cumcount()

    # Group lineid and program number into column containing a dict for each stopid. E.g. {'84X': 9, '46A': 15 ...}
    routes = routes_unstacked.groupby(['stopid']).apply(lambda x: dict(x[['lineid','program']].values))
    routes = pd.DataFrame(routes).reset_index()
    routes = routes.rename(columns={0: 'lineid'})

    # Get set of stops visted by the routes.
    stops_list = list(set(routes['stopid'].tolist()))

    # Get these rows in stops table
    stops = Stops.objects.filter(stopid__in=stops_list).values()
    stops = pd.DataFrame.from_records(stops)

    # Group lat and lng columns into list of form [lat, lng]
    stops = stops.groupby(['stopid', 'address'], as_index=False).apply(lambda x: x[['lng','lat']].values.tolist()[0])
    stops = pd.DataFrame(stops).reset_index()
    stops = stops.rename(columns={0: 'coord'})

    # Merge stops and routes to combine lineid info with coordinate and address.
    combined_df = pd.merge(stops, routes, on='stopid',sort=False)
    combined_df = combined_df[['stopid', 'address', 'lineid', 'coord']]

    # Rename to suit front end conventions
    combined_df = combined_df.rename(columns={'stopid': 'stop_id', 'address': 'stop_name'})

    return HttpResponse(list(combined_df.to_json(orient='records')), content_type='application/json')