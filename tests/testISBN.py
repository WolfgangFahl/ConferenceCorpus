from corpus.utils.isbn import IsbnType, ISBN
from tests.basetest import BaseTest


class TestISBN(BaseTest):
    """
    tests ISBN
    """

    def testGetType(self):
        """
        tests getType
        """
        testValues = [
            (IsbnType.ISBN_13, "978-1-4244-2047-6"),
            (IsbnType.ISBN_10, "1-4244-0225-5"),
            (IsbnType.NONE, "2022-01-01"),
            (IsbnType.NONE, "978-1-4244-2047-6 invalid"),
        ]
        for expectedType, testValue in testValues:
            actualType = ISBN.getType(testValue)
            self.assertIs(actualType, expectedType, f"'{testValue}' wrongfully detected as {actualType} → expected {expectedType}")

    def testConvertToIsbn13(self):
        """
        tests convertToIsbn13
        """
        testValues = [ # (expectedValue, testValue)
            ("978-1-4244-2047-6", "978-1-4244-2047-6"),
            ("978-1-4244-0225-5", "1-4244-0225-5"),
            (None, "2022-01-01")
        ]
        for expectedValue, testValue in testValues:
            convertedValue = ISBN.convertToIsbn13(testValue)
            self.assertEqual(convertedValue, expectedValue, f"'{testValue}' wrongfully converted to {convertedValue} expected {expectedValue}")