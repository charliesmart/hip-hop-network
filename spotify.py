import requests
import csv
import json
import time
import sys

reload(sys)

sys.setdefaultencoding('utf-8')

#Where our final data is stored. Will eventually be a dict of dicts
relationships = []

artist_list = []

#Keywords to check for duplicate albums
duplicate_keys = ['deluxe', 'remix', 'clean', 'edited']

#Keywords to check for unlisted featured artists
featured_keys = ['feat', 'featuring']

track_id = 1

def sanitize(string):
    return string.lower().replace(" ", "").replace("'", "").replace("$", "s").replace(".", "")

def check_relationships(f, t):
    string = sanitize(f) + sanitize(t)
    if string in relationships.keys():
        return True
    else:
        return False

def is_duplicate(name):
    if (name.lower() in albums) or (any(x in name.lower() for x in duplicate_keys)):
        return True
    else:
        return False

#Read the CSV with artist URIs and store it in a variable
csv_file = csv.reader(open('artists.csv'))

for row in csv_file:
    artist_list.append(row[0])

#Loop through the CSV and parse it into the artists dictionary
for current_artist in artist_list:

    search_name = current_artist.replace(" ", "+")

    artist_search = requests.get("https://api.spotify.com/v1/search?q=" + search_name + "&type=artist&market=US&limit=1").text

    search = json.loads(artist_search)

    if search['artists']['items']:

        uri = search['artists']['items'][0]['uri'][15:]

        #Get all the albums for each artist
        albums = requests.get('https://api.spotify.com/v1/artists/' + uri + '/albums')

        #Save the albums as a JSON object
        albums_parsed = json.loads(albums.text)

        #Keep a list of albums for the artist as we loop through them to avoid duplicates (e.g. delux and clean versions)
        albums = []

        #Loop through the albums we got for this artist
        for album in albums_parsed['items']:

            #print bcolors.WARNING + album['name'] + bcolors.ENDC

            if is_duplicate(album['name']):
                pass
            else:
                #Add our album to the list so we can keep track of it
                albums.append(album['name'].lower())

                #Get the URI so we can check the album's songs
                album_uri = album['uri']

                #Get only the characters of the URI that we need
                album_uri_part = album_uri[14:]

                #Get the tracks for the album
                tracks = requests.get('https://api.spotify.com/v1/albums/' + album_uri_part + '/tracks')
                tracks_parsed = json.loads(tracks.text)

                #Loop through the tracks
                for track in tracks_parsed['items']:

                    print track['name']

                    #Keep a list of the current track
                    track_artists = []

                    #Loop through the artists on the track and add them to the list, lowercase and minus special characters
                    for artist in track['artists']:
                        track_artists.append(artist['name'])

                    #Remove the album artist from the list, sicne we're only interested in who they're working with
                    if current_artist in track_artists:
                            track_artists.remove(current_artist)

                    print track_artists
                    #Loop through the list of featured artists that we just made
                    for featured in track_artists:
                        if featured in artist_list:
                            relationships.append({'Source': current_artist, 'Target': featured, 'Type': 'Undirected'})
                        time.sleep(0.03)


csv_keys = relationships[0].keys()

with open('edges.csv', 'wb') as output_file:
    writer = csv.DictWriter(output_file, csv_keys)
    writer.writeheader()
    writer.writerows(relationships)
