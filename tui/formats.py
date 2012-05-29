"""TUI Textual User Interface - A sane command line user interface.

Author: Joel Hedlund <yohell@ifm.liu.se>

This module contains format classes for use in textual user interfaces.

If you have problems with this package, please contact the author.

"""
__version__ = "1.1.0"
__copyright__ = "Copyright (c) 2011 Joel Hedlund."
__license__ = "MIT"

import os
import re
import shlex

class FormatError(Exception):
    """\
    Base class for all exceptions raised in the formats module.
    Do not instantiate directly. Use the proper subclass instead.

    """
    def __init__(self):
        raise NotImplementedError("Do not instantiate directly. Use the proper subclass instead.")

    def __str__(self):
        return self.sMessage
    


class DeveloperError(FormatError):
    """\
    Raised when a format is instantiated improperly.

    """
    def __init__(self, msg):
        self.sMessage = msg

    def __str__(self):
        return self.sMessage
    


class BadNumberOfArgumentsError(FormatError):
    """\
    Raised when a Format parser has been given the wrong number of
    arguments.

    """
    def __init__(self, format, required, supplied):
        sErrorMsg = "%s requires %s arguments and got %s."
        sErrorMsg %= (format, required, supplied)
        self.sMessage = sErrorMsg
        self.sFormat = str(format)
        self.iRequired = required
        self.iSupplied = supplied

    def format(self):
        return self.sFormat

    def required(self):
        return self.iRequired

    def supplied(self):
        return self.iSupplied
    

class BadArgumentError(FormatError):
    """\
    Raised when a Format parser encounters an argument that doesn't conform
    to the Format.

    """
    def __init__(self, format, argument, details):
        sErrorMsg = "%s is not an acceptable argument for %s (%s)."
        sErrorMsg %= (repr(argument), format, details)
        self.sMessage = sErrorMsg
        self.sFormat = str(format)
        self.sArgument = argument
        self.sDetails = details
    
    def format(self):
        return self.sFormat

    def argument(self):
        return self.sArgument

    def details(self):
        return self.sDetails

def default_presenter(value):
    s = str(value)
    for c in s:
        if c.isspace():
            return repr(s)
    return s

