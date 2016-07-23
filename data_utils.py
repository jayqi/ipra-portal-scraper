import json
import pandas as pd
import sys

def summarize_scrape(filename):

    print('Reading '+filename+'...')
    with open(filename) as datafile:
        data = json.load(datafile)

    print('Scraped time:', data['scraped_date_time'])

    print('Number of records:',len(data['records']))
    indent = '    '
    for recordno, recorddata in sorted(data['records'].items()):
        print(recordno)
        print(indent,'Post Date:',recorddata['post_date_time'])
        print(indent,'Incident Date:',recorddata['incident_date_time'])
        print(indent,'IPRA Notification Date:',recorddata['ipra_notification_date'])
        print(indent,'Subjects:',recorddata['subjects'])
        print(indent,'Notes:',recorddata['notes'])
        print(indent,'Number of Documents:',len(recorddata['documents']))
        print(indent,'Number of Audio:',len(recorddata['audio']))
        print(indent,'Number of Videos:',len(recorddata['video']))


def compare_scrapes(oldfile,newfile):

    # Read files

    with open(oldfile) as f1:
        old_data = json.load(f1)
    print('File 1:',oldfile,'::',old_data['scraped_date_time'])

    with open(newfile) as f2:
        new_data = json.load(f2)
        print('File 2:',newfile,'::',new_data['scraped_date_time'])

    # Identify new and removed record numbers

    new_records = sorted(list(
        set(new_data['records'].keys()) - set(old_data['records'].keys())
        ))
    print(len(new_records),'new records:',new_records)

    removed_records = sorted(list(
        set(old_data['records'].keys()) - set(new_data['records'].keys())
        ))
    print(len(removed_records),'removed records:',removed_records)

    # Iterate through overlapping records and record new or removed files

    new_files = {}
    removed_files = {}

    for recordno in list(
        set(new_data['records'].keys()) & set(old_data['records'].keys())
        ):
        # Need to work on.
        pass




###################################
######### Write CSV files #########
###################################

def json_to_incidents_csv(filename,outfilename='incidents_summary.csv'):
    """Reads in scraped json file and writes CSV table of summarizing incidents.
    """

    # Read file
    with open(filename) as datafile:
        data = json.load(datafile)

    # Create list of lists of data we want in csv
    rowlist = [['COMPLAINT_NUMBER',
                'POST_DATETIME',
                'INCIDENT_TYPE',
                'INCIDENT_DATETIME',
                'IPRA_NOTIF_DATE',
                'SUBJECTS_COUNT',
                'VIDEO_COUNT',
                'AUDIO_COUNT',
                'DOCUMENT_COUNT',
                'NOTES'
               ]]
    for recordno in sorted(data['records'].keys()):
        entry = data['records'][recordno]
        rowlist.append([
                recordno,
                entry['post_date_time'],
                entry['incident_type'],
                entry['incident_date_time'],
                entry['ipra_notification_date'],
                len(entry['subjects']),
                len(entry['video']),
                len(entry['audio']),
                len(entry['documents']),
                entry['notes'] if len(entry['notes']) > 0 else None
            ])

    # Use pandas to write csv file
    print('Writing to',outfilename)
    df = pd.DataFrame(rowlist[1:],columns=rowlist[0])
    df.to_csv(outfilename,index=False)
    print('... Done.')

def json_to_media_csv(filename,outfilename='media_files.csv'):
    """Reads in scraped json file and writes CSV table of media files
    """

    # Read file
    with open(filename) as datafile:
        data = json.load(datafile)

    # Create list of lists of data we want in csv
    rowlist = [['COMPLAINT_NUMBER', 'MEDIA_FILE_TYPE', 'IPRA_PORTAL_LABEL', 'IPRA_URL']]
    media_dict = {'documents' : 'DOCUMENT', 'audio' : 'AUDIO', 'video' : 'VIDEO'}
    for recordno in sorted(data['records'].keys()):
        for mediatype in ['video','audio','documents']:
            for entry in data['records'][recordno][mediatype]:
                rowlist.append([
                    recordno, media_dict[mediatype],entry['description'],entry['url']
                    ])

    # Use pandas to write csv file
    print('Writing to',outfilename)
    df = pd.DataFrame(rowlist[1:],columns=rowlist[0])
    df.to_csv(outfilename,index=False)
    print('... Done.')

def json_to_subject_csv(filename,outfilename='subjects.csv'):
    """Reads in scraped json file and writes CSV table of subjects in cases
    """

    # Read file
    with open(filename) as datafile:
        data = json.load(datafile)

    # Create list of lists of data we want in csv
    rowlist = [['COMPLAINT_NUMBER', 'INCIDENT_TYPE', 'INCIDENT_DATETIME', 'SUBJECT_NAME']]
    for recordno in sorted(data['records'].keys()):
        entry = data['records'][recordno]
        for person in entry['subjects']:
                rowlist.append([
                    recordno, entry['incident_type'],entry['incident_date_time'],person
                    ])

    # Use pandas to write csv file
    print('Writing to',outfilename)
    df = pd.DataFrame(rowlist[1:],columns=rowlist[0])
    df.to_csv(outfilename,index=False)
    print('... Done.')





if __name__ == '__main__':

    if len(sys.argv) > 2:
        if sys.argv[1] == "summarize":
            summarize_scrape(sys.argv[2])
        elif sys.argv[1] == "compare":
            compare_scrapes(sys.argv[2],sys.argv[3])
        elif sys.argv[1] == "writecsv":
            print('Reading',sys.argv[2])
            json_to_incidents_csv(sys.argv[2])
            json_to_media_csv(sys.argv[2])
            json_to_subject_csv(sys.argv[2])
    else:
        pass
