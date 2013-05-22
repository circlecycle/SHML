# SHML.py (shorthand markup language) by DOM Algebra, LLC. Author: James Robey, domalgebra@gmail.com
 
# Copyright (c) 2012-2013 James Robey, domalgebra@gmail.com
# All rights reserved.

# Redistribution and use in source and binary forms are permitted
# provided that the above copyright notice and this paragraph are
# duplicated in all such forms and that any documentation,
# advertising materials, and other materials related to such
# distribution and use acknowledge that the software was developed
# by the <organization>.  The name of the
# <organization> may not be used to endorse or promote products derived
# from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

# You process shml by making an instance of this and passing your TEXT
# SHML to Processor.process(text), receiving back your shml, or an exception
# if something went wrong.

# QUICK NOTE: Processor.process is the only public method, taking text, and returning text.

# SUMMARY:

# SHML stands for "Short-Hand-Markup-Language" and is a wonderfully timesaving method of writing programs in the Nametag Workshop without all that tiring "closing of tags" that is almost the trademark of writing in HTML.

# We chose a previous example, "Views within Views", to illustrate how SHML works. This is exactly equivalent to that example except you'll notice (almost) no close tags in the below.

# SHML is written exactly like HTML, except: 

#    0) Always use correct indentation 
#    1) Never use close tags for a tag opened at the start of a line; tag contents may continue on the same line, or indented on the next. 
#    2) You can have more than one tag on a line; all but the first must be closed normally. 
#    3) Comment blocks must open at the start of a line, and close at the end of one. 
#    4) there is no 4.

# We find it takes a short period of adjustment and then you'll probably want to use it for every project thereafter. It saves a lot of typing and leads to beautiful code.

""" SHML V1.0, author James Robey, jrobey.services@gmail.com.

        SHML is short for Shorthand Markup Language, a way of writing HTML that omits the closing tags.
    This module provides a SHML-to HTML-templating service, via making an instance and calling 
    it's .process(text) method.

        Summary: There is nothing done with Nametag in "normal" HTML that can't be represented in this shorthand.
    It's meant to make writing html easier, by being shorter, but equally familiar after a (very) brief
    acclimation period.
    
    Quick Start:
        SHML is written exactly like HTML, except:
            1) Never use close tags
            2) Always use correct indentation
            3) One element per line only strictly (for now) - NO attributes lined up by newline, for instance
            4) Comment blocks must open at the start of a line, and close at the end of one.
    
    Example:
        
        The HTML:
    
            <div id="Foo1" class="someclass">
                <span>
                    <b>My name is<b>: <i style="color:red">James</i>
                </span>
            </div>
        
        Is equal to this SHML:
    
            <div id="Foo1" class="someclass">
                <span>
                    <b>My name is:
                    <i style="color:red">James
            
     
        One perspective is that it does away with close tags at the price of having 
    one properly indented tag per line, instead of html's dismissal of whitespace. 
    Another perspective is that it helps coders change indent easily when copy
    and pasting code, and sharing snippets. Yet another is that it's a solution in 
    search of a problem, but *I* hardly think so! You might be reading HTML, but someone 
    has to type it, too, and honestly, it's not that hard to read, being almost identical
    to HTML anyway.
"""

#this SHML example is a little more involved; used when this module
#is run from the command line as a test.

test_contents = """

test<!-- /* this should be visible -->
<!-- /* no problem // <!-- --> 
/*
//-->

<script name="personinspector">
    __ready__.personinspector = function(){
        ...
    }
    
    <div> Hi There
    
        <span>This is a test
        <span>Tis is a second test
        
        <!-- make a button for the users to click -->
        <input name="somename" type="button" value="somename">
        <view>
            __ready__:function(){
                $(this.target).parent().jnamed('somename').click(function(){
                    alert("you pressed somename");
                });
            }
            
        <!-- this is okay because parsing continues until '>' seen at end of line. -->
        <input name="somename" 
               type="button" 
               value="somename">
        
    
<personinspector class="centered">
    __ready__:function(){
        ...
    }
            
"""

#our only dependency
import re

