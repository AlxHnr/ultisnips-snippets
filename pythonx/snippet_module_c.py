import re
import vim
from snippet_module_base import *

# build some regex expressions
unneeded_whitespaces = re.compile("\s+")
beginning_whitespaces = re.compile("^\s*")

# this function returns the definition string of the c function on the current
# line. I.e. if you are on a line that contains "int some_function(int some
# parameters, ...", it will return "int some_function("
def get_function_definition():
  current_buffer = vim.current.buffer
  current_line_num = int(vim.eval("line('.')")) - 1

  fun_match = re.match("^([_a-zA-Z]\w*)[\s\*]+([_a-zA-Z]\w*)([^\(=]*)\(", \
                       current_buffer[current_line_num])

  if not fun_match:
    return "none"

  return unneeded_whitespaces.sub(" ", fun_match.group(0))

def build_function_match(function_definition):
  # replace all whitespaces in 'function_definition' with '\s+' to generate
  # a search pattern, to search in the header for the function definition.
  function_match = re.sub("\s+", "\\s+", function_definition)
  function_match = re.sub("\(", "\\(", function_match)
  function_match = re.sub("\)", "\\)", function_match)
  function_match = re.sub("\*", "[\*\s]*", function_match)

  # this allows the function definition to match the function
  # definition in the header. It simply ignores prefixed specifier
  # like e.g. "extern", etc...
  function_match = "^\s*([_a-zA-Z]+\w*\s+|)[\*\s]*" + function_match

  return re.compile(function_match)

# Returns "void" for C and "" for C++.
def get_empty_parameters():
  if re.match(".*\.[ch]pp$", vim.current.buffer.name):
    return ""
  else:
    return "void"

# this function searches from the current line down and extracts all
# parameters from the function. It returns a multiline string on functions
# that take more than one line. It takes a open buffer as a parameter, and
# the index, which is the line number of the function. Unlike vim, Python
# counts from 0 up.
def get_function_parameters(buffer, index):
  # try to grab function parameters, or at least the first line of them.
  function_parameter = re.match(".*\((.*)", buffer[index])
  if not function_parameter:
    return get_empty_parameters()

  function_parameter = unneeded_whitespaces.sub(" ",
      function_parameter.group(1))

  function_definition = get_function_definition()
  indention_string = get_indention_string(len(function_definition))

  # check if the function definition is on one single line and
  # contains an equal amount of opening and closing parens.
  # the first paren is not in 'function_parameter', so we add 1.
  paren_count = \
      function_parameter.count("(") + 1 - function_parameter.count(")")

  if paren_count <= 0:
    parameters = re.sub("\)+;*$", "", function_parameter)
    if parameters:
      return parameters
    else:
      return get_empty_parameters()

  # count parameters in first line
  parameters = function_parameter + "\n"

  # append additional lines from the multiline function definition
  # to parameters string. Also re-indent them.
  for header_line in buffer[index + 1:]:
    tmp_line = unneeded_whitespaces.sub(" ", header_line)
    tmp_line = beginning_whitespaces.sub(indention_string, tmp_line)

    paren_count += tmp_line.count("(")
    paren_count -= tmp_line.count(")")
    if paren_count <= 0:
      parameters += re.sub("\)+;*$", "", tmp_line)
      break
    else:
      parameters += tmp_line + "\n"

  return parameters

# this function returns the matching parameters for the function on the current
# line by searching in the header the current file include.
def generate_function_parameters():
  current_buffer = vim.current.buffer

  # return void if we are expanding inside a header
  if re.match(".*\.h(pp)?$", current_buffer.name):
    return get_empty_parameters()

  # build some expressions
  current_file_path = re.sub("\/[^\/]*$", "", vim.current.buffer.name)
  current_line_num = int(vim.eval("line('.')")) - 2
  function_definition = get_function_definition()
  function_match = build_function_match(function_definition)
  local_include_match = re.compile("^#include\s*\"([^\"]+\.(h|hpp))\"$")

  # searches from the current line, up to line 0 for a valid '#include "..."'
  for current_line_num in range(current_line_num, -2, -1):
    header_file_name = \
        local_include_match.match(current_buffer[current_line_num])

    if not (header_file_name and header_file_name.group(1)):
      continue

    header_file_path = current_file_path + "/" + header_file_name.group(1)

    # search for the found header file in current buffers.
    header_file = None
    for buffer in vim.buffers:
      if buffer.name == header_file_path:
        header_file = buffer
        break

    # open file, if its not found in opened buffers, or if Vims buffer
    # cache is empty.
    if header_file is None or (len(buffer) == 1 and len(buffer[0]) == 0):
      try:
        header_file_handle = open(header_file_path, "r")
      except IOError:
        # if the file failed to open, try to search in the "src/" directory.
        try:
          header_file_handle = open("src/" + header_file_path, "r")
        except IOError:
          continue

      # read in whole file and close file handle.
      header_file = header_file_handle.readlines()
      header_file_handle.close()

    # search in header for the function definition.
    for index,header_line in enumerate(header_file):
      function_found = function_match.match(header_line)
      if function_found:
        break

    if not function_found:
      continue

    return get_function_parameters(header_file, index)

  return get_empty_parameters()
