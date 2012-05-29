"""TUI Textual User Interface - A sane command line user interface.

Author: Joel Hedlund <yohell@ifm.liu.se>

This module contains format classes for use in textual user interfaces.

If you have problems with this package, please contact the author.

"""
__version__ = "1.0.0"
__copyright__ = "Copyright (c) 2011 Joel Hedlund."
__license__ = "MIT"

import re

class TextBlockParserError(Exception):
    """
    Base class for exceptions raised in BlockReader. 
    """
    def __init__ (self, msg):
        self.sMessage = msg

    def __str__ (self):
        return self.sMessage    

class ParseError(TextBlockParserError):
    """\
    Raised on errors occurring while parsing text block files.

    """
    def __init__(self, file, line, details):
        self.sMessage = "[%s:%s] %s" % (repr(file), line, details)
    

class TextBlock:

    def __init__(self, tabsize = 4):
        """\
        Base class for TextBlock objects. Do not instantiate directly.
        Use a proper subclass instead.

        """
        self.lsLines = []
        self.iTabSize = tabsize
        raise NotImplementedError("Do not instantiate directly. Use a proper subclass instead.")


    def __len__(self):
        return len(self.lsLines)

    
    def _expandtabs(self, line):
        if self.iTabSize >= 0:
            return line.replace('\t', ' '*self.iTabSize)        

    def addline(self, line):
        """\
        Add a line (no trailing newlines) to the text block.

        """
        line = self._expandtabs(line)
        self.lsLines.append(line)

    def text(self):
        """\
        Return the text in the block as a list of lines.

        """
        return self.lsLines

    def tabsize(self):
        return self.iTabSize

    def reset(self):
        self.__init__(self.iTabSize)

        

class RawText(TextBlock):
    def __init__(self, tabsize = 4):
        """\
        Instantiate a RawText object.
        IN:
        tabsize <int>:
            Replace tabs with how many spaces? Set < 0 to disable.

        """
        self.lsLines = []
        self.iTabSize = tabsize


class SingleParagraph(TextBlock):

    def __init__(self, tabsize = 4):
        """\
        Instantiate a SingleParagraph object.
        IN:
        tabsize <int>:
            Replace tabs with how many spaces? Set < 0 to disable.

        """
        self.lsLines = []
        self.iTabSize = tabsize

    def addline(self, line):
        if not line.strip():
            return
        line = self._expandtabs(line)
        if self.lsLines:
            self.lsLines[0] += ' ' + line.strip()
        else:
            self.lsLines.append(line.strip())

    def text(self):
        """\
        Return the paragraph as a list of a single string.

        """
        return self.lsLines

    

class IndentedParagraphs(TextBlock):

    def __init__(self, tabsize = 4):
        """\
        Instantiate an IndentedParagraphs object.
        IN:
        tabsize <int>:
            Replace tabs with how many spaces? Set < 0 to disable.

        """
        self.lsLines = []
        self.iTabSize = tabsize
        self.iPreviousIndentLevel = -1
        self.bKeepIndent = True
        
    def addline(self, line):
        """\
        Add a line of text to the block.
        IN:
        line <str>:
            The line that should be added.

        """
        line = self._expandtabs(line)
        iIndentLevel = len(line) - len(line.lstrip())
        sRStrippedLine = line.rstrip()

        if sRStrippedLine.endswith('\\'):
            sRStrippedLine = sRStrippedLine[:-1].rstrip()
            bForceKeepNextIndent = True
        else:
            bForceKeepNextIndent = False

        if not sRStrippedLine:
            self.lsLines.append(sRStrippedLine)
            self.iPreviousIndentLevel = -1
        elif self.bKeepIndent or iIndentLevel != self.iPreviousIndentLevel:
            self.lsLines.append(sRStrippedLine)
            self.iPreviousIndentLevel = iIndentLevel
        else:
            self.lsLines[-1] += ' ' + sRStrippedLine.strip()

        self.bKeepIndent = bForceKeepNextIndent


        
    def text(self):
        """\
        Return the indented paragraphs as a list of strings.

        """
        return self.lsLines



