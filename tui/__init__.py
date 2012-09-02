"""TUI Textual User Interface - A sane command line user interface.

Author: Joel Hedlund <yohell@ifm.liu.se>

TUI is straightforward to use, both for developers and users. It can parse 
options from multiple config files and command line, and can produce 
constructive error messages given bad input. It can also help keep the 
source code clean by moving help text to a separate documentation file.

If you have problems with this package, please contact the author.

QUICKSTART:
Put myprog.docs in install_dir (possibly also .conf), and then write myprog: 
------------------------------------------------------------------------------
#!/usr/bin/env python
'''MyProgram 
A one line description of my program goes here.

You can put any amount of text in the rest of this docstring, and it will be 
ignored by get_metainfo(), however certain keywords are detected:

Website:   http://www.example.com
Download:  http://www.example.com/download
Author:    Joel Hedlund <yohell@ifm.liu.se>
Contact:   Please contact the author.
Copyright: Copyright blurb.
License:   Name of the license.
#Version:  Using __version__ is probably better. Commented this out for now.
'''
__version__ = "0.1.0"
import sys
import mypackage
def main(argv=sys.argv):
    from tui import (BadArgument, formats, get_metainfo, tui, Option, Posarg)
    ui = tui([Option('quiet', 'Flag', 'q'),
              Option('noise', 'Int', 'v', default=10),
              Option('job-tag', 'String', recurring=True),
              Posarg('in-file', formats.ReadableFile(special={'-': None})),
              Posarg('out-file', formats.WritableFile, optional=True)],
             version=__version__,
             install_dir=mypackage, # or __file__ if your .cfg is here. 
             ignore=['squeegees'],
             **get_metainfo(__file__))
    # Any additional custom parameter checking:
    if ui['noise'] > 9000:
        ui.graceful_exit(BadArgument('noise', ui['noise'], 'way too chatty'))
    if ui['in-file'] and open(ui['in-file']).read() == 'bad content':
        ui.graceful_exit('custom error message')
    # Tweak stuff if needed:
    if ui['noise'] < 8000:
        ui['noise'] %= 7
    # Go time!
    try:
        return mypackage.do_stuff(**ui.dict())
    except KeyboardInterrupt:
        ui.graceful_exit('interrupted by user')
    
if __name__ == '__main__':
    sys.exit(main() or 0)
------------------------------------------------------------------------------

We're pretty much done here, but if you feel like it, put this in myprog.docs:
------------------------------------------------------------------------------
PARAMETER: quiet
Suppress all normal output through speakers.

PARAMETER: noise
Level of chatter, less is more.

PARAMETER: in-file
What data file to read, in some format. 

PARAMETER: squeegees
This parameter is not used by myprog but a sibling program in the same suite.

GENERAL:
General info on how to use %(progname)s.

ADDITIONAL:
You can use docvars in docsfiles, e.g: %(progname)s v%(version)s by 
%(author)s is started using %(command)s. # This comment will be removed.
Since these lines have the same indent, they will be concatenated into a 
single paragraph, and later linewrapped to the user's current terminal width.
# This line is ignored.
This is a literal hash char \# in the last sentence in the first paragraph. 

This is a new paragraph, with a bullet list:
 * End paragraphs with backslash \
 * to indicate that next line with same indent \
 * is a new paragraph with same indent.

FILE: /etc/%(command)s/%(command)s-hosts.conf
Documentation on program specific file.
------------------------------------------------------------------------------

And if you like, something like this in myprog.conf:
------------------------------------------------------------------------------
# This is a comment. The DEFAULT section (always uppercase) is always read.
[DEFAULT]
# There is no 'server' option but you can do this to set other vars, see below.
server = liu.se
# The squeegee option is ignored in myprog, probably used by a sibling prog.
squeegee = moo

[myprog]
# This sets job-tag to liu.se/index.html
job-tag = %(server)s/index.html
# Use on,yes,true,1 or off,no,false,0 to set values for flags.  
quiet = no 

[myotherprog]
# This section is ignored by myprog, which only reads its own sections.
------------------------------------------------------------------------------

Then, on the command line:
$ myprog # Print short usage message.
$ myprog -h (or --help) # Print help message.
$ myprog -H (or --HELP) # Print more verbose help message.
$ myprog -V (or --version) # Print version.
$ myprog -S (or --settings) # Print settings and origin: builtin/file/cmdline.
$ myprog --job-tag a --job-tag b -q -v 14 - # Up to you!

In the latter case you get:
ui['quiet'] == True
ui['job-tag'] == ['liu.se/index.html', 'a', 'b'] # A list since it's recurring.
ui['in-file'] == sys.stdin # the special value - was used. 
ui['out-file'] == None # since it's optional and the user gave no arg for it. 


DETAILS:
As much as possible of the tui documentation has been pushed to __doc__ strings
for individual modules, functions, classes and methods, but here are some nice
entry points:

To get started you probably want to import tui, Option and Posarg from the tui
package, and possibly some formats from the tui.formats module.

The tui class is the main workhorse that holds all program info, knows how to
parse docs, config and command line parameters, and how to present all this
info to the user. Instantiate with metainfo (see GET_METAINFO() DOCSTRING 
SYNTAX just below) and a list of options and positional arguments, and tui will
find and read program documentation from docsfiles, find and parse settings 
from various configfiles and the command line, and will exit with helpful error
messages on parameter format errors (like when the user types 'monkey' when the
program expects a number, or gives a read-only file to write results to, and so
on), and finally it will react to some useful options (--help, --HELP, 
--version and --settings, see the example just above). You can of course 
customize all this, or sidestep the magic alltogether. Read method and class 
docs to see how it's done.

The format classes in the tui.formats module know how to take user supplied
strings and transform them into validated values usable in your program, for
examples: Int, ReadableFile, WritableDir, Choice, Flag, RegEx, and so on.
You can also write your own formats and add to your tui instance. Use 
existing formats as examples for that.


CONFIGFILE SYNTAX:
tui uses the ConfigParser file structure (see python docs), but case sensitive.
Thus the default section is [DEFAULT] (always uppercase).


GET_METAINFO() DOCSTRING SYNTAX:
If you've written your program __doc__ string right there is probably a lot of 
of useful program metainfo in there, which you could probably pull out using 
some simple string mangling tricks and feed to tui directly. get_metainfo() is 
a simple helper that can help you do this as long as you take a little care 
writing your docstring carefully. By default, it will return a metainfo dict 
with keys 'author', 'command', 'contact', 'copyright', 'description', 
'download', 'progname', 'version' and 'website'. 

The docstring needs to be multiline and the closing quotes need to be first 
on a line, optionally preceded by whitespace. 

Command is assumed to be os.path.basename(scriptfile) with any trailing .py*
filename extension removed.

The first non-whitespace line is re.search'ed using first_line_pattern, 
default e.g (version optional, contains no whitespace): PROGNAME [vVERSION]

The next non-whitespace, non-keyword line is expected to be the program 
description.

See python code above for a syntax example, and function docstring below for 
customisation details. This function will only make minimal efforts to succeed. 
If it doesn't fit your style: roll your own! It's really not that hard.


DOCSFILE SYNTAX:
Docsfiles are written as blocks, which start with a tag line followed by one or
more lines of text. Tags can be any of:

TAG          TYPE
ADDITIONAL:  [multiple paragraphs]
CONTACT:     [multiple paragraphs]
COPYRIGHT:   [multiple paragraphs]
DESCRIPTION: [single paragraph]
DOWNLOAD:    [multiple paragraphs]
GENERAL:     [multiple paragraphs]
GIT:         [multiple paragraphs]
SUBVERSION:  [multiple paragraphs]
TITLE:       [single paragraph]
USAGE:       [single paragraph]

Additionally, these labelled blocks are available:
PARAMETER:   [single paragraph]
FILE:        [multiple paragraphs]

which also require a label on the tag line (see examples above).

The PARAMETER block is used for both program options and positional 
parameters (so you can change type for parameters in code without having to 
update the docsfile as well).

All blocks can use documentation variables (docvars) using python string 
formatting, e.g: %(author)s, %(command)s, %(progname)s and %(version)s. This 
also works for FILE: labels (see examples above).

In single paragraph blocks, all text is concatenated into a single string, with 
newlines and blank lines converted to a single space character. In multiple 
paragraph blocks, all consecutive lines with the same indentation is 
concatenated into single paragraph strings with the same indentation. 
Consecutive lines with different indent will be stored as different paragraphs. 
If you need to store consecutive lines with the same indent as different 
paragraphs (for example for bulleted lists), end the preceding line with a 
backslash character '\'. To avoid preserving blank lines in multiple paragraph 
blocks, start the line with a comment character '#'.

Anything following a '#' character on a line is disregarded as a comment.
Use backslashes to escape # characters if you want to use them in text.
Backslashes have no special meaning anywhere else, but if you feel an urge
to have backslashes directly preceding hashes in your output, type twice as
many as you want, plus one more to keep the hash character from becoming a 
comment. Examples:   

#       is a comment
\#      is a hash character.
\\#     is a backslash followed by comment.
\\\\\#  is two backslashes and a hash character.
\\\\\\# is three backslashes and a comment.
...     you get the picture.


COPYRIGHT: 
Copyright (c) 2011 Joel Hedlund


LICENSE:
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

__version__ = "2.0.0rc1"
__copyright__ = "Copyright (c) 2012 Joel Hedlund."
__license__ = "MIT"

__all__ = ['BadAbbreviationBlock',
           'BadArgument',
           'BadNumberOfArguments',
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
           'formats',
           'tui',
           'textblockparser']

import ConfigParser
import fcntl
import os
import re
import sys
import struct
import termios
import textwrap

import formats
from textblockparser import (IndentedParagraphs,
                             SingleParagraph,
                             TextBlockParser)


class TUIBase(object):
    "Base class for tui.tui. Does nothing. Used only by tui exceptions."

## ERRORS

class ParseError(Exception):
    """Base class for exceptions raised while parsing option values."""
    template = None
    format_message = lambda self, args: self.template % args
    
    def __init__(self, *args, **kw):
        self.args = args
        self.message = kw.get('message') or self.format_message(args)
        
    def __str__(self):
        return self.message

class BadArgument(ParseError):
    """Raised when options get literals incompatible with their Format."""
    
    template = "%s is not an acceptable argument for %s (%s)."

    def __init__(self, name, value, details, message=None):
        super(BadArgument, self).__init__(value, name, details, message=message)

class BadNumberOfArguments(ParseError):
    """Raised when the user has supplied the wrong number of arguments."""

    template = "%s requires %s arguments and was given %s."
    
    def __init__(self, name, n_required, n_given, message=None):
        super(BadNumberOfArguments, self).__init__(name, n_required, n_given, message=message)

class InvalidOption(ParseError):
    """Raised on attempts to access nonexisting options."""
    
    template = "The option %s does not exist."

    def __init__(self, name, message=None):
        super(InvalidOption, self).__init__(name, message=message)
        
class OptionRecurrenceError(ParseError):
    """Raised on multiple use of single use options."""

    template = "The option %s can only be used once in an argument list."

    def __init__(self, name, message=None):
        super(OptionRecurrenceError, self).__init__(name, message=message)

class ReservedOptionError(ParseError):
    """Raised when command line reserved options are used in a config file."""

    template = "The option %s is reserved for command line use."

    def __init__(self, name, message=None):
        super(ReservedOptionError, self).__init__(name, message=message)
        
class BadAbbreviationBlock(ParseError):
    """Raised when poorly composed abbreviation blocks are encountered.
    
    For example if options that require value arguments occurs anywhere
    except last in the block.
    """
    template = "Option %s in the abbreviation block %s is illegal (%s)."

    def __init__(self, abbreviation, block, details, message=None):
        super(BadAbbreviationBlock, self).__init__(abbreviation, block, details, message=message)

## Internal helpers

_UNSET = []
def _list(value, default=_UNSET):
    if value is None:
        if default is _UNSET:
            return []
        return default
    if not isinstance(value, (list, tuple)):
        return [value]
    return value

def _docs(text, docvars):
    if not text:
        return
    if isinstance(text, basestring):
        return [text % docvars]
    if isinstance(text, dict):
        return dict((name % docvars, _docs(text, docvars)) for name, text in text.items())
    return [par % docvars for par in text]

class DocParser(TextBlockParser):
    """Read docsfiles for tui."""

    def __init__(self, tabsize=4):
        """
        tabsize > 0 replaces tab characters with that many spaces. Set <= 0 to 
        disable.
        """
        super(DocParser, self).__init__(untagged=None, tabsize=tabsize)
        self.addblock('title', SingleParagraph)
        self.addblock('description', SingleParagraph)
        self.addblock('usage', SingleParagraph)
        self.addblock('contact', IndentedParagraphs)
        self.addblock('website', IndentedParagraphs)
        self.addblock('download', IndentedParagraphs)
        self.addblock('git', IndentedParagraphs)
        self.addblock('subversion', IndentedParagraphs)
        self.addblock('copyright', IndentedParagraphs)
        self.addblock('license', IndentedParagraphs)
        self.addblock('general', IndentedParagraphs)
        self.addblock('additional', IndentedParagraphs)
        self.addblock('parameters', SingleParagraph, True, 'PARAMETER')
        self.addblock('files', IndentedParagraphs, True, 'FILE')

class StrictConfigParser(ConfigParser.SafeConfigParser):
    """A config parser that minimises the risks for hard-to-debug errors."""
    
    def optionxform(self, option):
        """Strip whitespace only."""
        return option.strip()

    def unusedoptions(self, sections):
        """Lists options that have not been used to format other values in 
        their sections. 
        
        Good for finding out if the user has misspelled any of the options.
        """
        unused = set([])
        for section in _list(sections):
            if not self.has_section(section):
                continue
            options = self.options(section)
            raw_values = [self.get(section, option, raw=True) for option in options]
            for option in options:
                formatter = "%(" + option + ")s"
                for raw_value in raw_values:
                    if formatter in raw_value:
                        break
                else:
                    unused.add(option) 
            return list(unused)

def get_terminal_size(default_cols=80, default_rows=25):
    """Return current terminal size (cols, rows) or a default if detect fails.

    This snippet comes from color ls by Chuck Blake:
    http://pdos.csail.mit.edu/~cblake/cls/cls.py

    """
    def ioctl_GWINSZ(fd):
        """Get (cols, rows) from a putative fd to a tty."""
        try:                               
            rows_cols = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')) 
            return tuple(reversed(rows_cols))
        except:
            return None
    # Try std in/out/err...
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    # ...or ctty...
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            # ...or fall back to defaults
            cr = (int(os.environ.get('COLUMNS', default_cols)), 
                  int(os.environ.get('LINES', default_rows)))
    return cr

def _autoindent(labels, indent=0, maxindent=25, extra=2):
    return max(indent + extra, *(len(s) for s in labels if len(s) < maxindent))

## Public API

def get_metainfo(scriptfile,
                 keywords=['author', 'contact', 'copyright', 'download', 'git', 'subversion', 'version', 'website'],
                 special={},
                 first_line_pattern=r'^(?P<progname>.+)(\s+v(?P<version>\S+))?',
                 keyword_pattern_template=r'^\s*%(pretty)s:\s*(?P<%(keyword)s>\S.+?)\s*$',
                 prettify = lambda kw: kw.capitalize().replace('_', ' ')):
    """Dumb helper for pulling metainfo from a script __doc__ string.
 
    Returns a metainfo dict with command, description, progname and the given 
    keywords (if present).   
    
    This function will only make minimal efforts to succeed. If you need 
    anything else: roll your own.
    
    The docstring needs to be multiline and the closing quotes need to be first 
    on a line, optionally preceeded by whitespace. 
    
    The first non-whitespace line is re.search'ed using first_line_pattern, 
    default e.g (version optional, contains no whitespace): PROGNAME [vVERSION]
    
    The next non-whitespace, non-keyword line is expected to be the program 
    description.

    The following lines are re.search'ed against a keyword:pattern dict which
    is constructed using  
    keyword_pattern % dict(pretty=prettify(keyword), keyword=keyword)
    Default prettify is keyword.capitalize().replace('_', ' '). Example,
    for the keyword "licence" will match the following line:
    License: The MIT license.
    and set the license metainfo to "The MIT license.".
        
    Any keyword:pattern pairs that need special treatment can be supplied with 
    special.
    """
    patterns = dict((kw, re.compile(keyword_pattern_template % dict(pretty=prettify(kw), keyword=kw))) for kw in keywords)
    patterns.update(special)
    metainfo = dict()
    
    if scriptfile[-4:] in ['.pyc', '.pyo']: 
        scriptfile = scriptfile[:-1]
    script = open(scriptfile)
    closer = ''
    for line in script:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line[:3] in ('"""', "'''"):
            closer = line[:3] 
            break
        raise ValueError('file contains no docstring')
    if not line:
        for line in script:
            line = line.strip()
            if line:
                break
    g = re.search(first_line_pattern, line[3:]).groupdict()
    metainfo['progname'] = g['progname']
    if g['version']:
        metainfo['version'] = g['version']
    for line in script:
        if line.strip().startswith(closer):
            break
        for keyword, pattern in patterns.items():
            m = pattern.search(line)
            if m:
                metainfo[keyword] = m.group(keyword)
                break
        if line.strip() and not 'description' in metainfo:
            metainfo['description'] = line.strip()
    return metainfo

