"""TUI Textual User Interface - A sane command line user interface.

Author: Joel Hedlund <yohell@ifm.liu.se>

TUI is straightforward to use, both for developes and users. It can parse 
options from multiple config files and command line, and can produce 
constructive error messages given bad input. It can also help keep the 
source code clean by moving help text to a separate documentation file.

If you have problems with this package, please contact the author.

GETTING STARTED:
Typically, you will need to import the tui class and some format classes 
from the tui.formats module. The tui.docparser module has documentation on how 
to write tui-compatible documentation files, but you won't likely need 
anything else from there. You probably won't ever have to use anything from 
the TextBlockParser module.

HOWTO:
Let's pretend we're making a moose counter. First, we create the script 
file 'moosecounter.py', a docs file 'moosecounter.docs' and a config file
'moosecounter.cfg' in the same dir. Leave the latter two empty and start 
editing the scriptfile.

Instantiate a textual user interface object and give it the proper name 
right from the start and use the magical initprog() feature, like so:

__version__ = "0.1.0"
if __name__ == '__main__':
    from tui import tui
    o = tui(main=__file__, progname='MooseCounter')
    o.initprog()

Save and execute your moose counter with no arguments, and voila: usage 
instructions! Execute it with the --HELP flag, and voila: verbose program 
information, including syntax help for the config file! The config files 
are meant to be used by your users to configure your program with, by the 
way.

A quick note on using main=__file__:
Doing this is handy because it enables tui to find any .cfg or .docs files
you want to distribute with your program, and find defaults for progname, 
command, versionstr and so on. However, if supplied, tui will attempt to 
import the module and read the __version__ and __doc__ attributes, so if 
you are planning to use this feature, make sure your script can be imported
without side effects. But as this is standard python coding practice, you 
should probably already be doing this anyway!

Now you can go on to adding more options to your moose counter. Just stick 
some o.makeoption() and o.makeposarg() clauses between the last two lines 
in the example above. You will probably also need to import some formats 
for your options from the formats module in this package. For example you 
can do something like this:

__version__ = "0.1.0"
if __name__ == '__main__':
    from tui import tui, formats
    o = tui.tui(main=__file__, progname='MooseCounter')
    o.makeoption('horn-points', formats.BoundedInt(lowerbound=1), 'p', 13)
    o.makeoption('weight', formats.Float, 'w', 450.0)
    o.makeposarg('observation_data', formats.ReadableFile)
    o.makeposarg('result_file', formats.WritableFile)
    o.initprog()


After you have saved you can execute your moose counter in same manner as 
before and see your new options turn up in the help screens. You are highly
encouraged to document the program and its options better, and your docs 
file is the place to do it. Check the help for the tui.docparser module for
the syntax. 

OK, so that's a handful of lines of code that take care of all the boring 
old run of the mill config file and parameter parsing and help screen 
generation, and now you're free to write code that actally counts mooses. 
Use o.options() to return a dict of options and values, and o.posargs() to 
get a list of values for all positional arguments.

FURTHER READING:
See the separate help docs on each individual module, class and method.

COPYRIGHT: 
The MIT License

Copyright (c) 2011 Joel Hedlund

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

__version__ = "1.3.0"
__copyright__ = "Copyright (c) 2011 Joel Hedlund."
__license__ = "MIT"

__all__ = ['BadAbbreviationBlockError',
           'BadArgumentError',
           'BadNumberOfArgumentsError',
           'DeveloperError',
           'DocumentationError',
           'InvalidOptionError',
           'Option',
           'OptionError',
           'OptionRecurrenceError',
           'ParseError',
           'PositionalArgument',
           'PositionalArgumentError',
           'ReservedOptionError',
           'StandardHelpOption',
           'StandardLongHelpOption',
           'StandardSettingsOption',
           'StandardVersionOption',
           'UserInterfaceError',
           'docparser',
           'formatstui',
           'textblockparser']

import docparser, formats
import ConfigParser, os, re, sys, textwrap

##################################################
##
## ERRORS
##

class UserInterfaceError(Exception):
    """Base class for exceptions raised in the tui package.
    
    Should not be instantiated directly. Use a proper subclass instead.

    """
    template = None
    def __str__(self):
        if len(self.args) > 1 and self.template is not None:
            return self.template % self.args
        return Exception.__str__(self)

# Argument parsing errors

class ParseError(UserInterfaceError):
    """Base class for exceptions raised while parsing option values.
    
    Should not be instantiated directly. Use a proper subclass instead.

    """
    
class BadArgumentError(ParseError):
    """Raised when options get literals incompatible with their Format."""
    
    template = "%s is not an acceptable argument for %s (%s)."
    def __init__(self, *args):
        """Instantiate with (name, value, details) or (message)."""
        ParseError.__init__(self, *args)

class BadNumberOfArgumentsError(ParseError):
    """Raised when an Option has been given the wrong number of arguments."""
    template = "%s requires %s arguments and was given %s."
    def __init__(self, *args):
        """Instantiate with (name, required, supplied) or (message)."""
        ParseError.__init__(self, *args)

class InvalidOptionError(ParseError):
    """Raised on attempts to access nonexisting options."""
        
class OptionRecurrenceError(ParseError):
    """Raised on multiple use of single use options."""
    template = "The option %s can only be used once in an argument list."
    def __init__(self, *args, **kw):
        """Instantiate with option name or message=... keyword argument."""
        if args and kw.get('message', None):
            raise ValueError('cannot use custom and default message at the same time')
        ParseError.__init__(self, *args)
        self.message = kw.get('message', None)
    
    def __str__(self):
        if self.message:
            return self.message
        return ParseError.__str__(self)

class ReservedOptionError(ParseError):
    """Raised when command line reserved options are used in a config file."""
    template = "The option %s is reserved for command line use."
    def __init__(self, *args, **kw):
        """Instantiate with option name or message=... keyword argument."""
        if args and kw.get('message', None):
            raise ValueError('cannot use custom and default message at the same time')
        ParseError.__init__(self, *args)
        self.message = kw.get('message', None)
    
    def __str__(self):
        if self.message:
            return self.message
        return ParseError.__str__(self)
        
class BadAbbreviationBlockError(ParseError):
    """Raised when poorly composed abbreviation blocks are encountered.
    
    For example if options that require value arguments occurs anywhere
    except last in the block.

    """
    template = "Option %s in the abbreviation block %s is illegal (%s)."
    def __init__(self, *args):
        """Instantiate with (abbreviation, block, details) or (message)."""
        ParseError.__init__(self, *args)

# Option creation errors

class DeveloperError(UserInterfaceError):
    """Raised on illegal creation or configuration of a tui instance.
    
    Should not be instantiated directly. Use a proper subclass instead.

    """

class OptionError(DeveloperError):
    """Raised on failed Option creation.
    
    For example when trying to add two Options with the same name.

    """

class PositionalArgumentError(DeveloperError):
    """Raised when PositionalArgument creation fails.
    
    For example when trying to add an argument that takes no value.

    """

class DocumentationError(DeveloperError):
    """Raised on errors in parsing documentation files."""
        
_UNSET = []
class Option:
    """A program option."""
    
    def __init__(self, 
                 name, 
                 format, 
                 abbreviation='', 
                 default=_UNSET, 
                 reserved=False, 
                 docs='', 
                 recurring=False):
        """
        ARGS:
        name <str>:
            The long option name. Used in settings files and with a '--'
            prefix on the command line. This should be as brief and
            descriptive as possible. Must be at least length 2, must start
            and end with a letter or number and may contain letters,
            numbers, underscores and hyphens in between.
        format <Format> or <class Format>:
            How to treat this option and any arguments it may require.
        default <str>:
            The string that will be fed to this option if the user
            doesn't supply any value (for example in settings files or
            on the command line).
        abbreviation <str>:
            The one-letter (or digit) abbreviation of the option name.
        reserved = False <bool>:
            Is the option reserved for command line use?
        docs = '' <str>:
            User friendly help text for the option. '' means use docs
            from the Format.
        recurring = False <bool>:
            Is the option allowed to occur several times on the command
            line? Note that when recurring = True, then .value() will
            return a list of values where the first item is the builtin
            default  and any following items will be the rest of the
            values in the order parsed.
        
        """
        sOptionNameRE = r'[A-Za-z0-9][\w-]*[A-Za-z0-9]'
        sOptionAbbreviationRE = r'[A-Za-z0-9]'
        if not re.match(sOptionNameRE, name):
            sErrorMsg = "Invalid name (does not match %s)."
            sErrorMsg %= repr(sOptionNameRE)
            raise OptionError(sErrorMsg)
        self.sName = name
        if isinstance(format, type(formats.Format)):
            format = format()
        self.oFormat = format
        if default is _UNSET:
            if recurring:
                default = []
            else:
                default = format.default
        self.xValue = default
        if abbreviation and len(abbreviation) != 1:
            raise ValueError("Option abbreviations must be strings of length 1.")
        if abbreviation and not re.match(sOptionAbbreviationRE, abbreviation):
            sErrorMsg = "Invalid abbreviation (does not match %s)."
            sErrorMsg %= repr(sOptionAbbreviationRE)
            raise OptionError(sErrorMsg)
        self.sAbbreviation = abbreviation
        self.bReserved = reserved
        if docs:
            self.sDocs = docs
        else:
            self.sDocs = self.oFormat.docs()
        self.bAllowRecurrence = recurring
        self.sLocation = "Builtin default."

    def parse(self, args, usedname, location):
        """Consume and process arguments and store the result.
        ARGS:
        args <list str>:
            The argument list to parse.
        usedname <str>:
            The string used by the user to invoke the option.
        location <str>:
            A user friendly sring describing where the parser got this
            data from.

        """
        try:
            xValue = self.oFormat.parse(args)
        except formats.BadNumberOfArgumentsError, e:
            raise BadNumberOfArgumentsError(usedname, e.required(), e.supplied())
        except formats.BadArgumentError, e:
            raise BadArgumentError(usedname, e.argument(), e.details())
        if self.bAllowRecurrence:
            self.xValue.append(xValue)
        else:
            self.xValue = xValue
        self.sLocation = location

    def parsestr(self, argsstr, usedname, location):
        """Parse a string lexically and store the result.
        ARGS:
        argsstr <str>:
            The string to parse.
        usedname <str>:
            The string used by the user to invoke the option.
        location <str>:
            A user friendly sring describing where the parser got this
            data from.

        """
        try:
            xValue = self.oFormat.parsestr(argsstr)
        except formats.BadNumberOfArgumentsError, e:
            raise BadNumberOfArgumentsError(usedname, e.required(), e.supplied())
        except formats.BadArgumentError, e:
            raise BadArgumentError(usedname, e.argument(), e.details())
        if self.bAllowRecurrence:
            self.xValue.append(xValue)
        else:
            self.xValue = xValue
        self.sLocation = location
        self.sLocation = location

    def strvalue(self):
        value = self.xValue
        if not self.bAllowRecurrence:
            value = [value]
        return ', '.join(self.oFormat.strvalue(v) for v in value)

    def formatname(self):
        return self.oFormat.shortname()

    def name(self):
        return self.sName

    def abbreviation(self):
        return self.sAbbreviation

    def value(self):
        return self.xValue

    def nargs(self):
        return self.oFormat.nargs()

    def docs(self):
        return self.sDocs

    def location(self):
        return self.sLocation

    def recurring(self):
        return self.bAllowRecurrence

    def reserved(self):
        return self.bReserved

    def setdocs(self, newdocs):
        self.sDocs = newdocs

class StandardHelpOption(Option):
    """A standard help option."""
    def __init__(self):
        Option.__init__(self, 'help', formats.Flag, 'h', reserved=True,
                        docs='Print command line help and exit.')

class StandardLongHelpOption(Option):
    """A standard long help option."""
    def __init__(self):
        Option.__init__(self, 'HELP', formats.Flag, 'H', reserved=True,
                        docs='Print verbose help and exit.')

class StandardVersionOption(Option):
    """A standard version option."""
    def __init__(self):
        Option.__init__(self, 'version', formats.Flag, 'V', reserved=True,
                        docs='Print version string and exit.')

class StandardSettingsOption(Option):
    """A standard settings option."""
    def __init__(self):
        Option.__init__(self, 'settings', formats.Flag, 'S', reserved=True,
                        docs='Print settings summary and exit.')

class PositionalArgument:
    """A positional command line program parameter."""
    
    def __init__(self, name, format, docs='', recurring=False, optional=False):
        """
        ARGS:
        name <str>:
            Will be shown on the help screen. Must be at least length 2,
            must start and end with a letter or number and may contain
            letters, numbers, underscores and hyphens in between.
        format <Format> or <class Format>:
            How to treat this argument. .nargs() must be > 0.
        docs = '' <str>:
            User friendly description of the argument. '' means use default
            docs for the format.
        recurring = False <bool>:
            Do we accept multiple (1 or more) occurrences for this arg?
            With recurring = True then the .parse() method will consume all
            argument items fed to it and return a list of parsed values.
        optional = False <bool>:
            Do we permit the user to leave this arg out of the command line?
        
        """
        sNameRE = r'[A-Za-z0-9][\w-]*[A-Za-z0-9]'
        if not re.match(sNameRE, name):
            sErrorMsg = "Invalid name (does not match %s)."
            sErrorMsg %= repr(sNameRE)
            raise PositionalArgumentError(sErrorMsg)
        self.sName = name
        if isinstance(format, type(formats.Format)):
            format = format()
        if format.nargs() == 0:
            raise PositionalArgumentError("PositionalArgument Formats must have .nargs() >= 1.")
        self.oFormat = format
        if not docs:
            docs = format.docs()
        self.sDocs = docs
        self.bRecurring = recurring
        self.bOptional = optional

    def parse(self, args):
        """Consume and process arguments and return the resulting value.
        ARGS:
        args <list str>:
            The list of arguments that should be parsed.
        RETURN:
        Whatever is returned by the Formats parser, or None if the the 
        positional argument is optional and there is nothing to parse.
        OR:
        A list of parsed items if self.bRecurring is True. This list will 
        be length 0 if the positional argument is optional and there is 
        nothing to parse.
            
        """
        try:
            if self.bRecurring:
                lxValue = []
                if not self.optional():
                    lxValue.append(self.oFormat.parse(args))
                while args:
                    lxValue.append(self.oFormat.parse(args))
                return lxValue
            else:
                if not args and self.optional():
                    return None
                return self.oFormat.parse(args)
        except formats.BadNumberOfArgumentsError, e:
            raise BadNumberOfArgumentsError(self.sName.upper(), e.required(), e.supplied())
        except formats.BadArgumentError, e:
            raise BadArgumentError(self.sName.upper(), e.argument(), e.details())
        
    def name(self):
        return self.sName

    def formatname(self):
        return self.oFormat.shortname()

    def docs(self):
        return self.sDocs

    def value(self):
        return self.xValue

    def setdocs(self, newdocs):
        self.sDocs = newdocs

    def recurring(self):
        return self.bRecurring

    def optional(self):
        return self.bOptional


class StrictConfigParser(ConfigParser.SafeConfigParser):
    """A config parser that minimises the risks for hard-to-debug errors."""
    
    def __init__(self, defaults=None, comment='#'):
        self.sLineCommentStart = comment
        ConfigParser.SafeConfigParser.__init__(self, defaults)

    def optionxform(self, option):
        """Strip whitespace only."""
        return option.strip()

    def unusedoptions(self, section):
        """Returns a list of options that are not used to format values for 
        any other options in the section. Good for finding out if the user
        has misspelled any of the options.
        IN:
        section <str>:
            What section to read.
        OUT:
            The names of unused options as a list of strings.
            
        """
        if not self.has_section(section):
            return []
        sRawValues = [self.get(section, x, raw=True) for x in self.options(section)]
        lsUnusedOptions = []
        for sOption in self.options(section):
            sFormatter  = "%%(%s)s" % sOption
            for sValue in sRawValues:
                if sFormatter in sValue:
                    break
            else:
                lsUnusedOptions.append(sOption)
        return lsUnusedOptions
    

def get_terminal_size(default_cols=80, default_rows=25):
    """Return current terminal size (cols, rows) or a default if detect fails.

    This snippet comes from color ls by Chuck Blake:
    http://pdos.csail.mit.edu/~cblake/cls/cls.py

    """
    def ioctl_GWINSZ(fd):
        try:                                
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return None
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)  # try open fds
    if not cr:                                                  # ...then ctty
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:                            # env vars or finally defaults
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            cr = (default_cols, default_rows)
    return int(cr[1]), int(cr[0])         # reverse rows, cols

class tui:
    """Textual user interface."""
    def __init__(self,
                 main=None,
                 progname=None,
                 programmer='ChangeThisProgrammerName',
                 versionstr='0.1.0',
                 title='%(progname)s v%(version)s by %(programmer)s.',
                 description=None,
                 contact=None,
                 copyright=None,
                 command='',
                 usage='',
                 generaldocs=None,
                 additionaldocs=None,
                 filedocs=None,
                 notedocs=None,
                 docsfile=None,
                 width=0,
                 configfiles=None,
                 sections=None,
                 helpoption=StandardHelpOption,
                 longhelpoption=StandardLongHelpOption,
                 versionoption=StandardVersionOption,
                 settingsoption=StandardSettingsOption):
        """
        ARGS:
        main = None <str>:
            Full path to the executed script. Will be used to determine 
            defaults for command, progname, versionstr and default search 
            paths for docsfile and configfiles. Note that the module will 
            be imported to check the __version__ attribute, so it should 
            know better than to do anything nasty on import. 
        progname = 'ChangeThisProgramName' <str>:
            The user friendly name of the program. Used for the doc string
            formatter %(progname)s.
        programmer = 'ChangeThisProgrammerName' <str>:
            Who made the program. Used for the doc string formatter
            %(programmer)s.
        versionstr = '0.1.0' <str>:
            The current program version. Used for the doc string
            formatter %(version)s.
        title = '%(progname)s v%(version)s by %(programmer)s.' <str>:
            What to put in the title line on help pages. May contain doc
            string formatters.
        description = 'ChangeThisDescription' <str>:
            A oneliner describing the program. May contain docvar
            formatters.
        contact = None <list str>, <str> or None:
            Contact information as a list of indented paragraphs. May
            contain docvar formatters. String values are interpreted as
            a list of one indented paragraph. None or an empty list means
            no such documentation.
        copyright = None <list str>, <str> or None:
            Copyright information as a list of indented paragraphs. May
            contain docvar formatters. String values are interpreted as
            a list of one indented paragraph. None or an empty list means
            no such documentation.
        command = '' <str>:
            File name of the main executable. How to execute the program.
            Used for the doc string formatter %(command)s. '' means
            the basename of sys.argv[0].
        usage = '' <str>:
            User friendly string showing how to run the program. May
            contain doc string formatters. '' means auto generate from
            options and positional parameters.
        generaldocs = None <list str>, <str> or None:
            General documentation on the program as a list of indented
            paragraphs. May contain docvar formatters. String values are
            interpreted as a list of one indented paragraph. None or an
            empty list means no such documentation.
        additionaldocs = None <list str>, <str> or None:
            Additional documentation on the program as a list of indented
            paragraphs. May contain docvar formatters. String values are
            interpreted as a list of one indented paragraph. None or an
            empty list means no such documentation.
        filedocs = None <dict str list str> or None:
            Docs on files used by the program as a dict of file names and
            indented paragraphs. May contain doc string formatters. None or
            an empty dict means no such documentation.
        notedocs = None <list str>, <str> or None:
            Docs on noteworthy quirks in the program as a list of indented
            paragraphs. May contain doc string formatters. String values are
            interpreted as a list of one indented paragraph. None or an
            empty list means no such documentation.
        docsfile = None <str> or None:
            Where to read docs for the prog. '' means there are no default
            docs to read. None means look for "%(command)s.docs" in the 
            script dir, and use '' if it's not there. Note that no docs will
            be read on instantation. Use .readdocs() (or .initprog()) for
            that.
        width = 0 <int>:
            The maximum allowed width for help text. 0 means try to guess
            the terminal width, and use 79 if that fails.
        configfiles = None <list str>, <str> or None:
            What config files to parse. Note that they will not be parsed
            on instantiation - first add options and then use .parsefiles()
            to parse. None means use a list of "%(command)s.cfg" in the
            script directory, "%(command)s.cfg" in the /etc/ directory, and
            ".%(command)s" in the users home directory. Any docvar
            formatters will be expanded at parse time. A string value will
            be interpreted as a list of one item. Set to [] to tell tui not
            to auto generate a "Config File" FILE entry for the longhelp on
            instantiation. Use setconfigfiles() to set config files and
            addconfigfiledocs() to auto generate the "Config File" FILE
            entry at a later stage.
        sections = None <list str>, <str> or None:
            What sections to read in config files. May contain docvar
            formatters. Str values will be interpreted as a list of one
            item. None means use the list ['%(progname)s']. The
            [DEFAULT] section is always read, and it is read as if its
            contents were copied to the beginning of all other sections.
        helpoption = StandardHelpOption <option>, <class Option> or None:
            Add an option that lets the user request help in the usual
            way. Default is '--help' or '-h', option reserved for command
            line use). None means don't add such an option.
        longhelpoption = StandardLongHelpOption <option>, <class Option>
          or None:
            Add an option that lets the user request more verbose help.
            Default is '--HELP' or '-H', option reserved for command
            line use). None means don't add such an option.
        versionoption = StandardVersionOption <option>, <class Option>
          or None:
            Add an option that lets the user print version information
            Default is '--version' or '-V', option reserved for command
            line use). None means don't add such an option.
        settingsoption = StandardSettingsOption <option>, <class Option>
          or None:
            Add an option that lets the user print the program settings
            Default is '--settings' or '-S', option reserved for command
            line use). None means don't add such an option.
        NOTE:
            Just adding the helpoption, longhelpoption, versionoption
            and settingsoption at instantiation will not activate their
            documented functionality. The developer will have to do this
            manually, or automatically using the initprog() method after
            all other options and positional arguments have been added.
 
        """

        if main:
            mainmodule_dir, mainmodule = os.path.split(main)
            if mainmodule.startswith('__init__.py'):
                sys.path.insert(0, os.path.dirname(mainmodule_dir))
                mainmodule = os.path.split(mainmodule_dir)[1]
            else:
                sys.path.insert(0, mainmodule_dir)
                mainmodule = mainmodule.split('.')[0]
            try:
                mod = __import__(mainmodule)
                versionstr = mod.__version__
                if description is None:
                    description = str(mod.__doc__).splitlines()[0]
            except:
                pass
            sys.path.pop(0)
            if command is None:
                command = mainmodule
            if progname is None:
                progname = mainmodule.capitalize()
            if docsfile is None:
                docsfile = os.path.join(mainmodule_dir, mainmodule + '.docs')
            if configfiles is None:
                configfiles = [os.path.join(mainmodule_dir, mainmodule + '.cfg'),
                               os.path.join('/etc/', '%(command)s.cfg'),
                               os.path.join(os.path.expanduser('~'), '.%(command)s')]
        self.dssDocVars = {'progname': progname,  'programmer': programmer,
                           'version': versionstr, 'command': command}
        self.sTitle = title
        self.sDescription = description
        self.sUsage = usage
        if generaldocs is None:
            generaldocs = []
        elif isinstance(generaldocs, str):
            generaldocs = [generaldocs]
        self.lsGeneralDocs = generaldocs
        if additionaldocs is None:
            additionaldocs = []
        elif isinstance(additionaldocs, str):
            additionaldocs = [additionaldocs]
        self.lsAdditionalDocs = additionaldocs
        if contact is None:
            contact = []
        elif isinstance(contact, str):
            contact = [contact]
        self.lsContact = contact
        if copyright is None:
            copyright = []
        elif isinstance(copyright, str):
            copyright = [copyright]
        self.lsCopyright = copyright
        if filedocs is None:
            filedocs = {}
        self.dslsFileDocs = filedocs
        if notedocs is None:
            notedocs = []
        elif isinstance(notedocs, str):
            notedocs = [notedocs]
        self.lsNoteDocs = notedocs
        if docsfile is None:
            if main:
                docsfile = os.path.splitext(main)[0] + '.docs'
            else:
                docsfile = os.path.join(sys.path[0], "%s.docs" % command)
            if not os.path.isfile(docsfile):
                docsfile = ''
        self.sDocsFile = docsfile
        if configfiles is None:
            configfiles = [os.path.join(sys.path[0], '%(command)s.cfg'),
                           os.path.join('/etc/', '%(command)s.cfg'),
                           os.path.join(os.path.expanduser('~'), '.%(command)s')]
        elif isinstance(configfiles, str):
            configfiles = [configfiles]
        self.lsConfigFiles = configfiles
        if sections is None:
            sections = ['%(command)s']
        elif isinstance(sections, str):
            sections = [sections]
        self.lsSections = sections
        if configfiles:
            self.addconfigfiledocs()
        self.dsoOptions = {}
        self.lsOptionOrder = []
        self.dsoAbbreviations = {}
        self.loPositionalArgs = []
        self.lxPositionalArgValues = []
        self.sHelpOption = ''
        self.sLongHelpOption = ''
        self.sVersionOption = ''
        self.sSettingsOption = ''
        if helpoption:
            if isinstance(helpoption, type(Option)):
                helpoption = helpoption()
            self.sHelpOption = helpoption.name()
            self.addoption(helpoption)
        if longhelpoption:
            if isinstance(longhelpoption, type(Option)):
                longhelpoption = longhelpoption()
            self.sLongHelpOption = longhelpoption.name()
            self.addoption(longhelpoption)
        if versionoption:
            if isinstance(versionoption, type(Option)):
                versionoption = versionoption()
            self.sVersionOption = versionoption.name()
            self.addoption(versionoption)
        if settingsoption:
            if isinstance(settingsoption, type(Option)):
                settingsoption = settingsoption()
            self.sSettingsOption = settingsoption.name()
            self.addoption(settingsoption)
        if not width:
            width = get_terminal_size()[0]
        self.iMaxHelpWidth = width

    def __getitem__(self, key):
        if key.startswith('-'):
            return self.dsoAbbreviations[key[1]]
        else:
            return self.dsoOptions[key]

    def __iter__(self):
        return self.dsoOptions.itervalues()

    def addoption(self, option):
        """Add an Option object to the user interface.
        ARGS:
        option <Option>:
            The option that you want to add.

        """
        sName = option.name()
        sAbbreviation = option.abbreviation()
        if sName in self.dsoOptions:
            sErrorMsg = "The name %s is already used by a previosly added option."
            sErrorMsg %= repr(sName)
            raise OptionError(sErrorMsg)
        if sAbbreviation and sAbbreviation in self.dsoAbbreviations:
            sErrorMsg = "The abbreviation %s is already used by the previosly added option %s."
            sErrorMsg %= (repr(sAbbreviation), repr(self.dsoAbbreviations[sAbbreviation].name()))
            raise OptionError(sErrorMsg)
        self.dsoOptions[option.name()] = option
        if sAbbreviation:
            self.dsoAbbreviations[sAbbreviation] = option
        self.lsOptionOrder.append(sName)

    def makeoption(self, 
                   name, 
                   format, 
                   abbreviation='',
                   default=_UNSET, 
                   reserved=False, 
                   docs='', 
                   recurring=False):
        """Instantiate an Option object and add it to the user interface.
        ARGS:
        name <str>:
            The long option name. Used in settings files and with a '--'
            prefix on the command line. This should be as brief and
            descriptive as possible. Must be at least length 2, must start
            and end with a letter or number and may contain letters,
            numbers, underscores and hyphens in between.
        format <Format> or <class Format>:
            How to treat this option and any arguments it may require.
        default <str>:
            The string that will be fed to this option if the user
            doesn't supply any value (for example in settings files or
            on the command line).
        abbreviation <str>:
            The one-letter (or digit) abreviation of the option name.
        reserved <bool>:
            Is the option reserved for command line use?
        docs <str>:
            User friendly help text for the option. '' means use docs
            from the Format.
        recurring = False <bool>:
            Is the option allowed to occur several times on the command
            line? Note that when recurring = True, then .value() will
            return a list of values where the first item is the builtin
            default  and any following items will be the rest of the
            values in the order parsed.        
        NOTE:
        This method is a convenience method for .addoption(tui.Option(...))

        """
        o = Option(name, format, abbreviation, default, reserved, docs, recurring)
        self.addoption(o)

    def appendposarg(self, posarg):
        """Append a PositionalArgument object to the user interface.
        ARGS:
        posarg <PositionalArgument>:
            The option that you want to add.
        NOTE:
            Optional positional arguments must be added after the required
            ones. The user interface can have at most one recurring
            positional argument, and if present, that argument must be the
            last one.

        """
        if self.loPositionalArgs:
            if self.loPositionalArgs[-1].recurring():
                raise PositionalArgumentError("Cannot add further PositionalArguments after a recurring positional argument has been added.")
            if self.loPositionalArgs[-1].optional() and not posarg.optional():
                raise PositionalArgumentError("Cannot add required PositionalArguments after an optional positional argument has been added.")
        self.loPositionalArgs.append(posarg)
    
    def makeposarg(self, 
                   name, 
                   format, 
                   doc='', 
                   recurring=False, 
                   optional=False):
        """Create a PositionalArgument object and add it to the user interface.
        ARGS:
        name <str>:
            The name of the positional argument. Shown to user in the
            command line help. This should be as brief and descriptive
            as possible.
        format <Format> or <class Format>:
            How to treat this option and any arguments it may require.
        doc <str>:
            User friendly help text for the option. '' means use docs
            from the Format.
        recurring = False <bool>:
            Do we accept multiple (1 or more consecutive) occurrences for
            this arg? With recurring = True then the .parse() method will
            consume all argument items fed to it and return a list of
            parsed values. There can be at most one recurring positional
            argument, and, if present, it must be the last one.
        optional = False <bool>:
            Do we require this arg on the command line? Optional positional
            arguments must be added after the required ones. The
            .parseargs() method will return None for unused optional
            positional arguments, or a list of length 0 if the optional
            positional argument is recurring.
        NOTE:
            This method is a convenience method for
            .addposarg(tui.PositionalArgument(...))

        """
        o = PositionalArgument(name, format, doc, recurring, optional)
        self.appendposarg(o)

    def readdocs(self, file=None):
        """Read program documentation from a docparser compatible file.
        ARGS:
        file = None <str> or None:
            The doc file to parse. None means use the default from
            self.sDocsFile, and do nothing if it's ''.

        """
        if file is None:
            file = self.sDocsFile
            if not file:
                return
        oDocs = docparser.parse(file)
        if oDocs.progname():
            self.setprogname(oDocs.progname())
        if oDocs.version():
            self.setversion(oDocs.version())
        if oDocs.programmer():
            self.setprogrammer(oDocs.programmer())
        if oDocs.title():
            self.settitle(oDocs.title())
        if oDocs.description():
            self.setdescription(oDocs.description())
        if oDocs.command():
            self.setcommand(oDocs.command())
        elif oDocs.progname():
            self.setcommand(''.join(oDocs.progname().lower().split()))
        if oDocs.usage():
            self.setusage(oDocs.usage())
        if oDocs.contact():
            self.setcontact(oDocs.contact())
        if oDocs.copyright():
            self.setcopyright(oDocs.copyright())
        if oDocs.additional():
            self.setadditionaldocs(oDocs.additional())
        if oDocs.general():
            self.setgeneraldocs(oDocs.general())
        if oDocs.notes():
            self.setnotedocs(oDocs.notes())
        for sOption, sDocs in oDocs.options().iteritems():
            if not sOption in self.dsoOptions:
                sErrorMsg = "The option %s does not exist."
                sErrorMsg %= repr(sOption)
                raise DocumentationError(sErrorMsg)
            self.dsoOptions[sOption].setdocs(sDocs % self.dssDocVars)
        lsPosArgs = map(lambda x: x.name(), self.loPositionalArgs)
        for sPosArg, sDocs in oDocs.arguments().iteritems():
            if not sPosArg in lsPosArgs:
                sErrorMsg = "The positional argument %s does not exist."
                sErrorMsg %= repr(sPosArg)
                raise DocumentationError(sErrorMsg)
            self.loPositionalArgs[lsPosArgs.index(sPosArg)].setdocs(sDocs % self.dssDocVars)
        for sFile, lsDocs in oDocs.files().iteritems():
            self.setfiledocs(sFile, lsDocs)

    def addconfigfiledocs(self):
        lsPaths = self.lsConfigFiles
        lsSections = self.lsSections
        lsDocs = ["You can put frequently used command line parameters here to avoid having to retype them. %(progname)s will look for copies of this file in the following loctions, and in the following order:"]
        c = lambda x,y:"  %s. %s." % (x, repr(y))
        lsDocs.extend(map(c, range(1, len(lsPaths) +1), lsPaths))
        lsDocs.append('')
        lsDocs.append("The following file sections will be parsed while reading the above files, and in the following order:")
        c = lambda x,y:"  %s. [%s]" % (x, y)
        lsDocs.extend(map(c, range(1, len(lsSections) +1), lsSections))
        lsDocs.append('')        
        lsDocs.append("The [DEFAULT] section is always read (if it's present), and it is read as if its contents were copied to the beginning of all other sections. If an option is set more than once then the latest found value will be used. Settings passed on the command line override any settings found in config files.")
        lsDocs.append('')        
        lsDocs.append('SYNTAX:')        
        lsDocs.append('  The syntax used is the one common in Windows .ini files with [Sections] and option:value pairs. Example:')        
        lsDocs.append('    [Section Name]')        
        lsDocs.append('    option1: value %%(option2)s ; comment')        
        lsDocs.append('    option2= value # comment')
        lsDocs.append('')
        lsDocs.append('  Option Names:')        
        lsDocs.append('    Option names are case sensitive, and in order for them to be to be valid they must be exactly the same as the long names of the command line options.')
        lsDocs.append('')
        lsDocs.append('  Formatting vs Nonformatting Options:')
        lsDocs.append('    In the example, the value of option2 is used to format the value of option1, while option1 is not used to format the value of any other option in the section. option1 is therefore called a nonformatting option while option2 is called a formatting option. The names for all nonformatting options must be valid for the program, while the names of formatting options may or may not be valid. If they are, then their values will be used in the program settings. Otherwise they will only be used for formatting.')
        lsDocs.append('')
        lsDocs.append('  Values:')
        lsDocs.append('    Input values exactly the same way as you would on the command line, except in the case of flags where the values "1", "Yes", "True" and "On" (case insensitive) mean setting the flag to True, and where the values "0", "No", "False" and "Off" mean setting the flag to False. Use "" for passing an empty string.')
        lsDocs.append('')
        self.dslsFileDocs['CONFIGFILE'] = lsDocs

    def parsefiles(self, files=None, sections=None):
        """Parse option settings from files. 
        ARGS:
        files <list str>, <str> or None:
            What files to parse. None means use self.lsConfigFiles. New
            values override old ones. A string value will be interpreted
            as a list of one item. May contain docvar formatters.
        sections <list str>, <str> or None:
            Which sections to parse from the files. None means use
            self.lsSections. A string value will be interpreted as a list
            of one item. May contain docvar formatters. The [DEFAULT]
            section is always read, and it is read as if its contents were
            copied to the beginning of all other sections.
            
        """
        if not files:
            files = self.lsConfigFiles
        elif isinstance(files, str):
            files = [files]
        if not sections:
            sections = self.lsSections
        elif isinstance(sections, str):
            sections = [sections]
        for sFile in files:
            sFile = sFile % self.dssDocVars
            o = StrictConfigParser()
            o.read(sFile)
            for sSection in sections:
                sSection = sSection % self.dssDocVars
                if not o.has_section(sSection):
                    continue
                for sUnusedOption in o.unusedoptions(sSection):
                    if sUnusedOption not in self.dsoOptions:
                        sErrorMsg = "The option %s in section [%s] of file %s does not exist."
                        sErrorMsg %= (repr(sUnusedOption), sSection, repr(sFile))
                        raise InvalidOptionError(sErrorMsg)
                for sOption in o.options(sSection):          
                    if sOption in self.dsoOptions:
                        if self.dsoOptions[sOption].reserved():
                            sErrorMsg = "The option %s in section [%s] of file %s is reserved for command line use."
                            sErrorMsg %= (repr(sUnusedOption), sSection, repr(sFile))
                            raise ReservedOptionError(sErrorMsg)
                        sValue = o.get(sSection, sOption)
                        self.dsoOptions[sOption].parsestr(sValue, sOption, '%s [%s]' % (repr(sFile), sSection))

    def _parseoptions(self, lsArgs, location):
        """Parse the options part of an argument list.
        IN:
        lsArgs <list str>:
            List of arguments. Will be altered.
        location <str>:
            A user friendly string describing where the parser got this
            data from.
            
        """
        loObservedNonRecurringOptions = []
        while lsArgs:
            if lsArgs[0].startswith('--'):
                sOption = lsArgs.pop(0)
                # '--' means end of options.
                if sOption == '--':
                    break
                if not sOption[2:] in self.dsoOptions:
                    sErrorMsg = "The option %s does not exist." % sOption
                    raise InvalidOptionError(sErrorMsg)
                oOption = self[sOption[2:]]
                if not oOption.recurring():
                    if oOption in loObservedNonRecurringOptions:
                        raise OptionRecurrenceError(sOption)
                    loObservedNonRecurringOptions.append(oOption)
                oOption.parse(lsArgs, sOption, location)
            elif lsArgs[0].startswith('-'):
                # A single - is not an abbreviation block.
                if len(lsArgs[0]) == 1:
                    break
                sBlock = lsArgs.pop(0)
                # Abbrevs for Options that take values go last in the block.
                for sAbbreviation in sBlock[1:-1]:
                    if self.dsoAbbreviations[sAbbreviation].nargs() != 0:
                        raise BadAbbreviationBlockError(sAbbreviation, sBlock, "options that require value arguments must be last in abbreviation blocks")
                # Parse individual options.
                for sAbbreviation in sBlock[1:]:
                    oOption = self.dsoAbbreviations[sAbbreviation]
                    if not oOption.recurring():
                        if oOption in loObservedNonRecurringOptions:
                            raise OptionRecurrenceError(oOption.name())
                        loObservedNonRecurringOptions.append(oOption)
                    oOption.parse(lsArgs, '-' + sAbbreviation, location)
            # only args that start with -- or - can be Options.
            else:
                break

    def _parsepositionalargs(self, lsArgs):
        """Parse the positional arguments part of an argument list.
        ARGS:
        lsArgs <list str>:
            List of arguments. Will be altered.

        """
        self.lxPositionalArgValues = []
        for oPositionalArg in self.loPositionalArgs:
            self.lxPositionalArgValues.append(oPositionalArg.parse(lsArgs))
        if lsArgs:
            sErrorMsg = 'This program accepts exactly %s positional arguments (%s given).'
            sErrorMsg %= (len(self.loPositionalArgs), len(self.loPositionalArgs) + len(lsArgs))
            raise PositionalArgumentError(sErrorMsg)
            
    def parseargs(self, argv=None, location=''):
        """Parse an argument vector.
        ARGS:
        args <list str> or None:
            The argument list to parse. None means use sys.argv. args[0] is
            ignored.
        location = '' <str>:
            A user friendly string describing where the parser got this
            data from. '' means use "Command line." if args == None, and
            "Builtin default." otherwise.
            
        """
        if not location:
            if argv is None:
                location = 'Command line.'
            else:        
                location = "Builtin default."
        if argv is None:
            argv = sys.argv
        lsArgs = list(argv[1:])
        self._parseoptions(lsArgs, location)
        self._parsepositionalargs(lsArgs)

    def options(self):
        """Return a dict of the names of the options and their values."""
        d = {}
        for o in self:
            d[o.name()] = o.value()
        return d

    def optionhelp(self, indent=0, maxindent=25, width=79):
        """Return user friendly help on positional arguments in the program.        

        """
        lsOut = []
        iHelpIndent = 0
        for sOption in self.lsOptionOrder:
            o = self.dsoOptions[sOption]
            sTags = '%*s--%s' % (indent, ' ', o.name())
            if o.abbreviation():
                sTags += ', -' + o.abbreviation()
            sTags += ': '
            iHelpIndent = max(iHelpIndent, len(sTags))
        iHelpIndent = min(maxindent, iHelpIndent)
        sI = ' ' * iHelpIndent
        for sOption in self.lsOptionOrder:
            o = self.dsoOptions[sOption]
            sTags = '%*s--%s' % (indent, ' ', o.name())
            if o.abbreviation():
                sTags += ', -' + o.abbreviation()
            sTags += ': '
            print o.sName, o.xValue, o.recurring()
            print o.strvalue() 
            sHelp = "%s(%s). %s" % (o.oFormat.shortname(), o.strvalue(), o.docs())
            if len(sTags) > iHelpIndent:
                ls = textwrap.wrap(sHelp, width = width, initial_indent = sI, subsequent_indent = sI)
                lsOut.append(sTags)
                lsOut.extend(ls)
            elif len(sTags) == iHelpIndent:
                ls = textwrap.wrap(sHelp, width = width, initial_indent = sI, subsequent_indent = sI)
                sFirstLine = "%s%s" % (sTags, ls[0].lstrip())
                lsOut.append(sFirstLine)
                lsOut.extend(ls[1:])
            else:
                ls = textwrap.wrap(sHelp, width = width, initial_indent = sI, subsequent_indent = sI)
                sFirstLine = "%s%*s%s" % (sTags, iHelpIndent - len(sTags), ' ', ls[0].lstrip())
                lsOut.append(sFirstLine)
                lsOut.extend(ls[1:])
        return '\n'.join(lsOut)

    def posargs(self):
        """Return the current list of parsed values for positional arguments."""
        return self.lxPositionalArgValues

    def posarghelp(self, indent=0, maxsamelinelength=25, width=79):
        """Return user friendly help on positional arguments in the program."""
        lsOut = []
        iMaxNameLength = 0
        for o in self.loPositionalArgs:
            iMaxNameLength = max(iMaxNameLength, len(o.name()))
        iDocIndent = min(iMaxNameLength + indent, maxsamelinelength) + 2
        for o in self.loPositionalArgs:
            sHelp = o.formatname() + '. ' + o.docs()
            if len(o.name()) + 2 > iDocIndent:
                sI = ' ' * iDocIndent
                ls = textwrap.wrap(sHelp, width = width, initial_indent = sI,
                                   subsequent_indent = sI)
                lsOut.append("%s%s:" % (' ' * indent, o.name().upper()))
                lsOut.extend(ls)
            else:
                sI = ' ' * iDocIndent
                ls = textwrap.wrap(sHelp, width = width, initial_indent = sI,
                                   subsequent_indent = sI)
                sFirstLine = "%s%s:%s%s"
                sFirstLine %= (' ' * indent, o.name().upper(),
                               ' ' * (iDocIndent - indent - len(o.name()) - 1),
                                      ls[0].lstrip())
                lsOut.append(sFirstLine)
                lsOut.extend(ls[1:])
        return '\n'.join(lsOut)
        
    def programmer(self):
        return self.dssDocVars['programmer']

    def setprogrammer(self, programmer):
        if not isinstance(programmer, str):
            raise ValueError("str value required.")
        self.dssDocVars['programmer'] = programmer

    def progname(self):
        return self.dssDocVars['progname']

    def setprogname(self, progname):
        if not isinstance(progname, str):
            raise ValueError("str value required.")
        self.dssDocVars['progname'] = progname

    def version(self):
        return self.dssDocVars['version']

    def setversion(self, version):
        if not isinstance(version, str):
            raise ValueError("str value required.")
        self.dssDocVars['version'] = version

    def command(self):
        return self.dssDocVars['command']

    def setcommand(self, command):
        if not isinstance(command, str):
            raise ValueError("str value required.")
        self.dssDocVars['command'] = command

    def title(self):
        """Return the title line."""
        return self.sTitle % self.dssDocVars

    def settitle(self, title):
        if not isinstance(title, str):
            raise ValueError("str value required.")
        self.sTitle = title

    def description(self):
        """Return the description line."""
        return self.sDescription % self.dssDocVars

    def setdescription(self, description):
        if not isinstance(description, str):
            raise ValueError("str value required.")
        self.sDescription = description

    def usage(self):
        """Return the usage string. If it's '' auto generate a good one."""
        if self.sUsage:
            return self.sUsage % self.dssDocVars
        sUsage = '%(command)s <OPTIONS>' % self.dssDocVars
        iOptionals = 0
        for oPositionalArgument in self.loPositionalArgs:
            sUsage += ' '
            if oPositionalArgument.optional():
                sUsage += "[" 
                iOptionals += 1
            sUsage += oPositionalArgument.name().upper()
            if oPositionalArgument.recurring():
                sUsage += ' [%s2 [...]]' % oPositionalArgument.name().upper()
        sUsage += ']' * iOptionals
        return sUsage
            
    def setusage(self, usage):
        if not isinstance(usage, str):
            raise ValueError("str value required.")
        self.sUsage = usage

    def contact(self):
        """Return the contact information as a list of indented paragraphs."""
        return map(lambda x: x % self.dssDocVars, self.lsContact)

    def setcontact(self, text):
        """Update the contact information.
        ARGS:
        text <list str> or <str>:
            The new info as a list of indented paragraphs. String values
            are interpreted as a list of one indented paragraph.

        """
        if isinstance(text, str):
            text = [text]
        self.lsContact = text

    def copyright(self):
        """Return the list of indented paragraphs that form the general docs."""
        return map(lambda x: x % self.dssDocVars, self.lsCopyright)

    def setcopyright(self, text):
        """Update the copyright information.
        IN:
        text <list str> or <str>:
            The new info as a list of indented paragraphs. String values
            are interpreted as a list of one indented paragraph.

        """
        if isinstance(text, str):
            text = [text]
        self.lsCopyright = text

    def generaldocs(self):
        """Return the list of indented paragraphs that form the general docs."""
        return map(lambda x: x % self.dssDocVars, self.lsGeneralDocs)

    def setgeneraldocs(self, text):
        """Update the general documentation.
        ARGS:
        text <list str> or <str>:
            The new info as a list of indented paragraphs. String values
            are interpreted as a list of one indented paragraph.

        """
        if isinstance(text, str):
            text = [text]
        self.lsGeneralDocs = text

    def additionaldocs(self):
        """Return the additional docs as a list of indented paragraphs."""
        return map(lambda x: x % self.dssDocVars, self.lsAdditionalDocs)

    def setadditionaldocs(self, text):
        """Update the additional documentation.
        ARGS:
        text <list str> or <str>:
            The new info as a list of indented paragraphs. String values
            are interpreted as a list of one indented paragraph.

        """
        if isinstance(text, str):
            text = [text]
        self.lsAdditionalDocs= text

    def notedocs(self):
        """Return the list of indented paragraphs that form the note docs."""
        return map(lambda x: x % self.dssDocVars, self.lsNoteDocs)

    def setnotedocs(self, text):
        """Update the documentation notes.
        ARGS:
        text <list str> or <str>:
            The new info as a list of indented paragraphs. String values
            are interpreted as a list of one indented paragraph.

        """
        if isinstance(text, str):
            text = [text]
        self.lsNoteDocs = text

    def filedocs(self, file):
        """Return docs for a specific file as a list of indented paragraphs."""
        return map(lambda x: x % self.dssDocVars, self.dslsFileDocs[file])

    def setfiledocs(self, name, text):
        """Update the docs for a specific program file.
        ARGS:
        name <str>:
            Internal name of the file in question.
        text <list str> or <str>:
            The new info as a list of indented paragraphs. String values
            are interpreted as a list of one indented paragraph.
        
        """
        if isinstance(text, str):
            text = [text]
        self.dslsFileDocs[name] = text

    def _wrapindentedparagraph(self, text, indent=0, width=0):
        """Textwrap an indented paragraph.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        sParagraph = text.lstrip()
        sI = ' ' * (len(text) - len(sParagraph) + indent)
        ls = textwrap.wrap(sParagraph, width=width, initial_indent=sI, subsequent_indent=sI)
        if ls:
            lsOut.extend(ls)
        else:
            lsOut.append('')
        return '\n'.join(lsOut)

    def _wrapindentedtext(self, text, indent=0, width=0):
        """Textwrap a list of indented paragraphs.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        for sIndentedParagraph in text:
            sParagraph = sIndentedParagraph.lstrip()
            sI = ' ' * (len(sIndentedParagraph) - len(sParagraph) + indent)
            ls = textwrap.wrap(sParagraph, width=width, initial_indent=sI, subsequent_indent=sI)
            if ls:
                lsOut.extend(ls)
            else:
                lsOut.append('')
        return '\n'.join(lsOut)

    def _wrapusage(self, width=0):
        """Textwrap usage instructions.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        return textwrap.fill('USAGE: ' + self.usage(), 
                             width=width,
                             subsequent_indent='  >>>   ')

    def shorthelp(self, width=0):
        """Return brief help containing Title and usage instructions.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        lsOut.append(self._wrapindentedparagraph(self.title()))
        if self.description():
            lsOut.append(self._wrapindentedparagraph(self.description(), indent=2, width=width))
        lsOut.append('')
        lsOut.append(self._wrapusage(width=width))
        lsOut.append('')
        return '\n'.join(lsOut)

    def help(self, width=0):
        """Return the standard formatted command line help for the prog.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        lsOut.append(self._wrapindentedparagraph(self.title(), width=width))
        if self.description():
            lsOut.append(self._wrapindentedparagraph(self.description(), indent=2, width=width))
        lsOut.append('')
        lsOut.append(self._wrapusage(width=width))
        if self.loPositionalArgs:            
            lsOut.append('')
            lsOut.append('ARGUMENTS:')
            lsOut.append(self.posarghelp(indent=2, width=width))
        if self.dsoOptions:
            lsOut.append('')
            lsOut.append('OPTIONS:')
            lsOut.append(self.optionhelp(indent=2, width=width))
        if self.lsGeneralDocs:
            lsOut.append('')
            lsOut.append(self._wrapindentedtext(self.generaldocs(), indent=2, width=width))
        if self.lsNoteDocs:
            lsOut.append('NOTE:')
            lsOut.append(self._wrapindentedtext(self.notedocs(), indent=2, width=width))
        return '\n'.join(lsOut)

    def longhelp(self, width=0):
        """Return the standard formatted help text for the prog. 
        
        This should have approximately the amount of information as you'd 
        expect in a man page.
        IN:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        lsOut.append(self._wrapindentedparagraph(self.title(), width=width))
        if self.description():
            lsOut.append(self._wrapindentedparagraph(self.description(), indent=2, width=width))
        lsOut.append('')
        if self.lsContact:
            lsOut.append('CONTACT:')
            lsOut.append(self._wrapindentedtext(self.contact(), indent=2, width=width))
        if self.lsCopyright:
            lsOut.append('COPYRIGHT:')
            lsOut.append(self._wrapindentedtext(self.copyright(), indent=2, width=width))
        lsOut.append(self._wrapusage())
        if self.loPositionalArgs:            
            lsOut.append('')
            lsOut.append('ARGUMENTS:')
            lsOut.append(self.posarghelp(indent=2, width=width))
        if self.dsoOptions:
            lsOut.append('')
            lsOut.append('OPTIONS:')
            lsOut.append(self.optionhelp(indent=2, width=width))
            lsOut.append('')
        if self.lsGeneralDocs:
            lsOut.append(self._wrapindentedtext(self.generaldocs(), indent=2, width=width))
        if self.lsAdditionalDocs:
            lsOut.append('ADDITIONAL:')
            lsOut.append(self._wrapindentedtext(self.additionaldocs(), indent=2, width=width))
        if self.lsNoteDocs:
            lsOut.append('NOTE:')
            lsOut.append(self._wrapindentedtext(self.notedocs(), indent=2, width=width))
        if self.dslsFileDocs:
            lsOut.append('FILES:')
            for sFile, lsDocs in self.dslsFileDocs.iteritems():
                lsOut.append('  %s:' % (sFile % self.dssDocVars))
                lsOut.append(self._wrapindentedtext(self.filedocs(sFile), indent=4, width=width))
        return '\n'.join(lsOut)

    def strsettings(self, indent=0, maxindent=25, width=79):
        """Return user friendly help on positional arguments.        
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        iIndent = 0
        for sOption in self.lsOptionOrder:
            o = self.dsoOptions[sOption]
            sTag = '%*s%s: ' % (indent, ' ', o.name())
            iIndent = max(iIndent, len(sTag))
        iIndent = min(maxindent, iIndent)
        sI = ' ' * iIndent
        for sOption in self.lsOptionOrder:
            o = self.dsoOptions[sOption]
            sTag = '%*s%s: ' % (indent, ' ', o.name())
            sSettings = "%s(%s): %s" % (o.oFormat.sShortName, o.strvalue(), o.location())
            if len(sTag) > iIndent:
                ls = textwrap.wrap(sSettings, width=width, initial_indent=sI, subsequent_indent=sI)
                lsOut.append(sTag)
                lsOut.extend(ls)
            elif len(sTag) == iIndent:
                ls = textwrap.wrap(sSettings, width=width, initial_indent=sI, subsequent_indent=sI)
                sFirstLine = "%s%s" % (sTag, ls[0].lstrip())
                lsOut.append(sFirstLine)
                lsOut.extend(ls[1:])
            else:
                ls = textwrap.wrap(sSettings, width=width, initial_indent=sI, subsequent_indent=sI)
                sFirstLine = "%s%*s%s" % (sTag, iIndent - len(sTag), ' ', ls[0].lstrip())
                lsOut.append(sFirstLine)
                lsOut.extend(ls[1:])
        return '\n'.join(lsOut)

    def settings(self, width=79):
        """Return a list of program options, their values and origins.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.iMaxHelpWidth
        lsOut = []
        lsOut.append(self.title())
        if self.description():
            lsOut.append('  ' + self.description())
        lsOut.append('')
        lsOut.append('SETTINGS:')
        lsOut.append(self.strsettings(indent=2, width=width))
        lsOut.append('')
        return '\n'.join(lsOut)

    def initprog(self,
                 debugparser=False,
                 docsfile=None,
                 configfiles=None,
                 sections=None,
                 argv=None,
                 showusageonnoargs=False,
                 width=None,
                 helphint="Use with --help or --HELP for more information.\n"):
        """Do the usual stuff to initiallize the program.
        
        Read docs and config files, parse arguments and print help, usage, 
        version and settings on demand and halt afterwards.
        ARGS:
        debugparser = False <bool>:
            Don't catch ParseErrors and give user friendly hints. Crash
            instead and give a traceback.
        docsfile = None <str> or None:
            Read a specific docsfile. '' means don't read any docs. None
            means use the default from self.sDocsFile.
        configfiles = None <list str>, <str> or None:
            Use a specific set of config files. None means use the default.
        sections = None <list str>, <str> or None:
            Read a specific set of config sections. None means use the
            default.
        argv = None <list str> or None:
            Use this argument list. None means use sys.argv. argv[0] is 
            ignored.
        showusageonnoargs = True <bool>:
            Show usage and exit if the user didn't give any args. Should be
            set to False if there are no required PositionalArgs in the UI.
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.
        helphint = "Use with --help or --HELP for more help." <str>:
            Give this hint on getting more help at the end of usage
            messages. Note that the default value really ends with a
            newline which has been stripped from the docs for reasons
            of readability.

        """
        if not width:
            width = self.iMaxHelpWidth
        if docsfile is None:
            docsfile = self.sDocsFile
        if docsfile:
            self.readdocs(docsfile)
        if showusageonnoargs:
            bPrintUsageAndExit = False
            if argv is None:
                if len(sys.argv) == 1:
                    bPrintUsageAndExit = True
            elif len(argv) == 0:
                bPrintUsageAndExit = True
            if bPrintUsageAndExit:
                print self.shorthelp()
                if helphint:
                    print self._wrapindentedparagraph(helphint, indent=2, width=width)
                sys.exit(0)
        bParseError = False
        try:
            self.parsefiles(configfiles, sections)
            self.parseargs(argv, 'Command line.')
        except ParseError, e:
            if debugparser:
                raise
            bParseError = True
        dsxOptions = self.options()
        if self.sSettingsOption and dsxOptions[self.sSettingsOption]:
            print self.settings()
            sys.exit()
        if self.sLongHelpOption and dsxOptions[self.sLongHelpOption]:
            print self.longhelp()
            sys.exit()
        if self.sHelpOption and dsxOptions[self.sHelpOption]:
            print self.help()
            sys.exit()
        if self.sVersionOption and dsxOptions[self.sVersionOption]:
            print self.version()
            sys.exit()
        if bParseError:
            print self.shorthelp()
            sys.exit("ERROR: %s" % e)
