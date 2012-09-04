================================================================
TUI Textual User Interface - A sane command line user interface.
================================================================

Copyright (c) 2012 Joel Hedlund.

Contact: Joel Hedlund <yohell@ifm.liu.se>

TUI is straightforward to use, both for developers and users. It can parse 
options from multiple config files and command line, and can produce 
constructive error messages given bad input. It can also help keep the 
source code clean by moving help text to a separate documentation file.

If you have problems with this package, please contact the author.


Requirements
============
Python 2, version 2.3 or later.


Documentation
=============
As much as possible of the tui documentation has been pushed to __doc__ strings
for individual modules, functions, classes and methods. To get going, please see
the example below, or this quick rundown of suggested entry points:

To get started you probably want to import Option, Posarg, get_metainfo and tui
from the tui package, and possibly some formats from the tui.formats module.

The tui class is the main workhorse that holds all program info, knows how to
parse docs, config and command line parameters, and how to present all this
info to the user. Instantiate with metainfo (see get_metainfo() for pulling 
this out of your program docstring) and a list of options and positional 
arguments, and tui will find and read program documentation from docsfiles, 
find and parse settings from various configfiles and the command line, and will
exit with helpful error messages on parameter format errors (like when the user
types 'monkey' when the program expects a number, or gives a read-only file to 
write results to, and so on), and finally it will react to some useful options
(--help, --HELP, --version and --settings, see the example just above). You can
of course customize all this, or sidestep the magic alltogether. Read method 
and class docs to see how it's done.

The format classes in the tui.formats module know how to take user supplied
strings and transform them into validated values usable in your program, for
examples: Int, ReadableFile, WritableDir, Choice, Flag, RegEx, and so on.
You can also write your own formats and add to your tui instance. Use 
existing formats as examples for that.


Examples
========
In a nutshell, you instantiate tui with some program metainformation and a list
of options and positional arguments, and tui will do its thing (read 
documentation files, parse config files and command line parameters, react to 
common options such as '--help' by printing user frendly help and exiting), and
then your whole parsed and validated program config is available to you through
simple dict like interface. Here is myprog (no extension), an example program 
that uses tui. (You could of course call it myprog.py and have distutils remove
the .py extension on install, which is what I commonly do, but nevermind, do as
you like, tui will work anyhow.): 

    #!/usr/bin/env python
    '''MyProgram 
    A one line description of my program goes here.
    
    The get_metainfo() function can be used to pull useful information out of your 
    program docstring so you don't have to retype it, such as program name and 
    description lines above and the keyword lines just below. All other text (such
    as this paragraph) is ignored, so you can feel free to type out as much as you 
    like. See the tui.get_metainfo() docstring for more info.
    
    Website:   http://www.example.com
    Download:  http://www.example.com/download
    Git:       http://www.example.com/git
    Author:    Joel Hedlund <yohell@ifm.liu.se>
    Contact:   Please contact the author.
    Copyright: Copyright blurb.
    License:   Name of the license.
    '''
    __version__ = "0.1.0"
    import sys
    import mypackage
    def main(argv=None):
        from tui import (BadArgument, Option, Posarg, get_metainfo, tui)
        from tui.formats import (ReadableFile, WritableFile)
        ui = tui([Option('quiet', 'Flag', 'q'),
                  Option('noise', 'Int', 'v', default=10),
                  Option('job-tag', 'String', recurring=True),
                  Posarg('in-file', ReadableFile(special={'-': None})),
                  Posarg('out-file', WritableFile, optional=True)],
                 __version__, # Program version right from the source.
                 mypackage, # Adds package dir to .conf and .docs search path.
                 argv, # What args to parse, None means copy of sys.argv. 
                 ignore=['squeegees'],
                 **get_metainfo(__file__))
        # Any additional custom parameter checking:
        if ui['noise'] > 9000:
            ui.graceful_exit(BadArgument('noise', ui['noise'], 'too chatty'))
        if ui['in-file'] and open(ui['in-file']).read() == 'bad content':
            ui.graceful_exit('custom error message')
        # Tweak stuff if needed:
        if ui['noise'] < 8000:
            ui['noise'] = 7
        # Go time!
        try:
            return mypackage.do_stuff(**ui.dict())
        except KeyboardInterrupt:
            ui.graceful_exit('interrupted by user')

    if __name__ == '__main__':
        sys.exit(main() or 0)

