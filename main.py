from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from StringIO import StringIO
# import logging, httplib

# httplib.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger('requests.packages.urllib3')
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


app = Flask(__name__)
app.debug = True


@app.route('/', methods=['GET'])
def main_page():
  return render_template('template.html', data=get_emoji())


@app.route('/', methods=['POST'])
def import_emoji():
  print request.form    #TODO: always empty. Why?
  return 'Done!'


### Slack scraping functions ###
def login(team, email, passwd):
  url = 'https://{}.slack.com'.format(team)

  r1 = do_request(requests.get, url)
  crumb = get_crumb(r1.text)

  r2 = do_request(
    requests.post, url, cookies=r1.cookies, allow_redirects=False,
    data={'signin': 1, 'crumb': crumb, 'email': email, 'password': passwd},
  )
  return r2.cookies


def upload_emoji(name, image_url, team, cookies):
  url = 'https://{}.slack.com/customize/emoji'.format(team)

  crumb_req = do_request(requests.get, url, cookies=cookies)
  crumb = get_crumb(crumb_req.text)

  img_req = do_request(requests.get, image_url)

  do_request(
    requests.post, url, cookies=cookies, allow_redirects=False,
    data={'add': 1, 'crumb': crumb, 'name': name, 'mode': 'data'},
    files={'img': StringIO(img_req.content)}
  )


### slack-emojinator scrapers ###
def get_emoji():
  req = do_request(requests.get, 'https://slackmojis.com/')
  soup = BeautifulSoup(req.text, 'html.parser')
  return {
    group.find('div', class_='title').string.strip(): {
      emoji.find('div', class_='name').string.strip(): emoji.find('a')['href'].strip()
      for emoji in group.find('ul', class_='emojis').find_all('li', recursive=False)
    }
    for group in soup.find_all('li', class_='group')
  }


### Helpers ###
def get_crumb(text):
  return BeautifulSoup(text, 'html.parser').find('input', attrs={'name': 'crumb'})['value']


def do_request(method, *args, **kwargs):
  resp = method(*args, **kwargs)
  resp.raise_for_status()
  return resp

if __name__ == '__main__':
  app.run(port=50001)
  # cookies = login('open5e', EMAIL, PASSWORD)
  # upload_emoji(
  #   'test',
  #   'http://emojis.slackmojis.com/emojis/images/1450464805/195/google.png?1450464805',
  #   'open5e',
  #   cookies,
  # )
  #pprint.pprint(get_emoji())