class Parameter(object):
    """A program parameter.
    
    Has subclasses Option and PositionalArgument.
    """
    def __init__(self, name, format, recurring=False, docs=None):
        self.name = name
        self.format = formats.get_format(format)
        self.docs = docs or self.format.docs
        self.recurring = recurring

    @property
    def strvalue(self):
        value = self.value
        if not self.recurring:
            value = [value]
        return ', '.join(self.format.present(v) for v in value)
    
    nargs = property(lambda self: self.format.nargs)
    formatname = property(lambda self: self.format.name)

    def parse(self, argv):
        """Consume and process arguments and store the result.

        Override in subclasses to do actual work. Subclasses may take other
        params.
        """

    def parsestr(self, argsstr, usedname, location):
        """Parse a string lexically and store the result.

        Override in subclasses to do actual work. Subclasses may take other
        params.
        """
    
class Option(Parameter):
    """A program option."""
    
    def __init__(self, 
                 name, 
                 format, 
                 abbreviation=None, 
                 default=_UNSET,
                 recurring=False, 
                 reserved=False,
                 docs=None):
        """
        name is the long option name. Used in settings files and with a '--'
        prefix on the command line. This should be as brief and descriptive 
        as possible. Must be at least length 2, must start and end with a 
        letter or number and may contain letters, numbers, underscores and 
        hyphens in between.
        
        format should be a formats.Format subclass or instance, and determines
        how this option behaves and what arguments it may require. The name of
        one of the formats in the tui.formats module is also accepted.
        
        abbreviation (if given) is the one-character abbreviation of the option
        name. Can be anything other than a literal '-' character. Used with a 
        '-' prefix on the command line.

        default is the option's default value. Omit to use format.default, or 
        an empty list if the option is recurring.

        If reserved is true the option will be reserved for command line use.
        
        docs is user friendly help text for the option. None means use 
        format.docs and add note on recurrence or command line reservation.
        
        If recurring is true, the option allowed to occur several times on the
        command line. .value will then be a list of all parsed values, in 
        parsing order. 
        """
        super(Option, self).__init__(name, format, recurring, docs)
        if default is _UNSET:
            if recurring:
                default = []
            else:
                default = self.format.default
        self.value = default
        if abbreviation and len(abbreviation) != 1:
            raise ValueError("Option abbreviations must be strings of length 1.")
        if abbreviation == '-':
            raise ValueError("Invalid abbreviation (cannot be '-').")
        self.abbreviation = abbreviation
        self.reserved = reserved
        self.location = "Builtin default."
        if docs is None:
            if recurring:
                self.docs += " Can be used repeatedly."
            if reserved:
                self.docs += " Reserved for command line use."

    def parse(self, argv, usedname, location):
        """Consume and process arguments and store the result.
        ARGS:
        argv <list str>:
            The argument list to parse.
        usedname <str>:
            The string used by the user to invoke the option.
        location <str>:
            A user friendly sring describing where the parser got this
            data from.

        """
        try:
            value = self.format.parse(argv)
        except formats.BadNumberOfArguments, e:
            raise BadNumberOfArguments(usedname, e.required, e.supplied)
        except formats.BadArgument, e:
            raise BadArgument(usedname, e.argument, e.message)
        if self.recurring:
            self.value.append(value)
        else:
            self.value = value
        self.location = location

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
            value = self.format.parsestr(argsstr)
        except formats.BadNumberOfArguments, e:
            raise BadNumberOfArguments(usedname, e.required, e.supplied)
        except formats.BadArgument, e:
            raise BadArgument(usedname, e.argument, e.message)
        if self.recurring:
            self.value.append(value)
        else:
            self.value = value
        self.location = location

