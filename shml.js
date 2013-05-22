// SHML.js (shorthand markup language) by DOM Algebra, LLC. Author: James Robey, domalgebra@gmail.com
   
// Copyright (c) 2012-2013 James Robey, domalgebra@gmail.com
// All rights reserved.
// 
// Redistribution and use in source and binary forms are permitted
// provided that the above copyright notice and this paragraph are
// duplicated in all such forms and that any documentation,
// advertising materials, and other materials related to such
// distribution and use acknowledge that the software was developed
// by the <organization>.  The name of the
// <organization> may not be used to endorse or promote products derived
// from this software without specific prior written permission.
// THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

// You process shml by making an instance of this and passing your TEXT
// SHML to instance.process(text), receiving back your shml, or an exception
// if something went wrong.

// QUICK NOTE: SHMLClass.process is the only public method, taking text, and returning text.

// SUMMARY:

// SHML stands for "Short-Hand-Markup-Language" and is a wonderfully timesaving method of writing programs in the Nametag Workshop without all that tiring "closing of tags" that is almost the trademark of writing in HTML.

//We chose a previous example, "Views within Views", to illustrate how SHML works. This is exactly equivalent to that example except you'll notice (almost) no close tags in the below.

//SHML is written exactly like HTML, except: 

//    0) Always use correct indentation 
//    1) Never use close tags for a tag opened at the start of a line; tag contents may continue on the same line, or indented on the next. 
//    2) You can have more than one tag on a line; all but the first must be closed normally. 
//    3) Comment blocks must open at the start of a line, and close at the end of one. 
//    4) there is no 4.

//We find it takes a short period of adjustment and then you'll probably want to use it for every project thereafter. It saves a lot of typing and leads to beautiful code.

var SHMLClass = function(indent_amt){
    var self = this;
    
    //How many spaces to a tab?this is autodetected along the way by looking at the first indent difference.
    self.indent_amt = indent_amt !== undefined ? indent_amt : 4;
    
    //constants for comparison when skipping over comments
    self.html_comment_open_symbol = "<!--";
    self.html_comment_close_symbol = "-->";
    self.js_comment_open_symbol = "/*";
    self.js_comment_close_symbol = "*/";
    self.js_comment_line_symbol = "//";
    
    return self;
};

SHMLClass.prototype.process = function(buf, autodetect_indent_amt){
    // I will take a string [of shml] and turn it into html, such that 
    // its an XML compliant document, with all the comments removed.
    // The autodetect_indent_amt feature will use the first
    // two non-blank lines in the document with an indent difference
    // to determine what the overall indenting of the document is
    // Otherwise you can pass false and set self.indent_amt yourself
    // before running this method. 
    
    var self = this;
    
    if(autodetect_indent_amt === undefined)
        autodetect_indent_amt = true;
    
    //this processor works on whole lines, not characters.
    self.lines = buf.split("\n");

    //if they ask, find out the indent of the document for them
    if(autodetect_indent_amt)
        self.indent_amt = self.detectIndent(self.lines);

    //state for the comment detector - this will go up as comments open 
    //and down as they close for the respective type of comment,
    //such that finding one type will cause the other to be ignored 
    //until that opened tag is closed again.
    self.html_comments_open = 0;
    self.js_comments_open = 0;
    
    //each call to recursiveProcessor will process one top level element, 
    //leaving any more unprocessed. Since the recursiveProcessor will 
    //eat up blank lines, the solution is to call the recursiveProcessor
    //repeatedly, until there are no more lines to process.
    var output = [];
    while(self.lines.length !== 0){
        output.push('\n');
        output.extend(self.recursiveProcessor());
    }
        
    //return the output as accumulated, rejoined into a string, as the final result
    return output.join("\n");
};

// Given some text broken up by new line into an array, 
// i'll look for the indent of the first non-blank line,
// and then the second, returning the difference.   
SHMLClass.prototype.detectIndent = function(lines){
    var self = this;
    
    var first_indent = false;

    for(var i = 0; i < lines.length ; i ++){
        var line = String(lines[i]);
        
        if(line.trim().length === 0) 
            continue;
            
        indent = line.length - line.ltrim().length;

        //first non-blank line
        if(first_indent === false){
            first_indent = indent;
            continue;
        }

        //if indent of current line is bigger then our first indent we're good
        else if(indent > first_indent)
            return indent - first_indent;
    }
        
    //If we are here then there was only one indent, or no indent, supply default
    return 4;
};

