import pytest
import override_data
import utils
from data_transfer import database
from unittest.mock import *

TEST_QRS = [
    {
        "data": "+A2$B1$C3306083210$D8.6.9$ECYAN$FTRUE%QS$RFALSE$SF$TO$UN$VTRUE$W143AT143AB135AU131AK130AM089AJ087AH085AN084AH076AM075AF074AJ057AN050AN047AN043AK042AM039AI028AF020AH016AM015AV$X1$Y29$Z3847",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1AVRX4A8D6BF5TNJ4FRE7",
        "readable_time": "2024-03-08 03:22:30.557000+00:00",
    },
    {
        "data": "+A2$B1$C1590849534$D9.9.1$EJIMOTHY$FTRUE%QS$RFALSE$SN$TN$UF$VTRUE$W152AT152AB151AH148AE147AE142AJ140AJ135AU132AL131AL116AE113AI099AP082AL080AN065AH063AL062AP057AK056AK050AO048AJ047AN043AE041AM023AF020AJ016AE015AV$X3$Y21$Z1671",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1AVRX6AF1837YHJKWJ6AB",
        "readable_time": "2024-03-08 03:22:30.558000+00:00",
    },
    {
        "data": "+A2$B1$C9717814354$D1.8.1$EBRYAN$FFALSE%QS$RFALSE$SF$TN$UN$VTRUE$W149AB135AU130AK127AN104AG102AE099AO098AP084AH079AE078AE072AM062AM061AK058AN055AJ054AK040AN032AK031AE023AK017AI015AV$X3$Y9$Z148",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1AVRYJYCBPVQZA8TR9WZZ",
        "readable_time": "2024-03-08 03:22:30.558000+00:00",
    },
    {
        "data": "+A2$B1$C1789386197$D1.3.1$ENOAH$FTRUE%QS$RTRUE$SN$TN$UF$VFALSE$W143AT143AB142AF142AK142AJ142AI142AE140AL140AG140AH140AE140AH135AU134AG132AI131AI128AF126AH123AM122AN121AM117AF115AE110AP101AG098AM092AJ090AH088AE085AP080AF079AM075AJ070AJ066AN060AO059AJ058AP056AG053AJ052AF049AJ045AM044AG039AO036AO032AI026AO016AF015AV$X2$Y29$Z1538",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1AVRYCM3C2SCCGT06YCS0",
        "readable_time": "2024-03-08 03:22:30.558000+00:00",
    },
    {
        "data": "+A2$B1$C4234563609$D4.8.2$ECHRIS$FFALSE%QS$RTRUE$SO$TN$UN$VFALSE$W143AA135AU133AJ131AL126AO125AK117AI109AM108AH096AN090AH087AF084AH081AP077AG070AK066AG064AK057AH053AI051AL048AK041AN039AI036AE034AL025AO019AF015AV$X2$Y1$Z1768",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1AVRY0JMPZ8Q48RC35T6F",
        "readable_time": "2024-03-08 03:22:30.558000+00:00",
    },
    {
        "data": "+A2$B1$C2902576486$D8.8.7$EJOHN$FFALSE%QN$RTRUE$SO$TO$UO$VFALSE$W150AA149AI149AL149AJ149AK149AG141AG141AE141AH141AF141AG135AU132AJ131AI130AE126AG119AO117AG112AG110AK109AF106AL104AF096AG087AE086AJ085AP084AM076AM048AN046AJ043AF040AP033AE029AG024AN021AF017AK016AG015AV$X3$Y28$Z2910",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1AVRYX8K7R9AWF18501SE",
        "readable_time": "2024-03-08 03:22:30.558000+00:00",
    },
    {
        "data": "+A2$B10$C6776371931$D9.9.4$EDYLAN$FFALSE%QF$RFALSE$SF$TO$UF$VFALSE$W135AU134AT134AB129AE124AE115AK111AI108AO107AK092AH091AE086AO083AP058AO048AE032AG031AK029AH028AF027AM018AJ015AV$X2$Y14$Z3476",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1WZKAJ8BD1HJPS2760GKH",
        "readable_time": "2024-03-08 03:32:24.298000+00:00",
    },
    {
        "data": "+A2$B10$C7628656050$D2.2.3$ECYAN$FFALSE%QN$RFALSE$SN$TF$UO$VTRUE$W149AT149AA135AU131AP128AE127AI109AH099AE095AE094AN093AP091AP090AI089AP076AN073AM063AM057AJ053AO034AL024AM023AH020AG015AV$X3$Y5$Z3663",
        "blocklisted": False,
        "override": {},
        "ulid": "01HRE1WZKAAN2DC79SVKT83XWE",
        "readable_time": "2024-03-08 03:32:24.298000+00:00",
    },
]


