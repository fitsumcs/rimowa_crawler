import unittest
from unittest.mock import patch, MagicMock
import asyncio
from main import get_ruble_rate, parse_product

class TestFunctions(unittest.TestCase):

    @patch('aiohttp.ClientSession.get')
    def test_get_ruble_rate_success(self, mock_get):
        class MockResponse:
            async def json(self):
                return {'rates': {'RUB': 75.5}}

            @property
            def status(self):
                return 200

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        mock_get.return_value = MockResponse()
        ruble_rate = asyncio.run(get_ruble_rate())
        self.assertEqual(ruble_rate, 75.5)

    @patch('aiohttp.ClientSession.get')
    def test_get_ruble_rate_failure(self, mock_get):
        class MockResponse:
            async def json(self):
                return {}

            @property
            def status(self):
                return 404

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        mock_get.return_value = MockResponse()
        ruble_rate = asyncio.run(get_ruble_rate())
        self.assertEqual(ruble_rate, 0.0)

    def test_parse_product_valid(self):
        ruble_rate = 75.5
        product = MagicMock()
        product.css.side_effect = lambda x: {
            '::attr(data-itemid)': MagicMock(get=MagicMock(return_value='1234')),
            '.product-name::text': MagicMock(get=MagicMock(return_value='Product Name')),
            '::attr(data-itemprice)': MagicMock(get=MagicMock(return_value='50.00')),
            'img': [MagicMock(css=MagicMock(return_value=MagicMock(get=MagicMock(return_value='image1.jpg')))),
                    MagicMock(css=MagicMock(return_value=MagicMock(get=MagicMock(return_value='image2.jpg'))))],
            '::attr(data-itemcategory)': MagicMock(get=MagicMock(return_value='Category')),
            '::attr(data-itemvariant)': MagicMock(get=MagicMock(return_value='Variant'))
        }[x]

        parsed_product = parse_product(product, ruble_rate)
        self.assertIsNotNone(parsed_product['id'])
        self.assertIsNotNone(parsed_product['title'])
        self.assertEqual(parsed_product['price'], 75.5 * 50.00 * 1.2)
        self.assertEqual(parsed_product['category'], ['Category'])

    def test_parse_product_invalid(self):
        ruble_rate = 75.5
        product = MagicMock()
        product.css.side_effect = lambda x: {
            '::attr(data-itemid)': MagicMock(get=MagicMock(return_value=None)),
            '.product-name::text': MagicMock(get=MagicMock(return_value=None)),
            '::attr(data-itemprice)': MagicMock(get=MagicMock(return_value=None)),
            'img': [],
            '::attr(data-itemcategory)': MagicMock(get=MagicMock(return_value=None)),
            '::attr(data-itemvariant)': MagicMock(get=MagicMock(return_value=None))
        }[x]

        parsed_product = parse_product(product, ruble_rate)
        self.assertIsNone(parsed_product['id'])
        self.assertIsNone(parsed_product['title'])
        self.assertIsNone(parsed_product['price'])
        self.assertEqual(parsed_product['category'], [])

if __name__ == '__main__':
    unittest.main()
