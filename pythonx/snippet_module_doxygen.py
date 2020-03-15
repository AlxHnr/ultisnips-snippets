from snippet_module_c import *
from snippet_module_base import *
import vim

def uses_single_line_c_comments():
  return vim.eval("&commentstring").startswith("//")

def get_doc_block_start():
  if uses_single_line_c_comments():
    return "///"
  else:
    return "/**"

def get_doc_empty_line(pre_indented):
  if uses_single_line_c_comments():
    return '\n' + pre_indented + '///'
  elif format_options_have_comment_leader():
    return '\n' + pre_indented + ' *'
  else:
    return '\n'

def get_doc_commend_ending():
  if uses_single_line_c_comments():
    return ''
  else:
    return "*/"

def get_doc_last_line(pre_indented):
  if uses_single_line_c_comments():
    return ''
  elif format_options_have_comment_leader():
    return "\n" + pre_indented + " " + get_doc_commend_ending()
  else:
    return "\n" + pre_indented + get_doc_commend_ending()

def get_doc_prefix():
  if uses_single_line_c_comments():
    return '/// '
  elif format_options_have_comment_leader():
    return ' * '
  else:
    return '  '
