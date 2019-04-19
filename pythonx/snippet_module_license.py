import re
import vim
import configparser
from time import strftime
from pathlib import Path
from snippet_module_base import *

def get_git_author_name():
  config = configparser.ConfigParser()
  config.read(str(Path.home()) + "/.gitconfig")
  return config["user"]["name"]

def get_license_header():
  path_to_file = os.path.dirname(vim.current.buffer.name)

  while path_to_file and path_to_file != "/":
    license_path = path_to_file + "/LICENSE"
    if os.path.isfile(license_path):
      with open(license_path) as f:
        return get_commented_textblock(f.read().splitlines())
    path_to_file = os.path.dirname(path_to_file)

  return ""

def get_mit_header():
  head = "Copyright (c) " + strftime("%Y") + " " + get_git_author_name()

  lines = [
    head,
    "",
    "Permission is hereby granted, free of charge, to any person obtaining a",
    "copy of this software and associated documentation files (the \"Software\"),",
    "to deal in the Software without restriction, including without limitation",
    "the rights to use, copy, modify, merge, publish, distribute, sublicense,",
    "and/or sell copies of the Software, and to permit persons to whom the",
    "Software is furnished to do so, subject to the following conditions:",
    "",
    "The above copyright notice and this permission notice shall be included in",
    "all copies or substantial portions of the Software.",
    "",
    "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR",
    "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,",
    "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE",
    "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER",
    "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING",
    "FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER",
    "DEALINGS IN THE SOFTWARE.",
  ]

  return get_commented_textblock(lines)
