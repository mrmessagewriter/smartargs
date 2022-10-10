#!/usr/bin
"""
    smartargs

    This is a smarter replacement for getopts.
    This adds new features that getopts doesn't already handle:
        - better descriptions, with live data.
        - option lists (options that have distinct set of values)
        - callbacks (when used a function will be called.)
        - multiple instance options (the same option can be included multiple times, and each time,
            the value of the option is added to a list.)
        - boolean options
"""
import json
from columnizer import columnizer


class SmartArgsCommandLineParseError(Exception):
    pass


class SmartArgsUnknownOption(Exception):
    pass


class SmartArgsUndefinedValueExists(Exception):
    pass


class SmartArgsArgumentNotAllowed(Exception):
    pass


class SmartArgs:
    def __init__(self, columndisplay=None):
        self.options = []
        self.columndisplay = columndisplay
        if columndisplay is None:
            self.columndisplay = columnizer.Columnizer([columnizer.ColumnLineWrap(35),
                                                        columnizer.ColumnLineWrap(35),
                                                        columnizer.ColumnLineWrap(30)],
                                                       style=columnizer.ColumnTableStyleNone())
        return

    def print_menu(self):
        rows = []
        for opt in self.options:
            row = [opt.menu_name(), opt.description]
            if opt.allowedvalues is not None:
                row.append("allowed:" + str(opt.allowedvalues))
            rows.append(row)
        print(self.columndisplay.apply(rows))

    def add_option(self, option):
        """
        :type option: SmartArgsOption
        """
        self.options.append(option)

    def find_option(self, shortname=None, longname=None):  # type: (basestring , basestring) -> SmartArgsOption
        for opt in self.options:
            if longname and shortname and opt.longname == longname and opt.shortname == shortname:
                return opt
            if shortname and opt.shortname == shortname:
                return opt
            if longname and opt.longname == longname:
                return opt
        return None

    def parse(self, args):  # type: (list) -> (dict,list)
        remainders = []
        foundargs = {}

        # first do a generic processing of each of the arguments incoming.
        processed_list = []
        open_argument = None

        for index in range(0, len(args)):
            curarg = args[index]

            if curarg == "-" or curarg == "--":
                raise SmartArgsCommandLineParseError("- or -- may not be used standalone in the command line.")

            if open_argument is None and len(curarg) <= 1:
                continue

            if open_argument is not None and curarg == "=":
                continue

            if open_argument is not None:
                if curarg[0] == "-":
                    processed_list.append({"name": open_argument})
                    open_argument = None
                    index -= 1
                    continue
                processed_list.append({"name": open_argument, "value": curarg})
                open_argument = None
                continue

            if curarg[0] == "-":
                # short name argument
                if curarg[1] != "-":
                    argname = curarg[1]
                    if len(curarg) > 2:
                        processed_list.append({"name": argname, "value": curarg[2:]})
                    else:
                        opt = self.find_option(shortname=argname)
                        if opt is None:
                            raise SmartArgsUnknownOption("option '%s' is not defined." % argname)
                        if opt.hasvalue:
                            open_argument = argname
                        else:
                            processed_list.append({"name": argname})
                # long name argument
                else:
                    argname = curarg[2:]
                    if argname.find("=") > -1:
                        if argname[-1] == "=":
                            open_argument = argname[:-1]
                            continue
                        argparts = argname.split("=")
                        processed_list.append({"name": argparts[0], "value": argparts[1]})
                    else:
                        opt = self.find_option(longname=argname)
                        if opt is None:
                            raise SmartArgsUnknownOption("option '%s' is not defined." % argname)
                        if opt.hasvalue:
                            open_argument = argname
                        else:
                            processed_list.append({"name": argname})
            else:
                if open_argument is None:
                    remainders = args[index:]
                    break

        for arg in processed_list:
            argname = arg["name"]
            argvalue = None
            if "value" in arg:
                argvalue = arg["value"]

            if len(argname) == 1:
                opt = self.find_option(shortname=argname)
            else:
                opt = self.find_option(longname=argname)

            if opt is None:
                raise SmartArgsUnknownOption("the option '%s' was not defined." % argname)

            if opt.localname in foundargs and not opt.islist:
                raise TypeError(
                    "cannot use the argument '%s' more then once, because it is not a list." % argname)

            if opt.hasvalue and argvalue is None:
                raise ValueError("the option '%s' does not have an associated value" % argname)

            if not opt.hasvalue and argvalue is not None:
                raise SmartArgsUndefinedValueExists(
                    "the option '%s' had the associated value '%s', but was not defined as having one." %
                    (
                        argname,
                        argvalue
                    )
                )

            if opt.allowedvalues is not None:
                if argvalue not in opt.allowedvalues:
                    raise SmartArgsArgumentNotAllowed(
                        "the option '%s' allows only '%s' but was set to '%s'" % (argname, opt.allowedvalues, argvalue))

            if opt.datatype is not None and opt.hasvalue is not None:
                if opt.datatype == "int":
                    try:
                        argvalue = int(argvalue)
                    except ValueError:
                        raise ValueError(
                            "the option '%s' is defined as an int but the value '%s' is not a integer convertible type."
                            % (
                                argname,
                                argvalue
                            )
                        )

                if opt.datatype == "float":
                    try:
                        argvalue = float(argvalue)
                    except ValueError:
                        raise ValueError(
                            "the option '%s' is defined as a float but the value '%s' is not a float convertible type."
                            % (
                                argname,
                                argvalue
                            )
                        )

                if opt.datatype == "boolean":
                    try:
                        argvalue = bool(int(argvalue))
                    except ValueError:
                        if argvalue[0].lower() == "t" or argvalue[0].lower() == "f":
                            if argvalue.lower() == "true":
                                argvalue = True
                            elif argvalue.lower() == "false":
                                argvalue = False
                        else:
                            raise ValueError(
                                "the option '%s' is defined as a boolean but the value '%s' is not a boolean." % (
                                    argname, argvalue))

            if opt.callback is not None:
               argvalue = opt.callback(argname, argvalue)

            if bool(opt.islist):
                if opt.localname in foundargs:
                    x = foundargs[opt.localname]
                    if isinstance(x, list):
                        foundargs[opt.localname] = list(x)
                else:
                    foundargs[opt.localname] = []
                foundargs[opt.localname].append(argvalue)
            else:
                foundargs[opt.localname] = argvalue




        for opt in self.options:
            if opt.default and opt.localname not in foundargs:
                foundargs[opt.localname] = opt.default

        return foundargs, remainders