//given a number of spaces to make, return a string of empty spaces to be used to indent tags
SHMLClass.prototype.makeIndent = function(amt){
    buf = [];
    while(buf.length < amt)
        buf.push(' ')
    return buf.join('');
};
    
// I will operate on lines such that myself and any lines greater 
// indent then me will be handled by me. I will change myself 
// into an open tag, with optional attributes (or optional text),
// and change everything inside of me into text.. except 
// that when i find another node i.e line starting with '>',
// i will invoke myself on that. As I go, I (or my child) will
// delete from the top of passed in lines variable sharing the 
// same reference, so that as my child processes, it gets 
// rid of input and accumulates output, and it all works 
// out in the end to expand the SHML syntax as designed!
SHMLClass.prototype.recursiveProcessor = function(base_indent, base_actual_indent){
    var self = this;
    
    if(base_indent === undefined)
        base_indent = 0;
    
    if(base_actual_indent === undefined)
        base_actual_indent = -1;
        
    //while loop state variables
    var output = [];
    var still_searching_for_base_indent = true;
    var tagname, attr, text;
    var current_indent = base_indent;
    
    while(1){
        //if we run out of lines (our ending condition) but are still 
        //in an open tag (i.e. not still searching for a base indent), 
        //flush out the final close tag.
        if(self.lines.length === 0){
            if(!still_searching_for_base_indent)
                output.push(self.makeIndent(current_indent*self.indent_amt)+"</"+tagname+">");
            break;
        }
            
        //we will look at the top most line - and delete it when we've evaluated it. always pull from top!
        var line = self.lines[0];
        var strippedline = String(line.trim());
        
        //get the line without end spaces for use below
        
        //if the line is blank of if, by state stored in self.html_comments_open or js_comments_open,
        //we find the line is part of a comment block, skip it.
        if(strippedline.length === 0 || self.skipLineIfInCommentBlock(strippedline)){
            self.lines.shift();
            continue;
        }   
        
        //okay we're past the comments. Find out if the line represents a new element (or just text of an element):
        var is_new_elem = strippedline.startswith("<") && (strippedline[1] != "!") && (strippedline[1] != "%");
                        
        //get the indent of the line (that is, the unstripped one)
        current_actual_indent = line.length - line.ltrim().length;
        
        //do a little friendly error checking - this should not happen in well formed SHML
        if(is_new_elem && (strippedline.startswith("</") || strippedline.endswith('/>')))
            throw "There is no need for close tags in a SHML file! (offending lines are:)\n"+self.lines.slice(0, 10).join("\n")+"\n";
            
        //if we have not yet encountered the first tag, and this line is a new tag
        if(still_searching_for_base_indent && is_new_elem){
            //if we are processing a new tag and it's multiline, continue to accumulate attrs until a line 
            //with '>' is seen.. this lets us have multiline tags!
            if(line.indexOf(">") === -1){
                line = line.rtrim();
                
                //prepare the loop 
                self.lines.shift();
                
                //accumlate until we see an end 
                while(self.lines[0].indexOf(">") === -1){
                    line += ' '+self.lines[0].trim();   
                    self.lines.shift();
                }
                    
                //accumulate the last line to get the full single line (carriage returns/spaces removed)
                line += ' '+self.lines[0].trim();
                
                /* update the stripped line that will be used below. tada */
                strippedline = line.trim();
            }   
                
            //found a new tag, record the indent, set state to start looking for content or close
            base_actual_indent = current_actual_indent;
            still_searching_for_base_indent = false;
            
            try{
                // extract the info we need from this new tag. The tagname, attrs, and text (last two optional)                
                // this was regex in the python version but used regex features javascript dont got, so i use this
                // ugly but works fine :)
                var tagname = strippedline.split("<").slice(1)[0].split(">").slice(0)[0].split(" ")[0];
                var attrs = strippedline.slice(strippedline.indexOf(tagname)+tagname.length).split(">")[0];
                var text = strippedline.split(">").slice(1).join(">");
            }catch(err){
                throw "It is probable your SHML has an error. it was detected when parsing this line: '"+line+"' Error is "+err;
            }
            
            //first space needed to keep things lookin' good, if no attrs
            //if(attrs)
            //    attrs = attrs;
            
            //append an opening tag to the output, for the element found
            output.push(self.makeIndent(current_indent*self.indent_amt)+'<'+tagname+attrs+">");
            
            //if text was found, add that too, with the right indent, in the output.
            if(text)
                output.push(
                    self.makeIndent((current_indent+1)*self.indent_amt)+text
                );
        }
                
        //if the indent of the material is such that the scope is closed, emit a close   
        else if(current_actual_indent <= base_actual_indent){
            still_searching_for_base_indent = true;
            output.push(self.makeIndent(current_indent*self.indent_amt)+"</"+tagname+">");
            current_indent -= 1;
            //if we've reached this point, we have found the end of a recursive call into the processor. return
            //without gobbling the line.. and this makes it so that text can't mess up indentation, only tags have to be right.
            return output;
        }
            
        //if we've found a new element - but we're already found our opening indent, recurse into this new element
        else if(is_new_elem){
            output.extend(self.recursiveProcessor(current_indent+1, current_actual_indent));
            continue;
        }
    
        //okay, it's just some text that goes in the tag currenlty opened, emit it.
        else
            output.push(line);
            
        //UPKEEP FOR WHILE 1 STATEMENT    
        //if that wasn't the last line, remove it from the top of the document and repeat!
        if(self.lines.length)
            self.lines.shift();
    }

    //return the output, having accumulated lines off the top of the input (lines) 
    //and appending lines to the output in response. 
    return output;
};

