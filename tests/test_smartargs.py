from unittest import TestCase
from smartargs import smartargs


class TestSmartArgsOption(TestCase):
    def test_should_not_allow_unnamed_arguments(self):
        with self.assertRaises(ValueError):
            smartargs.SmartArgsOption("a")

    def test_should_not_allow_unknown_named_arguments(self):
        with self.assertRaises(ValueError):
            smartargs.SmartArgsOption(unknown="GRATE!")

    def test_should_allow_known_named_arguments(self):
        for argumentName in smartargs.SmartArgsOption.validKeys:
            args = []
            kvargs = {argumentName: "boolean", "shortname": "a"}
            smartargs.SmartArgsOption(*args, **kvargs)

    def test_should_allow_only_known_datatypes(self):
        with self.assertRaises(TypeError):
            smartargs.SmartArgsOption(shortname="a", datatype="X")
        smartargs.SmartArgsOption(shortname="a", datatype="int")
        smartargs.SmartArgsOption(shortname="a", datatype="float")
        smartargs.SmartArgsOption(shortname="a", datatype="boolean")

    def test_should_not_allow_empty_arguments(self):
        with self.assertRaises(TypeError):
            smartargs.SmartArgsOption()

    def test_should_set_named_value(self):
        pyoption = smartargs.SmartArgsOption(shortname="x")
        self.assertEqual(pyoption["shortname"], "x", "shortname not found in pyoption")
        self.assertEqual(pyoption.shortname, "x", "shortname not found in pyoption")


