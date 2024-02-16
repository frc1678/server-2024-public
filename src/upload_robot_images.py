import os
from typing import Callable, List
import webbrowser
import http.server
import json
import asyncio
import base64
import requests
import glob
import csv
import logging

log = logging.getLogger(__name__)

from utils import TBA_EVENT_KEY

# Create OAUTH2 application at https://api.imgur.com/oauth2/addclient
# Make sure to set the "Callback URL" to "http://localhost:8678"

# Imgur application client id
with open("data/api_keys/imgur_client_id.txt", "r") as f:
    client_id = f.read().strip()

# Imgur application client secret
with open("data/api_keys/imgur_client_secret.txt", "r") as f:
    client_secret = f.read().strip()

if not client_id:
    log.error("No client ID found in imgur_client_id.txt")
    exit(1)

if not client_secret:
    log.error("No client secret found in imgur_client_secret.txt")
    exit(1)

api_creds = {"client_id": client_id, "client_secret": client_secret}


class ImgurClient:
    """
    Class to interact with the imgur API
    """

    base_imgur_api_url = "https://api.imgur.com/3"

    access_token: str
    account_id: str
    account_username: str
    expires_in: str
    refresh_token: str
    token_type: str
    client_id: str
    client_secret: str

    @staticmethod
    def get_auth_url(client_id):
        """
        Generates the URL to login to imgur
        """
        return f"https://api.imgur.com/oauth2/authorize?client_id={client_id}&response_type=token"

    def __init__(
        self,
        access_token: str,
        account_id: str,
        account_username: str,
        expires_in: str,
        refresh_token: str,
        token_type: str,
        client_id: str,
        client_secret: str,
    ):
        self.access_token = access_token
        self.account_id = account_id
        self.account_username = account_username
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.client_id = client_id
        self.client_secret = client_secret

    def upload_img_b64(self, data: str, title: str):
        """
        Uploads an image to imgur using the base64 encoded image data
        """
        return self.__base_post_request(
            "upload",
            {
                "image": data,
                "title": title,
                "type": "base64",
                "name": f"{title}.jpg",
                "description": title,
            },
        ).json()

    def upload_img_filename(self, filename: str, title: str):
        """
        Uploads an image to imgur using the filename
        """
        return self.upload_img_b64(load_img_to_b64(filename), title)

    def list_images(self, page: int = 0):
        """
        Lists the images in the account for a specific page. Defaults to page 0
        """
        return self.__base_get_request(f"account/{self.account_username}/images/{page}").json()

    def list_all_images(self, filtered: bool = False) -> List[dict]:
        """
        Pages thru account and returns all images on all pages.
        Filtered is a boolean to filter out images that are not from the current event
        """
        images = []
        image_count = self.image_count()
        page_count = 0
        while image_count > 0:
            image_page = self.list_images(page_count)
            images.extend(image_page["data"])
            page_count += 1
            image_count -= len(image_page["data"])

        if filtered:
            images = list(filter(filter_title, images))
            return images
        else:
            return images

    def image_count(self) -> int:
        """
        Returns the number of images in the account
        """
        return self.__base_get_request(f"account/{self.account_username}/images/count").json()[
            "data"
        ]

    def __base_get_request(self, path: str):
        """
        Base get request to the imgur API
        """
        return requests.get(
            f"{self.base_imgur_api_url}/{path}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

    def __base_post_request(self, path: str, data: dict):
        """
        Base post request to the imgur API
        """
        return requests.post(
            f"{self.base_imgur_api_url}/{path}",
            data=data,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )


def load_img_to_b64(img_path: str) -> str:
    """
    Loads an image to base64 encoded string by path
    """
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_paths() -> List[str]:
    """
    Gets all images from the devices directory
    """
    return glob.glob("data/devices/*/*.jpg", recursive=True)


def login(cb: Callable[[dict], None]):
    """
    Function to login to imgur and get authorization credentials.
    Callback is passed an object with the following attributes:
    access_token, account_id, account_username, expires_in, refresh_token, token_type
    """
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
        """
        Class to handle the http requests for the imgur authentication flow
        """

        def _set_response(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def do_GET(self):
            """
            Handles the GET requests that redirect from the imgur authentication flow
            """
            # print(f"Address: {(self.requestline)}")

            self._set_response()

            # Imgur sends the credentials in the url as a hash fragment so it i so it is never sent to the server
            # To get past that you can return javascript that then sends the credentials to the server in a post request
            # It uses regex to get the credentials from the url
            # It then uses fetch to post the credentials to the server at the same url
            message = """
            <script>
            const urlregex = /(?:(\w*)=(\w*))+/gm;
    const str = (new URL(window.location
        .href)).hash;
    let m;
    const out = {};
    while ((m = urlregex.exec(str)) !==
        null) {
        if (m.index === urlregex
            .lastIndex) {
            urlregex.lastIndex++;
        }


        out[m[1]] = m[2];
    }
    console.log(out);
    fetch("/", {
            method: 'POST',
            body: JSON.stringify(out)
        }).then(v => document.body
            .appendChild(document
                .createTextNode(
                    "Success, Probably")))
        .catch(e => document.body
            .appendChild(
                document.createTextNode(
                    "Error")))</script>
    """
            self.wfile.write(bytes(message, "utf8"))

        # Handles the incoming post request from the imgur authentication flow
        def do_POST(self):
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            self._set_response()
            self.wfile.write("POST request for {}".format(self.path).encode("utf-8"))
            asyncio.get_event_loop().run_in_executor(None, cb, data)
            self.server.shutdown()
            self.server.server_close()
            # cb(data)
            return

        def log_message(self, format, *args):
            return

    # Start the server
    httpd = http.server.HTTPServer(
        server_address=("", 8678), RequestHandlerClass=MyHttpRequestHandler
    )
    # Open the auth url in the browser
    webbrowser.open(ImgurClient.get_auth_url(api_creds["client_id"]))

    httpd.serve_forever(5)

    return future


def filter_title(image: dict) -> bool:
    """
    Only returns images that are from the current event
    """
    if image["title"] == None:
        return False
    return image["title"].startswith(TBA_EVENT_KEY)


def run(creds):
    """
    Main function to run the CLI
    """
    imgur = ImgurClient(**{**creds, **api_creds})

    while True:
        prompt = input(
            "\nPress 1 for uploading image. \nPress 2 for listing images. \nPress 3 for exporting the images to a csv. \n(1, 2, or 3): "
        ).strip()
        images = imgur.list_all_images(filtered=True)
        if prompt == "1":
            image_titles = [image["title"] for image in images]
            # Uploads each image in the devices directory
            for img_path in get_image_paths():
                # Prefix image name with event key
                title = TBA_EVENT_KEY + "_" + (os.path.basename(img_path).split(".")[0])
                # Check if the image is already on imgur and skip if it is
                if title in image_titles:
                    continue
                # Upload image to imgur
                resp = imgur.upload_img_filename(img_path, title)
                log_string = f"Response success: {resp['success']}    Title: {title}    Link: {resp['data']['link']}"
                log.info(log_string)
        if prompt == "2":
            # print(images)

            images = list(map(lambda x: f"{x['title']}: {x['link']}", images))
            for image in images:
                log.info(image)

        if prompt == "3":
            teams: dict[str, List[str]] = {}

            for image in images:
                splitted: List[str] = image["title"].split("_")
                team = splitted[1]
                # Take everything after the team number to get the image type
                img_type = "_".join(splitted[2:])
                # print(img_type)
                if team not in teams:
                    teams[team] = []
                # Prioritize the full_robot images over everything else
                if img_type in ["full_robot_1", "full_robot_2"]:
                    teams[team].insert(0, image["link"])
                else:
                    teams[team].append(image["link"])
            # Write everything to images.csv
            with open("data/images.csv", "w", newline="") as csvfile:
                file_writer = csv.writer(csvfile)
                for team in teams:
                    file_writer.writerow([team] + teams[team])


if __name__ == "__main__":

    # Callback function for login flow
    def done(data):
        run(data)

    login(done)
