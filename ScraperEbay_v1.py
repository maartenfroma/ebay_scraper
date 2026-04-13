from dotenv import load_dotenv
import os
import csv
import time
import requests

class Scraper_EBAY:

    scraper_count=0

    def __init__(self, marketplace_id="EBAY_US",query="laptop", pages=3, output_file=None):
        load_dotenv(override=True)
        self.__client_id = os.getenv("EBAY_CLIENT_ID")      # App ID
        self.__client_secret = os.getenv("EBAY_CLIENT_SECRET")  # Cert ID / Client Secret

        self.__token_url="https://api.ebay.com/identity/v1/oauth2/token"
        self.__search_url="https://api.ebay.com/buy/browse/v1/item_summary/search"
        self.__scope = "https://api.ebay.com/oauth/api_scope"


        self.marketplace_id=marketplace_id
        self.query=query
        self.pages=pages

        #If output file is passed save it in folder files
        if output_file is None:
            raise ValueError("No output file given")
        else:
            # Always save inside /files/
            base = os.path.dirname(os.path.abspath(__file__))
            files_dir = os.path.join(base, "files")
            os.makedirs(files_dir, exist_ok=True)
            self.output_file=os.path.join(files_dir, output_file)

    #---------------------------------------------------------------------------------------------------------------
    #Token
    #-------------------------------------------------------------------------------------------------------------------
    def get_app_token(self):
        #Check if client id and secret are set as environment variables
        if not self.__client_id or not self.__client_secret:
            raise RuntimeError("Set client id and secret in environment variables")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
        "grant_type": "client_credentials",
        "scope": self.__scope,}

        # HTTP Basic auth met client_id:client_secret
        resp=requests.post(self.__token_url,headers=headers, data=data, auth=(self.__client_id, self.__client_secret), timeout=30)
        resp.raise_for_status()
        resp_json=resp.json()

        return resp_json["access_token"], resp_json.get("expires_in", 0)
    #----------------------------------------------------------------------------------------------------------------------------
    #Search
    #------------------------------------------------------------------------------------------------------------------------

    def search_items(self, token, limit=50, offset=0 ):

        headers = {
            "Authorization": f"Bearer {token}",
            "X-EBAY-C-MARKETPLACE-ID": self.marketplace_id,  # which marketplace
            "Accept": "application/json",
        }
        params = {
            "q": self.query,
            "limit": limit,
            "offset": offset,
        }

        resp=requests.get(self.__search_url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()

        return resp.json()

    #-------------------------------------------------------------------------------------------------------------------
    #Extract data from json file and return a list of rows
    #--------------------------------------------------------------------------------------------------------------------
    def extract_rows(self, search_json):
        rows=[]

        for it in search_json.get("itemSummaries", []):
            price=it.get("price") or {}
            seller=it.get("seller") or {}
            rows.append({"title": it.get("title"),
                         "brand": it.get("brand"),
                         "price": price.get("value"),
                         "currency": price.get("currency"),
                         "itemWebUrl": it.get("itemWebUrl"),
                         "sellerUsername": seller.get("username"),
                         "itemId": it.get("itemId"),
                         })
        return rows
    #-------------------------------------------------------------------------------------------------------------------
    #Create csv file
    #--------------------------------------------------------------------------------------------------------------------
    # def scrape_to_csv(self, page_size=50):
    #     token, _= self.get_app_token()
    #     all_rows=[]
    #     offset=0
    #
    #     for p in range(self.pages):
    #         print(f"page {p + 1} is loading...")
    #         data=self.search_items(token,limit=page_size, offset=offset)
    #         rows=self.extract_rows(data)
    #
    #         if not rows:
    #             print(f"No results at page {p + 1}")
    #             break
    #
    #         all_rows.extend(rows)
    #         offset+=page_size
    #
    #         time.sleep(1.0)

    def save_csv(self, rows):

        fieldnames = ["title", "brand", "price", "currency", "itemWebUrl", "sellerUsername", "itemId"]
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            w=csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

        print(f"Saved {len(rows)} in output file {self.output_file}")

        return self.output_file




    #-------------------------------------------------------------------------------------------------------------------
    #Return string object Scraper_EBAY class
    #-------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return str([self.marketplace_id, self.query, self.pages, self.output_file])