import unittest
from parameterized import parameterized

from shared.domain.model.valueobject.url import Url, InvalidUrlException


class UrlTest(unittest.TestCase):
    @parameterized.expand(
        ["http:www.example.com/main.html", "foobar", "//foo.com", "www.google.com"]
    )
    def test_if_it_raise_an_exception_when_address_is_invalid(self, url: str) -> None:
        with self.assertRaises(InvalidUrlException):
            Url(url)

    @parameterized.expand(
        [
            "http://www.example.com/main.html",
            "https://foo.com",
            "https://foo.com/bar/baz",
            "https://www.google.com",
        ]
    )
    def test_if_it_not_raise_an_exception_when_address_is_valid(
        self, address: str
    ) -> None:
        url = Url(address)
        self.assertEqual(address, url.address)
