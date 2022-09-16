from datetime import datetime, timedelta
import gpxpy
import gpxpy.gpx
from PIL import Image
# from PIL import ExifTags
from PIL.ExifTags import TAGS
import pytz
import os

utc=pytz.UTC

ALLOW_TIME_DIFF_IN_SECONDS = 60

def assembly_file_path(dir, file_name):
    return '%s/%s' % (dir, file_name)

def get_dir_list_of_files(dir):
    files = []
    for ent in os.listdir(dir):
        path = assembly_file_path(dir, ent)
        if (os.path.isfile(path)):
            files.append(ent)
    return files

def collect_points_coords_by_day(tracks_dir, track_files):
    result = {}
    for file_name in track_files:
        file_path = assembly_file_path(tracks_dir, file_name)
        file = open(file_path, 'r')     
        
        gpx = gpxpy.parse(file)
        for track in gpx.tracks:
            for segment in track.segments:
                point_time = None
                point_date = None
                point_coords = None
                for point in segment.points:                     
                    point_date_and_time = point.time + timedelta(hours = 7)
                    point_date = point_date_and_time.date()
                    point_time = point_date_and_time.time()
                    point_coords = [point.latitude, point.longitude]
                    if (point_date not in result):
                        result[point_date] = {}
                    result[point_date][point_time] = point_coords
        file.close()
    return result

def get_timedelta(time1, time2):
    return timedelta(
        hours=(time1.hour - time2.hour), 
        minutes=(time1.minute - time2.minute),
        seconds=(time1.second - time2.second)) 

def collect_photos_time_by_day(photos_dir, photo_files):
    result = {}
    for file_name in photo_files:
        file_path = assembly_file_path(photos_dir, file_name)
        file = Image.open(file_path)
        exifdata = file.getexif()

        photo_date = None
        photo_time = None
        photo_name = file_name

        for key, val in exifdata.items():
                if key in TAGS:
                    if (TAGS[key] == 'DateTime'):
                        date_and_time = datetime.strptime(val, '%Y:%m:%d %H:%M:%S')
                        date_and_time = utc.localize(date_and_time)
                        photo_date = date_and_time.date()
                        photo_time = date_and_time.time()   
                    

        if (photo_date not in result):
            result[photo_date] = []
        
        photo_info = [photo_name, photo_time]
        result[photo_date].append(photo_info)
    return result


tracks_dir = './tracks'
photos_dir = './photos'

track_files = get_dir_list_of_files(tracks_dir)
photo_files = get_dir_list_of_files(photos_dir)

track_points_by_date = collect_points_coords_by_day(tracks_dir, track_files)
photos_time_by_date = collect_photos_time_by_day(photos_dir, photo_files)


result_gpx = gpxpy.gpx.GPX()


for date in sorted(photos_time_by_date.keys()):
    if (date not in track_points_by_date):
        print("Connot find track for date: %s" % date)
        break
    points = track_points_by_date[date]
    sort_points_times = sorted(points.keys())
    for photo_info in photos_time_by_date[date]:
        photo_name = photo_info[0]
        photo_time = photo_info[1]
        is_find = False
        for i in range(len(sort_points_times)):
            if (i > 0):
                point_time_prev = sort_points_times[i - 1]
                point_time = sort_points_times[i]
                if photo_time < point_time:
                    left_diff = get_timedelta(photo_time, point_time_prev).total_seconds()
                    right_diff = get_timedelta(point_time, photo_time).total_seconds()
                    
                    if (left_diff > ALLOW_TIME_DIFF_IN_SECONDS and right_diff > ALLOW_TIME_DIFF_IN_SECONDS):
                        print('Warning: too big diff', min(left_diff, right_diff))                    
                    res_index = i
                    if (left_diff < right_diff):
                        res_index = i - 1
                    print('Find:', photo_time, photo_name, points[sort_points_times[res_index]])
                    lat = points[sort_points_times[res_index]][0]
                    lon = points[sort_points_times[res_index]][1]
                    result_gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(latitude=lat, longitude=lon, name=photo_name))
                    is_find = True
                    break
        if (not is_find):
            print('Cannot find time point')


output = open('./output.gpx', 'w')
output.write(result_gpx.to_xml(version="1.1"))
output.close()