help_option = Option('help', formats.Flag, 'h', reserved=True, docs='Print help and exit.')
longhelp_option = Option('HELP', formats.Flag, reserved=True, docs='Print verbose help and exit.')
version_option = Option('version', formats.Flag, 'V', reserved=True, docs='Print version string and exit.')
settings_option = Option('settings', formats.Flag, reserved=True, docs='Print settings summary and exit.')

class PositionalArgument(Parameter):
    """A positional command line program parameter."""
    
    _name_re = r'[A-Za-z0-9][\w-]*[A-Za-z0-9]'
    
    def __init__(self, name, format, recurring=False, optional=False, docs='', displayname=None):
        """
        name is the name of the positional argument. Must be at least length 2,
        must start and end with a letter or number and may contain letters, 
        numbers, underscores and hyphens in between.
        
        format should be a formats.Format subclass or instance, and determines
        how this positional argument behaves and what arguments it may require. 
        The name of one of the formats in the tui.formats module is also 
        accepted.
        
        docs is user friendly help text for the option. None means use 
        format.docs.
        
        If recurring is true, this positional argument can be used multiple 
        times on the command line, and .parse() will consume all arguments fed
        to it.
        
        If optional is true, the user is permitted to omit this argument from 
        the command line?
        """
        super(PositionalArgument, self).__init__(name, format, recurring, docs)
        self.optional = optional
        self._value = None
        self.displayname = displayname or name.upper().replace('-', '_')
        if docs is None:
            if recurring:
                self.docs += " Can be used multiple times on the command line."
            if optional:
                self.docs += " Optional."

    def _get_value(self):
        try:
            return self._value
        except AttributeError:
            raise AttributeError('value does not exist before parsing arguments')

    nargs = property(lambda self: self.format.nargs)
    formatname = property(lambda self: self.format.name)
    value = property(_get_value, lambda self, value: setattr(self, '_value', value))

    def parse(self, argv):
        """Consume and process arguments and store the result.
        
        argv is the list of arguments to parse (will be modified).
        
        Recurring PositionalArgumants get a list as .value.
        
        Optional PositionalArguments that do not get any arguments to parse get
        None as .value, or [] if recurring. 
        """
        if not argv and self.optional:
            self.value = [] if self.recurring else None
            return
        try:
            value = self.format.parse(argv)
            if not self.recurring:
                self.value = value
                return
            self.value = [value]
            while argv:
                self.value.append(self.format.parse(argv))
        except formats.BadNumberOfArguments, e:
            raise BadNumberOfArguments(self.displayname, e.required, e.given)
        except formats.BadArgument, e:
            raise BadArgument(self.displayname, e.argument, e.details)

