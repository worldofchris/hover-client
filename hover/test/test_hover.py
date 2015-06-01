# -*- coding: utf-8 -*-

import unittest
from mock import patch, PropertyMock, Mock

import requests

from hover.client import HoverClient


class TestHover(unittest.TestCase):

    def setUp(self):

        self.DNS_ID = 12345

        with patch('requests.post') as patched_post, patch('requests.request') as patched_request:
            type(patched_post.return_value).ok = PropertyMock(return_value=True)
            type(patched_post.return_value).cookies = PropertyMock(
                return_value={"hoverauth": "foo",
                              "domains": []})

            type(patched_request.return_value).ok = PropertyMock(return_value=True)
            type(patched_request.return_value).json = Mock(
                return_value={"succeeded": True,
                              "domains": [{"domain_name": "worldofchris.com",
                                           "id": self.DNS_ID}]})

            username = 'mrfoo'
            password = 'keyboardcat'
            domain_name = 'worldofchris.com'
            self.client = HoverClient(username=username,
                                      password=password,
                                      domain_name=domain_name)

    def testInitClient(self):
        """
        Initalise the client
        """

        self.assertEqual(self.client.dns_id, self.DNS_ID)

    def testAddCname(self):
        """
        Add a CNAME
        """
        with patch('requests.request') as patched_request:
            type(patched_request.return_value).json = Mock(
                return_value={"succeeded": True})
            expected = {"succeeded": True}
            actual = self.client.add_record(type="CNAME",
                                            name="megatron",
                                            content="crazyland.aws.com")
            self.assertEqual(actual, expected)

    def testRemoveCname(self):
        """
        Remove a CNAME
        """
        with patch('requests.request') as patched_request:
            type(patched_request.return_value).json = Mock(
                side_effect=[{"succeeded": True,
                              "domains": [{"entries": [{"type": "CNAME",
                                                        "name": "megatron",
                                                        "id":   "dns1234"}]}
                                          ]},
                             {"succeeded": True}])
            expected = {"succeeded": True}
            actual = self.client.remove_record(type="CNAME",
                                               name="megatron")
            self.assertEqual(actual, expected)
