import re

class getSheetID:
    def __init__(self,url):
        self.url = url
    
    def scraper(self):
        # url = ""
        # #declare reqs, soup
        import requests
        from bs4 import BeautifulSoup
        url = self.url
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
 
        urls = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if 'spreadsheets' in href:
                urls.append(href)

        # Regular expression pattern to match the spreadsheet ID
        pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"

        # Iterate through the URLs and extract the spreadsheet IDs
        spreadsheet_ids = []
        for url in urls:
            match = re.search(pattern, url)
            if match:
                spreadsheet_id = match.group(1)
                spreadsheet_ids.append(spreadsheet_id)

        return spreadsheet_ids

test = getSheetID("https://peddie.bywatersolutions.com/")
print(test.scraper())