class tui(TUIBase):
    """Textual user interface."""
    
    # What sections to include in help and longhelp, and in what order.
    help_sections = ['title',
                     'description',
                     'usage',
                     'arguments',
                     'options',
                     'general']
    longhelp_sections = ['title',
                         'description',
                         'contact',
                         'website',
                         'download',
                         'license',
                         'usage',
                         'arguments',
                         'options',
                         'general',
                         'additional',
                         'files']
    
    def __init__(self,
                 parameters=None,
                 version=None,
                 install_dir=None,
                 argv=None,
                 launch=True,
                 # Most of the rest of the args are highly situational.
                 # Consider calling with **get_metainfo(__file__) instead. 
                 progname=None,
                 author=None,
                 title='%(progname)s v%(version)s by %(author)s.',
                 description=None,
                 contact=None,
                 website=None,
                 download=None,
                 license=None,
                 copyright=None,
                 command=None,
                 usage=None,
                 general=None,
                 additional=None,
                 note=None,
                 filedocs=None,
                 docsfiles=None,
                 docsfilenames=None,
                 width=None,
                 configfiles=None,
                 configdirs=None,
                 configfilenames=None,
                 sections=None,
                 ignore=None,
                 helpoption=help_option,
                 longhelpoption=longhelp_option,
                 versionoption=version_option,
                 settingsoption=settings_option):
        """
        Many of the metainfo parameters (author, progname...) should already
        be present in the program docstring if you're coding by the book. You 
        can avoid repeating them by doing something like: 
        ui = tui(..., **get_metainfo(__file__)).
        The parameters that will be available using the above incantation are
        marked with asterixes* below.
        
        .readdocs() can read most user documentaion from external docsfiles, 
        so there is typically no need to supply that on instantiation. See the
        docsfile parameter. Parameters that can be set using .readdocs() are 
        marked with percent% below.
        
        All parameters that take a list of indented paragraphs can use docvars.
        They also accept just a string which, is then taken as a list of one 
        paragraph. None means there is no such documentation.
        
        All parameters that take an Option also accept factory functions for
        Option objects (like a class, or a function like help_option). None
        means don't add such an option. Note however that just adding the 
        helpoption, longhelpoption, versionoption and settingsoption at 
        instantiation will not activate their documented functionality. Use 
        e.g. .start() for this.
        
        parameters is a list of Options and PositionalArguments to be added
        to the user interface.
        
        version* is the current program version string. Although you *can* set
        this using get_metainfo, you typically want to pass __version__ here
        instead. Available as a docvar.

        install_dir (if given) will be searched for configfiles and docsfiles.
        Use containing dir if given a python package or a path to a file (e.g. 
        mypackage or __file__).
        
        argv is the list of command line arguments to use (see launch just 
        below). None means use a copy of sys.argv.

        If launch is True (default) then .launch(argv) will be called after 
        initiallization.
         
        *progname is the user friendly name of the program. Available as a 
        docvar. 
        
        *author is who made the program. Available as a docvar. 
        
        title is what to put in the title line on help pages. Can use docvars.

        *%description is a oneliner describing the program. Can use docvars.
        
        *%contact is contact information as a list of indented paragraphs.

        *%website is the url to the website of the program. Can be given as a
        list of indented paragraphs if needed.

        *%download is where the program can be downloaded. Can be given as a
        list of indented paragraphs if needed.
        
        *%copyright is copyright information as a list of indented paragraphs. 
        
        *%license is brief information on the licensing conditions of the 
        program. Can be given as a list of indented paragraphs if needed.

        *command* is how to execute the program. Available as a docvar. None 
        means use the basename of sys.argv[0].
        
        usage is user friendly help on how to execute the program. Can 
        use docvars. None means auto generate from options and positional 
        arguments.
        
        %general is general program documentation as a list of indented
        paragraphs. Typically displayed on the normal help page. 

        %additional is additional program documentation as a list of indented
        paragraphs. Typically only displayed in verbose help (longhelp). 

        %note is the same as additional, only with a different label.

        %filedocs is documentation on files used by the program, as a dict of
        file names and indented paragraphs. Typically only displayed in 
        verbose help (longhelp). Keys and values may use docvars. None means 
        no such documentation.
        
        docsfilenames is a list of basenames of docsfiles and is only useful 
        together with install_dir. A str means a list of one item. None means 
        [basename(install_dir) + 'docs' (if given), command + '.docs']. 
        Do not use together with the docsfiles parameter.

        docsfiles is a list of paths to potential DocParser docsfiles; parse if
        present, in the given order. None means look for each docsfilename in
        install_dir (if given). A str means a list of one item. Note that no 
        docs will be read on instantation. Use .readdocs() (or .launch()) for 
        that.
        
        width is the maximum allowed width for help text. 0 means try to guess
        the terminal width, and use 79 if that fails.
        
        configdirs is a list of paths to directories to search for configfiles.
        None means [install_dir (if given), '/etc/' + command, '~/.' + command].
        A str means the same, but with this string replacing command. Do not 
        use together with the configfiles parameter.
        
        configfilenames is a list of basenames of configfiles. A str means a 
        list of one item. None means [command + '.conf']. Do not use together 
        with the configfiles parameter.
        
        configfiles is a list of config files to parse. None means try each 
        configfilename in the given order, in each of the configdirs in the 
        given order. configfiles are parsed incrementally by .parsefiles() (or
        .launch()). A str means a list of one item. [] means no configfiles.
        
        sections is a list of sections to read in config files. A str means a 
        list of one item. None means [command]. The DEFAULT section (note 
        uppercase) is always read, and it is read as if its contents were 
        copied to the beginning of all other sections.
        
        ignore is a list of option and positional argument names that should be
        ignored if encountered in configfiles or docsfiles. Any other unknown 
        names will raise an error. This is primarily to help users catch 
        spelling mistakes. This feature is useful for example if you are using
        the same files for several programs in a suite, where some parameters 
        are shared and you want to ignore the others. Set to None to ignore all
        all unknown (not recommended). 
        
        options can be used to supply a preconfigured option dictionary, if you
        for some reason prefer this to .makeoption(). tui will not check this 
        for you. See also option_order and abbreviations.
        
        option_order determines the order in which the options will be shown in
        help texts.
        
        abbreviations is a abbreviation:option dict, similar to options.
        
        positional_args can be used to supply a list of preconfigured positional
        arguments, if you for some reason prefer this to .makeposarg(). tui will 
        not check this for you. See also positional_arg_names.
        
        positional_arg_names are the display names for positional arguments in
        help texts.
        
        helpoption adds an option that lets the user request help in the usual
        way. Default is '--help' or '-h', option reserved for command line use.
        None means don't add such an option.
        
        longhelpoption adds an option that lets the user request verbose help.
        Default is '--HELP' or '-H', option reserved for command line use. None
        means don't add such an option. 

        versionoption adds an option that lets the user print the version 
        string. Default is '--version' or '-V', option reserved for command
        line use). None means don't add such an option.

        settingsoption adds an option that lets the user print a brief summary
        of program settings. Default is '--settings' or '-S', option reserved 
        for command line use). None means don't add such an option.
        """
        params = locals()
        self.options = dict()
        self.option_order = []
        self.abbreviations = dict()
        self.positional_args = []
        for p in parameters:
            if isinstance(p, Option):
                self._add_option(p)
            elif isinstance(p, PositionalArgument):
                self._add_positional_argument(p)
            else:
                raise TypeError('unknown parameter type')
        self.basic_option_names = dict()
        for optiontype in ['help', 'longhelp', 'settings', 'version']:
            option = params[optiontype + 'option']
            if not option:
                continue
            if not isinstance(option, Option):
                option = option()
            self._add_option(option)
            self.basic_option_names[optiontype] = option.name

        # Did the user give a module/package rather than a path? 
        if isinstance(install_dir, type(sys)):
            install_dir = install_dir.__file__
        if isinstance(install_dir, basestring) and os.path.isfile(install_dir):
            install_dir = os.path.dirname(install_dir)
        
        self.docvars = dict((s, params[s]) for s in ['author', 'progname', 'version'])
        if command is None:
            command = os.path.basename(sys.argv[0])
        self.docvars['command'] = command
        self.docs = dict(title=_docs(title, self.docvars),
                         usage=_docs(usage, self.docvars),
                         files=_docs(filedocs, self.docvars))
        if filedocs is None:
            filedocs = dict()
        self.docs['files'] = filedocs
        self.docs.update((name, _list(params[name])) for name in ['additional', 'contact', 'copyright', 'description', 'download', 'general', 'license', 'website'])
        self.ignore = _list(ignore)
        if docsfiles is None:
            if install_dir:
                if docsfilenames is None:
                    docsfilenames = [os.path.basename(install_dir) + '.docs']
                    if command:
                        docsfilenames.append(command + '.docs')
                docsfiles = [os.path.join(install_dir, f) for f in docsfilenames]
        elif docsfilenames:
            raise ValueError('do not use docsfilenames together with docsfiles')
        self.read_docs(docsfiles)
        
        self.sections = _list(sections, [command])
        if configfiles is None:
            dirname = command
            if isinstance(configdirs, basestring):
                dirname = configdirs
                configdirs = None
            if configdirs is None:
                configdirs = []
                if install_dir:
                    configdirs.append(install_dir)
                configdirs += [os.path.join('/etc', dirname), 
                               os.path.expanduser(os.path.join('~', '.' + dirname))]
            configfilenames = _list(configfilenames, [command + '.conf'])
            configfiles = [os.path.join(d, f) for d in configdirs for f in configfilenames]
        elif configdirs or configfilenames:
            raise ValueError('do not use configfiles together with configdirs and configfilenames')
        elif isinstance(configfiles, basestring):
            configfiles = [configfiles]
        self.configfiles = configfiles
        if self.configfiles:
            self.addconfigfiledocs()
        
        if not width:
            width = get_terminal_size()[0]
        self.width = width
        
        if launch:
            self.launch(argv)

    def __iter__(self):
        """Iterate over .keys()."""
        return iter(self.keys())
    
    def __contains__(self, key):
        """Shorthand for key in .keys()."""
        return key in self.keys()
    
    def __getitem__(self, key):
        """Shorthand for .getparam(key).value."""
        return self.getparam(key).value
    
    def __setitem__(self, key, value):
        """Shorthand for .getparam(key).value = value.
        
        Useful when doing additional modifications after tui is done parsing.
        """
        self.getparam(key).value = value
    
    def keys(self):
        """List names of options and positional arguments."""
        return self.options.keys() + [p.name for p in self.positional_args]

    def values(self):
        """List values of options and positional arguments."""
        return self.options.values() + [p.value for p in self.positional_args]

    def items(self):
        """List values of options and positional arguments."""
        return [(p.name, p.value) for p in self.options.values() + self.positional_args]

    def dict(self):
        """Return a name:value dict of all options and positional arguments.
        
        Useful when you absolutely need a dict, e.g: do_stuff(**ui.dict()).
        """
        return dict(self.items())
    
    def getparam(self, key):
        """Get option or positional argument, by name, index or abbreviation.
        
        Abbreviations must be prefixed by a '-' character, like so: ui['-a']
        """
        try:
            return self.options[key]
        except:
            pass
        for posarg in self.positional_args:
            if posarg.name == key:
                return posarg
        try:
            return self.abbreviations[key[1:]]
        except:
            raise KeyError('no such option or positional argument')
    
    def _add_option(self, option):
        """Add an Option object to the user interface."""
        if option.name in self.options:
            raise ValueError('name already in use')
        if option.abbreviation in self.abbreviations:
            raise ValueError('abbreviation already in use')
        if option.name in [arg.name for arg in self.positional_args]:
            raise ValueError('name already in use by a positional argument')
        self.options[option.name] = option
        if option.abbreviation:
            self.abbreviations[option.abbreviation] = option
        self.option_order.append(option.name)

    def _add_positional_argument(self, posarg):
        """Append a positional argument to the user interface.

        Optional positional arguments must be added after the required ones. 
        The user interface can have at most one recurring positional argument, 
        and if present, that argument must be the last one.
        """
        if self.positional_args:
            if self.positional_args[-1].recurring:
                raise ValueError("recurring positional arguments must be last")
            if self.positional_args[-1].optional and not posarg.optional:
                raise ValueError("required positional arguments must precede optional ones")
        self.positional_args.append(posarg)
    
    def read_docs(self, docsfiles):
        """Read program documentation from a DocParser compatible file.

        docsfiles is a list of paths to potential docsfiles: parse if present.
        A string is taken as a list of one item.
        """
        updates = DocParser()
        for docsfile in _list(docsfiles):
            if os.path.isfile(docsfile):
                updates.parse(docsfile)
        self.docs.update((k, _docs(updates[k], self.docvars)) for k in self.docs if updates.blocks[k])
        for name, text in updates['parameters'].items():
            if name in self:
                self.getparam(name).docs = text[0] % self.docvars
            elif name not in self.ignore:
                raise ValueError("parameter %r does not exist" % name)

    def addconfigfiledocs(self):
        docs = ["A %(progname)s configuration file. %(progname)s will look configfiles in the following loctions, and in the following order:" % self.docvars]
        docs.extend("  %s. %s" % (i + 1, p) for i, p in enumerate(self.configfiles))
        docs.append('')
        docs.append("The following sections will be parsed, and in the following order:")
        docs.extend("  %s. [%s]" % (i + 1, s) for i, s in enumerate(self.sections))
        docs.append('')        
        docs.append("The [DEFAULT] section (note uppercase) is always read if present, and it is read as if its contents were copied to the beginning of all other sections. Settings on the command line override any settings found in configfiles.")
        docs.append('')        
        docs.append('SYNTAX:')        
        docs.append("  The syntax is similar to what you would find in Microsoft Windows .ini files, with [Sections] and option:value pairs. Specifically, it is a case sensitive version of python's ConfigParser. Example:")        
        docs.append('    [Section Name]')        
        docs.append('    option1: value %(option2)s ; comment')        
        docs.append('    option2= value # comment')
        docs.append('')
        docs.append('  Names:')
        ignore = ''
        if self.ignore:
            ignore = (' %(progname)s ignores the following names: ' % self.docvars + 
                      ', '.join(repr(name) for name in self.ignore) + 
                      '. Note that these may likely still be used by other programs that use the same configfile.')
        docs.append('    Section and option names are case sensitive, and for options, only the long variant is valid (and not -a style abbreviations).' + ignore)
        docs.append('')
        docs.append('  Formatting vs Nonformatting Options:')
        docs.append('    In the example, the value of option2 is used to format the value of option1, while option1 is not used to format the value of any other option in the section. option1 is therefore called a nonformatting option while option2 is called a formatting option. The names for all nonformatting options must be valid for the program, while the names of formatting options may or may not be valid. If they are, then their values will be used in the program settings. Otherwise they will only be used for formatting.')
        docs.append('')
        docs.append('  Values:')
        docs.append('    Type values exactly as you would on the command line, except in the case of flags where the values "1", "Yes", "True" and "On" (case insensitive) mean setting the flag to True, and where the values "0", "No", "False" and "Off" mean setting the flag to False. Use "" for passing an empty string.')
        docs.append('')
        self.docs['files']['CONFIGFILE'] = docs

    def parse_files(self, files=None, sections=None):
        """Parse configfiles. 
        files <list str>, <str> or None:
            What files to parse. None means use self.configfiles. New
            values override old ones. A string value will be interpreted
            as a list of one item.
        sections <list str>, <str> or None:
            Which sections to parse from the files. None means use
            self.sections. A string value will be interpreted as a list
            of one item. The [DEFAULT]
            section is always read, and it is read as if its contents were
            copied to the beginning of all other sections.
            
        """
        files = _list(files, self.configfiles)
        sections = _list(sections, self.sections)
        for file in files:
            parser = StrictConfigParser()
            parser.read(file)
            for section in sections:
                if not parser.has_section(section):
                    continue
                for unused in parser.unusedoptions(section):
                    if unused not in self.options and unused not in self.ignore: 
                        templ = "The option %r in section [%s] of file %s does not exist."
                        raise InvalidOption(unused, message=templ % (unused, section, file))
                for name in parser.options(section):          
                    if name in self.options:
                        if self.options[name].reserved():
                            templ = "The option %s in section [%s] of file %s is reserved for command line use."
                            raise ReservedOptionError(message=templ % (unused, section, file))
                        value = parser.get(section, name)
                        self.options[name].parsestr(value, name, '%r [%s]' % (file, section))

    def _parse_options(self, argv, location):
        """Parse the options part of an argument list.
        IN:
        lsArgs <list str>:
            List of arguments. Will be altered.
        location <str>:
            A user friendly string describing where this data came from.
            
        """
        observed = []
        while argv:
            if argv[0].startswith('--'):
                name = argv.pop(0)[2:]
                # '--' means end of options.
                if not name:
                    break
                if name not in self.options:
                    raise InvalidOption(name)
                option = self.options[name]
                if not option.recurring:
                    if option in observed:
                        raise OptionRecurrenceError(name)
                    observed.append(option)
                option.parse(argv, name, location)
            elif argv[0].startswith('-'):
                # A single - is not an abbreviation block, but the first positional arg.
                if argv[0] == '-':
                    break
                block = argv.pop(0)[1:]
                # Abbrevs for options that take values go last in the block.
                for abbreviation in block[:-1]:
                    if self.abbreviations[abbreviation].nargs != 0:
                        raise BadAbbreviationBlock(abbreviation, block, "options that require value arguments must be last in abbreviation blocks")
                # Parse individual options.
                for abbreviation in block:
                    option = self.abbreviations[abbreviation]
                    if not option.recurring:
                        if option in observed:
                            raise OptionRecurrenceError(option.name)
                        observed.append(option)
                    option.parse(argv, '-' + abbreviation, location)
            # only arguments that start with -- or - can be Options.
            else:
                break

    def _parse_positional_arguments(self, argv):
        """Parse the positional arguments part of an argument list.
        argv <list str>:
            List of arguments. Will be altered.
        """
        for posarg in self.positional_args:
            posarg.parse(argv)
        if argv:
            if None in [p.nargs for p in self.positional_args]:
                msg = '%s too many argument%s given'
                plural_s = len(argv) > 1 and 's' or ''
                raise BadNumberOfArguments(message=msg % (len(argv), plural_s))
            msg = 'This program accepts exactly %s positional arguments (%s given).'
            required = len([p.nargs for p in self.positional_args])
            raise BadNumberOfArguments(message=msg % (required, required + len(argv)))
            
    def parse_argv(self, argv=None, location='Command line.'):
        """Parse command line arguments.
        
        args <list str> or None:
            The argument list to parse. None means use a copy of sys.argv. argv[0] is
            ignored.
        location = '' <str>:
            A user friendly string describing where the parser got this
            data from. '' means use "Command line." if args == None, and
            "Builtin default." otherwise.
            
        """
        if argv is None:
            argv = list(sys.argv)
        argv.pop(0)
        self._parse_options(argv, location)
        self._parse_positional_arguments(argv)

    def optionhelp(self, indent=0, maxindent=25, width=79):
        """Return user friendly help on program options."""
        def makelabels(option):
            labels = '%*s--%s' % (indent, ' ', option.name)
            if option.abbreviation:
                labels += ', -' + option.abbreviation
            return labels + ': '
        docs = []
        helpindent = _autoindent([makelabels(o) for o in self.options.values()], indent, maxindent)
        for name in self.option_order:
            option = self.options[name]
            labels = makelabels(option)
            helpstring = "%s(%s). %s" % (option.formatname, option.strvalue, option.docs)
            wrapped = self._wrap_labelled(labels, helpstring, helpindent, width)
            docs.extend(wrapped)
        return '\n'.join(docs)

    def posarghelp(self, indent=0, maxindent=25, width=79):
        """Return user friendly help on positional arguments in the program."""
        docs = []
        makelabel = lambda posarg: ' ' * indent + posarg.displayname + ': '
        helpindent = _autoindent([makelabel(p) for p in self.positional_args], indent, maxindent)
        for posarg in self.positional_args:
            label = makelabel(posarg)
            text = posarg.formatname + '. ' + posarg.docs
            wrapped = self._wrap_labelled(label, text, helpindent, width)
            docs.extend(wrapped)
        return '\n'.join(docs)
        
    def format_usage(self, usage=None):
        """Return a formatted usage string. 
        
        If usage is None, use self.docs['usage'], and if that is also None, 
        generate one.
        """
        if usage is None:
            usage = self.docs['usage']
        if usage is not None:
            return usage[0] % self.docvars
        usage = self.docvars['command']
        if self.options:
            usage += ' <OPTIONS>'
        optional = 0
        for posarg in self.positional_args:
            usage += ' '
            if posarg.optional:
                usage += "[" 
                optional += 1
            usage += posarg.displayname
            if posarg.recurring:
                usage += ' [%s2 [...]]' % posarg.displayname
        usage += ']' * optional
        return usage

    def _wrap(self, text, indent=0, width=0):
        """Textwrap an indented paragraph.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        text = _list(text)
        if not width:
            width = self.width
        paragraph = text[0].lstrip()
        s = ' ' * (len(text[0]) - len(paragraph) + indent)
        wrapped = textwrap.wrap(paragraph.strip(), width, initial_indent=s, subsequent_indent=s)
        return '\n'.join(wrapped)

    def _wraptext(self, text, indent=0, width=0):
        """Shorthand for '\n'.join(self._wrap(par, indent, width) for par in text)."""
        return '\n'.join(self._wrap(par, indent, width) for par in text)

    def _wrap_labelled(self, label, helpstring, indent=0, width=0):
        if not width:
            width = self.width
        s = ' ' * indent
        wrapped = textwrap.wrap(helpstring, width, initial_indent=s, subsequent_indent=s)
        if len(label) > indent:
            return [label] + wrapped
        wrapped[0] = label + ' ' * (indent - len(label)) + wrapped[0].lstrip()
        return wrapped

    def _wrapusage(self, usage=None, width=0):
        """Textwrap usage instructions.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        if not width:
            width = self.width
        return textwrap.fill('USAGE: ' + self.format_usage(usage), width=width, subsequent_indent='    ...')

    def versionhelp(self, width=0):
        """Return self.docvars['version']. 
        
        width is ignored and is present only for symmetry with other help methods.
        """
        return self.docvars['version']
        
    def shorthelp(self, width=0):
        """Return brief help containing Title and usage instructions.
        ARGS:
        width = 0 <int>:
            Maximum allowed page width. 0 means use default from
            self.iMaxHelpWidth.

        """
        out = []
        out.append(self._wrap(self.docs['title'], width=width))
        if self.docs['description']:
            out.append(self._wrap(self.docs['description'], indent=2, width=width))
        out.append('')
        out.append(self._wrapusage(width=width))
        out.append('')
        return '\n'.join(out)

    def customhelp(self, help_sections, width=0):
        out = []
        def heading(name):
            out and not out[-1].isspace() and out.append('')
            name and out.append(name.upper() + ':')
        for section in help_sections:
            if section == 'title':
                out.append(self._wrap(self.docs[section], width=width))
            elif section == 'description':
                if self.docs[section]:
                    out.append(self._wrap(self.docs[section], width=width, indent=2))
            elif section == 'usage':
                heading(None)
                out.append(self._wrapusage(width=width))
            elif section == 'arguments':
                if self.positional_args:
                    heading(section)
                    out.append(self.posarghelp(indent=2, width=width))
            elif section == 'options':
                if self.options:
                    heading(section)
                    out.append(self.optionhelp(indent=2, width=width))
            elif section == 'general':
                if self.docs[section]:
                    heading(None)
                    out.append(self._wraptext(self.docs[section], width=width))
            elif section == 'files':
                if self.docs[section]:
                    heading(section)
                    for file, docs in self.docs[section].items():
                        out.append('  %s:' % file)
                        out.append(self._wraptext(docs, indent=4, width=width))
            else:
                if self.docs[section]:
                    heading(section)
                    out.append(self._wraptext(self.docs[section], indent=2, width=width))
        return '\n'.join(out)
    
    def help(self, width=0):
        """Return the standard formatted command line help for the prog.

        width is maximum allowed page width, use self.width if 0.
        """
        return self.customhelp(self.help_sections, width)
                
    def longhelp(self, width=0):
        """Return the standard formatted help text for the prog. 
        
        This should have approximately the amount of information as you'd 
        expect in a man page.

        width is maximum allowed page width, use self.width if 0.
        """
        return self.customhelp(self.longhelp_sections, width)
                
    def strsettings(self, indent=0, maxindent=25, width=0):
        """Return user friendly help on positional arguments.        

        indent is the number of spaces preceeding the text on each line. 
        
        The indent of the documentation is dependent on the length of the 
        longest label that is shorter than maxindent. A label longer than 
        maxindent will be printed on its own line.
        
        width is maximum allowed page width, use self.width if 0.
        """
        out = []
        makelabel = lambda name: ' ' * indent + name + ': '
        settingsindent = _autoindent([makelabel(s) for s in self.options], indent, maxindent)
        for name in self.option_order:
            option = self.options[name]
            label = makelabel(name)
            settingshelp = "%s(%s): %s" % (option.formatname, option.strvalue, option.location)
            wrapped = self._wrap_labelled(label, settingshelp, settingsindent, width)
            out.extend(wrapped)
        return '\n'.join(out)

    def settingshelp(self, width=0):
        """Return a summary of program options, their values and origins.
        
        width is maximum allowed page width, use self.width if 0.
        """
        out = []
        out.append(self._wrap(self.docs['title'], width=width))
        if self.docs['description']:
            out.append(self._wrap(self.docs['description'], indent=2, width=width))
        out.append('')
        out.append('SETTINGS:')
        out.append(self.strsettings(indent=2, width=width))
        out.append('')
        return '\n'.join(out)

    def launch(self,
               argv=None,
               showusageonnoargs=False,
               width=0,
               helphint="Use with --help or --HELP for more information.\n",
               debug_parser=False):
        """Do the usual stuff to initiallize the program.
        
        Read config files and parse arguments, and if the user has used any 
        of the help/version/settings options, display help and exit.
        
        If debug_parser is false, don't catch ParseErrors and exit with user
        friendly help. Crash with traceback instead.
        
        configfiles is a list of config files. None means use self.configfiles.
        
        sections is a list of configfile section names to read. None means use
        self.sections.
        
        argv is a list of arguments to parse. Will be modified. None means use
        copy of sys.argv. argv[0] is ignored.
        
        If showusageonnoargs is true, show usage and exit if the user didn't 
        give any args. Should be False if there are no required PositionalArgs.
        
        width is the maximum allowed page width. 0 means use self.width.
        
        helphint is a string that hints on how to get more help which is 
        displayed at the end of usage help messages. 
        """
        if showusageonnoargs and len(argv) == 1:
            print self.shorthelp(width=width)
            if helphint:
                print self._wrap(helphint, indent=2, width=width)
            sys.exit(0)
        parsing_error = None
        try:
            self.parse_files()
            self.parse_argv(argv)
        except ParseError, parsing_error:
            if debug_parser:
                raise
        for optiontype in ['help', 'longhelp', 'settings', 'version']:
            name = self.basic_option_names.get(optiontype)
            if name and self[name]:
                methodname = optiontype.rstrip('help') + 'help'
                print getattr(self, methodname)(width)
                sys.exit()
        if parsing_error:
            self.graceful_exit(parsing_error, width)
            
    def graceful_exit(self, error_message, width=0):
        print >> sys.stderr, self.shorthelp(width)
        sys.exit("ERROR: %s" % error_message)
        