SHML
====

SHML (shorthand markup language)

SHML is copyright DOM Algebra, 2012-2013, authored by James Robey. Comments/praise/complaints at domalgebra@gmail.com

SHML stands for "Short-Hand-Markup-Language" and is a wonderfully timesaving
method of writing programs in the Nametag Workshop without all that tiring 
"closing of tags" that is almost the trademark of writing in HTML.

We chose a previous example, "Views within Views", to illustrate how SHML works.
This is exactly equivalent to that example except you'll notice (almost) no
close tags in the below. 

SHML is written exactly like HTML, except:
   0) Always use correct indentation
   1) Never use close tags for a tag opened at the start of a line; 
      tag contents may continue on the same line, or indented on the next.
   2) You can have more than one tag on a line; all but the first must be closed normally.
   3) Comment blocks must open at the start of a line, and close at the end of one.
   4) there is no 4.

We find it takes a short period of adjustment and then you'll probably 
want to use it for every project thereafter. It saves a lot of typing and 
leads to beautiful code.

The following example is written in the Nametag Runtime, you can find out more about it at 

http://nametagworks.com

The output of this code would be wellformed XML 

      <view>
          list:[
              {person:"James", phone:"123-456-7890", age:"22"},
              {person:"Bob", phone:"123-456-7890", age:"25"},
              {person:"Jill", phone:"012-9348-576", age:"24"},
              {person:"Jacob", phone:"012-9348-576", age:"23"},
              {person:"Jen", phone:"012-9348-576", age:"26"}
          ],
          
          selectable:"lightyellow, lightBlueGradient, lightGreyGradient" //Nametag ships with these CSS verbs.
          
          <div class="rounded padded bottomspacer">
              <div>Record for: <b>[=person=]</b>
              <div class="leftspacer">phone: [=phone=]
              <div class="leftspacer">age: [=age=]
              
              //our list within a list takes care of a basic indicator of how we met them.
              <view>
                  list:["Business", "Personal", "Community"],
                  selectable:"lightgreen, forestGradient fgwhite, fgblack",
                  toggleselect:true //a new special attribute makes the list toggled.
                  <span class="leftspacer rounded leftpadded rightpadded smaller">
                      [=item=]
                
                
