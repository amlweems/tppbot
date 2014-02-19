import requests
import time
import re

class Captcha:

    def __init__(self, public_key):
        self.public_key = public_key

    def get_challenge(self):
        url = "http://www.google.com/recaptcha/api/challenge"
        data = {"k": self.public_key}
        resp = requests.get(url, params=data)
        challenge = re.findall("challenge : '([^']+)", resp.content)
        if resp.status_code == 200 and len(challenge) == 1:
            return challenge[0]
        else:
            raise Exception("Unable to generate reCAPTCHA token")

    def get_image(self, challenge):
        url = "http://www.google.com/recaptcha/api/image"
        data = {"c": challenge}
        resp = requests.get(url, params=data)
        if resp.status_code == 200:
            return resp.content
        else:
            raise Exception("Unable to fetch reCAPTCHA for token {}".format(challenge))

    def verify(self, private_key, ip_addr, challenge, response):
        url = "http://www.google.com/recaptcha/api/verify"
        data = {"privatekey": private_key,
                "remoteip":   ip_addr, 
                "challenge":  challenge,
                "response":   response}
        resp = requests.get(url, params=data).content.split("\n")
        if len(resp) >= 1:
            return resp[0] == "true"
        else:
            raise Exception("Unknown reponse from server")