_UNSET = []
class Format:
    """\
    A data format for an Option.

    """
    default = None
    def __init__(self, shortname, parser, presenter = default_presenter, nargs = 1, docs = '',
                 acceptemptystring = False, acceptedspecials = None,
                 pargs = None, kwargs = None, addspecialsdocs = True, default = _UNSET):
        """\
        Instantiate a Format object. 
        IN:
        shortname <str>:
            The shortest word that accurately describes the Format.
        parser <callable>:
            A function that parses a string value and returns a sanity
            checked value in the correct type. The function should accept
            one string argument and possibly also optional positional
            and/or keyword arguments. The function should raise any kind
            of Exception if the string argument is not parsable into the
            correct format or fails sanity check.
        presenter = str <callable>:
            The inverse of parser. Should take a value as returned by
            parser and return a string that can be used with parser to
            recreate the value. Should accept one argument of the same
            type as returned by parser and possibly also optional
            positional and/or keyword arguments.
        nargs = 1 <int>:
            How many value parameters does this format require?
        docs = '' <str>:
            User friendly description of the format. '' means use a string
            that tells how many arguments the format requires.
        acceptemptystring = False <bool>:
            Is the empty string an accepted argument? Note that in order for
            an argument passed from within python to be interpreted as an
            empty string you will have to pass something like "''" or '""'.
        acceptedspecials = None <list str>, <str> or None:
            Any strings with special mening that should be accepted even
            though they do not represent a path to a readable file. A string
            value will be interpreted as a list of one item. None means
            use the empty list, e.g: there are no special exceptions. If
            acceptemptystring is set then '' will be added to the list after
            all other interpretations are done.
        pargs = None <list x> or None:
            Any extra positional arguments that should be fed to the
            format on each parse/present.
        kwargs = None <dict str x> or None:
            Any extra keyword arguments that should be fed to the format
            on each parse/present.
        
        NOTE:
            The most common argument formats already have premade Format
            subclasses, but if none of them are suitable - just
            instantiate a Format object with your parser of taste, 
            and possibly a presenter. For weirder option formats, like 
            for example such that take a variable number of arguments,
            all you need to do is subclass it and adapt the methods
            accordingly.

            Also, if an argument provided by the user is found among the
            accepted specials it will be returned unparsed, so the
            developer must check on this manually at a later stage.
            
        """
        self.sShortName = shortname
        self.cParser = parser
        self.cPresenter = presenter
        if nargs < 0:
            raise ValueError("nargs must be >= 0.")
        self.iNArgs = nargs

        if acceptedspecials is None:
            acceptedspecials = []
        elif isinstance(acceptedspecials, str):
            acceptedspecials = [acceptedspecials]
        if acceptemptystring and '' not in acceptedspecials:
            acceptedspecials.append('')
        self.lsAcceptedSpecials = acceptedspecials

        if docs:
            self.sDocs = docs
        elif nargs == 0:
            self.sDocs = "Takes no argument."
        else:
            if nargs == 1:
                self.sDocs = "Takes 1 argument."
            else:
                self.sDocs = "Takes %s arguments." % nargs
        if acceptedspecials and nargs > 0 and addspecialsdocs:
            self.sDocs += " These special arguments are also accepted: %s." % acceptedspecials
        if pargs is None:
            pargs = []
        self.lxPArgs = pargs
        if kwargs is None:
            kwargs = {}
        self.dsxKWArgs = kwargs
        
        if default is not _UNSET:
            self.default = default


    def __str__(self):
        return self.sShortName



    def parse(self, args):
        """\
        Pops the first self.nargs() values from the args list, feeds them
        to the parser and return the result. Subclass and override if
        this is not the desired behavior. This function will change the
        args list.
        IN:
        args <list str>:
            The list of arguments available for parsing. Will be changed by
            the method.
        OUT:
            Whatever is returned by the callback. "A list of ..." if
            nargs > 1. Should never return None.

        """
        if len(args) < self.iNArgs:
            raise BadNumberOfArgumentsError(self, self.iNArgs, len(args))

        if self.iNArgs == 0:
            return self.cParser(*self.lxPArgs, **self.dsxKWArgs)
        elif self.iNArgs == 1:
            sValue = args.pop(0)
            if sValue in self.lsAcceptedSpecials:
                return sValue
            try:
                return self.cParser(sValue, *self.lxPArgs, **self.dsxKWArgs)
            except Exception, e:
                raise BadArgumentError(self, sValue, str(e))
        else:
            lxValues = []
            for i in range(self.iNArgs):
                sValue = args.pop(0)
                if sValue in self.lsAcceptedSpecials:
                    lxValues.append(sValue)
                try:
                    lxValues.append(self.cParser(sValue, *self.lxPArgs, **self.dsxKWArgs))
                except Exception, e:
                    raise BadArgumentError(self, sValue, str(e))
            return lxValues
        


    def parsestr(self, argstr):
        """\
        Parse arguments found in settings files.
        IN:
        argstr <str>:
            The string that should be parsed. '""' or "''" means pass an
            empty string.
        *pargs <list x> [optional]:
            Any optional positional arguments will be piped to the parser.
            callback.
        **kwargs <dict x x> [optional]:
            Any optional keyword arguments will be piped to the parser.
        OUT:
            Whatever is returned by the callback. "A list of ..." if
            nargs > 1. Should never return None.
        NOTE:
            When parsing Boolean Flag option formats that do not accept
            argument values on the command line, "1", "yes" or "true"
            for True, or "0", "no" or "false" for False, case insensitive.

        """
        args = shlex.split(argstr, comments = True)

        if len(args) == 0:
            raise BadNumberOfArgumentsError(self, 1, 0)
        
        if self.iNArgs == 0:
            sValue = args.pop(0)
            v = sValue.lower()
            if v in ['1', 'yes', 'true', 'on']:
                return True
            elif v in ['0', 'no', 'false', 'off']:
                return False
            else:
                raise BadArgumentError(self, sValue, "Allowed values include 'True' and 'False', among others")
            
        elif len(args) != self.iNArgs:
            raise BadNumberOfArgumentsError(self, self.iNArgs, len(args))
        
        return self.parse(args)



    def shortname(self):
        """\
        Return the short name of the Format.

        """
        return self.sShortName


    
    def strvalue(self, value):
        """\
        Return a user friendly string formatted value.
        IN:
        value <x>:
            What to string convert.
        OUT:
            A string that can be used with parsevalue to recreate the
            value.

        """
        if self.iNArgs > 1:
            sValue = " " .join(map(self.cPresenter, value))
        else:
            sValue = self.cPresenter(value, *self.lxPArgs, **self.dsxKWArgs)
        return sValue

    def nargs(self):
        return self.iNArgs

    def docs(self):
        return self.sDocs

    