class SmartArgsOption:
    validKeys = ["localname", "shortname", "longname", "hasvalue", "default", "callback", "allowedvalues",
                 "description", "datatype", "islist"]

    def __init__(self, *args, **kvargs):
        self.values = {
            "localname": None,
            "hasvalue": False,
            "shortname": None,
            "longname": None,
            "default": None,
            "callback": None,
            "allowedvalues": None,
            "description": None,
            "datatype": None,
            "islist": False
        }

        if len(args):
            raise ValueError("No standard arguments allowed.")

        if len(kvargs.keys()) == 0:
            raise TypeError("Empty named arguments not allowed")

        if "shortname" not in kvargs.keys() and "longname" not in kvargs.keys():
            raise ValueError("Must include either a shortname or a longname")

        for key in kvargs:
            if self.__class__.validKeys.count(key) == 0:
                raise KeyError("Invalid key '%s'" % key)
            self.values[key] = kvargs[key]

        if self.values["localname"] is None:
            localname = self.values["longname"]
            if localname is None:
                localname = self.values["shortname"]
            self.values["localname"] = localname

        if self.values["datatype"] is not None:
            valid_datatypes = ["float", "int", "boolean"]
            if self.values["datatype"] not in valid_datatypes:
                raise TypeError(
                    "datatype must be one of: %s but was %s" % (valid_datatypes, self.values["datatype"]))

        if "allowedvalues" in kvargs or "datatype" in kvargs or "islist" in kvargs:
            self.values["hasvalue"] = True

        return

    def menu_name(self):
        result = ""
        if self.shortname is not None:
            result += "-" + self.shortname
            if "hasvalue" in self.values:
                result += " VALUE"
        if self.longname is not None:
            if len(result):
                result += " , "
            result += "--" + self.longname
            if "hasvalue" in self.values:
                result += "=VALUE"
        return result

    def __repr__(self):
        return str(json.dumps(self.values))

    def __eq__(self, other):
        return id(self) == id(other)

    def __getattr__(self, item):
        return self.values[item]

    def __getitem__(self, item):
        return self.values[item]


if __name__ == "__main__":
    pyargs = SmartArgs()
    pyargs.add_option(SmartArgsOption(shortname="a", longname="address",
                                      description="address for the the users, perhaps their real names as well."))
    pyargs.add_option(
        SmartArgsOption(shortname="b", longname="bloodtype",
                        allowedvalues=["a", "b", "a+", "a-", "ab+", "ab-", "o", "o+", "o-"],
                        description="bloodtype of the users."))
    pyargs.print_menu()