And when you run that without arguments you get:    

    $ python myprog
    MyProgram v0.1.0 by Joel Hedlund <yohell@ifm.liu.se>.
      A one line description of my program goes here.
    
    USAGE: myprog [--help] <OPTIONS> IN_FILE [OUT_FILE]
    
    ERROR: IN_FILE requires 1 arguments and was given 0.

ui['in-file'] wasn't optional, remember? You can also use --help to get help:

    $ python myprog --help
    MyProgram v0.1.0 by Joel Hedlund <yohell@ifm.liu.se>.
      A one line description of my program goes here.
    
    USAGE: myprog.py [--help] <OPTIONS> IN_FILE [OUT_FILE]
    
    ARGUMENTS:
      IN_FILE:  ReadableFile. A readable file. These special values are
                accepted: '-'.
      OUT_FILE: WritableFile. A writable file, will be created if possible.
    
    OPTIONS:
      --quiet, -q:   Flag(False). Takes no argument on the command line. Use 1,
                     yes, true, on, 0, no, false or off in configfiles (case
                     insensitive).
      --noise, -v:   Int(10). An integer number.
      --job-tag:     String(). A string of characters. Can be used repeatedly.
      --help, -h:    Flag(True). Print help and exit.
      --HELP:        Flag(False). Print verbose help and exit.
      --settings:    Flag(False). Print settings summary and exit.
      --version, -V: Flag(False). Print version string and exit.

The more verbose --HELP option also prints contact/website/download/git/etc... 
information, and explains the configfile syntax (more on that below).

At this stage some of the help text is a bit generic, but this can be remedied
using a .docs file, which serves to factor out as much human readable help text
as possible from the source, so the next step is to put myprogs.docs where tui 
can find it. In this case we gave mypackage as the install_dir, so put it 
in the mypackage package directory.

    PARAMETER: quiet
    Suppress all normal output through speakers.
    
    PARAMETER: noise
    Level of chatter, less is more.
    
    PARAMETER: in-file
    What data file to read, in some format. 
    
    PARAMETER: squeegees
    This parameter is not used by myprog but a sibling program in the same 
    suite.
    
    GENERAL:
    General info on how to use %(progname)s.
    
    ADDITIONAL:
    You can use docvars in docsfiles, e.g: %(progname)s v%(version)s by 
    %(author)s is started using %(command)s. # This comment will be removed.
    Since these lines have the same indent, they will be concatenated into a 
    single paragraph, and later linewrapped to the user's current terminal 
    width.
    # This line is ignored.
    This is a literal hash char \# in the last sentence in the first paragraph. 
    
    This is a new paragraph, with a bullet list:
     * End paragraphs with backslash \
     * to indicate that next line with same indent \
     * is a new paragraph with same indent.
    
    FILE: /etc/%(command)s/%(command)s-hosts.conf
    Documentation on program specific file.

While we're at it let's make a config file, part to show off the syntax, but 
also so I can showcase the --settings feature in just a little while. There's
a number of places you can put config files so tui will find them, but for now,
just put this in a file called myprog.conf in the install_dir as well.

    # This is a comment. The DEFAULT section (always uppercase) is always read.
    [DEFAULT]
    # There is no 'server' option but you set other vars this way, see below.
    server = liu.se
    # squeegees is ignored in myprog, probably used by a sibling prog.
    squeegees = moo
    
    [myprog]
    # This sets job-tag to liu.se/index.html
    job-tag = %(server)s/index.html
    # Use on,yes,true,1 or off,no,false,0 to set values for flags.  
    quiet = yes 
    
    [myotherprog]
    # This section is ignored by myprog, which only reads its own sections.
 
Now with our new .docs, the --help becomes more specific:

    $ python myprog --help
    MyProgram v0.1.0 by Joel Hedlund <yohell@ifm.liu.se>.
      A one line description of my program goes here.
    
    USAGE: test.py [--help] <OPTIONS> IN_FILE [OUT_FILE]
    
    ARGUMENTS:
      IN_FILE:  ReadableFile. What data file to read, in some format.
      OUT_FILE: WritableFile. A writable file, will be created if possible.
    
    OPTIONS:
      --quiet, -q:   Flag(False). Suppress all normal output through speakers.
      --noise, -v:   Int(10). Level of chatter, less is more.
      --job-tag:     String(). A string of characters. Can be used repeatedly.
      --help, -h:    Flag(True). Print help and exit.
      --HELP:        Flag(False). Print verbose help and exit.
      --settings:    Flag(False). Print settings summary and exit.
      --version, -V: Flag(False). Print version string and exit.
    
    General info on how to use MyProgram.

