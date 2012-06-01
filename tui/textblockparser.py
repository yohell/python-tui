"""TUI Textual User Interface - A sane command line user interface.

Author: Joel Hedlund <yohell@ifm.liu.se>

This module contains format classes for use in textual user interfaces.

If you have problems with this package, please contact the author.

"""
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2011 Joel Hedlund."
__license__ = "MIT"

import re

class ParseError(Exception):
    def __init__(self, file, line, details, message=None):
        if message is None:
            message = "[%r:%s] %s" % (file, line, details)
        elif file or line or details:
            raise ValueError('use either default or custom error message, not both')
        self.message = "[%r:%s] %s" % (file, line, details)

    def __str__ (self):
        return self.message    

class TextBlock(object):
    def __init__(self, tabsize=4):
        """
        tabsize > 0 replaces tab characters with that many spaces. Set <= 0 to 
        disable.
        """
        self.lines = []
        self.tabsize = tabsize

    def __len__(self):
        return len(self.lines)
    
    def startblock(self):
        pass
    
    def addline(self, line):
        """Add a line (no trailing newlines) to the text block."""
        self.lines.append(line)

    def text(self):
        """Return the text in the block as a list of lines."""
        return self.lines

class SingleParagraph(TextBlock):
    def addline(self, line):
        line = line.strip()
        if not line:
            return
        self.lines.append(line)

    def text(self):
        """Return the paragraph as a string."""
        return [' '.join(self.lines)]

class IndentedParagraphs(TextBlock):
    def startblock(self):
        self._previous_indent = -1
        self._keep_indent = True
    
    def addline(self, line):
        if self.tabsize:
            line = line.replace('\t', ' ' * self.tabsize)
        indent = len(line) - len(line.lstrip())
        rstripped = line.rstrip()
        if rstripped.endswith('\\'):
            rstripped = rstripped[:-1].rstrip()
            keep_next_indent = True
        else:
            keep_next_indent = False
        if not rstripped:
            self.lines.append(rstripped)
            self._previous_indent = -1
        elif self._keep_indent or indent != self._previous_indent:
            self.lines.append(rstripped)
            self._previous_indent = indent
        else:
            self.lines[-1] += ' ' + rstripped.strip()
        self._keep_indent = keep_next_indent
        
    def text(self):
        """Return the indented paragraphs as a list of strings."""
        return self.lines

class Decommenter(object):
    """Base class for Decommenters for TextBlockParsers."""
    
    def decomment(self, line):
        """Remove the comment parts from a line of text.

        Return None to indicate that the line is completely commented out and
        that it should not be fed to TextBlock storage.
        """

class UnescapedHashDecommenter(Decommenter):
    """Shell style unescaped hash line comments. 
    
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
    """

    def decomment(self, line):
        if line and line[0] == '#':
            return None
        decomment = r'(\\*)\1(#.*|\\(#))'
        # repl is a workaround for the fact that python <3.3 re gives None 
        # rather than '' for nonmatching groups.
        repl = lambda m: m.group(1) + (m.group(3) or '')
        return re.sub(decomment, repl, line)
    
class TextBlockParser(object):
    def __init__(self,
                 untagged=IndentedParagraphs,
                 decommenter=UnescapedHashDecommenter,
                 tabsize=4,
                 blocks=None,
                 labelled_classes=None,
                 names=None):
        """
        untagged determines what to do with text before the first tagged text 
        block and should be a TextBlock subclass, or None to raise ParseError.
        
        decommenter determines how to strip comments from the text. Set to None
        to not decomment.
        
        tabsize > 0 replaces tab characters with that many spaces. Set <= 0 to 
        disable.
        """
        if isinstance(untagged, type(TextBlock)):
            untagged = untagged()
        self.untagged = untagged 
        if isinstance(decommenter, type(Decommenter)):
            decommenter = decommenter()
        self.decommenter = decommenter
        self.tabsize = tabsize
        if blocks is None:
            blocks = {}
        self.blocks = blocks
        if labelled_classes is None:
            labelled_classes = dict()
        self.labelled_classes = labelled_classes
        if names is None:
            names = dict((name.upper, name) for name in blocks)
        self.names = names

    def __getitem__(self, name):
        if name in self.labelled_classes:
            return dict((label, labelled_block.text()) for label, labelled_block in self.blocks[name].items())
        return self.blocks[name].text()

    def addblock(self, name, textblockclass, labelled=False, tag=None):
        if name in self.blocks:
            raise ValueError('name already in use') 
        if not tag:
            tag = name.upper()
        if tag in self.names:
            raise ValueError('tag already in use') 
        self.names[tag] = name
        if labelled:
            self.blocks[name] = dict()
            self.labelled_classes[name] = textblockclass
        else:
            self.blocks[name] = textblockclass()

    def parse(self, file):
        """Parse text blocks from a file."""
        if isinstance(file, basestring):
            file = open(file)
        line_number = 0
        label = None
        block = self.untagged
        for line in file:
            line_number += 1
            line = line.rstrip('\n')
            if self.tabsize > 0:
                line = line.replace('\t', ' ' * self.tabsize)
            if self.decommenter:
                line = self.decommenter.decomment(line)
                if line is None:
                    continue
            tag = line.split(':', 1)[0].strip()
            # Still in the same block?
            if tag not in self.names:
                if block is None and not line.isspace():
                    raise ParseError(file.name, line, "garbage before first block: %r" % line)
                block.addline(line)
                continue
            # Open a new block.
            name = self.names[tag]
            label = line.split(':',1)[1].strip()
            if name in self.labelled_classes:
                if not label:
                    raise ParseError(file.name, line, "missing label for %r block" % name)
                block = self.blocks[name].setdefault(label, self.labelled_classes[name]())
            else:
                if label:
                    msg = "label %r present for unlabelled block %r" % (label, name)
                    raise ParseError(file.name, line_number, msg)
                block = self.blocks[name]
            block.startblock()
            
    def text(self):
        return dict((name, self[name]) for name in self.blocks)
    