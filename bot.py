# Importa l'API de Telegram
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import data
import random
import os

# Defineix una funció que saluda i que s'executarà quan el bot rebi el missatge /start.
# Tambe es crea un graf per defecte de mida 1000.


def start(bot, update, user_data):
    username = update.message.chat.last_name
    if 'graph' not in user_data:
        user_data['graph'] = data.new_graph(1000)
        missatge = "🤵 Welcome Sir/Madam %s, I'm " % (username) + '''*Alfredo*''' + "\n" + "🤔 Ready for another journey?"
    else:
        missatge = "⏳ Restarting graph ⏳"
        bot.send_message(chat_id=update.message.chat_id, text=missatge)
        user_data['graph'] = data.new_graph(1000)
        missatge = "It's done Sir/Madam"
    bot.send_message(chat_id=update.message.chat_id, text=missatge, parse_mode=telegram.ParseMode.MARKDOWN)

# L'Alfredo mostra un missatge on explica l'ús de les comandes i les seves funcions


def helps(bot, update):
    missatge = ("🤵 Here is a list of the various actions I can perform for you, Sir/Madam.\n" + "\n" +
                "▪ /start : Start a conversation with me or restart the graph at its default distance. \n" +
                "▪ /authors: It shows the names and emails of my fantastic creators. \n" +
                "▪ /graph ⟨distance⟩: The graph is replaced by a new one using the distance specified. \n" +
                "▪ /nodes : Writes the number of nodes of the graph. \n" +
                "▪ /edges : Writes the number of edges of the graph. \n" +
                "▪ /components: Writes the number of connected components of the graph.\n" +
                "▪ /plotgraph: Shows a map with all the stations and the edges that connect them.\n" +
                "▪ /route ⟨origin, destination⟩: Shows a map with the fastest way to go from a origin to a destination. \n" +
                "▪ /distribute ⟨bikes, docks⟩: Given restrictions in bikes and docks, it returns de total" +
                "cost of moving all the bikes in order to satisfy the restrictions. \n" + "\n" +
                "🤵 I hope this has been useful for you, Sir/Madam 🤵")
    bot.send_message(chat_id=update.message.chat_id, text=missatge)

# L'Alfredo mostra un missatge amb la informacio dels autors del bot


def authors(bot, update):
    missatge = ("🤵 My creators are:\n" + "▪ Maria Ribot i Vilà (maria.ribot.vila@est.fib.upc.edu)\n" +
                "▪ Arnau Turch Ferreres (arnau.turch@est.fib.upc.edu)\n")
    bot.send_message(chat_id=update.message.chat_id, text=missatge)

# L'Alfredo diu el nombre d'estacions que hi ha en servei a temps real


def nodes(bot, update, user_data):
    n_nodes = str(data.number_nodes(user_data['graph']))
    missatge = "Your graph has a total of %s nodes" % (n_nodes)
    bot.send_message(chat_id=update.message.chat_id, text=missatge)

# L'Alfredo diu el nombre de conneccions entre estacions que hi ha en el graf actual


def edges(bot, update, user_data):
    n_edges = str(data.number_edges(user_data['graph']))
    missatge = "Your graph has a total of %s edges" % (n_edges)
    bot.send_message(chat_id=update.message.chat_id, text=missatge)

# L'Alfredo diu a l'usuari quantes components connectades entre si que hi ha en el graf actual


def components(bot, update, user_data):
    n_components = str(data.components(user_data['graph']))
    missatge = "Your graph has a total of %s connected components" % (n_components)
    bot.send_message(chat_id=update.message.chat_id, text=missatge)

# Es crea un graf amb les arestes de distancia menor o igual a la distància que ha donat l'usuari


def graph(bot, update, args, user_data):
    try:
        dist = float(args[0])
        user_data['graph'] = data.new_graph(dist)
        missatge = "It's done Sir/Madam"
        bot.send_message(chat_id=update.message.chat_id, text=missatge)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="🤷‍♂️ Sir/Madam, specify a distance please 🤷‍♂️")


def plotgraph(bot, update, user_data):
    username = update.message.chat.first_name + update.message.chat.last_name
    file_name = "%d.png" % random.randint(1000000, 9999999)
    data.mapa(user_data['graph'], file_name)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(file_name, 'rb'))
    bot.send_message(chat_id=update.message.chat_id, text="🥰 Beautiful, isn't it? 🥰")
    os.remove(file_name)

# El bot ensenya una imatge de la ruta recomanada des de dues adreces donades per l'usuari.


def route(bot, update, user_data):
    username = update.message.chat.first_name + update.message.chat.last_name
    addresses = update.message.text[7:]
    coords = data.addressesTOcoordinates(addresses)
    file_name = "%d.png" % random.randint(1000000, 9999999)
    if coords is None:
        bot.send_message(chat_id=update.message.chat_id, text="This address couldn't be found")
    else:
        h, m = data.shortest_route(user_data['graph'], coords, file_name)
        if(h == 0):
            missatge = "Expected time %s min." % (m)
        else:
            missatge = "Expected time %s h and %s min." % (h, m)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(file_name, 'rb'))
        bot.send_message(chat_id=update.message.chat_id, text=missatge)
        os.remove(file_name)

# Respon el missatge amb el valor del recorregut amb més bicicletes portades i kilòmetres circulats


def distribute(bot, update, args, user_data):
    try:
        r, d = int(args[0]), int(args[1])
        err, bmove, max_cost = data.flow(user_data['graph'], r, d)
        if (not err):
            missatge = "ERROR"
        else:
            missatge = "Total cost: %s\n" % (bmove) + "Biggest cost: %s." % (max_cost)
        bot.send_message(chat_id=update.message.chat_id, text=missatge)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="Sir/Madam two numbers are needed for this command")

'''
def distribute(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="This functionality is still under contruction")
'''

# Quan l'Alfredo no reconeix la comanda s'escriu el següent missatge


def unknown(bot, update):
    message = "🤵 Excuse me Sir/Madam, I didn't understand that command. \n🙏 Can You repeat it please?"
    bot.send_message(chat_id=update.message.chat_id, text=message)

# declara una constant amb el access token que llegeix de token.txt
TOKEN = open('token.txt').read().strip()

# crea objectes per treballar amb Telegram
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# indica que quan el bot rebi la comanda /start s'executi la funció start
dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('help', helps))
dispatcher.add_handler(CommandHandler('authors', authors))
dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data=True))
dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data=True))
dispatcher.add_handler(CommandHandler('components', components, pass_user_data=True))
dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True, pass_user_data=True))
dispatcher.add_handler(CommandHandler('plotgraph', plotgraph, pass_user_data=True))
dispatcher.add_handler(CommandHandler('route', route, pass_user_data=True))
dispatcher.add_handler(CommandHandler('distribute', distribute, pass_args=True, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Engega el bot
updater.start_polling()