And now, --settings will show us not only what the current values are for all
program options, but also where they came from so you can easily find and 
correct errors.

    $ python myprog --settings
    MyProgram v0.1.0 by Joel Hedlund <yohell@ifm.liu.se>.
      A one line description of my program goes here.
    
    SETTINGS:
      quiet:    Flag(True): /home/joel/test/myprog.conf [myprog]
      noise:    Int(10): Builtin default.
      job-tag:  String(liu.se/index.html): /home/joel/test/myprog.conf [test]
      help:     Flag(False): Builtin default.
      HELP:     Flag(False): Builtin default.
      settings: Flag(True): Command line.
      version:  Flag(False): Builtin default.
 
Now for that verbose --HELP that spills all the beans we've stuffed in so far.
Note especially that it tells you where tui looks for .conf files by default:

    $ python myprog --HELP
    MyProgram v0.1.0 by Joel Hedlund <yohell@ifm.liu.se>.
      A one line description of my program goes here.
    
    CONTACT:
      Please contact the author.
    
    WEBSITE:
      http://www.example.com
    
    DOWNLOAD:
      http://www.example.com/download
    
    GIT:
      git@example.com:myprog
    
    USAGE: myprog [--help] <OPTIONS> IN_FILE [OUT_FILE]
    
    ARGUMENTS:
      IN_FILE:  ReadableFile. A readable file. These special values are
                accepted: '-'.
      OUT_FILE: WritableFile. A writable file, will be created if possible.
    
    OPTIONS:
      --quiet, -q:   Flag(False). Takes no argument on the command line. Use 1,
                     yes, true, on, 0, no, false or off in configfiles (case
                     insensitive).
      --noise, -v:   Int(10). An integer number.
      --job-tag:     String(). A string of characters. Can be used repeatedly.
      --help, -h:    Flag(False). Print help and exit.
      --HELP:        Flag(True). Print verbose help and exit.
      --settings:    Flag(False). Print settings summary and exit.
      --version, -V: Flag(False). Print version string and exit.
    
    FILES:
      CONFIGFILE:
        A MyProgram configuration file. MyProgram will look configfiles in the
        following loctions, and in the following order:
          1. /home/joel/test/myprog.conf
          2. /etc/myprog/myprog.conf
          3. /home/joel/.myprog/myprog.conf
    
        The following sections will be parsed, and in the following order:
          1. [myprog]
    
        The [DEFAULT] section (note uppercase) is always read if present, and it
        is read as if its contents were copied to the beginning of all other
        sections. Settings on the command line override any settings found in
        configfiles.
    
        SYNTAX:
          The syntax is similar to what you would find in Microsoft Windows .ini
          files, with [Sections] and option:value pairs. Specifically, it is a
          case sensitive version of python's ConfigParser. Example:
            [Section Name]
            option1: value %(option2)s ; comment
            option2= value # comment
    
          Names:
            Section and option names are case sensitive, and for options, only
            the long variant is valid (and not -a style abbreviations).
            MyProgram ignores the following names: 'squeegees'. Note that these
            may likely still be used by other programs that use the same
            configfile.
    
          Formatting vs Nonformatting Options:
            In the example, the value of option2 is used to format the value of
            option1, while option1 is not used to format the value of any other
            option in the section. option1 is therefore called a nonformatting
            option while option2 is called a formatting option. The names for
            all nonformatting options must be valid for the program, while the
            names of formatting options may or may not be valid. If they are,
            then their values will be used in the program settings. Otherwise
            they will only be used for formatting.
    
          Values:
            Type values exactly as you would on the command line, except in the
            case of flags where the values "1", "Yes", "True" and "On" (case
            insensitive) mean setting the flag to True, and where the values
            "0", "No", "False" and "Off" mean setting the flag to False. Use ""
            for passing an empty string.
    
And that's enough examples for today. Go play! Try stuff out! Read the 
docstrings! Good luck! 


Further reading
===============

See the separate help docs on each individual module, class and method.


Copyright
=========
 
The MIT License

Copyright (c) 2011 Joel Hedlund.

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
