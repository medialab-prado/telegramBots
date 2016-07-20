var TelegramBot = require('node-telegram-bot-api');
var scrapm = require('scrapm');
var scrapy = require('node-scrapy'),
    url = 'https://www.google.es/movies',
    selector = '.movie',
    model = {
      titulos: {
        selector: '.movie_results .movie .header h2 a',
        required: true
      },
      cines: {
        selector: '.movie_results .movie .theater .name'
      }
    };


var token = '197080842:AAHvDSxy0vQ3bYxbL8Y_5zhj2DB-Z65evY4';
// Setup polling way
var bot = new TelegramBot(token, {polling: true});
var personas = {};

bot.getMe().then(function(data){
	console.log(data);
});


// bot.onText(/\/echo (.+)/, function (msg, match) {
//   var fromId = msg.from.id;
//   var resp = match[1];
//   bot.sendMessage(fromId, resp);
// });

bot.onText(/\/start/, function (msg, match) {
  var fromId = msg.from.id;

  console.log('===> [START]');
  bot.sendMessage(fromId, 'Hola '+msg.chat.first_name+'. Si deseas buscar una película solo tienes usar el comando /peli. Bienvenido!');
});


bot.onText(/\/peli/, function (msg, match) {
  var fromId = msg.from.id;
  //var peli = match[1];

  // ?near=madrid%2C+m%2C+esp&q=ice+age

  console.log('===> [PELI]');
  console.log(msg);
  //console.log(match);



  personas[fromId] = {};

  bot.sendMessage(fromId, 'Dime '+msg.chat.first_name+', ¿qué película quieres ver?');
});

bot.on('message', function (msg) {
    var chatId = msg.chat.id;
	  // photo can be: a file path, a stream or a Telegram file_id
	//   var photo = 'cats.png';
	//     bot.sendPhoto(chatId, photo, {caption: 'Lovely kittens'});

  console.log('==> [MESSAGE]');

  if(personas[chatId] !== undefined && personas[chatId].movie === undefined)
  {
    console.log('-> Film');
    personas[chatId].movie = msg.text;
    bot.sendMessage(msg.chat.id, '¿En qué localidad te gustaría ver '+msg.text+'?');
  }
  else if(personas[chatId] !== undefined && personas[chatId].city === undefined)
  {
    console.log('-> City');
    personas[chatId].city = msg.text;

    bot.sendMessage(msg.chat.id, 'Ok ' + msg.from.first_name + '. Estamos buscando cines en tu localidad con esa película...');

    var busqueda = url + '?near='+personas[chatId].city+'&q=' + personas[chatId].movie;

    scrapm({url: busqueda}, function(err, $){
      
      if($('.movie').length <= 0)
      {
        bot.sendMessage(msg.chat.id, 'Lo siento ' + msg.from.first_name + ', pero no hemos encontrado nada con los criterios que has marcado :( Intenta con otra película o ciudad');
        return;
      }

      $.each($('.movie'), function(i, obj){


        $.each($(obj).find('.theater'), function(j, theater){

          var btns = [];

          $.each($(theater).find('.times span a'), function(h, mTime){

            btns.push([{
              text: $(mTime).html(),
              url: $(mTime).attr('href').split('?q=')[1],
              callback_data: j
            }]);
          });

          var options = {
            reply_markup: JSON.stringify({
              inline_keyboard: btns
            })
          };

          bot.sendMessage(msg.chat.id, '-> ' + $(theater).find('.name a').html(), options);

        });

      });
    });
  }

});

bot.on('callback_query', function(data){
  console.log('===> [CALLBACKQUERY]', data);
});

bot.on('new_chat_participant', function(user){
  console.log('===> [WELCOME]');
});
bot.on('start', function(user){
  console.log('===> [WELCOME]');
});
