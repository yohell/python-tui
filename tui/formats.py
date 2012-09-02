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
    """Base class for exceptions raised while converting arguments to values."""
    def __str__(self):
        return self.message

class BadArgument(FormatError):
    """Raised when Formats are given incompatible literals."""
    
    def __init__(self, argument, message):
        """
        value is the bad value or string literal, or a tui instance to use 
        value[name].
        """
        self.argument = argument
        self.message = message

class BadNumberOfArguments(FormatError):
    """Raised when the user has supplied the wrong number of arguments.""" 

    def __init__(self, required, given, message=None):
        self.required = required
        self.given = given
        if message is None:
            message = "requires %d arguments and was given %d" % (required, given)
        self.message = message

def default_presenter(value):
    s = str(value)
    for c in s:
        if c.isspace():
            return repr(s)
    return s

_UNSET = []

class BaseFormat(object):
    """Base for the format API."""
    default = None

    # nargs < 0 implies variable number of args, which is probably a bad idea
    # in most circumstances.
    nargs = 1

    def __init__(self,
                 name=None,
                 nargs=None,     
                 special=None,
                 casesensitive=False,
                 addspecialdocs=True):
        if name is not None:
            self._name = name
        if nargs is not None:
            self.nargs = nargs
        if isinstance(special, basestring):
            special = {special: special}
        elif special is None:
            special = dict()
        else:
            try:
                special = dict(special)
            except:
                special = dict((s, s) for s in special)
        self.special = special
        self.casesensitive = casesensitive
        if addspecialdocs and special:
            self._docs = self.docs + ' These special values are accepted: ' + ', '.join(repr(s) for s in special) + '.' 
    
    docs = property(lambda self: getattr(self, '_docs', self.__class__.__doc__.splitlines()[0].strip()))
    name = property(lambda self: getattr(self, '_name', self.__class__.__name__))

    def parse(self, argv):
        """Pop, parse and return the first self.nargs items from args.

        Subclasses that desire other behavior can override this (must be 
        overridden if self.nargs is None). 

        if self.nargs > 1 a list of parsed values will be returned.
        
        Raise BadNumberOfArguments or BadArgument on errors.
         
        NOTE: args may be modified in place by this method.
        """

    def parsestr(self, argstr):
        """Parse arguments found in settings files.
        
        argstr is the string that should be parsed. Use e.g. '""' to pass an
        empty string.

        if self.nargs > 1 a list of parsed values will be returned.

        NOTE: formats with nargs == 0 or None probably want to override this 
        method.
        """
        argv = shlex.split(argstr, comments=True)
        if len(argv) != self.nargs:
            raise BadNumberOfArguments(self.nargs, len(argv))
        return self.parse(argv)

    def present(self, value):
        """Return a user-friendly representation of a value.
        
        Lookup value in self.specials, or call .to_literal() if absent.
        """

def get_format(format):
    """Get a format object.
    
    If format is a format object, return unchanged. If it is a string 
    matching one of the BaseFormat subclasses in the tui.formats module
    (case insensitive), return an instance of that class. Otherwise assume 
    it'a factory function for Formats (such as a class) so call and return,
    and raise ValueError on error.
    """
    if isinstance(format, BaseFormat):
        return format
    if isinstance(format, basestring):
        for name, formatclass in globals().items():
            if name.lower() == format.lower():
                if not issubclass(formatclass, BaseFormat):
                    raise ValueError('%s is not the name of a format class' % format)
                return formatclass()
    try:
        return format()
    except:
        raise ValueError('no such format')

class Metaformat(BaseFormat):
    """A format that uses other formats to do most of the work."""

