================================================================
TUI Textual User Interface - A sane command line user interface.
================================================================

Copyright (c) 2011 Joel Hedlund.

Contact: Joel Hedlund <yohell@ifm.liu.se>

TUI is straightforward to use, both for developers and users. It can parse 
options from multiple config files and command line, and can produce 
constructive error messages given bad input. It can also help keep the 
source code clean by moving help text to a separate documentation file.

If you have problems with this package, please contact the author.


Requirements
============
Python 2, version 2.3 or later.


Getting started
===============

Typically, you will need to import the tui class and some format classes 
from the tui.formats module. The tui.docparser module has documentation on how 
to write tui-compatible documentation files, but you won't likely need 
anything else from there. You probably won't ever have to use anything from 
the TextBlockParser module.


Howto
=====

Let's pretend we're making a moose counter. First, we create the script 
file 'moosecounter.py', a docs file 'moosecounter.docs' and a config file
'moosecounter.cfg' in the same dir. Leave the latter two empty and start 
editing the scriptfile.

Instantiate a textual user interface object and give it the proper name 
right from the start and use the magical initprog() feature, like so::

	#!/usr/bin/env python

	from tui import tui, formats
	
	__version__ = "0.1.0"
	if __name__ == '__main__':
	    o = tui(progname='MooseCounter', main=__file__)
	    o.initprog()

Save and execute your moose counter with no arguments, and voila: usage 
instructions! Execute it with the --HELP flag, and voila: verbose program 
information, including syntax help for the config file! The config files 
are meant to be used by your users to configure your program with, by the 
way.

A quick note on using main=__file__:

Doing this is handy because it enables tui to find any .cfg or .docs files
you want to distribute with your program, however if you do not supply a 
version str, tui will attempt to import the module and read the __version__
attribute (if present), so if you are planning to use this feature, make 
sure your script can be imported without side effects. But as this is 
standard python coding practice, you should probably be doing this already!

Now you can go on to adding more options to your moose counter. Just stick 
some o.makeoption() and o.makeposarg() clauses between the last two lines 
in the example above. You will probably also need to import some formats 
for your options from the formats module in this package. For example you 
can do something like this::

	#!/usr/bin/env python

	from tui import tui, formats

	__version__ = "0.1.0"
	if __name__ == '__main__':
	    o = tui(main=__file__, progname='MooseCounter')
	    o.makeoption('horn-points', formats.BoundedInt(lowerbound=1), '13')
	    o.makeoption('weight', formats.Float, '450.0', 'w')
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
