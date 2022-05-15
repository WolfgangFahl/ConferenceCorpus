import re
from enum import Enum


class IsbnType(Enum):
    ISBN_10 = "ISBN-10"
    ISBN_13 = "ISBN-13"
    NONE = None


class ISBN:
    """
    Provides Functions to detect the ISBN version and convert between them if possible
    """

    # https://www.wikidata.org/wiki/Property:P957
    ISBN_10_REGEX_PATTERN = "([0-57]-(\d-\d{7}|\d\d-\d{6}|\d{3}-\d{5}|\d{4}-\d{4}|\d{5}-\d{3}|\d{6}-\d\d|\d{7}-\d)|(" \
                            "65|8\d|9[0-4])-(\d-\d{6}|\d\d-\d{5}|\d{3}-\d{4}|\d{4}-\d{3}|\d{5}-\d\d|\d{6}-\d)|(6[" \
                            "0-4]|9[5-8])\d-(\d-\d{5}|\d\d-\d{4}|\d{3}-\d{3}|\d{4}-\d\d|\d{5}-\d)|99[0-8]\d-(\d-\d{" \
                            "4}|\d\d-\d{3}|\d{3}-\d\d|\d{4}-\d)|999\d\d-(\d-\d{3}|\d\d-\d\d|\d{3}-\d))-[\dX]"

    # https://www.wikidata.org/wiki/Property:P212
    ISBN_13_REGEX_PATTERN = "97(8-([0-57]-(\d-\d{7}|\d\d-\d{6}|\d{3}-\d{5}|\d{4}-\d{4}|\d{5}-\d{3}|\d{6}-\d\d|\d{" \
                            "7}-\d)|(65|8\d|9[0-4])-(\d-\d{6}|\d\d-\d{5}|\d{3}-\d{4}|\d{4}-\d{3}|\d{5}-\d\d|\d{" \
                            "6}-\d)|(6[0-4]|9[5-8])\d-(\d-\d{5}|\d\d-\d{4}|\d{3}-\d{3}|\d{4}-\d\d|\d{5}-\d)|99[" \
                            "0-8]\d-(\d-\d{4}|\d\d-\d{3}|\d{3}-\d\d|\d{4}-\d)|999\d\d-(\d-\d{3}|\d\d-\d\d|\d{" \
                            "3}-\d))|9-(8-(\d-\d{7}|\d\d-\d{6}|\d{3}-\d{5}|\d{4}-\d{4}|\d{5}-\d{3}|\d{6}-\d\d|\d{" \
                            "7}-\d)|(1[0-2]|6\d)-(\d-\d{6}|\d\d-\d{5}|\d{3}-\d{4}|\d{4}-\d{3}|\d{5}-\d\d|\d{" \
                            "6}-\d)))-\d|"

    @classmethod
    def getType(cls, value:str) -> IsbnType:
        if re.fullmatch(cls.ISBN_10_REGEX_PATTERN, value):
            return IsbnType.ISBN_10
        elif re.fullmatch(cls.ISBN_13_REGEX_PATTERN, value):
            return IsbnType.ISBN_13
        else:
            return IsbnType.NONE

    @classmethod
    def convertToIsbn13(cls, value) -> str:
        """
        If given value is a valid ISBN-10 the value is converted to ISBN-13.
        If the given value is already a valid ISBN-13 the value is returned.
        Otherwise, None is returned

        see https://en.wikipedia.org/wiki/ISBN#ISBN-10_to_ISBN-13_conversion
        Args:
            value: isbn value

        Returns:
            str ISBN-13 value or None if the value can not be converted to a ISBN-13 value
        """
        isbn_type = cls.getType(value)
        if isbn_type is IsbnType.ISBN_10:
            value = f"978-{value}"
        elif isbn_type is IsbnType.NONE:
            value = None
        elif isbn_type is IsbnType.ISBN_13:
            pass
        return value
