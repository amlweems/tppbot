#!/usr/bin/env python
# -*- coding: utf-8 -*-

from StringIO import StringIO
from PIL import Image
from faker import Factory
import requests
import random
import time
import re

faker = Factory.create()

class BlockedException(Exception): pass
class PhraseException(Exception): pass
class FastException(Exception): pass

def generate_data():
    username = re.sub("\W", "#", faker.user_name()) + "####"
    username = faker.numerify(username)
    password = username[::-1]
    data = {
        "utf8":                       u"✓",
        "authenticity_token":         "",
        "user_facebook_uid":          "",
        "user_facebook_access_token": "",
        "user_name":                  "",
        "show_facebook_status":       "true",
        "user[login]":                username,
        "user[password]":             password,
        "date[month]":                random.randint(1,12),
        "date[day]":                  random.randint(1,28),
        "date[year]":                 random.randint(1950, 2000),
        "user[email]":                "{}@trebuchet.me".format(username),
        "recaptcha_challenge_field":  "",
        "recaptcha_response_field":   ""
    }
    return data

def register(challenge, response):
    url = "http://www.twitch.tv/signup"
    session = requests.session()
    resp = session.get(url)

    if "blacklist_message" in resp.content:
        raise BlockedException("Twitch has issued an IP ban")
    
    token = re.findall('name="authenticity_token" type="hidden" value="([^"]+)"', resp.content)[0]
    
    data = generate_data()
    data["recaptcha_challenge_field"] = challenge
    data["recaptcha_response_field"] = response
    data["authenticity_token"] = token

    headers = {"X-Requested-With": "XMLHttpRequest", "User-Agent": faker.user_agent()}

    resp = session.post(url, headers=headers, data=data)
    if resp.status_code == 200:
        print challenge
        username = data["user[login]"]
        password = data["user[password]"]
        try:
            token = oauth(username, password)
        except:
            token = "oauth:"
        open('accounts.txt','a').write("{0}::{1}\n".format(username, token))
    else:
        if "phrase" in resp.content:
            raise PhraseException("Incorrect captcha: {}".format(challenge))
        elif "fast" in resp.content:
            raise FastException("You're registering accounts too quickly")
        else:
            raise Exception("Error from server: {}".format(resp.content))

def oauth(username, password):
    url = "https://api.twitch.tv/kraken/oauth2/authorize"
    session = requests.session()
    data = {
        "response_type": "token",
        "client_id":     "q6batx0epp608isickayubi39itsckt", 
        "redirect_uri":  "http://twitchapps.com/tmi/",
        "scope":         "chat_login"
    }
    resp = session.get(url, params=data)
    token = re.findall('name="authenticity_token" type="hidden" value="([^"]+)"', resp.content)[0]

    url = "https://api.twitch.tv/kraken/oauth2/login"
    data = {
        "authenticity_token": token,
        "login_type":         "login",
        "response_type":      "token",
        "client_id":          "q6batx0epp608isickayubi39itsckt",
        "redirect_uri":       "http://twitchapps.com/tmi/",
        "scope":              "chat_login",
        "user[login]":        username,
        "user[password]":     password
    }
    resp = session.post(url, data=data)
    if "api.twitch.tv" in resp.url:
        token = re.findall('name="authenticity_token" type="hidden" value="([^"]+)"', resp.content)[0]

        url = "https://api.twitch.tv/kraken/oauth2/allow"
        data["authenticity_token"] = token
        del data["user[login]"]
        del data["user[password]"]
        resp = session.post(url, data=data)

    token = re.findall("access_token=([^&]+)", resp.url)[0]
    return "oauth:"+token

def main():
    f = open('captcha.txt', 'r')
    line = f.readline().rstrip()
    dry = False
    while True:
        while line == "":
            if not dry: print("Please insert more tokens!")
            dry = True
            time.sleep(random.randint(0,20))
            line = f.readline().rstrip()
        dry = False
        try:
            register(*line.split("::"))
            time.sleep(45*5)
        except BlockedException as err:
            print(err)
            break
        except FastException as err:
            print(err)
            time.sleep(random.randint(60,120))
        except PhraseException as err:
            print(err)
        except Exception as err:
            print(err)
        line = f.readline().rstrip()

if __name__ == "__main__":
    main()