def test_rollback_match():
    thing = database.Database
    test_db = database.Database()
    test_db.insert_documents("raw_qr", TEST_QRS)
    database.Database = MagicMock(return_value=test_db)
    # test normal
    with patch("builtins.input", side_effect=["0", "n", "1"]):
        override_data.main()
    for test_qr in test_db.find("raw_qr"):
        if "$B1$" in test_qr["data"]:
            assert test_qr["blocklisted"]
        else:
            assert not test_qr["blocklisted"]

    # test undo
    with patch("builtins.input", side_effect=["0", "y", "1"]):
        override_data.main()
    for test_qr in test_db.find("raw_qr"):
        assert not test_qr["blocklisted"]

    database.Database = thing


def test_blocklist_qr():
    thing = database.Database
    test_db = database.Database()
    test_db.insert_documents("raw_qr", TEST_QRS)
    database.Database = MagicMock(return_value=test_db)

    # test normal
    with patch("builtins.input", side_effect=["1", "n", "1", "cyaN"]):
        override_data.main()
    with patch("builtins.input", side_effect=["1", "n", "1", "bRYan"]):
        override_data.main()
    with patch("builtins.input", side_effect=["1", "n", "10", "dylaN"]):
        override_data.main()
    for test_qr in test_db.find("raw_qr"):
        if "$B1$" in test_qr["data"] and ("CYAN" in test_qr["data"] or "BRYAN" in test_qr["data"]):
            assert test_qr["blocklisted"]
        elif "$B10$" in test_qr["data"] and "DYLAN" in test_qr["data"]:
            assert test_qr["blocklisted"]
        else:
            assert not test_qr["blocklisted"]

    # test undo
    with patch("builtins.input", side_effect=["1", "y", "1", "BRyAN"]):
        override_data.main()
    for test_qr in test_db.find("raw_qr"):
        if "$B1$" in test_qr["data"] and "CYAN" in test_qr["data"]:
            assert test_qr["blocklisted"]
        elif "$B10$" in test_qr["data"] and "DYLAN" in test_qr["data"]:
            assert test_qr["blocklisted"]
        else:
            assert not test_qr["blocklisted"]

    database.Database = thing


def test_edit_data():
    thing = database.Database
    test_db = database.Database()
    test_db.insert_documents("raw_qr", TEST_QRS)
    database.Database = MagicMock(return_value=test_db)

    # test normal
    with patch(
        "builtins.input", side_effect=["2", "n", "1", "cyan", "time_from_far_to_amp", "3.14"]
    ):
        override_data.main()
    with patch("builtins.input", side_effect=["2", "n", "1", "cyan", "tele_amp", "420"]):
        override_data.main()
    with patch(
        "builtins.input", side_effect=["2", "n", "1", "bryan", "tele_failed_amplified", "5"]
    ):
        override_data.main()
    with patch("builtins.input", side_effect=["2", "n", "10", "dylan", "auto_speaker", "69"]):
        override_data.main()
    for test_qr in test_db.find("raw_qr"):
        if "$B1$" in test_qr["data"] and "CYAN" in test_qr["data"]:
            assert test_qr["override"] == {"time_from_far_to_amp": 3.14, "tele_amp": 420}
        elif "$B1$" in test_qr["data"] and "BRYAN" in test_qr["data"]:
            assert test_qr["override"] == {"tele_failed_amplified": 5}
        elif "$B10$" in test_qr["data"] and "DYLAN" in test_qr["data"]:
            assert test_qr["override"] == {"auto_speaker": 69}
        else:
            assert test_qr["override"] == {}

    # test clear overrides
    with patch("builtins.input", side_effect=["2", "y", "1", "cyan", "a", "0"]):
        override_data.main()
    with patch("builtins.input", side_effect=["2", "y", "1", "bryan", "a", "0"]):
        override_data.main()
    for test_qr in test_db.find("raw_qr"):
        if "$B10$" in test_qr["data"] and "DYLAN" in test_qr["data"]:
            assert test_qr["override"] == {"auto_speaker": 69}
        else:
            assert test_qr["override"] == {}

    database.Database = thing
