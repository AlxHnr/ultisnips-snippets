import os
import re
import vim

# takes indention width in characters and returns the
# indention string in tabs/whitespaces depending on the vim settings.
def get_indention_string(length):
  if int(vim.eval("&expandtab")):
    return " " * length
  else:
    tabstop = int(vim.eval("&tabstop"))
    tab_amount = (length - length % tabstop) / tabstop
    spaces_amount = length % tabstop
    return "\t" * tab_amount + " " * spaces_amount

def get_comment_prefix():
  prefix = vim.eval("&commentstring").split("%s", 2)[0]
  if not re.match("^.*\s$", prefix):
    prefix += " "

  return prefix

def get_comment_postfix():
  commentMarks = vim.eval("&commentstring").split("%s", 2)
  if len(commentMarks) != 2:
    return ""

  postfix = commentMarks[1]
  if not re.match("^\s", postfix):
    postfix = " " + postfix

  return postfix

# Takes a list of strings, which will be commented out and joined to a
# newline-seperated string. This function will comment out either each
# line seperatey, or only the first and last line of the block, depending
# on 'commentstring'.
def get_commented_textblock(string_list):
  filetype = vim.eval("&filetype")
  if not filetype:
    return "\n".join(string_list)

  comment_prefix = get_comment_prefix().strip()
  comment_postfix = get_comment_postfix().strip()

  line_prefix = "\n  "
  last_line = ""
  foldmarker = vim.eval("&foldmarker").split(",", 2)

  if comment_postfix:
    string_list.insert(0, comment_prefix)
    last_line = "\n" + comment_postfix
  else:
    line_prefix = "\n" + comment_prefix + " "
    string_list[0] = comment_prefix + " " + string_list[0]

  if vim.eval("&foldmethod") == "marker" and len(string_list) > 2:
    string_list[0] += " " + foldmarker[0]
    if comment_postfix:
      last_line = "\n" + foldmarker[1] + " " + comment_postfix
    else:
      last_line = "\n" + comment_prefix + " " + foldmarker[1]

  commented_string = line_prefix.join(string_list) + last_line
  return re.sub("[\t ]+\n", "\n",
      re.sub("\n\s+\n", "\n\n", commented_string))

# returns the parent directory name from 'path'.
def get_parent_dirname(path):
  return os.path.basename(os.path.dirname(os.path.realpath(path)))

# lowercases 'string' and seperate by 'seperator'. I.e. if 'seperator' is
# '_' then "CamelCase" will become "camel_case".
def delimiter_seperate(string, seperator):
  tmp_string = re.sub("([A-Z]+)", seperator + r"\1", string)
  tmp_string = re.sub("[\W_]+", seperator, tmp_string).lower()
  tmp_string = re.sub("(^" + seperator + "+|" + seperator + "+$)", \
      "", tmp_string)
  return re.sub(seperator + "{2,}", seperator, tmp_string)

def get_lisp_case(string):
  return delimiter_seperate(string, "-")

def get_underscore(string):
  return delimiter_seperate(string, "_")

def get_pascal_case(string):
  return re.sub(r'\W*(\w+)\W*',
      lambda match: match.group(1).capitalize(),
      string)

def get_camel_case(string):
  pascal_case = get_pascal_case(string)
  return pascal_case[0].lower() + pascal_case[1:]
