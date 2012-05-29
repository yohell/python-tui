"""DocParser - Read documentation for tui based programs.

By Joel Hedlund <yohell@ifm.liu.se>

If you have problems with this module, please contact the author.

SYNTAX OF DOCUMENTATION FILES:

 * Anything following a '#' character on a line is disregarded as a comment.
   Use "\#" to denote an actual '#' character

 * The following block tags are supported (always in capital letters):

    - Unlabelled block tags:
        ADDITIONAL:  [multiple paragraphs]  .additional()
        COMMAND:     [single paragraph]     .command()
        CONTACT:     [multiple paragraphs]  .contact()
        COPYRIGHT:   [multiple paragraphs]  .copyright()
        DESCRIPTION: [single paragraph]     .description()
        GENERAL:     [multiple paragraphs]  .general()
        NOTE:        [multiple paragraphs]  .notes()
        PROGNAME:    [single paragraph]     .progname()
        PROGRAMMER:  [single paragraph]     .programmer()
        TITLE:       [single paragraph]     .title()
        USAGE:       [single paragraph]     .usage()
        VERSION:     [single paragraph]     .version()
        
    - Labelled block tags:
        ARGUMENT:    [single paragraph]     .arguments()
        OPTION:      [single paragraph]     .options()
        FILE:        [multiple paragraphs]  .files()

 * All blocks start with a tag line that must contain the block tag and 
   nothing else, with the possible exception of comments and whitespace.
   The Labelled block tag lines are exceptions to this rule, as they are
   required to have a label after the block tag, like so:

       OPTION: help

 * In blocks marked with [single paragraph] all text will be concatenated
   into a single string, with newlines and blank lines converted to a single
   space. In blocks marked with [multiple paragraphs] all consecutive lines of
   text with the same indentation will be concatenated into single paragraph
   strings that start with a number of spaces corresponding to the indentation
   of that paragraph. Consecutive lines with different indent will be stored
   in different paragraph strings. If you want two consecutive lines with the
   same indent to go into different paragraph strings (as for example in the
   case of bulleted lists) you can end the first line with '\\' to override
   the concatenation. The only way of avoing preservation of a blank line in
   multiple paragraph blocks is to start the line with a '#' character.

 * In tui, the blocks PROGNAME, VERSION, PROGRAMMER and COMMAND are treated
   as documentation variables (DocVars). All other text blocks (and also
   FILE: labels) can use these through python string formatting, like so:

       "The benefit of using %(progname)s for this kind of problem is..."

   This helps in avoiding lagging documentation somewhat.    

COPYRIGHT:
The MIT License

Copyright (c) <year> <copyright holders>

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

__version__ = "2.0.0"
__copyright__ = "Copyright (c) 2011 Joel Hedlund."
__license__ = "MIT"


from textblockparser import (IndentedParagraphs,
                             SingleParagraph,
                             TextBlockParser)

class DocParser(TextBlockParser):
    """\
    TextBlockParser specially tuned to read .doc files used by tui. Also
    with some convenience functions to get at the text.

    """

    def __init__(self, tabsize = 4):
        """\
        Instatiate a DocParser object.
        IN:
        tabsize = 4 <int>:
            Replace tabs with this many spaces. Set < 0 to disable.

        """
        TextBlockParser.__init__(self, untaggedtextclass = None, tabsize = tabsize)
        self.addblock('progname', SingleParagraph)
        self.addblock('version', SingleParagraph)
        self.addblock('programmer', SingleParagraph)
        self.addblock('title', SingleParagraph)
        self.addblock('description', SingleParagraph)
        self.addblock('command', SingleParagraph)
        self.addblock('usage', SingleParagraph)
        self.addblock('contact', IndentedParagraphs)
        self.addblock('copyright', IndentedParagraphs)
        self.addblock('options', SingleParagraph, True, 'OPTION')
        self.addblock('arguments', SingleParagraph, True, 'ARGUMENT')
        self.addblock('notes', IndentedParagraphs, tag = 'NOTE')
        self.addblock('general', IndentedParagraphs)
        self.addblock('additional', IndentedParagraphs)
        self.addblock('files', IndentedParagraphs, True, 'FILE')

    def progname(self):
        """\
        Return the progname as a string.

        """
        ls = self.dsoUnlabelledBlocks['progname'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def version(self):
        """\
        Return the version as a string.

        """
        ls = self.dsoUnlabelledBlocks['version'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def programmer(self):
        """\
        Return the programmer as a string.

        """
        ls = self.dsoUnlabelledBlocks['programmer'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def title(self):
        """\
        Return the title as a string.

        """
        ls = self.dsoUnlabelledBlocks['title'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def description(self):
        """\
        Return the description as a string.

        """
        ls = self.dsoUnlabelledBlocks['description'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def command(self):
        """\
        Return the command as a string.

        """
        ls = self.dsoUnlabelledBlocks['command'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def usage(self):
        """\
        Return the usage as a string.

        """
        ls = self.dsoUnlabelledBlocks['usage'].text()
        if ls:
            return ls[0]
        else:
            return ''

    def contact(self):
        """\
        Return the contact information as a string.

        """
        return self.dsoUnlabelledBlocks['contact'].text()
        
    def copyright(self):
        """\
        Return the copyright information as a string.

        """
        return self.dsoUnlabelledBlocks['copyright'].text()
        
    def notes(self):
        """\
        Return the notes as a list of indented paragraphs.

        """
        return self.dsoUnlabelledBlocks['notes'].text()

    def general(self):
        """\
        Return the general documentation as a string.

        """
        return self.dsoUnlabelledBlocks['general'].text()
        
    def additional(self):
        """\
        Return the additional documentation as a string.

        """
        return self.dsoUnlabelledBlocks['additional'].text()
        
    def options(self):
        """\
        Return a dict where the documented options are keys <str> and the
        docs are values <str>.

        """
        d = {}
        for s, o in self.dsoLabelledBlocks['options'].iteritems():
            d[s] = o.text()[0]
        return d

    def arguments(self):
        """\
        Return a dict where the documented positional arguments are keys
        <str> and the docs are values <str>.

        """
        d = {}
        for s, o in self.dsoLabelledBlocks['arguments'].iteritems():
            d[s] = o.text()[0]
        return d

    def files(self):
        """\
        Return a dict where the documented options are keys <str> and the
        indented paragraph docs are values <list str>.

        """
        d = {}
        for s, o in self.dsoLabelledBlocks['files'].iteritems():
            d[s] = o.text()
        return d



def parse(file, tabsize = 4):
    """\
    Instantiate a DocParser object, use it to parse the given file, and
    return it.

    """
    o = DocParser(tabsize)
    o.parse(file)
    return o

##o = DocParser()
##o.parse('eraseme2.doc')
##for k, v in o.unlabelledblocks().iteritems():
##    print k
##    print v.text()
##print
##print
##
##for name, container in o.labelledblocks().iteritems():
##    print name
##    print '=' * len(name)
##    for label, block in container.iteritems():
##        print label
##        print block.text()
