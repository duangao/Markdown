# Markdown interpreter

## Install

+ First you can download it.
+ cd path_to_markdown.py 
+ ln -s full_path_to_markdown.py  /usr/bin/Markdown 
> You may need root. 

+ You can run it by Markdown in any path. 


## Usage
Markdown source_file [options]

**options:**
+ -h, --help: 
	show you the help messages
+ -o, --output + [dest_html_file]:
	Set output in specific HTML file
	Default name is "default_output.html"
+ -p, --print + dest_pdf_file:	
	Set output in specific PDF file.
> Warning: If you use this option, you must use -o meanwhile.

+ -P, --Print +dest_pdf_file:
	Generate PDf file only.

## Feature 
+ Six ranks title 
```
	# ---------h1
	##---------h2
	###--------h3
	####-------h4
	#####------h5
	######-----h6

```
+ horizen line 
```
At least three '-' are needed.
```
+ Unordered list
> +,*,- are okay.

+ Ordered list
> Begin with 'number. '

+ Line quote
```
You should put '>' at begin of line.
And this can be nested.
```
+ bold  Italic Delete 
> *italic*
> **bold**
> ~delete~
And you can nest them.

+ Superscript/Subscript
> Superscript: x^[1]
> Subscript:   x/[1]

+ Link and image
```
 \[text](url)
 ![image](url)
```

+ Block and Code block
> Block must begin with '```' and end with '```'.
> Code block must begin with '```[language]' and end with '```'.
[Language]: python c++ 

Warning: Token handle with not be execute in block, like bold italic and so on. 

+ Table 

> First line is the table header.
> Second line must be one or more (---|),where '-' can be one or more.
> Extra lines are the body of table.

+ Math formula 
> Inner line formula : begin and end with '$'
> Line formula: begin and with '$$'

Tips: You should connect to Internet. 

## Dependency
+ wkhtmltopdf
	PDF export needs wkhtmlpdf,You can download it from \[wkhtmltopdf](wkhtmltopdf.org)
+ mathjax
	You should connect to Internet to support mathjax working.
+ python3 
	You should use python3 instead of python2, if you must use it in python2,you can replace enum to your own class defination. And remove "from functools import reduce".