class Format(BaseFormat):
    """Base class for normal data format for tui.Parameters."""
        
    def __init__(self,
                 args=None,
                 kw=None,
                 **kwargs):
        """
        special is a argument:value dict of arguments with special meaning, 
        where arguments (keys) must be strings and value can be any python 
        object. Can also be given as an iterable for argument:value pairs, or 
        as an iterable for arguments that should be passed through untouched, 
        or as a single string which is taken as a list of one item.
        
        If case is False then all literals will be converted to lowercase for
        lookup in self.specials.    
        
        If addspecialdocs is true then a notice of the accepted special 
        arguments will be appended to self.docs.
         
        args and kw are additional positional and keyword parameters to be 
        passed to self.to_python and self.to_literal.
        """
        super(Format, self).__init__(**kwargs)
        if args is None:
            args = tuple()
        self.args = tuple(args)
        if kw is None:
            kw = dict()
        self.kw = dict(kw)

    def to_python(self, literal, *args, **kw):
        """Convert a literal to a python object."""
        return literal
    
    def to_literal(self, value, *args, **kw):
        """Convert a value to a user-friendly representation."""
        return str(value)
    
    def parse_argument(self, arg):
        """Parse a single argument.
        
        Lookup arg in self.specials, or call .to_python() if absent. Raise 
        BadArgument on errors.
        """
        lookup = self.casesensitive and arg or arg.lower()
        if lookup in self.special:
            return self.special[lookup]
        try:
            return self.to_python(arg, *self.args, **self.kw)
        except Exception, e:
            raise BadArgument(arg, str(e))
    
    def parse(self, argv):
        """Pop, parse and return the first self.nargs items from args.

        if self.nargs > 1 a list of parsed values will be returned.
        
        Raise BadNumberOfArguments or BadArgument on errors.
         
        NOTE: argv may be modified in place by this method.
        """
        if len(argv) < self.nargs:
            raise BadNumberOfArguments(self.nargs, len(argv))
        if self.nargs == 1:
            return self.parse_argument(argv.pop(0))
        return [self.parse_argument(argv.pop(0)) for tmp in range(self.nargs)]

    def present(self, value):
        """Return a user-friendly representation of a value.
        
        Lookup value in self.specials, or call .to_literal() if absent.
        """
        for k, v in self.special.items():
            if v == value:
                return k
        return self.to_literal(value, *self.args, **self.kw)

class Flag(Format):
    """A boolean flag, True if present on the command line"""
    
    default = False
    nargs = 0
    true = ['1', 'yes', 'true', 'on']
    false = ['0', 'no', 'false', 'off']
    allowed = ', '.join(true + false[:-1]) + ' or ' + false[-1]
    _docs = "Takes no argument on the command line. Use %s in configfiles (case insensitive)." % allowed

    def parse(self, argv):
        return True
        
    def parsestr(self, argstr):
        """Parse arguments found in settings files.
        
        Use the values in self.true for True in settings files, or those in 
        self.false for False, case insensitive.
        """
        argv = shlex.split(argstr, comments=True)
        if len(argv) != 1:
            raise BadNumberOfArguments(1, len(argv))
        arg = argv[1]
        lower = arg.lower()
        if lower in self.true:
            return True
        if lower in self.false:
            return False
        raise BadArgument(arg, "Allowed values are " + self.allowed + '.')
        
class String(Format):
    "A string of characters."
    default = ''
    
class Int(Format):
    """An integer number."""
    default = 0
    
    def __init__(self,
                 lower=None,
                 upper=None,
                 inclusive=None,
                 lowerinclusive=True,
                 upperinclusive=True,
                 **kw):
        """
        lower and upper (if not None) give the lower and upper bounds of 
        permissible values. 
        
        lowerinclusive and upperinclusive state whether the bound values 
        themselves are within the permissible range.
        
        inclusive (if not None) overrides lowerinclusive and upperinclusive.
        """
        super(Int, self).__init__(**kw)
        if inclusive is not None:
            lowerinclusive = upperinclusive = inclusive
        self.lower = lower
        self.upper = upper
        self.lowerinclusive = lowerinclusive
        self.upperinclusive = upperinclusive
        docs = [self.docs[:-1]]
        if lower is not None:
            if lowerinclusive:
                docs.append('no less than ' + self.to_literal(lower))
            else:
                docs.append('greater than ' + self.to_literal(lower))
            if upper is not None:
                docs.append('but')
        if upper is not None:
            if upperinclusive:
                docs.append('no greater than ' + self.to_literal(upper))
            else:
                docs.append('less than ' + self.to_literal(upper))
        self._docs = ' '.join(docs) + '.'
                
    
    @property
    def name(self):
        if getattr(self, '_name', None):
            return self._name
        name = self.__class__.__name__
        if self.lower is not None:
            if self.upper is not None:
                return (name + 
                        (self.lowerinclusive and '[' or '<') +
                        self.to_literal(self.lower, *self.args, **self.kw) +
                        ',' +
                        self.to_literal(self.upper, *self.args, **self.kw) +
                        (self.upperinclusive and ']' or '>'))
            return (name +
                    '>' +
                    (self.lowerinclusive and '=' or '') +
                    self.to_literal(self.lower, *self.args, **self.kw))
        if self.upper is not None:
            return (name +
                    '<' +
                    (self.upperinclusive and '=' or '') +
                    self.to_literal(self.upper, *self.args, **self.kw))
        return name

    def _to_python(self, literal):
        return int(literal)

    def to_python(self, literal):
        value = self._to_python(literal)
        if self.lower is not None:
            if self.lowerinclusive:
                if value < self.lower:
                    raise ValueError('must not be less than ' + self.to_literal(self.lower))
            elif value <= self.lower:
                raise ValueError('must be greater than ' + self.to_literal(self.lower))
        if self.upper is not None:
            if self.upperinclusive:
                if value > self.upper:
                    raise ValueError('must not be greater than ' + self.to_literal(self.upper))
            elif value >= self.upper:
                raise ValueError('must be less than ' + self.to_literal(self.upper))
        return value
    
