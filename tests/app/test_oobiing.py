# -*- encoding: utf-8 -*-
"""
tests.app.test_multisig module

"""
import json

import falcon
from falcon import testing
from hio.base import doing
from keri.app import habbing, oobiing, notifying
from keri.peer import exchanging

from tests.app import openMultiSig


def test_oobi_share():
    oobi = "http://127.0.0.1:5642/oobi/Egw3N07Ajdkjvv4LB2Mhx2qxl6TOCFdWNJU6cYR_ImFg/witness" \
           "/BGKVzj4ve0VSd8z_AmvhLg4lqcC_9WYX90k03q-R_Ydo?name=Phil"
    with habbing.openHab(name="test", temp=True) as (hby, hab):
        exc = exchanging.Exchanger(hby=hby, handlers=[])
        notifier = notifying.Notifier(hby=hby)

        oobiing.loadHandlers(hby=hby, exc=exc, notifier=notifier)

        assert "/oobis" in exc.routes

        handler = exc.routes["/oobis"]
        msg = dict(
            pre=hab.kever.prefixer,
            payload=dict(
                oobi=oobi
            ))
        handler.msgs.append(msg)

        limit = 1.0
        tock = 0.25
        doist = doing.Doist(limit=limit, tock=tock)
        doist.do(doers=[handler])
        assert doist.tyme == limit

        obr = hby.db.oobis.get(keys=(oobi,))
        assert obr is not None

        assert len(notifier.signaler.signals) == 1
        signal = notifier.signaler.signals.popleft()
        assert signal.pad['r'] == '/notification'
        rid = signal.attrs['note']['i']

        note, _ = notifier.noter.get(rid)
        assert note.attrs == {'oobi': 'http://127.0.0.1:5642/oobi/Egw3N07Ajdkjvv4LB2Mhx2qxl6TOCFdWNJU6cYR_ImFg/witness/'
                                      'BGKVzj4ve0VSd8z_AmvhLg4lqcC_9WYX90k03q-R_Ydo?name=Phil',
                              'oobialias': 'Phil',
                              'r': '/oobi',
                              'src': 'EIaGMMWJFPmtXznY1IIiKDIrg-vIyge6mBl2QV8dDjI3'}

        msg = dict(
            pre=hab.kever.prefixer,
            payload=dict(
            ))
        handler.msgs.append(msg)

        limit = 1.0
        tock = 0.25
        doist = doing.Doist(limit=limit, tock=tock)
        doist.do(doers=[handler])
        assert doist.tyme == limit
        assert len(notifier.signaler.signals) == 0

        exn, atc = oobiing.oobiRequestExn(hab=hab, dest="EO2kxXW0jifQmuPevqg6Zpi3vE-WYoj65i_XhpruWtOg",
                                          oobi="http://127.0.0.1/oobi")
        assert exn.ked == {'a': {'dest': 'EO2kxXW0jifQmuPevqg6Zpi3vE-WYoj65i_XhpruWtOg',
                                 'oobi': 'http://127.0.0.1/oobi'},
                           'd': 'EGkcFuzBKKPI8MxP3u5Z0nxyuKOOu1GfWaWx2UT7mU_C',
                           'q': {},
                           'r': '/oobis',
                           't': 'exn',
                           'v': 'KERI10JSON0000c5_'}
        assert atc == (b'-HABEIaGMMWJFPmtXznY1IIiKDIrg-vIyge6mBl2QV8dDjI3-AABAABjXDLWfNtF'
                       b'GQAvJwJk-LeyzCXcCXLqxhPhQgiR45jZ-rzFoxjG2C3SaX7AbaGbm0XImx7XtK02'
                       b'YkjK792iDOIC')


def test_oobi_share_endpoint():
    with openMultiSig(prefix="test") as ((hby1, hab1), (hby2, hab2), (hby3, hab3)):
        app = falcon.App()
        oobiEnd = oobiing.OobiResource(hby=hby1)
        app.add_route("/oobi/groups/{alias}/share", oobiEnd, suffix="share")
        client = testing.TestClient(app)

        body = dict(oobis=[
            "http://127.0.0.1:3333/oobi",
            "http://127.0.0.1:5555/oobi",
            "http://127.0.0.1:7777/oobi"
        ])
        raw = json.dumps(body).encode("utf-8")

        result = client.simulate_post(path="/oobi/groups/test_1/share", body=raw)
        assert result.status == falcon.HTTP_400
        result = client.simulate_post(path="/oobi/groups/fake/share", body=raw)
        assert result.status == falcon.HTTP_404
        result = client.simulate_post(path="/oobi/groups/test_group1/share", body=raw)
        assert result.status == falcon.HTTP_200

        # Assert that a message has been send to each participant for each OOBI
        assert len(oobiEnd.postman.evts) == 6

