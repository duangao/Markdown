#! /usr/bin/python3
import os,re
import sys,getopt
from enum import Enum
from subprocess import call
from functools import reduce


class TABLE(Enum):
    Init=1
    Format=2
    Table=3

class ORDERLIST(Enum):
    Init=1
    List=2

class BLOCK(Enum):
    Init=1
    Block=2
    CodeBlock=3

table_state=TABLE.Init
orderList_state=ORDERLIST.Init
block_state=BLOCK.Init
is_code=False
is_normal=True

temp_table_first_line=[]
temp_table_first_line_str=""

need_mathjax=False




def test_state(input):
    Code_List=["python\n","c++\n","c\n"]
    global table_state,orderList_state,block_state,is_code,temp_table_first_line,temp_table_first_line_str

    result=input

    pattern = re.compile(r'```(\s)*\n')
    a=pattern.match(input)

    # BEGIN: block and code block
    if  a and block_state==BLOCK.Init:
        result="<blockquote>"
        block_state=BLOCK.Block
        is_normal=False

    elif len(input)>4 and input[0:3]=='```' and (input[3:9]=="python" or input[3:6]=="c++" or input[3:4]=="c") and block_state==BLOCK.Init:
        block_state=BLOCK.Block
        result="<code></br>"
        is_code=True
        is_normal=False

    elif block_state==BLOCK.Block and input=='```\n':
        if is_code:
            result="</code>"
        else:
            result="</blockquote>"
        block_state=BLOCK.Init
        is_code=False
        is_normal=False

    elif block_state==BLOCK.Block:
        pattern=re.compile(r'[\n\r\v\f\ ]')
        result=pattern.sub("&nbsp",result)
        pattern=re.compile(r'\t')
        result=pattern.sub("&nbsp"*4,result)
        result="<span>"+result+"</span></br>"
        is_normal=False
    # END

    #BEGIN : order list 
    if len(input)>2 and input[0].isdigit() and input[1]=='.' and orderList_state==ORDERLIST.Init:
        orderList_state=ORDERLIST.List
        result="<ol><li>"+input[2:]+"</li>"
        is_normal=False

    elif len(input)>2 and  input[0].isdigit() and input[1]=='.' and orderList_state==ORDERLIST.List:
        result="<li>"+input[2:]+"</li>"
        is_normal=False

    elif orderList_state==ORDERLIST.List and (len(input)<=2 or input[0].isdigit()==False or input[1]!='.'):
        result="</ol>"+input
        orderList_state=ORDERLIST.Init

    #END

    #BEGIN: table 
    pattern=re.compile(r'^((.+)\|)+((.+))$')
    match=pattern.match(input)
    if match:
        l=input.split('|')
        l[-1]=l[-1][:-1]
        if l[0] == '':
            l.pop(0)
        if l[-1]=='':
            l.pop(-1)
        if table_state==TABLE.Init:
            table_state=TABLE.Format
            temp_table_first_line=l
            temp_table_first_line_str=input
            result=""

        elif table_state==TABLE.Format :
            if reduce(lambda a,b:a and b,[all_same(i,'-') for i in l],True):
                table_state=TABLE.Table
                result="<table><thread><tr>"
                is_normal=False
           
                for i in temp_table_first_line:
                    result+="<th>"+i+"</th>"
                result+="</tr>"
                result+="</thread><tbody>"
                is_normal=False
            else:
                result=temp_table_first_line_str+"</br>"+input
                table_state=TABLE.Init

        elif table_state==TABLE.Table:
            result="<tr>"
            for i in l:
                result+="<td>"+i+"</td>"
            result+="</tr>"

    elif table_state==TABLE.Table:
        table_state=TABLE.Init
        result="</tbody></table>"+result
    elif table_state==TABLE.Format:
        pass

    #END

    
    return result



def all_same(lst,sym):
    return not lst or sym*len(lst) == lst


def handleTitle(s,n):
    temp="<h"+repr(n)+">"+s[n:]+"</h"+repr(n)+">"
    return temp
        
def handleUnorderd(s):
    s="<ul><li>"+s[1:]
    s+="</li></ul>"
    return s

def tokenTemplate(s,match):
    pattern=""
    if match == '*':
        pattern="\*([^\*]*)\*"
    if match == '~~':
        pattern="\~\~([^\~\~]*)\~\~"
    if match == '**':
        pattern ="\*\*([^\*\*]*)\*\*"
    return pattern

def tokenHandle(s):
    l=['b','i','S']
    j=0
    for i in ['**','*','~~']:
        pattern=re.compile(tokenTemplate(s,i))
        match=pattern.finditer(s)
        k=0
        for a in match:
            if a:
                content=a.group(1)
                x,y=a.span()
                c=3
                if i=='*':
                    c=5
                s=s[:x+c*k]+"<"+l[j]+">"+content+"</"+l[j]+">"+s[y+c*k:]
                k+=1
        pattern=re.compile(r'\$([^\$]*)\$')
        a=pattern.search(s)
        if a:
            global need_mathjax
            need_mathjax=True

        j+=1

    return s

