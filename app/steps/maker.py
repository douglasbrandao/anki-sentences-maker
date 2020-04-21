import requests
from app.utils.reformat_word import reformat_word
from app.utils.split_word import split_word
from bs4 import BeautifulSoup


class SentenceMaker:

    def __init__(self, word):
        self.word = word

    def scrap_oxford(self):
        word = reformat_word(self.word)
        url = requests.get('https://www.oxfordlearnersdictionaries.com/us/definition/english/' + word)
        soup = BeautifulSoup(url.text, 'html.parser')
        name = soup.find('h1').contents[0]

        try:
            ipa = soup.find('span', class_='phon').contents[0]
        except AttributeError:
            phrasal_verb = split_word(self.word)
            verb = phrasal_verb[0]
            adverb = phrasal_verb[1]
            ipa = '\{}/'.format(self.find_phonetic(verb, adverb))

        definitions = [s.text for s in soup.find_all('span', class_='def')][:2]
        examples = [s.text for s in soup.select('ul.examples > li > span.x')]

        if not examples:
            raise AttributeError("We haven't found a list of examples on Oxford. I'll try the next one.")

        return {
            'name': name,
            'ipa': ipa,
            'definitions': definitions,
            'examples': examples[0:3]
        }

    def scrap_cambridge(self):
        word = reformat_word(self.word)
        url = requests.get('https://dictionary.cambridge.org/dictionary/english/' + word)
        soup = BeautifulSoup(url.text, 'html.parser')

        name = [s.text for s in soup.select('div.di-title')][0]

        try:
            ipa = [s.text for s in soup.find_all('span', class_='pron dpron')][0]
        except IndexError:
            phrasal_verb = split_word(self.word)
            verb = phrasal_verb[0]
            adverb = phrasal_verb[1]
            ipa = '\{}/'.format(self.find_phonetic(verb, adverb))

        definitions = [s.text for s in soup.find_all('div', class_='def ddef_d db')][:2]
        examples = [s.text for s in soup.find_all('div', class_='examp dexamp')]

        if not examples:
            raise AttributeError("We haven't found a list of examples on Cambridge. I'll try the next one.")

        return {
            'name': name,
            'ipa': ipa,
            'definitions': definitions,
            'examples': examples[0:3]
        }

    @staticmethod
    def find_phonetic(word1, word2):
        verb = requests.get('https://www.oxfordlearnersdictionaries.com/us/definition/english/' + word1)
        adverb = requests.get('https://www.oxfordlearnersdictionaries.com/us/definition/english/' + word2)

        soup_verb = BeautifulSoup(verb.text, 'html.parser')
        soup_adverb = BeautifulSoup(adverb.text, 'html.parser')

        verb_ipa = soup_verb.find('span', class_='phon').contents[0]
        adverb_ipa = soup_adverb.find('span', class_='phon').contents[0]

        ipa = '{} {}'.format(verb_ipa, adverb_ipa)

        return ''.join(a for a in ipa if a not in '\/')

    def find_word(self):

        try:
            oxford = self.scrap_oxford()
            return oxford
        except AttributeError as error:
            print(error)

        try:
            cambridge = self.scrap_cambridge()
            return cambridge
        except AttributeError as error:
            print(error)
        except IndexError as error:
            print(error)