class TestSmartArgs(TestCase):
    def test_should_only_allow_SmartArgsOption(self):
        testarg = smartargs.SmartArgs()
        x = smartargs.SmartArgsOption(shortname="a")
        testarg.add_option(x)
        self.assertIn(x, testarg.options)

    def test_should_parse_single_character_boolean(self):
        testarg = smartargs.SmartArgs()

        opt = smartargs.SmartArgsOption(shortname="a")
        testarg.add_option(opt)

        opt = smartargs.SmartArgsOption(shortname="t")
        testarg.add_option(opt)

        foundargs, remainders = testarg.parse(["-a", "-t", "remainders"])
        self.assertEqual({"a": None, "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_be_able_to_find_option(self):
        testarg = smartargs.SmartArgs()
        a = smartargs.SmartArgsOption(shortname="A", longname="EH")
        b = smartargs.SmartArgsOption(shortname="B", longname="BEE")
        c = smartargs.SmartArgsOption(shortname="C", longname="CEE")

        testarg.add_option(a)
        testarg.add_option(b)
        testarg.add_option(c)

        self.assertEqual(testarg.find_option(shortname="A"), a, "short name not matched")
        self.assertEqual(testarg.find_option(longname="BEE"), b, "long name not matched")
        self.assertEqual(testarg.find_option(shortname="A", longname="EH"), a, "short and long names did not match")

    def test_should_parse_single_character_with_value(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(shortname="a", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse(["-a", "AVALUE", "-t", "remainders"])
        self.assertDictEqual({"a": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_single_character_with_buttedup_value(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(shortname="a", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse(["-aAVALUE", "-t", "remainders"])
        self.assertDictEqual({"a": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_not_parse_unknown_shortname_with_buttedup_value(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(shortname="a", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        with self.assertRaises(smartargs.SmartArgsUnknownOption):
            testarg.parse(["-bAVALUE", "-t", "remainders"])

    def test_should_parse_longname_with_value(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=False))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=False))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse(["--test1", "AVALUE", "-t", "remainders"])
        self.assertDictEqual({"test1": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_longname_with_seperated_equalsign_and_value(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=False))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=False))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse(["--test1", "=", "AVALUE", "-t", "remainders"])
        self.assertDictEqual({"test1": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_longname_with_equalsign(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse(["--test1=", "AVALUE", "-t", "--test2=AVALUE", "remainders"])
        self.assertDictEqual({"test1": "AVALUE", "test2": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_parse_longname_with_localname(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(localname="ppp", longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse(["--test1=", "AVALUE", "-t", "--test2=AVALUE", "remainders"])
        self.assertDictEqual({"ppp": "AVALUE", "test2": "AVALUE", "t": None}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_should_return_defaults(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(longname="test1", hasvalue=True, default="default1"))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True, default="default2"))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True, default="default3"))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        foundargs, remainders = testarg.parse([])
        self.assertDictContainsSubset({"test1": "default1", "test2": "default2"}, foundargs)

    def callback_test_function(self, name, value):
        print(f"name={name}, value={value}")
        self.callback_test_called = True

    def test_should_make_callback_when_parsed(self):
        testarg = smartargs.SmartArgs()
        self.callback_test_called = False
        testarg.add_option(
            smartargs.SmartArgsOption(callback=self.callback_test_function, longname="test1", hasvalue=True))
        testarg.add_option(
            smartargs.SmartArgsOption(callback=self.callback_test_function, longname="test2", hasvalue=True))
        testarg.add_option(
            smartargs.SmartArgsOption(callback=self.callback_test_function, longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(callback=self.callback_test_function,
                                                     shortname="t",
                                                     hasvalue=False))
        testarg.parse(["--test1=", "AVALUE", "-t", "--test2=AVALUE", "remainders"])
        self.assertTrue(self.callback_test_called, "Callback failed")

    def test_should_only_allow_values_from_set(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(
            smartargs.SmartArgsOption(
                longname="test1",
                hasvalue=True,
                allowedvalues=["default", "AVALUE", "GRASS"],
                default="default1"
            )
        )
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True, default="default2"))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True, default="default3"))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=False))
        with self.assertRaises(smartargs.SmartArgsArgumentNotAllowed):
            testarg.parse(["--test1=", "NOTGRASS"])
        testarg.parse(["--test1=", "GRASS"])

    def test_should_add_multiple_items_as_list(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(localname="ppp", longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=True, islist=True))
        foundargs, remainders = testarg.parse(
            ["--test1=", "AVALUE", "-t5", "-t1", "-t3", "-t4", "-t5", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": ["5", "1", "3", "4", "5"]}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_add_multiple_items_as_list_asintegers(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(localname="ppp", longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=True, islist=True, datatype="int"))
        foundargs, remainders = testarg.parse(
            ["--test1=", "AVALUE", "-t5", "-t1", "-t3", "-t4", "-t5", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": [5, 1, 3, 4, 5]}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_add_multiple_items_as_list_asfloats(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(localname="ppp", longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=True, islist=True, datatype="float"))
        foundargs, remainders = testarg.parse(
            ["--test1=", "AVALUE", "-t5", "-t1.1", "-t3", "-t4.2", "-t5", "--test2=AVALUE", "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE", "test2": "AVALUE", "t": [5.0, 1.1, 3.0, 4.2, 5.0]}, foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_add_multiple_items_as_list_asbools(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(localname="ppp", longname="test1", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test2", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(longname="test3", hasvalue=True))
        testarg.add_option(smartargs.SmartArgsOption(shortname="t", hasvalue=True, islist=True, datatype="boolean"))
        testarg.add_option(smartargs.SmartArgsOption(shortname="h", hasvalue=True, islist=True, datatype="boolean"))
        foundargs, remainders = testarg.parse(
            ["--test1=", "AVALUE", "-t0", "-t1", "-t3", "-t4", "-t0", "-hTrue", "-hFalse", "-htrue", "-hfalse",
             "--test2=AVALUE",
             "remainders"])
        self.assertDictContainsSubset({"ppp": "AVALUE",
                                       "test2": "AVALUE",
                                       "h": [True, False, True, False],
                                       "t": [False, True, True, True, False]},
                                      foundargs)
        self.assertEqual(["remainders"], remainders)

    def test_should_not_parse_non_booleans(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(shortname="h", hasvalue=True, islist=True, datatype="boolean"))
        with self.assertRaises(ValueError):
            testarg.parse(["-hX", "remainders"])

    def test_should_not_allow_more_then_one_instance_of_singular_argument(self):
        testarg = smartargs.SmartArgs()
        testarg.add_option(smartargs.SmartArgsOption(shortname="a"))
        with self.assertRaises(TypeError):
            testarg.parse(["-a", "-a"])