class Flag(Format):
    """\
    An option that does not digest any additional arguments. Its mere
    presence on the command line sets it. In settings files: use "1",
    "yes" or "true" for True, or "0", "no" or "false" for False,
    case insensitive.
    
    """
    default = False
    def __init__(self, commandline_value = True,
                 acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a Flag Format object.
        IN:
        commandline_value <bool>:
            What to return if the value is encountered on the command line.

        """
        Format.__init__(self, 'Flag', lambda: commandline_value, nargs = 0,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)
        


class Int(Format):
    """\
    A format that accept one integer value.

    """
    default = 0
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate an Int Format object.

        """
        Format.__init__(self, 'Int', self._parser,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)

    def _parser(self, argument):
        try:
            return int(argument)
        except ValueError:
            raise ValueError("cannot transform it to integer")



class PositiveInt(Format):
    """\
    A format that accepts one positive integer value.

    """
    default = 0
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a PositiveInt Format object.
    
        """
        Format.__init__(self, 'PositiveInt', self._parser, docs = "Must be > 0.",
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)

        

    def _parser(self, argument):
        try:
            i = int(argument)
        except ValueError:
            raise ValueError("cannot transform it to integer")
        if i < 1:
            raise ValueError("it is < 1")
        return i



class NonnegativeInt(Format):
    """\
    A format that accepts one positive integer value.

    """
    default = 1
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a PositiveInt Format object.
    
        """
        Format.__init__(self, 'NonnegativeInt', self._parser, docs = "Must not be < 0.",
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)

        

    def _parser(self, argument):
        try:
            i = int(argument)
        except ValueError:
            raise ValueError("cannot transform it to integer")
        if i < 0:
            raise ValueError("it is < 0")
        return i



class BoundedInt(Format):
    """\
    A format that accepts one integer value in a given interval

    """
    default = 0
    def __init__(self, lowerbound = None, upperbound = None,
                 acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a PositiveInt Format object.
        IN:
        lowerbound = None <int> or None:
            The lowest allowed value. None means unbound downwards.
        upperbound = None <int> or None:
            The highest allowed value. None means unbound upwards.
        NOTE:
            Both bounds cannot be None simultaneously.
    
        """
        if lowerbound is None:
            if upperbound is None:
                raise DeveloperError("Both upper and lower bounds cannot be None simultaneously.")
            sShortName = "Int<=%s" % upperbound
        else:
            if upperbound is None:
                sShortName = "Int>=%s" % lowerbound
            else:
                if upperbound < lowerbound:
                    raise DeveloperError("Upper bound must not be lower than lower bound.")
                sShortName = "Int%s-%s" % (lowerbound, upperbound)
        self.iLowerBound = lowerbound
        self.iUpperBound = upperbound
        Format.__init__(self, sShortName, self._parser, docs = "Must be in the given range.",
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)

        

    def _parser(self, argument):
        try:
            i = int(argument)
        except ValueError:
            raise ValueError("cannot transform it to integer")
        if not (self.iLowerBound is None) and i < self.iLowerBound:
            raise ValueError("it is < %s" % self.iLowerBound)
        if not (self.iUpperBound is None) and i > self.iUpperBound:
            raise ValueError("it is > %s" % self.iUpperBound)
        return i



class Float(Format):
    """\
    A format that accepts one Float value.

    """
    default = 0.0
    def __init__(self, formatter = None, acceptemptystring = False,
                 acceptedspecials = None):
        """\
        Instantiate a Float Format object.
        IN:
        formatter = None <str> or None:
            A positional python string formatter for a float value. Used
            with the presenter. None means use str() to format.

        """
        kwargs = {'formatter': formatter}
        Format.__init__(self, 'Float', self._parser, presenter = self._presenter,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring, kwargs = kwargs)

    def _parser(self, argument, **kwargs):
        try:
            return float(argument)
        except ValueError:
            raise ValueError("cannot transform it to float")

    def _presenter(self, value, formatter = '%.2f'):
        if formatter is None:
            return str(value)
        else:
            return formatter % value


        
class BoundedFloat(Format):
    """\
    A format that accepts one integer value in a given interval

    """
    default = 0.0
    def __init__(self, lowerbound = None, upperbound = None, formatter = None,
                 acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a PositiveInt Format object.
        IN:
        lowerbound = None <float> or None:
            The lowest allowed value. None means unbound downwards.
        upperbound = None <float> or None:
            The highest allowed value. None means unbound upwards.
        formatter = None <str> or None:
            A positional python string formatter for a float value. Used
            with the presenter. None means use str() to format.
        
        NOTE:
            Both bounds cannot be None simultaneously.
    
        """
        if lowerbound is None:
            if upperbound is None:
                raise DeveloperError("Both upper and lower bounds cannot be None simultaneously.")
            sShortName = "Float<=%s" % upperbound
        else:
            if upperbound is None:
                sShortName = "Float>=%s" % lowerbound
            else:
                if upperbound < lowerbound:
                    raise DeveloperError("Upper bound must not be lower than lower bound.")
                sShortName = "Float%s-%s" % (lowerbound, upperbound)
        self.nLowerBound = lowerbound
        self.nUpperBound = upperbound
        kwargs = {'formatter': formatter}
        Format.__init__(self, sShortName, self._parser, self._presenter,
                        docs = "Must be in the given range.",
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring, kwargs = kwargs)

        

    def _parser(self, argument, **kwargs):
        try:
            n = float(argument)
        except ValueError:
            raise ValueError("cannot transform it to float")
        if not (self.nLowerBound is None) and n < self.nLowerBound:
            raise ValueError("it is < %s" % self.nLowerBound)
        if not (self.nUpperBound is None) and n > self.nUpperBound:
            raise ValueError("it is > %s" % self.nUpperBound)
        return n


    def _presenter(self, value, formatter = None):
        if formatter is None:
            return str(value)
        else:
            return formatter % value



class NonnegativeFloat(Format):
    """\
    A format that accepts one integer value in a given interval

    """
    default = 0.0
    def __init__(self, formatter = None, acceptemptystring = False,
                 acceptedspecials = None):
        """\
        Instantiate a NonnegativeFloat Format object.
        IN:
        formatter = None <str> or None:
            A positional python string formatter for a float value. Used
            with the presenter. None means use str() to format.
        
        """
        sShortName = "Float<=0"
        kwargs = {'formatter': formatter}
        Format.__init__(self, sShortName, self._parser, self._presenter,
                        docs = "Must be >= 0.",
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring, kwargs = kwargs)

        

    def _parser(self, argument, **kwargs):
        try:
            n = float(argument)
        except ValueError:
            raise ValueError("cannot transform it to float")
        if n < 0:
            raise ValueError("it is < 0")
        return n


    def _presenter(self, value, formatter = None):
        if formatter is None:
            return str(value)
        else:
            return formatter % value



class FloatPercentage(Format):
    """\
    A format that accepts one Float value between 0.0 and 100.0.

    """
    default = 0.0
    def __init__(self, acceptemptystring = False, acceptedspecials = None,
                 formatter = None):
        """\
        Instantiate a Float Format object.
        formatter = None <str> or None:
            A positional python string formatter for a float value. Used
            with the presenter. None means use str() to format.

        """
        kwargs = {'formatter': formatter}
        Format.__init__(self, 'Percentage', self._parser, self._presenter,
                        docs = "Value must be between 0.0 and 100.0.",
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring, kwargs = kwargs)



    def _parser(self, argument, **kwargs):
        try:
            n = float(argument)
        except ValueError:
            raise ValueError("cannot transform it to float")
        if n > 100.0:
            raise ValueError("it is > 100.0")
        if n < 0.0:
            raise ValueError("it is < 0.0")
        return n
        

    def _presenter(self, value, formatter = None):
        if formatter is None:
            return str(value)
        else:
            return formatter % value


        
class String(Format):
    """\
    A format that accepts one String value.

    """
    default = ''
    def __init__(self):
        """\
        Instantiate a Float Format object.

        """
        Format.__init__(self, 'String', str)



class ReadableFile(Format):
    """\
    A format that accepts one readable file.

    """
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a ReadableFile Format object. 

        """
        sDocs = "A (path to a) readable file."
        Format.__init__(self, 'ReadableFile', self._parser, docs = sDocs,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)


    def _parser(self, argument):
        if argument in self.lsAcceptedSpecials:
            return argument
        try:
            f = open(argument)
            f.close()
        except IOError, e:
            raise ValueError(e.strerror)
        return argument
        

        
class WritableFile(Format):
    """\
    A format that accepts one writable file. Nonexisting files will be
    created if possible.

    """
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a WritableFile Format object.

        """
        sDocs = "A (path to a) writable file. Nonexisting files will be created if possible. Otherwise the program will halt."
        Format.__init__(self, 'WritableFile', self._parser, docs = sDocs,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)


    def _parser(self, argument):
        if argument in self.lsAcceptedSpecials:
            return argument
        try:
            f = open(argument, 'a')
            f.close()
        except IOError, e:
            raise ValueError(e.strerror)
        return argument
        

        
class ReadableDir(Format):
    """\
    A format that accepts one readable directory.

    """
    default = '.'
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a ReadableDir Format object.

        """
        sDocs = "A (path to a) readable directory."
        Format.__init__(self, 'ReadableDir', self._parser, docs = sDocs,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)


    def _parser(self, argument):
        if argument in self.lsAcceptedSpecials:
            return argument
        if not os.access(argument, os.R_OK):
            raise ValueError('it does not exist')
        elif not os.path.isdir(argument):
            raise ValueError('it is not a directory')
        elif not os.access(argument, os.R_OK):
            raise ValueError('it is not readable')
        return argument
        

        
class WritableDir(Format):
    """\
    A format that accepts one writable file. Nonexisting files will be
    created if possible.

    """
    default = '.'
    def __init__(self, acceptemptystring = False, acceptedspecials = None):
        """\
        Instantiate a Float Format object. 

        """
        sDocs = "A (path to a) writable directory. Nonexisting directories will be created if possible. Otherwise the program will halt."
        Format.__init__(self, 'WritableDir', self._parser, docs = sDocs,
                        acceptedspecials = acceptedspecials,
                        acceptemptystring = acceptemptystring)


    def _parser(self, argument):
        if argument in self.lsAcceptedSpecials:
            return argument
        if not os.path.isdir(argument):
            try:
                os.mkdir(argument)
            except Exception:
                raise ValueError('it does not exist and cannot be created')
        elif not os.access(argument, os.W_OK):
            raise ValueError('it is not writable')
        return argument
        

        
class Choice(Format):
    """\
    A format that accepts one string out of a given set of strings.

    """
    def __init__(self, choices = None, acceptemptystring = False,
                 acceptedspecials = None, casesensitive = False):
        """\
        Instantiate a Choice Format object.
        IN:
        choices = None <list str>:
            The list of legal choices for this option. None is not accepted.

        """
        if len(choices) < 2:
            raise DeveloperError("Must have at least two choices")
        sCS = 'case sensitive'
        if not casesensitive:
            choices = map(lambda x: x.upper(), choices)
            sCS = 'case insensitive'
        kwargs = {'choices': choices, 'casesensitive': casesensitive}
        sChoices = ', '.join(map(repr, choices[:-1]))
        sChoices += ' and ' + repr(choices[-1])
        sDocs = "Accepted values are %s, %s." % (sChoices, sCS)
        Format.__init__(self, 'Choice', self._parser, presenter = self._presenter,
                        acceptedspecials = acceptedspecials, docs = sDocs,
                        acceptemptystring = acceptemptystring, kwargs = kwargs)

    def _parser(self, argument, choices = None, casesensitive = False):
        if not casesensitive:
            argument = argument.upper()
        if not argument in choices:
            raise ValueError("it's not among the legal choices")
        return argument

    def _presenter(self, value, **kwargs):
        return str(value)


class RegEx(Format):
    """A format that accepts a regular expression."""
    default = ''
    def __init__(self, acceptemptystring=None, acceptedspecials=None, flags=0):
        """flags should be an integer and is passed to re.compile. It can 
        also be a string of one or more of the letters 'iLmsux' (the short 
        names of the re flags).
        """
        if isinstance(flags, str):
            flags = flags.upper()
            if flags.strip('ILMSUX'):
                raise DeveloperError('illegal flags')
            flags = reduce(lambda i, flag: i | getattr(re, flag), flags, 0)
        docs = "A python re (a regular experssion)."
        Format.__init__(self, 
                        shortname='RegEx', 
                        parser=re.compile, 
                        presenter=lambda r: repr(r.pattern) if r else '', 
                        docs=docs,
                        acceptemptystring=acceptemptystring, 
                        acceptedspecials=acceptedspecials)
