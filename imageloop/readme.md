#ImageLoop

ImageLoop is a tiny Telegram bot to generate Exquisite corpse like narratives, using a photograph as a starting point. 

Using a photograph as a seed, the bot will mutate the image using a two part process:

* First the bot will extract the tags associated with the photograph, using [Clarifai](http://clarifai.com/)
* Using the tags, the bot obtains a new image from [DuckDuckGo](https://duckduckgo.com/)

This process is repeated seven times. 

###Configuration
ImageLoop needs:

* Python 2.7
* [Telepot](https://github.com/nickoala/telepot) library 
* A [Clarifai](http://clarifai.com/) free account

Three enviroment variables are needed:

* TELEGRAM_TOKEN: Telegram's token for the bot
* CLARIFAI_APP_SECRET, CLARIFAI_APP_ID: info provided by Clarifai


Bot by [Juan Alonso](https://github.com/juanalonso/)