class Float(Int):
    """A decimal number."""
    default = 0.0
    formatter = None
    
    def __init__(self,
                 lower=None,
                 upper=None,
                 inclusive=None,
                 lowerinclusive=True,
                 upperinclusive=True,
                 formatter=None,
                 **kw):
        """
        formatter should be a python string interpolation format stating how 
        to display the value. None means use plain str.
        """
        super(Float, self).__init__(lower, upper, inclusive, lowerinclusive, upperinclusive, **kw)
        if formatter:
            self.kw['formatter'] = formatter

    def to_literal(self, value, formatter=None, *args, **kw):
        if formatter is None:
            return str(value)
        return formatter % value

    def _to_python(self, literal):
        return float(literal)
    
class Percentage(Float):
    """A decimal number in percent units."""
    
class ReadableFile(Format):
    """A readable file.

    Understands home directory expansion (e.g. ~/foo or ~joel/foo) using 
    os.path.expanduser().
    """
    mode = 'r'
    default = ''
    
    def to_python(self, literal):
        try:
            open(os.path.expanduser(literal), self.mode)
        except IOError, e:
            raise ValueError(e.strerror)
        return literal

class WritableFile(ReadableFile):
    """A writable file, will be created if possible.

    Understands home directory expansion (e.g. ~/foo or ~joel/foo) using 
    os.path.expanduser().
    """
    mode = 'a'
    
class ReadableDir(Format):
    """A readable directory."""
    default = '.'
    
    def to_python(self, literal):
        if not os.access(literal, os.R_OK):
            raise ValueError('it does not exist')
        elif not os.path.isdir(literal):
            raise ValueError('it is not a directory')
        elif not os.access(literal, os.R_OK):
            raise ValueError('it is not readable')
        return literal
        
class WritableDir(ReadableDir):
    """A writable directory, will be created if possible."""    
    def to_python(self, literal):
        if not os.path.isdir(literal):
            try:
                os.mkdir(literal)
            except Exception:
                raise ValueError('it does not exist and cannot be created')
        elif not os.access(literal, os.W_OK):
            raise ValueError('it is not writable')
        return literal
        
class Choice(Format):
    """Choose among the allowed values."""
    
    def __init__(self,
                 choices,
                 **kw):
        if not choices:
            raise ValueError('need at least one choice')
        super(Choice, self).__init__(special=choices, **kw)
        self._docs = "%s: %s." % (self.__class__.__doc__.splitlines()[0][:-1], self.allowed) 
    
    allowed = property(lambda self: ', '.join(repr(s) for s in self.special))
    
    def to_python(self, literal, *args, **kw):
        raise ValueError("it is not among the legal choices: " + self.allowed + '.')

class RegEx(Format):
    """A perl like regular expression."""
    default = ''
    name = 'RegEx'
    
    def __init__(self, flags=0, **kw):
        """flags should be an integer and is passed to re.compile. It can 
        also be a string of one or more of the letters 'iLmsux' (the short 
        names of the re flags).
        """
        if isinstance(flags, basestring):
            flags = flags.upper()
            if flags.translate(None, 'ILMSUX'):
                raise ValueError('illegal flags ' + flags.translate(None, 'ILMSUX'))
            flags = reduce(lambda i, flag: i | getattr(re, flag), flags, 0)
        super(RegEx, self).__init__(**kw)
        self.kw['flags'] = flags

    def to_python(self, literal, flags=0, *args, **kw):
        return re.compile(literal, flags)
        
    def to_literal(self, value, flags=0, *args, **kw):
        return value and value.pattern or ''