def link_image(s):
    pattern=re.compile(r'\\\[(.*)\]\((.*)\)')
    match=pattern.finditer(s)
    for a in match:
        if a:
            text,url=a.group(1,2)
            x,y=a.span()
            s=s[:x]+"<a href="+url+" target=\"_blank\">"+text+"</a>"+s[y:]


    pattern=re.compile(r'!\[(.*)\]\((.*)\)')
    match=pattern.finditer(s)
    for a in match:
        if a:
            text,url=a.group(1,2)
            x,y=a.span()
            s=s[:x]+"<img src="+url+" target=\"_blank\">"+"</a>"+s[y:]

    pattern=re.compile(r'(.)\^\[([^\]]*)\]')
    match=pattern.finditer(s)
    k=0
    for a in match:
        if a:
            sym,index=a.group(1,2)
            x,y=a.span()
            s=s[:x+8*k]+sym+"<sup>"+index+"</sup>"+s[y+8*k:]
        k+=1
    
    pattern=re.compile(r'(.)/\[(.*)\]')
    match=pattern.finditer(s)
    for a in match:
        if a:
            sym,index=a.group(1,2)
            x,y=a.span()
            s=s[:x]+sym+"<sub>"+index+"</sub>"+s[y:]
    
    return s


def parse(input):
     global block_state,is_normal
     is_normal=True

    result=input

    result=test_state(input)
    

   
    if block_state==BLOCK.Block :
        return result

    # BEGIN: handle title
    title_rank=0
    for i in range(6,0,-1):
        if input[:i] == '#'*i:
            title_rank=i
            break
    if title_rank!=0:
        result=handleTitle(input,title_rank)
        return result
    # END

    #BEGIN: horizen line 
    if len(input)>2 and all_same(input[:-1],'-') and input[-1]=='\n':
        result="<hr>"
        return result
    #END

    # BEGIN: unordered list
    unorderd=['+','*','-']
    if result != "" and result[0] in unorderd :
        result=handleUnorderd(result)
        is_normal=False
    # END

    f=input[0]
    count=0
    sys_q=False
    while f=='>':
        count+=1
        f=input[count]
        sys_q=True
    if sys_q:
    
        result=" <blockquote style=\"color:#8fbc8f\"> "*count+"<b>"+input[count:]+"</b>"+"</blockquote>"*count
        is_normal=False

    # BEGIN: token replace,while title and list don't use it,so put it behind them.
    result=tokenHandle(result)
    # END

    #BEGIN: link and image
    result = link_image(result)
    #END
    pa=re.compile(r'^(\s)*$')
    a=pa.match(input)
    if input[-1]=="\n" and is_normal==True and not a :
    
        result+="</br>"

    return result 


#"""

def print_usage():
    print("Usage: markdown source_file [options]")
    print("source_file suffix must be one of: md, markdown, mdown,mkd")
    print(" Options:")
    print("     -h,--help:    show you help message")
    print("     -o,--output:  set output in specific HTML file,\n \
                if -o is not specified, the default is to put to default_output.html .\n\
                -p,--print    set output in specific PDF  file, this option needs you generate HTML meanwhile.") 
    print("     -P,--Print,   only generate PDF file, you need not to generate HTML file. ")
    


def main():
    dest_file="default_output.html"
    dest_pdf_file=""

    only_pdf=False

    try:
        opts,args = getopt.gnu_getopt(sys.argv[1:],"ho:p:P:",["help","output=","print=","Print="])
        for opt,arg in opts:
            if opt in ["-h","--help"]:
                print_usage()
                sys.exit(1)
            elif opt in ["-o","--output"]:
                dest_file=arg
            elif opt in ["-p","--print"]:
                dest_pdf_file=arg
            elif opt in ["-P","--Print"]:
                dest_pdf_file=arg
                only_pdf=True
            else:
                print("%s====>%s"%(opt,arg))

        if len(args)==1:
            run(args[0],dest_file,dest_pdf_file,only_pdf)
        elif len(args)==0:
            print_usage()
            sys.exit(1)

    except getopt.GetoptError:
        print("Error input!")
        print_usage()
        sys.exit(1)



def run(source_file,dest_file,dest_pdf_file,only_pdf):
    file_name=source_file
    dest_name=dest_file
    dest_pdf_name=dest_pdf_file

    name,suffix=os.path.splitext(file_name)
    if suffix not in [".md",".markdown",".mdown","mkd"]:
        print_usage()
        sys.exit(1)

    if only_pdf:
        dest_name=".~temp~.html"


    f=open(file_name,"r")


    f_r=open(dest_name,"w")
    f_r.write("<style type=\"text/css\">div {display: block;font-family: \"Times New Roman\",Georgia,Serif}\
          #wrapper { width: 100%;height:100%; margin: 0; padding: 0;}#left { float:left; \
         width: 10%;  height: 100%;  }#second {   float:left;   width: 80%;height: 100%;   \
        }#right {float:left;  width: 10%;  height: 100%; \
        }</style><div id=\"wrapper\"> <div id=\"left\"></div><div id=\"second\">")
    f_r.write("<meta charset=\"utf-8\"/>")
    
    for eachline in f:
        result=parse(eachline)
        if result!="":
            f_r.write(result)

    f_r.write("</br></br></div><div id=\"right\"></div></div>")

    global need_mathjax
    if need_mathjax:
        f_r.write("<script type=\"text/x-mathjax-config\">\
  MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['\\\\(','\\\\)']]}});</script><script type=\"text/javascript\" src=\"http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML\"></script>")
    f_r.close()
    f.close()

    if dest_pdf_name != "" or only_pdf:
        call(["wkhtmltopdf",dest_name,dest_pdf_name])
    if only_pdf:
        call(["rm",dest_name])


if __name__=="__main__":
    main() 

