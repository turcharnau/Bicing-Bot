# PROJECTE BICING BOT: ALFREDO

Desenvolupament d'un bot de telegram que satisfà diferents qüestions que poden sorgir als usuaris del bicing o a l'organització del servei, d'acord amb l'enunciat donat pels professors d'AP2 del GCED del curs 2019.

Si desitjeu més informació relacionat amb aquest treball la podreu trobar [aqui](https://github.com/jordi-petit/ap2-bicingbot-2019)

## Preparació

### Prerequisites

S'han de tenir instal·lats diferents paquets de Python al sistema operatiu:

* [Pandas](https://pandas.pydata.org/)
  `pip install pandas`
* [Networkx](https://networkx.github.io/)
  `pip install networkx`
* [Haversine](https://github.com/mapado/haversine)
  `pip install haversine`
* [Geopy](https://geopy.readthedocs.io/en/stable/)
  `pip install geopy`
* [Staticmap](https://github.com/komoot/staticmap)
  `pip install staticmap`
* [Python-telegram-bot](https://python-telegram-bot.org/)
  `pip install python-telegram-bot`

L'entorn on s'utilitza el bot és l'aplicació de missatgeria telegram. Pot ser instal·lada des de vàries plataformes:
  * Dispositius mòbils iOS: [Telegram app](https://itunes.apple.com/us/app/telegram-messenger/id686449807?mt=8)
  * Dispositius mòbils android: [Telegram app](https://play.google.com/store/apps/details?id=org.telegram.messenger&hl=en)
  * Dispositius pc: [Telegram](https://desktop.telegram.org/), aquí es pot descarregar l'aplicació en versió al sistema operatiu del pc de l'usuari

### Instal·lació

En primer lloc, s'ha d'extreure del zip els arxius data.py i bot.py.

Es pot emprar la comanda següent a la terminal. Desempaqueta el zip i es guarda al directori especificat.

```
$> sudo apt-get install unzip
$> unzip alfredo.zip -d [destination_folder]
```
Cal executar els arxius data.py i bot.py per tal que el bot pugui fer servir totes les comandes que conté.

```
$> python3.7 data.py
$> python3.7 bot.py
```
El bot estarà "viu" des del moment en que s'executa la comanda ```python3.7 bot.py ```.
Quan volguèssim apagar el bot serà suficient en premer ``` ctrl+c``` a la terminal des d'on està funcionant.

Després, heu d'anar a telegram i buscar el bot, el seu username és: @turchri_bot  

Per iniciar la vostra aventura amb el magnific bot Alfredo, heu d'enviar la comanda ``` /start ```.

## Tests

Tot seguit deixem unes poques comandes amb la resposta esperada. Aquestes retornen un missatge de text, cal remarcar que el bot en disposa d'altres que retornen una imatge com per exemple ``` /route ``` o ``` /plotgraph ```.

<table>
<tr>
<td>

```
/graph 400
/edges
/components
/graph 700
/nodes
/modes
/route avinguda diagonal 65, avinguda diagonal 70
```

</td>
<td>

```
It's done Sir/Madam
Your graph has a total of 820 edges
Your graph has a total of 26 connected components
It's done Sir/Madam
Your graph has a total of 401 nodes (Varia depen del moment)
🤵 Excuse me Sir/Madam, I didn't understand that command. 🙏 Can You repeat it please?
(image) + Expected time 1 min.
```

</td>
</tr>
</table>

## Built With

- `pandas` per a utilitzar `DataFrames`.
- `networkx` per a manipular grafs.
- `haversine` per a calcular distàncies entre coordenades.
- `geopy` per a calcular coordenades geogràfiques (latitud, longitud) a partir d'adreces.
- `staticmap` per pintar mapes.
- `python-telegram-bot` per interactuar amb Telegram.

## Autors

* **Maria Ribot i Vilà** - (maria.ribot.vila@est.fib.upc.edu).
* **Arnau Turch Ferreres** - (arnau.turch@est.fib.upc.edu).

## Llicència

Aquest projecte està llicenciat sota la llicència [UPC](https://www.upc.edu/ca).

