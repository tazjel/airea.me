# -*- coding: utf-8 -*- 
# Este fichero forma parte de airea.me
#
# Copyright 2011 Plexxoo Interactiva S.L.
# Copyright Daniel Gonzalez     <demetrio@plexxoo.com>
# Copyright Jon Latorre         <moebius@plexxoo.com>
# Copyright Silvia Martín       <smartin@plexxoo.com>
# Copyright Jesus Martinez      <jamarcer@plexxoo.com>
#
# Este fichero se distribuye bajo la licencia GPL según las
# condiciones que figuran en el fichero 'licence' que se acompaña.
# Si se distribuyera este fichero individualmente, DEBE incluirse aquí
# las condiciones expresadas allí.
#
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

def rest_station_get(code=None):
    data={}
    query=((db.zone.id==db.station.zone)&(db.town.id==db.station.town))
    if code is not None:
        query=query&(db.station.code==code)
    else:
        query=query&(db.station.id>0)
    
    rows=db(query).select(db.station.id,db.station.identifier,db.station.code,db.station.name,db.station.address,db.town.name,db.zone.code,db.station.latitude,db.station.longitude)
    num=1
    for row in rows:
        station_elements=get_station_ca_elements(row.station.code)
        #if len(station_elements) > 0:
        tmp={}
        tmp['id']=row.station.identifier
        tmp['name']=row.station.name
        tmp['code']=row.station.code
        tmp['address']="%s - %s"%(row.station.address,row.town.name)
        tmp['external_url']=ESTATION_LINK%(row.zone.code,row.station.code)
        tmp['lat']=row.station.latitude
        tmp['lon']=row.station.longitude
        if len(station_elements)==0:
            tmp['level']=0
            tmp['qa']={}
        else:            
            tmp['level']=get_station_ca_level(row.station.code)
            tmp['qa']=rest_station_qa_get(row.station.code)
        data[num]=tmp
        num+=1        
    return data

def _get_station_data(query=None,ca=False):
    if query is None:
        return {}
    
    # Get Values
    rows=db(query).select(db.measurement.id,db.measurement.element,db.measurement.measurement_hour,db.measurement.value,orderby="measurement.element ASC,measurement.measurement_hour ASC")
    elements={}
    for row in rows:
        if ca:
            if (row.element in QUALITY_ELEMENTS) is False:
                continue
        if (row.element in elements.keys()) is False:
            elements[row.element]={}
        elements[row.element][row.measurement_hour]=row.value
    values={}
    for index in range(1,25):
        values[index]=[]
    
    for item in elements.keys():
        elem=elements[item]
        for index in range(1,25):
            values[index].append(elem[index])
            
    return {'values': values,'columns':elements.keys()}

def _get_station_range(query=None,ca=False):
    if query is None:
        return {}
    
    data={}
    
    # Get Values
    rows=db(query).select(db.daily_statistics.element,db.daily_statistics.statistic_date,db.daily_statistics.value,orderby="daily_statistics.element ASC,daily_statistics.statistic_date ASC")

    counter=0
    for row in rows:
        tmp={}
        tmp['name']=row.element
        tmp['date']=row.statistic_date
        tmp['value']=row.value
        tmp['element']=row.element
        add_elem=True
        if ca:
            if (row.element in QUALITY_ELEMENTS) is False:
                add_elem=False
        if add_elem:
            data[counter]=tmp
            counter+=1
    return data

def _get_station_range_mobile(query=None,ca=False):
    if query is None:
        return {}
    
    data={}
    
    # Get Values
    rows=db(query).select(db.daily_statistics.element,db.daily_statistics.statistic_date,db.daily_statistics.value,orderby="daily_statistics.element ASC,daily_statistics.statistic_date ASC")
    dates=[]
    elements={}
    for row in rows:
        if ca:
            if (row.element in QUALITY_ELEMENTS) is False:
                continue
        if (row.element in elements.keys()) is False:
            elements[row.element]={}
        #date_lit=row.statistic_date.toordinal() #strftime('%Y%m%d')
        date_lit=int(row.statistic_date.strftime('%m%d'))
        if (date_lit in dates) is False:
            dates.append(date_lit)
        elements[row.element][date_lit]=row.value
