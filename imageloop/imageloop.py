import telepot
import urllib
import json
import time
import os

from clarifai.client import ClarifaiApi
from pprint import pprint

clarifai_api = ClarifaiApi()  

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

if TELEGRAM_TOKEN is None:
  print 'Remember to set the following enviroment variables: TELEGRAM_TOKEN, CLARIFAI_APP_SECRET and CLARIFAI_APP_ID'

bot = telepot.Bot(TELEGRAM_TOKEN)

maxSteps = 7;

def handle(msg):
    
    #pprint(msg)

    global maxSteps, TELEGRAM_TOKEN

    userID = msg['chat']['id']
    print 'ImageLoop START for user ' + str(userID) + '\n'

    if 'photo' in msg:
      
      fileInfo = bot.getFile(msg['photo'][-1]['file_id'])
      imageUrl = 'https://api.telegram.org/file/bot'+TELEGRAM_TOKEN+'/'+fileInfo['file_path']
      lasttags = None
      
      step = 0

      while True:

        print 'Step ' + str(step+1)
        print 'Getting tags      ',

        result = clarifai_api.tag_image_urls(imageUrl)

        try:
          tags = result['results'][0]['result']['tag']['classes'][0:4]
        except KeyError:
          break

        tags = ' '.join(tags)
        print tags

        if lasttags == tags:
          print '********* Loop detected *********'
          break
        else:
          lasttags = tags

        bot.sendMessage(userID, tags)

        tags = urllib.quote_plus(tags)


        searchUrl = 'https://duckduckgo.com/i.js?q=' + tags
        print 'Search URL        ' + searchUrl
        print 'Retrieving image  ',
        searchJSON = urllib.urlopen(searchUrl).read()
        search = json.loads(searchJSON)

        try:
          imageUrl = search['results'][0]['image']
        except KeyError:
          break
        
        print imageUrl

        f = urllib.urlopen(imageUrl)
        print 'Uploading image'
        bot.sendPhoto(userID, ('dummy.jpg', f))

        step+=1

        if step >= maxSteps:
          break

        print 

    print '\nImageLoop END for user ' + str(userID) + '\n\n'


bot.message_loop(handle)

while 1:
    time.sleep(10)