import argparse
import socket
import sys
from typing import List, Tuple, Union
import justpy as jp

from ptp.eventrefparser import EventReferenceParser


class QuasarColorPalette:
    """
    Provides the Quasar color palette

    see https://quasar.dev/style/color-palette
    """

    colors = ["red", "pink","purple", "deep-purple", "indigo", "blue", "light-blue", "cyan", "teal", "green",
              "light-green", "lime", "yellow", "amber", "orange", "deep-orange", "brown", "grey", "blue-grey"]

    @classmethod
    def colorPalette(cls):
        palette = []
        for color in cls.colors:
            colors = [f"{color}-{i}" for i in range(1,15)]
            palette.append(color)
            palette.extend(colors)
        return palette

    @classmethod
    def getBackgroundColor(cls, color:str):
        return f"bg-{color}"

    @classmethod
    def getTextColor(cls, color:str):
        return f"text-{color}"

    @classmethod
    def getAllBackgroundColors(cls):
        return [cls.getBackgroundColor(color) for color in cls.colorPalette()]

    @classmethod
    def getAllTextColors(cls):
        return [cls.getTextColor(color) for color  in cls.colorPalette()]


class Token(jp.QDiv):
    """
    Displays a token and its label in a given color
    """
    TOKEN_CLASSES = "rounded-borders text-center row inline flex-center brand-color shadow-4 q-mx-xs"
    TOKEN_VALUE_CLASSES = "q-pa-xs"
    TOKEN_LABEL_CLASSES = "text-italic text-weight-light text-white q-pa-xs"

    def __init__(self, label:str, value:str, color:str=None, **kwargs):
        """
        constructor
        Args:
            label: label of the token (token name in NER)
            value: value of the token
            color: background color of the token Should be in QuasarColorPalette.colorPalette()
            **kwargs:
        """
        if color is None:
            color = "primary"
        classes = f"{self.TOKEN_CLASSES} bg-{color}"
        super(Token, self).__init__(classes=classes, **kwargs)
        self.label = label
        self.value = value
        self.valueWrapper = jp.QDiv(a=self, classes=self.TOKEN_VALUE_CLASSES)
        jp.QDiv(a=self.valueWrapper, text=self.value, classes="col")
        self.labelWrapper = jp.QDiv(a=self, classes=self.TOKEN_LABEL_CLASSES)
        jp.QDiv(a=self.labelWrapper, text=self.label, classes="col")


class TokenSequence(jp.QDiv):
    """
    Displays the sequence of given tokens.
    If the Token is a tuple of the form (label, value) the token value is displayed with its label.

    inspired by https://github.com/tvst/st-annotated-text
    """

    def __init__(self, tokens:List[Union[str,Tuple[str,str]]], colorMap:dict=None, **kwargs):
        super(TokenSequence, self).__init__(classes="q-pr-md q-ma-lg row justify-start", **kwargs)
        if colorMap is None:
            colorMap={}
            labels = {token[0] for token in tokens if isinstance(token, tuple)}
            colors = [ color for color in QuasarColorPalette.colorPalette() if '4' in color]
            totalColors=len(colors)
            for i, label in enumerate(labels):
                colorIndex = label.__hash__() % totalColors
                colorMap[label]=colors[colorIndex]
        for token in tokens:
            if isinstance(token, str):
                jp.QDiv(a=self, text=token, classes="q-mx-xs text-center")
            else:
                label, value = token
                Token(label, value, color=colorMap.get(label),a=self)


class EventReferenceParserWebInterface:

    parser = EventReferenceParser()

    def webPage(self):
        '''
        Returns:
            a Justpy reactive webPage
        '''
        self.wp = jp.QuasarPage()
        self.referenceInput = jp.QInputChange(label="Event Reference",key="eventRef", placeholder="Please enter an event reference", a=self.wp)
        self.referenceInput.on("change", self.parseEventReference)
        self.referenceInput.parser = self.parser
        self.referenceInput.output = jp.QDiv(a=self.wp)
        return self.wp

    @staticmethod
    def parseEventReference(self, msg):
        tokenSeq = self.parser.parse(msg.value, "eventRefParser", show=True)
        # show parsing
        lut = {}
        for token in tokenSeq.matchResults:
            if token.name not in ["first Letter", "word"]:
                if token.pos in lut:
                    lut[token.pos].append(token)
                else:
                    lut[token.pos] = [token]
        annText=[]
        for i, word in enumerate(msg.value.split(" ")):
            if i in lut:
                name = "/".join([c.name for c in lut[i]])
                annText.append((name, word))
            else:
                annText.append(f"{word} ")
        self.output.delete_components()
        print(annText)
        TokenSequence(tokens=annText, a=self.output)
        # show statistics
        jp.QHeader(text="Statistics", a=self.output)
        item_list = jp.QList(classes="rounded-borders", padding=True, bordered=True, a=self.output)
        for category in self.parser.categories:
                expansion_item = jp.QExpansionItem(label=category.name, a=item_list, dense=True, dense_toggle=True, expand_separator=True)
                card = jp.QCard(a=expansion_item)
                sec=jp.QCardSection(a=card)
                jp.Markdown(markdown=category.mostCommonTable(tablefmt="github"), a=sec, classes='m-2')


def main(_argv=None):
    '''
    command line entry point
    '''
    parser = argparse.ArgumentParser(description='Event Reference Parser Web Interface')
    parser.add_argument('--host',default=socket.getfqdn())
    parser.add_argument('--port',type=int,default=8500)
    args = parser.parse_args()
    dashboard=EventReferenceParserWebInterface()
    jp.justpy(dashboard.webPage,host=args.host,port=args.port)


if __name__ == '__main__':
    sys.exit(main())
