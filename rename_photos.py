from datetime import datetime, timedelta
from time import time
from unittest import result
from PIL import Image
from PIL.ExifTags import TAGS
import pytz
import os

utc=pytz.UTC


def assembly_file_path(dir, file_name):
    return '%s/%s' % (dir, file_name)

def get_dir_list_of_files(dir):
    files = []
    for ent in os.listdir(dir):
        path = assembly_file_path(dir, ent)
        if (os.path.isfile(path)):
            files.append(ent)
    return files

def get_sorted_by_time_photos_list(photos_dir):

    photo_files = get_dir_list_of_files(photos_dir)    

    result_dict = {}
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

        if (photo_date not in result_dict):
            result_dict[photo_date] = {}
        
        if (photo_time in result_dict[photo_date]):
            print('Warning: photo with same date and time!')
        result_dict[photo_date][photo_time] = photo_name
    
    result = []
    sorted_dates = sorted(result_dict.keys())
    for date_index in range(len(sorted_dates)):
        date = sorted_dates[date_index]
        date_times = result_dict[date]
        sorted_times = sorted(date_times.keys())
        for time_index in range(len(sorted_times)):
            time = sorted_times[time_index]
            name = date_times[time]
            result.append(name)
    return result


photos_list = get_sorted_by_time_photos_list('./dph')

for name in photos_list:
    print(name)