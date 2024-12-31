from bs4 import BeautifulSoup
import re
import requests
import urllib.parse

def harris_county_appraisals(address=None, hcad_id=None):
    if hcad_id == None:
        base_url = "https://arcweb.hcad.org/server/rest/services/public/public_query/MapServer/0/query?"

        if address == None:
            address = input("Insert an address from Harris County: ")

        params = {
            "f": "json",
            "where": f"UPPER(address) LIKE '{address}%'",
            "returnGeometry": "false",
            "outFields": "HCAD_NUM, address, owner, OBJECTID"
        }

        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}{query_string}"

        response = requests.get(full_url, verify=False)

        if response.status_code == 200:
            data = response.json()
        else:
            print("Error getting info")

        if data['features'] and len(data['features']) == 1:
            attributes = data['features'][0]['attributes']
            hcad = attributes['HCAD_NUM']
        else:
            print(len(data['features']))
            return None
    else:
        hcad = ((13 - len(str(hcad_id))) * '0') + str(hcad_id)

            
    

    # Define the session to persist cookies across requests
    session = requests.Session()

    # URL for the initial POST request
    url = "https://public.hcad.org/records/SelectRecord.asp"

    # Headers for the request
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://public.hcad.org",
        "Referer": "https://public.hcad.org/records/Real.asp?search=acct",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    # Form data for the POST request
    data = {
        "TaxYear": "2024",
        "searchtype": "strap",
        "searchval": hcad,
    }

    # Cookies for the request
    cookies = {
        "_gid": "GA1.2.1549291931.1734966001",
        "_ga_DH8C4FWZ73": "GS1.1.1734966203.1.1.1734966916.0.0.0",
        "ASPSESSIONIDSWRRBRAS": "NPLJBLHALBPBEIHKELMOOFBO",
        "cf_clearance": "Z_Og1bDuvCwGdHgc.jIBVqHmON2.EG8u4DDDHQDsvKU-1734973496-1.2.1.1",
    }

    # Perform the POST request
    response = session.post(url, headers=headers, data=data, cookies=cookies, allow_redirects=False)

    # Check if the response is a 302 redirect
    if response.status_code == 302:
        redirect_url = response.headers.get("Location")
        # print(f"https://public.hcad.org/records/{redirect_url}")

        # Follow the redirect if needed
        redirect_response = session.get(f"https://public.hcad.org/records/{redirect_url}", headers=headers)
        soup = BeautifulSoup(redirect_response.text, 'html.parser')
        
        links = soup.find_all('a')

        history_links = [
            link.get("href") for link in links 
            if link.get("href") and link.get("href").startswith("HistoryValue.asp?")
        ]

        if history_links[0]:
            appraisal_url = history_links[0]
    else:
        print("Unexpected response:", response.status_code)
        return None

    appraisal_resp = session.get(f"https://public.hcad.org/records/{appraisal_url}", headers=headers)

    if appraisal_resp.status_code == 200:
        appraisal = BeautifulSoup(appraisal_resp.text, 'html.parser')
        years = appraisal.find_all('td')
        values = appraisal.find_all('th')
        
        appraised_years = []
        for year in years:
            if year.text:
                match = re.search(r'\b\d{4}\b', year.text.strip())
                if match:
                    appraised_years.append(year.text)

        appraised_values = []
        for value in values:
            if value.text:
                match = re.search(r'\$?(\d{1,3}(?:,\d{3})*)', value.text.strip())
                if match:
                    appraised_values.append(int(match.group(1).replace(',', '')))

    else:
        print("Error: Failed to get appraisals")
        return None

    # print("Appraised Value History")
    appraisals = []
    for year, value in zip(appraised_years, appraised_values):
        # print(f"{year}: ${value}")
        appraisals.append({year: value})
    return appraisals
        

print(harris_county_appraisals(hcad_id=70570450019))