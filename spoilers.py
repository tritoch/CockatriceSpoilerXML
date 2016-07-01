import requests
import feedparser
import re
import json

SPOILER_RSS = 'http://www.mtgsalvation.com/spoilers.rss'
IMAGES = 'http://magic.wizards.com/en/content/eldritch-moon-cards'
IMAGES2 = 'http://mythicspoiler.com/newspoilers.html'

patterns = ['<b>Name:</b> <b>(?P<name>.*?)<',
            'Cost: (?P<cost>\d{0,2}[WUBRGC]*?)<',
            'Type: (?P<type>.*?)<',
            'Pow/Tgh: (?P<pow>.*?)<',
            'Rules Text: (?P<rules>.*?)<br /',
            'Rarity: (?P<rarity>.*?)<',
            'Set Number: #(?P<setnumber>.*?)/'
            ]

related_cards = {'Gisela, the Broken Blade': 'Brisela, Voice of Nightmares',
                 'Bruna, the Fading Light': 'Brisela, Voice of Nightmares',
                 'Ulrich of the Krallenhorde': 'Ulrich, Uncontested Alpha',
                 'Lone Rider': 'It That Rides as One',
                 'Grizzled Angler': 'Grisly Anglerfish',
                 'Docent of Perfection': 'Final Iteration',
                 'Cryptolith Fragment': 'Aurora of Emrakul',
                 'Hanweir Battlements': 'Hanweir, the Writhing Township',
                 'Hanweir Garrison': 'Hanweir, the Writhing Township',
                 'Midnight Scavengers': 'Chittering Host',
                 'Graf Rats': 'Chittering Host',
                 }

def get_cards():
    text = requests.get(SPOILER_RSS).text
    text = text.replace('&#x27;','\'')
    d = feedparser.parse(text)

    cards = []
    for entry in d.items()[5][1]:
    #for entry in d.items()[5][1][:5]:
        card = dict(cost='',cmc='',img='',pow='',name='',rules='',type='',
                color='', altname='', colorIdentity='', colorArray=[], colorIdentityArray=[], setnumber='', rarity='')
        summary = entry['summary']
        for pattern in patterns:
            match = re.search(pattern, summary, re.MULTILINE|re.DOTALL)
            if match:
                dg = match.groupdict()
                card[dg.items()[0][0]] = dg.items()[0][1]
        cards.append(card)
        fix_cards(cards)

    return cards

def fix_cards(cards):
    for card in cards:
        card['name'] = card['name'].replace('&#x27;','\'')
        card['rules'] = card['rules'].replace('&#x27;','\'').replace('&lt;i&gt;','').replace('&lt;/i&gt;','')
        card['altname'] = card['name']
        if (card['name'] == 'Vidlin-Pack Outcast'):
            card['name'] == 'Vildin-Pack Outcast'
            card['altname'] = 'Vildin-Pack Outcast'
        if (card['name'] == 'Decimator of the Provinces'):
            card['altname'] = 'Decimator of Provinces'
        if (card['name'] == 'GrizAngler'):
            card['name'] = 'Grizzled Angler'
            card['altname'] = 'Grizzled Angler'
        if (card['name'] == 'Stitcher&#x27;s Graft'):
            card['altname'] = 'Graft Stapler'
        if (card['name'] == 'Emrakul&#x27;s Influence'):
            card['altname'] = 'Influence of Emrakul'

def add_images(cards):
    text = requests.get(IMAGES).text
    text2 = requests.get(IMAGES2).text
    wotcpattern = r'<img alt="{}.*?" src="(?P<img>.*?\.png)"'
    mythicspoilerpattern = r' src="emn/cards/{}.*?.jpg">'
    for c in cards:
        match = re.search(wotcpattern.format(c['name']), text, re.DOTALL)
        if match:
            c['img'] = match.groupdict()['img']
        else:
            match2 = re.search(mythicspoilerpattern.format((c['altname']).lower().replace(' ','').replace('&#x27;','').replace('-','')), text2, re.DOTALL)
            if match2:
                c['img'] = match2.group(0).replace(' src="','http://mythicspoiler.com/').replace('">','')
            else:
                pass
                #print('image for {} not found'.format(c['name']))

