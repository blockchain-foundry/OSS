from decimal import Decimal

from django.test import TestCase

import mock
from gcoinrpc.data import TransactionInfo
from tornado.httpclient import HTTPResponse

from notification.models import TxSubscription, TxNotification
from notification.daemon import TxNotifyDaemon


class TxNotifyDaemonTestCase(TestCase):

    def setUp(self):
        self.tx_subscription1 = TxSubscription.objects.create(
                                    tx_hash='3da27893cd84d307fccad65d5c0a75fca29efbb4070b1899f2d48725254bbb5e',
                                    callback_url="http://callback.com",
                                    confirmation_count=5
                                )

        self.rawtx1 = {
            "hex" : "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff6b4830450221009b1db0692690af5b1b6559e47d1a4605b8fa2516704e9ebde673622461a1987c022008c58973dbf685170511b10a3a8a52c8a69f46c3a7213bc4fedb377112fe56ef01210366f972fa600de7f12ec28873e859c7f6953782308f6bd958cb06b3bde28273baffffffff0100e40b54020000001976a914aea4b2bcf13e1ba5e7793a759ef0503ae3e1ac0c88ac010000000000000001000000",
            "txid" : "3da27893cd84d307fccad65d5c0a75fca29efbb4070b1899f2d48725254bbb5e",
            "version" : 1,
            "locktime" : 0,
            "type" : "MINT",
            "size" : 200,
            "vin" : [
                {
                    "coinbase" : "4830450221009b1db0692690af5b1b6559e47d1a4605b8fa2516704e9ebde673622461a1987c022008c58973dbf685170511b10a3a8a52c8a69f46c3a7213bc4fedb377112fe56ef01210366f972fa600de7f12ec28873e859c7f6953782308f6bd958cb06b3bde28273ba",
                    "scriptSig" : {
                        "asm" : "30450221009b1db0692690af5b1b6559e47d1a4605b8fa2516704e9ebde673622461a1987c022008c58973dbf685170511b10a3a8a52c8a69f46c3a7213bc4fedb377112fe56ef01 0366f972fa600de7f12ec28873e859c7f6953782308f6bd958cb06b3bde28273ba",
                        "hex" : "4830450221009b1db0692690af5b1b6559e47d1a4605b8fa2516704e9ebde673622461a1987c022008c58973dbf685170511b10a3a8a52c8a69f46c3a7213bc4fedb377112fe56ef01210366f972fa600de7f12ec28873e859c7f6953782308f6bd958cb06b3bde28273ba"
                    },
                    "sequence" : 4294967295
                }
            ],
            "vout" : [
                {
                    "value" : 10000000000,
                    "n" : 0,
                    "scriptPubKey" : {
                        "asm" : "OP_DUP OP_HASH160 aea4b2bcf13e1ba5e7793a759ef0503ae3e1ac0c OP_EQUALVERIFY OP_CHECKSIG",
                        "hex" : "76a914aea4b2bcf13e1ba5e7793a759ef0503ae3e1ac0c88ac",
                        "reqSigs" : 1,
                        "type" : "pubkeyhash",
                        "addresses" : [
                            "1GvRsoxx67CzRxvMXofDEVSTX4m29V9kE5"
                        ]
                    },
                    "color" : 1
                }
            ],
            "blockhash" : "00000c771a4fddac120115415b97a5668ed43d8f22a43ac6d3e1db1181f5c98b",
            "confirmations" : 11,
            "time" : 1470207763,
            "blocktime" : 1470207763
        }
        self.tx1 = TransactionInfo(**self.rawtx1)

        self.best_block = {
            u'merkleroot': u'6b91a66c096ea475ec7cad61d3a795a06c7bdc81ca3b7b5b7ca9341480bd29a4',
            u'nonce': 2356050,
            u'previousblockhash': u'00000b92c5ed60e1f8e637c0a546cf13592e8b958f5952ade1f1825f42e15b9f',
            u'hash': u'00000070b0bc8334373e8565bc419349ae476f676c12e75e156ab2b8fc16dd1a',
            u'version': 3,
            u'tx': [u'6b91a66c096ea475ec7cad61d3a795a06c7bdc81ca3b7b5b7ca9341480bd29a4'],
            u'chainwork': u'0000000000000000000000000000000000000000000000000000000010901090',
            u'height': 264,
            u'difficulty': Decimal('0.00024414'),
            u'confirmations': 1,
            u'starttime': 1470207767,
            u'time': 1470207769,
            u'bits': u'1e0ffff0',
            u'size': 330
       }

    def clean(self):
        TxSubscription.objects.all().delete()
        TxNotification.objects.all().delete()

    @mock.patch('notification.daemon.TxNotifyDaemon.get_transaction')
    @mock.patch('notification.daemon.TxNotifyDaemon.get_best_block')
    @mock.patch('notification.daemon.TxNotifyDaemon.start_notify')
    def test_run_forever_1(self, mock_start_notify, mock_get_best_block, mock_get_transaction):
        """
        normal situation
        """
        mock_get_best_block.return_value = self.best_block
        mock_get_transaction.return_value = self.tx1

        daemon = TxNotifyDaemon()
        daemon.run_forever(test=True)

        notifications = TxNotification.objects.filter(is_notified=False)
        mock_get_transaction.assert_called_with("3da27893cd84d307fccad65d5c0a75fca29efbb4070b1899f2d48725254bbb5e")
        self.assertEqual(notifications.count(), 1)
        self.assertQuerysetEqual(notifications, map(repr, mock_start_notify.call_args[0][0]), ordered=False)

    @mock.patch('notification.daemon.TxNotifyDaemon.get_transaction')
    @mock.patch('notification.daemon.TxNotifyDaemon.get_best_block')
    @mock.patch('notification.daemon.TxNotifyDaemon.start_notify')
    def test_run_forever_2(self, mock_start_notify, mock_get_best_block, mock_get_transaction):
        """
        no new block and no not notified notification
        """
        mock_get_best_block.return_value = self.best_block
        mock_get_transaction.return_value = self.tx1

        daemon = TxNotifyDaemon()
        daemon.last_seen_block = self.best_block
        daemon.run_forever(test=True)

        notifications = TxNotification.objects.filter(is_notified=False)
        self.assertFalse(mock_get_transaction.called)
        self.assertEqual(notifications.count(), 0)

    @mock.patch('notification.daemon.TxNotifyDaemon.get_transaction')
    @mock.patch('notification.daemon.TxNotifyDaemon.get_best_block')
    @mock.patch('notification.daemon.TxNotifyDaemon.start_notify')
    def test_run_forever_3(self, mock_start_notify, mock_get_best_block, mock_get_transaction):
        """
        no new block but exists not notified notification
        """
        s = TxSubscription.objects.create(
                tx_hash='abcce180d8aaec88f9c9f80168705aa85a02e5f82d717dbef96657078cede9c8',
                callback_url='http://callback.com',
                confirmation_count=10
            )
        TxNotification.objects.create(subscription=s)

        mock_get_best_block.return_value = self.best_block
        mock_get_transaction.return_value = self.tx1

        daemon = TxNotifyDaemon()
        daemon.last_seen_block = self.best_block
        daemon.run_forever(test=True)

        notifications = TxNotification.objects.filter(is_notified=False)
        self.assertFalse(mock_get_transaction.called)
        self.assertEqual(notifications.count(), 1)
        self.assertQuerysetEqual(notifications, map(repr, mock_start_notify.call_args[0][0]), ordered=False)

    @mock.patch('notification.daemon.TxNotifyDaemon.get_transaction')
    @mock.patch('notification.daemon.TxNotifyDaemon.get_best_block')
    @mock.patch('notification.daemon.TxNotifyDaemon.start_notify')
    def test_run_forever_4(self, mock_start_notify, mock_get_best_block, mock_get_transaction):
        """
        confirmation is not greater than confirmation count that subscribe
        """
        mock_get_best_block.return_value = self.best_block
        self.tx1.confirmations = 1
        mock_get_transaction.return_value = self.tx1

        daemon = TxNotifyDaemon()
        daemon.run_forever(test=True)

        notifications = TxNotification.objects.filter(is_notified=False)
        mock_get_transaction.assert_called_with("3da27893cd84d307fccad65d5c0a75fca29efbb4070b1899f2d48725254bbb5e")
        self.assertEqual(notifications.count(), 0)

    @mock.patch('notification.daemon.TxNotifyDaemon.get_transaction')
    @mock.patch('notification.daemon.TxNotifyDaemon.get_best_block')
    @mock.patch('notification.daemon.TxNotifyDaemon.start_notify')
    def test_run_forever_5(self, mock_start_notify, mock_get_best_block, mock_get_transaction):
        """
        tx is still in mempool
        """
        mock_get_best_block.return_value = self.best_block
        delattr(self.tx1, 'confirmations')
        mock_get_transaction.return_value = self.tx1

        daemon = TxNotifyDaemon()
        daemon.run_forever(test=True)

        notifications = TxNotification.objects.filter(is_notified=False)
        mock_get_transaction.assert_called_with("3da27893cd84d307fccad65d5c0a75fca29efbb4070b1899f2d48725254bbb5e")
        self.assertEqual(notifications.count(), 0)

    @mock.patch('notification.daemon.ioloop.IOLoop.instance')
    @mock.patch('notification.daemon.AsyncHTTPClient')
    def test_start_notify(self, mock_asynchttpclient, mock_ioloop_instance):

        # mock client.fetch
        mock_asynchttpclient_instance = mock.MagicMock(fetch=mock.MagicMock())
        mock_asynchttpclient.return_value = mock_asynchttpclient_instance

        # mock ioloop.IOLoop.instance().start() and ioloop.IOLoop.instance().stop()
        mock_ioloop_instance_obj = mock.MagicMock(start=mock.MagicMock(), stop=mock.MagicMock())
        mock_ioloop_instance.return_value = mock_ioloop_instance_obj

        # prepare notification to notify
        s1 = TxSubscription.objects.create(
                tx_hash='abcce180d8aaec88f9c9f80168705aa85a02e5f82d717dbef96657078cede9c8',
                callback_url='http://callback1.com',
                confirmation_count=10
            )
        s2 = TxSubscription.objects.create(
                tx_hash='ce1fe377472da26d2561e36fbdc8d8a67e2e59e2d55da99dab77d5903aeedf2b',
                callback_url='http://callback2.com',
                confirmation_count=10
            )
        TxNotification.objects.bulk_create([
            TxNotification(subscription=s1),
            TxNotification(subscription=s2)
        ])
        notifications = TxNotification.objects.filter(is_notified=False)

        daemon = TxNotifyDaemon()
        daemon.start_notify(notifications)

        # test fetch call
        call_list = mock_asynchttpclient_instance.fetch.call_args_list
        requests = []
        callback_funcs = []
        for index, notification in enumerate(notifications):
            request = call_list[index][0][0]
            requests.append(request)
            callback_funcs.append(call_list[index][0][1])
            self.assertEqual(request.url, notification.subscription.callback_url)

        # mock responses and manually call all callback_funcs
        responses = [
            HTTPResponse(request=requests[0], code=200),
            HTTPResponse(request=requests[1], code=404)
        ]
        for index, callback in enumerate(callback_funcs):
            callback(responses[index])

        for notification in notifications:
            notification.refresh_from_db()

        # test notification instance is updated in callback func
        self.assertTrue(notifications[0].is_notified)
        self.assertEqual(notifications[0].notification_attempts, 1)

        self.assertFalse(notifications[1].is_notified)
        self.assertEqual(notifications[1].notification_attempts, 1)

        # start and stop is called once and only once
        self.assertEqual(mock_ioloop_instance_obj.stop.call_count, 1)
        self.assertTrue(mock_ioloop_instance_obj.start.call_count, 1)

    @mock.patch('notification.daemon.ioloop.IOLoop.instance')
    @mock.patch('notification.daemon.AsyncHTTPClient')
    def test_start_notify_no_notification(self, mock_asynchttpclient, mock_ioloop_instance):

        # mock client.fetch
        mock_asynchttpclient_instance = mock.MagicMock(fetch=mock.MagicMock())
        mock_asynchttpclient.return_value = mock_asynchttpclient_instance

        # mock ioloop.IOLoop.instance().start() and ioloop.IOLoop.instance().stop()
        mock_ioloop_instance_obj = mock.MagicMock(start=mock.MagicMock(), stop=mock.MagicMock())
        mock_ioloop_instance.return_value = mock_ioloop_instance_obj

        daemon = TxNotifyDaemon()
        daemon.start_notify(TxNotification.objects.filter(is_notified=False))

        self.assertFalse(mock_ioloop_instance_obj.start.called)
        self.assertFalse(mock_ioloop_instance_obj.stop.called)