class UnlabelledTextBlockContainer:
    def __init__(self, textblockclass, tabsize = 4):
        """\
        Instantiate a LabelledTextBlockContainer object.
        IN:
        tag = '' <str>:
            The block start tag. 
        textblockclass <class TextBlock>:
            What type of text blocks to contain.
        tabsize = 4 <int>:
            Replace tabs with how many spaces? Set < 0 to disable.

        """
        self.oTextBlock = textblockclass(tabsize)

    def __len__(self):
        return len(self.oTextBlock)

    def reset(self):
        self.oTextBlock.reset()

    def text(self):
        return self.oTextBlock.text()

    def addline(self, line):
        #print repr(line)
        self.oTextBlock.addline(line)
        
            

class LabelledTextBlockContainer:
    def __init__(self, textblockclass, tabsize = 4):
        """\
        Instantiate a LabelledTextBlockContainer object.
        IN:
        textblockclass <class TextBlock>:
            What type of text blocks to contain.
        tabsize = 4 <int>:
            Replace tabs with how many spaces? Set < 0 to disable.

        """
        self.dsoTextBlocks = {}
        self.cTextBlockClass = textblockclass
        self.iTabSize = tabsize


    def __getitem__(self, label):
        return self.dsoTextBlocks[label]


    def __iter__(self):
        return self.dsoTextBlocks.__iter__()

    def addlabel(self, label):
        self.dsoTextBlocks[label] = self.cTextBlockClass(self.iTabSize)

    def iteritems(self):
        return self.dsoTextBlocks.iteritems()



class Decommenter:
    """\
    Base class for Decommenters for TextBlockParsers.

    """
    def __init__(self):
        """\
        Do not instantiate directly. Use a subclass instead.

        """
        raise NotImplementedError("Do not instantiate directly. Use a subclass instead.")


    def decomment(self, line):
        """\
        Remove the comment parts from a line of text.
        IN:
        line <str>:
            The line to decomment.
        OUT:
            A decommented string. Return None to indicate that the line
            is completely commented out and that it should not be fed to
            TextBlock storage.

        """

class UnescapedHashDecommenter(Decommenter):
    """\
    Dumb pseudo shell style decommenter that strips everything on a line
    following non-escaped hash characters.

    """
    def __init__(self):
        self.rComment = re.compile(r'([^\\]|^)#')

    def decomment(self, line):
        if not line:
            return line
        ls = self.rComment.split(line, 1)
        if len(ls) == 1:
            return line.replace('\#', '#')
        sDecommentedLine = ls[0] + ls[1]
        if not sDecommentedLine:
            return None
        else:
            return sDecommentedLine.replace('\#', '#')

        