def make_json(cards):

    cardsjson = {
        "block": "Shadows over Innistrad",
        "border": "black",
        "code": "EMN",
        "magicCardsInfoCode": "emn",
        "name": "Eldritch Moon",
        "releaseDate": "2016-07-22",
        "type": "expansion",
        "booster": [
                [
                "rare",
                "mythic rare"
                ],
            "uncommon",
            "uncommon",
            "uncommon",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "common",
            "land",
            "marketing",
            "double-faced"
        ],
        "cards": []
    }

    for card in cards:
        #card['colorIdentityArray'] = []
        for cid in card['color']:
            card['colorIdentityArray'].append(cid)
        #card['colorArray'] = []
        #colornames = ['White','Blue','Black','Red','Green']
        if 'W' in card['color']:
            card['colorArray'].append('White')
        if 'U' in card['color']:
            card['colorArray'].append('Blue')
        if 'B' in card['color']:
            card['colorArray'].append('Black')
        if 'R' in card['color']:
            card['colorArray'].append('Red')
        if 'G' in card['color']:
            card['colorArray'].append('Green')
        cardpower = ''
        cardtoughness = ''
        if len(card['pow'].split('/')) > 1:
            #print len(card['pow'].split('/'))
            cardpower = card['pow'].split('/')[0]
            cardtoughness = card['pow'].split('/')[1]
        cardnames = []
        if card['name'] in related_cards:
            cardnames.append(card['name'])
            cardnames.append(related_cards[card['name']])
        for namematch in related_cards:
            if card['name'] == related_cards[namematch]:
                cardnames.append(namematch)
                cardnames.append(card['name'])
        cardtypes = []
        if not '-' in card['type']:
            cardtypes.append(card['type'])
        else:
            cardtypes = card['type'].replace('Legendary ','').split('-')[0].split(' ')[:-1]
        cardsjson['cards'].append(
            {
                "cmc": card['cmc'],
                "colorIdentity": card['colorIdentityArray'],
                "colors": card['colorArray'],
                "manacost": card['cost'],
                "name": card['name'],
                "names": cardnames,
                "number": card['setnumber'],
                "rarity": card['rarity'],
                "power": cardpower,
                "text": card['rules'],
                #if len(card['pow'].split('/'):
                "toughness": cardtoughness,
                "type": card['type'],
                "types": cardtypes,
                "url": card['img']
            }
        )

    with open('ema.json', 'w') as outfile:
        json.dump(cardsjson, outfile, sort_keys=True, indent=2, separators=(',', ': '))


def make_xml(cards):
    print """<cockatrice_carddatabase version="3">
    <sets>
        <set>
            <name>EMN</name>
            <longname>Eldritch Moon</longname>
            <settype>Expansion</settype>
            <releasedate>2016-07-22</releasedate>
        </set>
    </sets>
    <cards>
    """
    for card in cards:
      try:
        # figure out cmc from cost
        if 'cost' in card and len(card['cost']) > 0:
            m = re.search('(\d+)', card['cost'])
            cmc = 0
            if m:
                cmc += int(m.group())
                cmc += len(card['cost']) - 1 # account for colored symbols
            else:
                cmc += len(card['cost']) # all colored symbols
            card['cmc'] = cmc
        # figure out color
        for c in 'WUBRG' :
            if c in card['cost']:
                card['color'] += c

                card['colorIdentity'] += c
            if (c + '}') in card['rules']:
                if not (c in card['colorIdentity']):
                    card['colorIdentity'] += c
        print """
<card>
    <name>{name}</name>
    <set picURL="{img}">EMN</set>
    <color>{color}</color>
    <manacost>{cost}</manacost>
    <cmc>{cmc}</cmc>
    <type>{type}</type>
    <pt>{pow}</pt>
    <rarity>{rarity}</rarity>
    <tablerow>2</tablerow>
    <text>{rules}</text>
</card>
        """.format(**card)
      except Exception as e:
          print card
          raise

    print """</cards>
    </cockatrice_carddatabase>
    """

if __name__ == '__main__':
    cards = get_cards()
    add_images(cards)
    make_xml(cards)
    make_json(cards)