class Processor:
    #this is autodetected along the way by looking at the first indent difference.
    indent_amt = 4
    
    def process(self, buf, autodetect_indent_amt=True):
        """ I will take a string [of shml] and turn it into html, such that 
            its an XML compliant document, with all the comments removed.
            The autodetect_indent_amt feature will use the first
            two non-blank lines in the document with an indent difference
            to determine what the overall indenting of the document is
            Otherwise you can pass false and set self.indent_amt yourself
            before running this method. 
        """
        
        #this processor works on whole lines, not characters.
        self.lines = buf.split("\n")
    
        #if they ask, find out the indent of the document for them
        if autodetect_indent_amt:
            self.indent_amt = self.detectIndent(self.lines)
    
        #state for the comment detector - this will go up as comments open 
        #and down as they close for the respective type of comment,
        #such that finding one type will cause the other to be ignored 
        #until that opened tag is closed again.
        self.html_comments_open = 0
        self.js_comments_open = 0
        
        #each call to recursiveProcessor will process one top level element, 
        #leaving any more unprocessed. Since the recursiveProcessor will 
        #eat up blank lines, the solution is to call the recursiveProcessor
        #repeatedly, until there are no more lines to process.
        output = []
        while self.lines:
            output.append('\n')
            output.extend(self.recursiveProcessor())
        
        #return the output as accumulated, rejoined into a string, as the final result
        return "\n".join(output)
        
    def detectIndent(self, lines):
        """ Given some text broken up by new line into an array, 
            i'll look for the indent of the first non-blank line,
            and then the second, returning the difference.
        """
        first_indent = None

        for line in lines:
            if not line.strip(): continue
            indent = len(line) - len(line.lstrip())

            #first non-blank line
            if first_indent is None: 
                first_indent = indent
                continue

            #if indent of current line is bigger then our first indent we're good
            elif indent > first_indent:
                return indent - first_indent

        #If we are here then there was only one indent, or no indent, supply default
        return 4

    def recursiveProcessor(self, base_indent=0, base_actual_indent=-1):
        """ I will operate on lines such that myself and any lines greater 
            indent then me will be handled by me. I will change myself 
            into an open tag, with optional attributes (or optional text),
            and change everything inside of me into text.. except 
            that when i find another node i.e line starting with '>',
            i will invoke myself on that. As I go, I (or my child) will
            delete from the top of passed in lines variable sharing the 
            same reference, so that as my child processes, it gets 
            rid of input and accumulates output, and it all works 
            out in the end to expand the SHML syntax as designed!
        """
        
        #while loop state variables
        output = []
        still_searching_for_base_indent = True   
        current_indent = base_indent
    
        while 1:
            #if we run out of lines (our ending condition) but are still 
            #in an open tag (i.e. not still searching for a base indent), 
            #flush out the final close tag.
            if not self.lines:
                if not still_searching_for_base_indent:
                    output.append("%s</%s>"%(" "*(current_indent*self.indent_amt), tagname))
                break
        
            #we will look at the top most line - and delete it when we've evaluated it. always pull from top!
            line = self.lines[0]
            
            #get the line without end spaces for use below,
            strippedline = line.strip()
            
            #if the line is blank of if, by state stored in self.html_comments_open or js_comments_open,
            #we find the line is part of a comment block, skip it.
            if (not strippedline) or self.skipLineIfInCommentBlock(strippedline): 
                del self.lines[0]
                continue
            
            #okay we're past the comments. Find out if the line represents a new element (or just text of an element):
            is_new_elem = strippedline.startswith("<") and (strippedline[1] is not "!") and (strippedline[1] is not "%")
                            
            #get the indent of the line (that is, the unstripped one)
            current_actual_indent = len(line) - len(line.lstrip())
            
            #do a little friendly error checking - this should not happen in well formed SHML
            if is_new_elem and (strippedline.startswith("</") or strippedline.endswith('/>')):
                raise Exception, "There is no need for close tags in a SHML file! (offending lines are:)\n%s\n"%("\n".join(self.lines[:10]))
                
            #get the indent of the line (that is, the unstripped one)
            #current_actual_indent = len(line) - len(line.lstrip())
            #print "current_actual_indent: line", current_actual_indent, line
                
            #if we have not yet encountered the first tag, and this line is a new tag
            if still_searching_for_base_indent and is_new_elem:
                
                #if we are processing a new tag and it's multiline, continue to accumulate attrs until a line 
                #with '>' is seen.. this lets us have multiline tags!
                if ">" not in line:   
                    #prepare the loop 
                    del self.lines[0]
                    #accumlate until we see an end 
                    while ">" not in self.lines[0]:
                        line += " "+self.lines[0].strip()
                        del self.lines[0]
                    #accumulate the last line to get the full single line (carriage returns/spaces removed)
                    line += " "+self.lines[0].strip()
                    
                #found a new tag, record the indent, set state to start looking for content or close
                base_actual_indent = current_actual_indent
                still_searching_for_base_indent = False
                
                try:
                    # extract the info we need from this new tag. The tagname, attrs, and text (last two optional)
                    tagname = re.search('(?<=\<)\w+(?=\s?|\>?)', line).group(0).strip()
                    attrs = re.search('(?<=\<%s).*?(?=\>)'%(tagname), line).group(0).strip()
                    text = re.search('(?<=\>).*', line).group(0).strip()
                except Exception, e:
                    raise Exception, "It is probable your SHML has an error. it was detected when parsing this line: '%s' Error is %s"%(line,e)
                
                #first space needed to keep things lookin' good, if no attrs
                if attrs: attrs = " %s"%(attrs) 
                
                #append an opening tag to the output, for the element found
                output.append('%s<%s%s>'%(" "*(current_indent*self.indent_amt), tagname, attrs))
                
                #if text was found, add that too, with the right indent, in the output.
                if text: output.append("%s%s"%(" "*((current_indent+1)*self.indent_amt), text))
                
            #if the indent of the material is such that the scope is closed, emit a close   
            elif current_actual_indent <= base_actual_indent:
                still_searching_for_base_indent = True
                output.append("%s</%s>"%(" "*(current_indent*self.indent_amt), tagname))
                current_indent -= 1
                #if we've reached this point, we have found the end of a recursive call into the processor. return
                #without gobbling the line.. and this makes it so that text can't mess up indentation, only tags have to be right.
                return output
  
            #if we've found a new element - but we're already found our opening indent, recurse into this new element
            elif is_new_elem:
                output.append('\n')
                output.extend(self.recursiveProcessor(base_indent=current_indent+1, base_actual_indent=current_actual_indent))
                continue
        
            #okay, it's just some text that goes in the tag currenlty opened, emit it.
            else:
                output.append(line)
            
            #UPKEEP FOR WHILE 1 STATEMENT    
            #if that wasn't the last line, remove it from the top of the document and repeat!
            if self.lines:  del self.lines[0]    

        #return the output, having accumulated lines off the top of the input (lines) 
        #and appending lines to the output in response. 
        return output
        
        
    #these are the symbols that define start and stop of comments for the method skipLineIfInCommentBlock
    html_comment_open_symbol = "<!--"
    html_comment_close_symbol = "-->"
    js_comment_open_symbol = "/*"
    js_comment_close_symbol = "*/"
    js_comment_line_symbol = "//"
    
    def skipLineIfInCommentBlock(self, strippedline):
        """ I am a simple state machine (who's state is stored on this class, such that only
            one thread should call any given instance at a time) that will tell you if the lines 
            passed in succession are part of a comment block or not, working line by line and keeping track 
            of the number of comment opens and closes. I have been written to work with nested comments 
            properly, so except for the rule below, compliant with HTML and javascripts commenting styles
            
            The major limitation is that all multiline comments must be on their own lines /entirely/.
            Comments made after - but on the same line as - javascript code will not be recognized as 
            the start of a comment block (and will be left in); those types of comments will not count 
            towards opens or closes of comments.
            
            The rule is: all multiline comments must start on their own line.
        """
        
        ##########################################################################################################
        #### If an open of html or js was found, look only for that type of comment until closed. Also, dont start a 
        #### new block if the symbol doesn't start at the beginning of the line! Note we always check for closes the same time as opens
        #### (even though we know we'll skip the line in the end) hence no returns in this section.
        
        #check the num. of html comment opens/closes (when not in a js comment block already) 
        if not self.js_comments_open:
            if self.html_comments_open:
                self.html_comments_open += strippedline.count(self.html_comment_open_symbol)
                
            elif strippedline.startswith(self.html_comment_open_symbol):
                self.html_comments_open += strippedline.count(self.html_comment_open_symbol)
                
            #if we are opened, check for closes! do we balance? or will we skip more lines?
            if self.html_comments_open:
                self.html_comments_open -= strippedline.count(self.html_comment_close_symbol)
                return True
        
        #check the num. of js comment opens/closes (when not in an html comment block already)
        if not self.html_comments_open:
            if self.js_comments_open:
                self.js_comments_open += strippedline.count(self.js_comment_open_symbol)
                
            elif strippedline.startswith(self.js_comment_open_symbol):
                self.js_comments_open += strippedline.count(self.js_comment_open_symbol)
                
            #if we are opened, check for closes! do we balance? or will we skip more lines?
            if self.js_comments_open:
                self.js_comments_open -= strippedline.count(self.js_comment_close_symbol)
                return True
           
        ##########################################################################################################
        #### skip a line starting with the js line comment symbol ("//") if we're in no other comment.  
        if strippedline.startswith(self.js_comment_line_symbol):
            return True
         
        ##########################################################################################################
        #### if we're in either a js or html comment returning True indicates we should skip the line (else it's normal!)
        return self.html_comments_open or self.js_comments_open
        
   
if __name__ == '__main__':
    #given a source string (like test_contents), print the translation
    print Processor().process(test_contents)
    