//I am a simple state machine (who's state is stored on this class, such that only
//one thread should call any given instance at a time) that will tell you if the lines 
//passed in succession are part of a comment block or not, working line by line and keeping track 
//of the number of comment opens and closes. I have been written to work with nested comments 
//properly, so except for the rule below, compliant with HTML and javascripts commenting styles
//
//The major limitation is that all multiline comments must be on their own lines /entirely/.
//Comments made after - but on the same line as - javascript code will not be recognized as 
//the start of a comment block (and will be left in); those types of comments will not count 
//towards opens or closes of comments.
//
//The rule is: all multiline comments must start on their own line.
SHMLClass.prototype.skipLineIfInCommentBlock = function(strippedline){
    var self = this;
    
    // If an open of html or js was found, look only for that type of comment until closed. Also, dont start a 
    // new block if the symbol doesn't start at the beginning of the line! Note we always check for closes the same time as opens
    // (even though we know we'll skip the line in the end) hence no returns in this section.
    
    strippedline = String(strippedline);
    
    //check the num. of html comment opens/closes (when not in a js comment block already) 
    if(!self.js_comments_open){
        if(self.html_comments_open)
            self.html_comments_open += strippedline.count(self.html_comment_open_symbol);
            
        else if(strippedline.startswith(self.html_comment_open_symbol))
            self.html_comments_open += strippedline.count(self.html_comment_open_symbol);
            
        //if we are opened, check for closes! do we balance? or will we skip more lines?
        if(self.html_comments_open){
            self.html_comments_open -= strippedline.count(self.html_comment_close_symbol);
            return true;
        }
    }
        
    //check the num. of js comment opens/closes (when not in an html comment block already)
    if(!self.html_comments_open){
        if(self.js_comments_open)
            self.js_comments_open += strippedline.count(self.js_comment_open_symbol);
            
        else if(strippedline.startswith(self.js_comment_open_symbol))
            self.js_comments_open += strippedline.count(self.js_comment_open_symbol);
            
        //if we are opened, check for closes! do we balance? or will we skip more lines?
        if(self.js_comments_open){
            self.js_comments_open -= strippedline.count(self.js_comment_close_symbol);
            return true;
        }
    }
        
    // skip a line starting with the js line comment symbol ("//") if we're in no other comment.  
    if(strippedline.startswith(self.js_comment_line_symbol))
        return true;
     
    // if we're in either a js or html comment returning true indicates we should skip the line (else it's normal!)
    return self.html_comments_open || self.js_comments_open;
};




