import requests
import re
from bs4 import BeautifulSoup
import datetime as dt
import json

# Compiled regex
re_newline = re.compile(r'\n')
re_tab = re.compile(r'\t')
re_notefind = re.compile(r"Note:")
re_notecapture = re.compile(r"Note:\s*(.*)")
re_juvnotefind = re.compile(r"Pursuant")
re_subjectfind = re.compile(r"Subject:")
re_subjectcapture = re.compile(r"Subject:\s*(.*)")
re_subjectsmultfind = re.compile(r"Subjects:")
re_fileid = re.compile(r"'#modal(\d+)'")
re_mediasrc = re.compile(r"var\s+src\s*=\s*'([^']+)'")

def scrape_ipra():

    data = {'records' : {},
       'scraped_date_time' : dt.datetime.now().isoformat()}

    # Get index page table
    print('Scraping index table...')
    url = "http://portal.iprachicago.org/wp-content/themes/ipra/DynamicSearch.php"
    headers = {
        'user-agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }
    r = requests.get(url, headers=headers)
    print("Status Code: ", r.status_code)
    content = r.json()['caseSearch']['items']
    content = re_newline.sub('',content)
    content = re_tab.sub('',content)
    soup = BeautifulSoup(content,'html.parser')
    table = soup.find('table', attrs={'id':'ipra-case-search-data-table'})
    rows = table.find_all('tr')

    # Scrape rows in index table
    for row in rows[1:]:

        th = row.find('th')
        logno = th.find('a').string.strip()

        record = {}
        record['record_url'] = th.find('a').get('href').strip()

        tdlist = row.find_all('td')

        record['incident_type'] = tdlist[0].string.strip()
        record['ipra_notification_date'] = tdlist[1].string.strip()
        record['incident_date_time'] = tdlist[2].string.strip()

        data['records'][logno] = record

    # Iterate through each record's page
    for logno, record in data['records'].items():

        print('Scraping ' + logno + '...')

        # Scrape record page with beautiful soup
        r = requests.get(record['record_url'], headers=headers)
        print("Status Code: ", r.status_code)
        soup = BeautifulSoup(r.content,'html.parser')

        # Convenient sections
        content = soup.find(id='main')
        entry = content.find('div',attrs={'class' : 'entry-content'})

        # Get date and time posted on IPRA portal
        record['post_date_time'] = content.find('time',attrs={'class' : 'entry-date published'}).get("datetime")

        # Get notes
        record['notes'] = []
        # If "Note:" exists
        note = entry.find('p',string=re_notefind)
        if note:
            record['notes'].append(re_notecapture.search(note.string).groups()[0].strip())
        # If Illinois Juvenile Court Act note exists
        for p in entry.find_all('p'):
            if re_juvnotefind.search(p.text):
                record['notes'].append(p.text.strip())

        # Get single Subject if exists
        subject = entry.find('p',string=re_subjectfind)
        if subject:
            record['subjects'] = [re_subjectcapture.search(subject.string).groups()[0].strip()]

        # Get multiple Subjects if exists
        if entry.find('p',string=re_subjectsmultfind):
            record['subjects'] = [li.string.strip() for li in entry.ul.find_all('li')]

        # Scrape media
        media = entry.find_all('div',attrs={'class' : 'col-sm-4'})

        record['documents'] = []
        record['audio'] = []
        record['video'] = []

        for elem in media:
            iconclasses = elem.find('span',attrs={'class':'fa'}).get('class')

            # If document
            if 'fa-file-pdf-o' in iconclasses:
                record['documents'].append(
                    {'description' : elem.a.text.strip(),
                    'url' : elem.a.get('href').strip()}
                    )

            # If video
            elif 'fa-file-video-o' in iconclasses:
                descript = elem.find('div',attrs={'class':'large-icon'}).text.strip()

                js = elem.find('script').text
                js = re_newline.sub('',js)
                js = re_tab.sub('',js)

                file_id = re_fileid.search(js).groups()[0]

                url = re_mediasrc.search(js).groups()[0]

                record['video'].append({
                        'description' : descript,
                        'file_id' : file_id,
                        'url' : url})

            # If audio
            elif 'fa-file-sound-o' in iconclasses:
                descript = elem.find('div',attrs={'class':'large-icon'}).text.strip()

                js = elem.find('script').text
                js = re_newline.sub('',js)
                js = re_tab.sub('',js)

                file_id = re_fileid.search(js).groups()[0]

                url = re_mediasrc.search(js).groups()[0]

                record['audio'].append({
                        'description' : descript,
                        'file_id' : file_id,
                        'url' : url})

    return data

if __name__ == "__main__":
    data = scrape_ipra()

    with open(data['scraped_date_time']+'.json','w') as outfile:
        json.dump(data,outfile)
