"""
Read from a CSV file data already determined for various cars and tracks.
Also functions to create and update that data.
End user program references this data when scanning user's car and track files.
"""

import csv
import os

from data.rFactoryConfig import rF2root, CarDatafilesFolder, \
    TrackDatafilesFolder, dataFilesExtension, markerfileExtension
from data.utils import getListOfFiles, readFile, writeFile, getTags

from data.LatLong2Addr import google_address, country_to_continent


class Cached_data:
    cache = []

    def __init__(self, cache_filename, tags):
        self.cache_filename = cache_filename
        self.cache_tags = tags
        if 'DB file ID' in tags:
            self.cache_tags.remove('DB file ID')  # Remove to move to col 1
            # Move to the end because it's verbose
            self.cache_tags.remove('Desc')
        self.cache_tags = ['DB file ID'] + \
            self.cache_tags + ['strippedName', 'Desc']

    def load(self):
        """ Load the cached data CSV """
        self.cache = []
        if os.path.isfile(self.cache_filename):
            with open(self.cache_filename, mode='r') as csv_file:
                for row in csv.DictReader(csv_file):
                    row.pop('xDate', None)  # Remove Date
                    self.cache.append(row)
                pass
        else:
            self.cache = []

    def set_value(self, id, key, value):
        """ Set a value in one row of the dict """
        if value == '':
            return
        if key in self.cache_tags:
            for row in self.cache:
                if row['DB file ID'] == id:
                    if row[key] == '':
                        row[key] = value
                    return
            # New entry
            self.__new_entry(id)
            # Newly appended so it will be the last
            self.cache[-1][key] = value

    def __new_entry(self, id):
        row = {}
        for tag in self.cache_tags:
            row[tag] = ''
        row['DB file ID'] = id
        self.cache.append(row)

    def delete_entry(self, id):
        """ Delete one row of the dict """
        for i, row in enumerate(self.cache):
            if row['DB file ID'] == id:
                del self.cache[i]
                break

    def get_values(self, id):
        """
        Return the row for id if it is present
        """
        for row in self.cache:
            if row['DB file ID'] == id:
                return row
        # No such entry
        return dict()

    def write(self):
        """
        Write the spreadsheet
        """
        with open(self.cache_filename, mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.cache_tags)
            writer.writeheader()
            writer.writerows(self.cache)