class TextBlockParser:
    def __init__(self, untaggedtextclass = IndentedParagraphs,
                 decomment = True, tabsize = 4,
                 decommenter = UnescapedHashDecommenter):
        """\
        Instantiate a TextBlockParser object.
        IN:
        untaggedtextclass = IndentedParagraphs <class TextBlock> or None:
            What to do with text that appears before the first tagged
            text block. None means raise a ParseError if any is found.
        decomment = True <bool>:
            Strip comments from the text?
        tabsize = 4 <int>:
            Convert tabs to this many spaces. Set < 0 to disable.
        decommenter=UnescapedHashDecommenter <Decommenter> <class Decommenter>:
            How should comments be removed?
        
        """
        if untaggedtextclass is None:
            self.oUntaggedBlock = None
        else:
            self.oUntaggedBlock = UnlabelledTextBlockContainer(untaggedtextclass, tabsize)
        self.bDeComment = decomment
        self.iTabSize = tabsize
        self.sLabel = ''
        self.sBlock = ''
        self.oCurrentBlock = self.oUntaggedBlock
        self.dsoUnlabelledBlocks = {}
        self.dsoLabelledBlocks = {}
        self.dssNames = {}
        if decommenter is None:
            decommenter = UnescapedHashDecommenter()
        elif isinstance(decommenter, type(Decommenter)):
            decommenter = decommenter()
        self.oDecommenter = decommenter



    def addblock(self, name, textblockclass, labelled = False, tag = None):
        if name in self.dsoLabelledBlocks:
            sErrorMsg = "The name %s is already in use by a previously added labelled block."
            sErrorMsg %= repr(name)
            raise BlockReaderError(sErrorMsg) 
        elif name in self.dsoUnlabelledBlocks:
            sErrorMsg = "The name %s is already in use by a previously added unlabelled block."
            sErrorMsg %= repr(name)
            raise BlockReaderError(sErrorMsg) 

        if not tag:
            tag = name.upper()

        if tag in self.dssNames:
            sErrorMsg = "The name %s is already in use by the previously added block %s."
            sErrorMsg %= (repr(name), repr(tag))
            raise BlockReaderError(sErrorMsg) 

        self.dssNames[tag] = name
        
        if labelled:
            self.dsoLabelledBlocks[name] = LabelledTextBlockContainer(textblockclass, self.iTabSize)
        else:
            self.dsoUnlabelledBlocks[name] = UnlabelledTextBlockContainer(textblockclass, self.iTabSize)



    def parse(self, file):
        """\
        Parse text blocks from a file.
        IN:
        file <str>:
            The file to parse.

        """
        iLine = 0
        f = open(file)
        for sLine in f:
            iLine += 1
            sLine = sLine.rstrip('\n')
            #print repr(sLine)
            if self.bDeComment:
                sLine = self.oDecommenter.decomment(sLine)
                if sLine is None:
                    continue
            #print repr(sLine)
            
            # Open a new text block?
            sPutativeTag = sLine.split(':', 1)[0].strip()
            if sPutativeTag in self.dssNames:
                sTag = sPutativeTag
                sName = self.dssNames[sTag]
                sLabel = sLine.split(':',1)[1].strip()

                if sName in self.dsoUnlabelledBlocks:
                    if sLabel:
                        sErrorMsg = "Label %s present for unlabelled block %s, tag: %s)."
                        sErrorMsg %= (repr(sLabel), repr(sName), repr(sTag))
                        raise ParseError(file, iLine, sErrorMsg)
                    oBlock = self.dsoUnlabelledBlocks[sName]
                    oBlock.reset()
                        
                else:
                    if not sLabel:
                        sErrorMsg = "Missing label for labelled block %s (Tag: %s)."
                        sErrorMsg %= (repr(sName), repr(sTag))
                        raise ParseError(file, iLine, sErrorMsg)
                    
                    oBlock = self.dsoLabelledBlocks[sName]
                    if sLabel in oBlock:
                        oBlock[sLabel].reset()
                    else:
                        oBlock.addlabel(sLabel)
                        
                self.sLabel = sLabel
                self.oCurrentBlock = oBlock
                

            # Are we reading a labelled block?
            elif self.sLabel:
                self.oCurrentBlock[sLabel].addline(sLine)

            # Are we reading an unlabelled block? May be allowed text
            # before the first tagged block.
            elif not self.oCurrentBlock is None:
                #print "Its in an unlabelled block."
                #print repr(sLine)
                self.oCurrentBlock.addline(sLine)

            # We're reading disallowed text before the first tagged block.
            # Any non-whitespace here is an error.
            elif sLine.strip():
                sErrorMsg = "Garbage text before first block (%s)."
                sErrorMsg %= repr(sLine)
                raise ParseError(file, iLine, sErrorMsg)


                    
    def labelledblocks(self):
        """\
        Return the dict containing the labelled blocks.

        """
        return self.dsoLabelledBlocks

    def unlabelledblocks(self):
        """\
        Return the dict containing the unlabelled blocks.

        """
        return self.dsoUnlabelledBlocks

    def untaggedblock(self):
        """\
        Return the untagged block.

        """
        return self.oUntaggedBlock
    