class List(Metaformat):
    """A simple list metaformat."""
    separator = ','
    separator_name = 'comma'
    
    def __init__(self,
                 format,
                 separator=None,
                 separator_name=None,
                 strip=True,
                 **kw):
        self.format = get_format(format)
        super(List, self).__init__(**kw)
        if self.format.nargs == 0:
            raise ValueError('format.nargs cannot be 0')
        self.separator = separator or self.__class__.separator
        self.separator_name = separator_name or self.__class__.separator_name
        self.strip = strip
        
    @property
    def name(self):
        return "ListOf" + self.format.name
    
    @property
    def docs(self):
        out = ['A %s separated list of %s.' % (self.separator_name, self.format.name)]
        if self.special:
            out.append('These special values are accepted:')
            out.append(', '.join(repr(s) for s in self.special) + '.')
        out.append('%s: %s' % (self.format.name, self.format.docs))
        return ' '.join(out)
    
    def parse(self, argv):
        """Pop, parse and return the first arg from argv.
        
        The arg will be .split() based on self.separator and the (optionally 
        stripped) items will be parsed by self.format and returned as a list. 

        Raise BadNumberOfArguments or BadArgument on errors.
         
        NOTE: args will be modified.
        """
        if not argv:
            raise BadNumberOfArguments(1, 0)
        argument = argv.pop(0)
        lookup = self.casesensitive and argument or argument.lower()
        if lookup in self.special:
            return self.special[lookup]
        argv = [(self.strip and s.strip() or s) for s in argument.split(self.separator)]
        values = []
        while argv:
            values.append(self.format.parse(argv))
        return values
    
    def present(self, value):
        """Return a user-friendly representation of a value.
        
        Lookup value in self.specials, or call .to_literal() if absent.
        """
        for k, v in self.special.items():
            if v == value:
                return k
        return self.separator.join(self.format.present(v) for v in value)

class Tuple(Metaformat):
    """A simple tuple metaformat."""
    separator = ':'

    def __init__(self,
                 format,
                 separator=None,
                 strip=True,
                 **kw):
        """
        self.separator should be a string of separator characters. If there are
        more formats than separators, the last given separator will be used 
        repeatedly for all the rest. 
        
        If strip is true, each part of the split argument will be stripped 
        before passed to its format for parsing.
        
        See Metaformat and Baseformat for other parameters.  
        """
        self.format = []
        for f in format:
            self.format.append(get_format(f))
            if f.nargs == 0:
                raise ValueError('format.nargs cannot be 0')
        super(Tuple, self).__init__(**kw)
        self.separator = separator or self.__class__.separator
        if len(self.separator) >= len(format):
            raise ValueError('needs more formats than separator characters') 
        self.strip = strip

    def get_separator(self, i):
        """Return the separator that preceding format i, or '' for i == 0."""
        return i and self.separator[min(i - 1, len(self.separator) - 1)] or ''

    @property
    def name(self):
        return 'Tuple(%s)' % ''.join(self.get_separator(i) + format.name for i, format in enumerate(self.format))
    
    @property
    def docs(self):
        sep = 'by '
        if len(self.separator) > 1:
            sep = ', '.join(repr(c) for c in self.separator[:-1])
            if len(self.format) - 1 > len(self.separator):
                sep = 'first by ' + sep + ' and the rest by '
            else:
                sep += 'by ' + sep + ' and '
        sep += repr(self.separator[-1])
        out = ['A tuple of values separated %s.' % sep]
        if self.special:
            out.append('These special values are accepted:')
            out.append(', '.join(repr(s) for s in self.special) + '.')
        shown = []
        for format in self.format:
            docs = '%s is %s' % (format.name, format.docs[0].lower() + format.docs[1:])
            if docs not in shown:
                out.append(docs)
                shown.append(docs)
        return ' '.join(out)
    
    def parse(self, argv):
        """Pop, parse and return the first arg from argv.
        
        The arg will be repeatedly .split(x, 1) based on self.get_separator() and the 
        (optionally stripped) items will be parsed by self.format and returned
        as a list. 

        Raise BadNumberOfArguments or BadArgument on errors.
         
        NOTE: args will be modified.
        """
        if not argv:
            raise BadNumberOfArguments(1, 0)
        remainder = argv.pop(0)
        lookup = self.casesensitive and remainder or remainder.lower()
        if lookup in self.special:
            return self.special[lookup]
        values = []
        for i, format in enumerate(self.format[:-1]):
            print i, self.get_separator(i)
            try:
                arg, remainder = remainder.split(self.get_separator(i + 1), 1)
            except:
                raise BadArgument(remainder, 'does not contain required separator ' + repr(self.get_separator(i + 1)))
            if self.strip:
                arg = arg.strip()
            values.append(format.parse([arg]))
        if self.strip:
            remainder = remainder.strip()
        values.append(format.parse([remainder]))
        return values
    
    def present(self, value):
        """Return a user-friendly representation of a value.
        
        Lookup value in self.specials, or call .to_literal() if absent.
        """
        for k, v in self.special.items():
            if v == value:
                return k
        return ''.join(self.get_separator(i) + self.format[i].present(v) for i, v in enumerate(value))
    