#        elements[row.element][row.statistic_date]=row.value
    values={}
    for index in dates:
        values[index]=[]
    
    for item in elements.keys():
        elem=elements[item]
        for index in dates:
            values[index].append(elem[index])
#    s_values=sorted_dict(values)
    return {'values': values,'columns':elements.keys()}


def rest_station_last(code=None,ca=False):
    # Data
    data={}
    if code is None:
        return data
    
    # Initialize configuration
    cfg=Configure()
    cur_date = cfg.get('current_date')
    if cur_date is None:
        return data
    # Prepare date
    today=get_date_from_string(cur_date, "%Y-%m-%d")

    # Get Values
    query=(db.measurement.measurement_date==today)&(db.measurement.station==db.station.id)&(db.station.code==code)
    return _get_station_data(query,ca)

def rest_station_seven(code=None,ca=False):
    from datetime import timedelta
    
    # Data
    if code is None:
        return {}
    
    # Initialize configuration
    cfg=Configure()
    cur_date = cfg.get('current_date')
    if cur_date is None:
        return data
    # Prepare date
    today=get_date_from_string(cur_date, "%Y-%m-%d")
    seven_days = timedelta(days=7)
    last7_date=today-seven_days
    

    # Get Values
    query=(db.daily_statistics.statistic_date>=last7_date)&(db.daily_statistics.statistic_date<=today)&(db.daily_statistics.station==db.station.id)&(db.station.code==code)
    if check_is_mobile():
        return _get_station_range_mobile(query,ca)
    else:
        return _get_station_range(query,ca)

def rest_station_month(code=None,ca=False):
    from datetime import timedelta
    
    # Data
    if code is None:
        return {}
    
    # Initialize configuration
    cfg=Configure()
    cur_date = cfg.get('current_date')
    if cur_date is None:
        return data
    # Prepare date
    today=get_date_from_string(cur_date, "%Y-%m-%d")
    seven_days = timedelta(days=30)
    last7_date=today-seven_days
    

    # Get Values
    query=(db.daily_statistics.statistic_date>=last7_date)&(db.daily_statistics.statistic_date<=today)&(db.daily_statistics.station==db.station.id)&(db.station.code==code)
    if check_is_mobile():
        return _get_station_range_mobile(query,ca)
    else:
        return _get_station_range(query,ca)

def rest_station_year(code=None,ca=False):
    from datetime import timedelta
    
    # Data
    if code is None:
        return {}
    
    # Initialize configuration
    cfg=Configure()
    cur_date = cfg.get('current_date')
    if cur_date is None:
        return data
    # Prepare date
    today=get_date_from_string(cur_date, "%Y-%m-%d")
    seven_days = timedelta(days=365)
    last7_date=today-seven_days
    

    # Get Values
    query=(db.daily_statistics.statistic_date>=last7_date)&(db.daily_statistics.statistic_date<=today)&(db.daily_statistics.station==db.station.id)&(db.station.code==code)
    if check_is_mobile():
        return _get_station_range_mobile(query,ca)
    else:
        return _get_station_range(query,ca)

def rest_quality(code=None,type=None):
    # Data
    data={}
    if code is None:
        return data
    if type is None:
        type='current'
        
    if type=='current':
        return rest_station_last(code,True)
    elif type=='seven':
        return rest_station_seven(code,True)
    elif type=='month':
        return rest_station_month(code,True)
    elif type=='year':
        return rest_station_year(code,True)
    else:
        return data
    

def rest_station_qa_get(code=None):
    data={}   
    if code is None:
        return data
    # Get station
    station=get_station_by_code(code)
    
    # Initialize configuration
    cfg=Configure()
    cur_date = cfg.get('current_date')
    if cur_date is None:
        return data
    # Prepare date
    today=get_date_from_string(cur_date, "%Y-%m-%d")

    # Get Values
    query=(db.daily_statistics.statistic_date==today)&(db.daily_statistics.station==station.id)
    rows=db(query).select(db.daily_statistics.element,db.daily_statistics.statistic_date,db.daily_statistics.value,orderby="daily_statistics.element ASC")
    
    for row in rows:
        if row.element in QUALITY_ELEMENTS:
            data[row.element]=row.value 
    data['level']=calculate_ca(data)
    
    return data