#!/usr/bin/env python

###
# Copyright (C) 2002-2004, Tamer Fahmy <tamer@tammura.at>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

###
# Pivy distutils setup script.
#

"""Pivy is an Open Inventor binding for Python. Open Inventor is an object
oriented 3D toolkit which presents a programming model based on a 3D scene
database. It was developed by Silicon Graphics.

The binding has been interfaced to Coin - a 3D graphics library with an C++
Application Programming Interface based on the Open Inventor 2.1 API.

Pivy has been developed by Tamer Fahmy and is made available under a
BSD-style license.
"""

###
# Setup file for the Pivy distribution.
#

classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Multimedia :: Graphics
Topic :: Multimedia :: Graphics :: 3D Modeling
Topic :: Multimedia :: Graphics :: 3D Rendering
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
"""


from distutils.command.build import build
from distutils.command.clean import clean
from distutils.core import setup
from distutils.extension import Extension
from distutils.sysconfig import get_python_inc
import os, shutil, sys

# if we are on a gentoo box salute the chap and output stuff in nice colors
# Gentoo is Python friendly, so be especially friendly to them! ;)
try:
    from output import green, blue, turquoise, red, yellow
    print red("Oooh, it's a Gentoo! Nice nice! tuhtah salutes you! :)\n")
except:
    def red(text): return text
    def green(text): return text
    def blue(text): return text
    def turquoise(text): return text
    def yellow(text): return text


VERSION = "0.1.0"

class pivy_build(build):
    PIVY_SNAKES = r"""
                            _____
                        .-'`     '.                                     
                     __/  __       \                                   
                    /  \ /  \       |    ___                          
                   | /`\| /`\|      | .-'  /^\/^\                   
                   | \(/| \(/|      |/     |) |)|                     
                  .-\__/ \__/       |      \_/\_/__..._             
          _...---'-.                /   _              '.               
         /,      ,             \   '|  `\                \           
        | ))     ))           /`|   \    `.       /)  /) |             
        | `      `          .'       |     `-._         /               
        \                 .'         |     ,_  `--....-'               
         `.           __.' ,         |     / /`'''`                     
           `'-.____.-' /  /,         |    / /                           
               `. `-.-` .'  \        /   / |                           
                 `-.__.'|    \      |   |  |-.                         
                    _.._|     |     /   |  |  `'.                       
              .-''``    |     |     |   /  |     `-.                    
           .'`         /      /     /  |   |        '.                  
         /`           /      /     |   /   |\         \               
        /            |      |      |   |   /\          |               
       ||            |      /      |   /     '.        |                
       |\            \      |      /   |       '.      /              
       \ `.           '.    /      |    \        '---'/               
        \  '.           `-./        \    '.          /                
         '.  `'.            `-._     '.__  '-._____.'--'''''--.         
           '-.  `'--._          `.__     `';----`              \       
              `-.     `-.          `.''```                     ;        
                 `'-..,_ `-.         `'-.                     /         
                        '.  '.           '.                 .'          


                            ~~~ HISSSSSSSSSS ~~~
                           Welcome to Pivy %s!
                 Building Pivy has never been so much fun!

    """ % VERSION

    pivy_header_include = """\
#ifdef __PIVY__
%%include %s
#endif

"""

    SWIG = "swig"
    SWIG_SUPPRESS_WARNINGS = "-w302,306,307,312,389,362,503,509,510"
    SWIG_PARAMS = "-c -v -c++ -python -includeall " + \
                  "-D__PIVY__ -I. -Ifake_headers -I%s %s -o %s_wrap.cxx %s.i"

    SOGUI = ['SoQt', 'SoXt', 'SoGtk', 'SoWin']
    MODULES = {'pivy'  : ('_pivy',  'coin-config'),
               'SoQt'  : ('_soqt',  'soqt-config'),
               'SoXt'  : ('_soxt',  'soxt-config'),
               'SoGtk' : ('_sogtk', 'sogtk-config'),
               'SoWin' : ('_sowin', 'sowin-config')}

    SUPPORTED_SWIG_VERSIONS = ['1.3.19']
    SWIG_COND_SYMBOLS = []
    CXX_INCS = ""
    CXX_LIBS = "-lswigpy" + " "

    ext_modules=[]
    py_modules=['sogui']

    def do_os_popen(self, cmd):
        "returns the output of a command in a single line."
        fd = os.popen(cmd)
        lines = fd.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
        lines = " ".join(lines)
        fd.close()
        return lines

    def check_cmd_exists(self, cmd):
        "returns the path of the specified command if it exists."
        print blue("Checking for %s..." % cmd),
        for path in os.environ['PATH'].split(':'):
            if os.path.exists(os.path.join(path, cmd)):
                print blue("'%s'" % os.path.join(path, cmd))
                return 1
        print red("not found.")
        return 0

    def check_python_version(self):
        "checks the Python version."
        print blue("Python version...%s" % sys.version.split(" ")[0])
        if int(sys.version[0]) < 2:
            print red("Pivy only works with Python versions >= 2.0.")
            sys.exit(1)

    def check_coin_version(self):
        "checks the Coin version."
        if not self.check_cmd_exists("coin-config"):
            sys.exit(1)
        print blue("Coin version..."),
        version = self.do_os_popen("coin-config --version")
        print blue("%s" % version)
        if not version.startswith('2.3'):
            print yellow("** Warning: Pivy has only been tested with Coin "
                         "versions 2.3.x.")

    def check_gui_bindings(self):
        "checks for availability of SoGui bindings and removes the not available ones."
        for gui in self.SOGUI:
            gui_config_cmd = self.MODULES[gui][1]
            if not self.check_cmd_exists(gui_config_cmd):
                del self.MODULES[gui]
            else:
                print blue("Checking for %s version..." % gui),
                version = self.do_os_popen("%s --version" % gui_config_cmd)
                print blue("%s" % version)

    def get_coin_features(self):
        "sets the global variable SWIG_COND_SYMBOLS needed for conditional " + \
        "wrapping"

        print blue("Checking for Coin features..."),
        if not os.system("coin-config --have-feature 3ds_import"):
            self.SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_3DS_IMPORT")
            print green("3ds import "),

        if not os.system("coin-config --have-feature vrml97"):
            self.SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_VRML97")
            print green("vrml97 "),

        if not os.system("coin-config --have-feature sound"):
            self.SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_SOUND")
            print green("sound "),

        if not os.system("coin-config --have-feature superglu"):
            self.SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_SUPERGLUE")
            print green("superglu "),

        if not os.system("coin-config --have-feature threads"):
            self.SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_THREADS")
            print green("threads "),

        if not os.system("coin-config --have-feature threadsafe"):
            self.SWIG_COND_SYMBOLS.append("-DHAVE_FEATURE_THREADSAFE")
            print green("threadsafe "),

        print

    def check_swig_version(self, swig):
        "checks for the swig version."
        if not self.check_cmd_exists(swig):
            sys.exit(1)
        print blue("Checking for SWIG version..."),
        fd = os.popen("%s -version 2>&1" % swig)
        version = fd.readlines()[1].strip().split(" ")[2]
        fd.close()
        print blue("%s" % version)
        if not version in self.SUPPORTED_SWIG_VERSIONS:
            print yellow("Warning: Pivy has only been tested with the following" + \
                         "SWIG versions: %s." % " ".join(self.SUPPORTED_SWIG_VERSIONS))

    def copy_and_swigify_coin_headers(self):
        """there are times where a function simply has to do what a function
        has to do. indeed, tralala..."""

        coin_includedir = self.do_os_popen("coin-config --includedir")

        for root, dirs, files in os.walk("Inventor"):
            if 'CVS' in dirs:
                dirs.remove('CVS')

            for name in files:
                if name[-2:] == ".i":
                    file_i = os.path.join(root, name)
                    file_h = os.path.join(root, name)[:-2] + ".h"

                    if not os.path.exists(file_h):
                        print blue("Copying ") + turquoise(os.path.join(coin_includedir, file_h)),
                        print blue("to ") + turquoise(file_h)
                        shutil.copyfile(os.path.join(coin_includedir, file_h), file_h)
                        print blue("Pivyizing ") + turquoise(file_h),
                        fd = open(file_h, 'rw+')
                        contents = fd.readlines()

                        ins_line_nr = -1
                        for line in contents:
                            ins_line_nr += 1
                            if "#include " in line:
                                break

                        if ins_line_nr != -1:
                            contents.insert(ins_line_nr, self.pivy_header_include % (file_i))
                            fd.seek(0)
                            fd.writelines(contents)
                            print blue("[") + green("done") + blue("]")
                        else:
                            print blue("[") + red("failed") + blue("]")
                        fd.close


    def pivy_configure(self):
        "configures Pivy"
        print turquoise(self.PIVY_SNAKES)
        print blue("Platform...%s" % sys.platform)
        self.check_python_version()
        self.check_coin_version()
        if self.SOGUI: self.check_gui_bindings()
        self.get_coin_features()
        self.check_swig_version(self.SWIG)
        self.copy_and_swigify_coin_headers()        

    def swig_generate(self):
        "build all available modules"
        for module in self.MODULES.keys():
            module_name = self.MODULES[module][0]
            config_cmd = self.MODULES[module][1]

            if not os.path.isfile(module.lower() + "_wrap.cxx"):
                print red("\n=== Generating %s_wrap.cxx for %s ===\n" % (module.lower(), module))
                print blue(self.SWIG + " " + self.SWIG_SUPPRESS_WARNINGS + " " + self.SWIG_PARAMS %
                           (self.do_os_popen("coin-config --includedir"),
                            self.CXX_INCS + self.do_os_popen("%s --cppflags" % config_cmd),
                            module.lower(),
                            module.lower()))
                if os.system(self.SWIG + " " + self.SWIG_SUPPRESS_WARNINGS + " " + self.SWIG_PARAMS %
                             (self.do_os_popen("coin-config --includedir"),
                              self.CXX_INCS + self.do_os_popen("%s --cppflags" % config_cmd),
                              module.lower(), module.lower())):
                    print red("SWIG did not generate wrappers successfully! ** Aborting **")
                    sys.exit(1)
            else:
                print red("=== %s_wrap.cxx for %s already exists! ===" % (module.lower(),
                                                                            module))

            self.ext_modules.append(Extension(module_name, [module.lower() + "_wrap.cxx"],
                                              extra_compile_args=(self.CXX_INCS + self.do_os_popen("%s --cppflags" % config_cmd)).split(),
                                              extra_link_args=(self.CXX_LIBS + self.do_os_popen("%s --ldflags --libs" % config_cmd)).split()))
            self.py_modules.append(module.lower())

    def run(self):
        "the entry point for the distutils build class"
        self.pivy_configure()
        self.swig_generate()

        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)


class pivy_clean(clean):
    WRAPPER_FILES = ('pivy_wrap.cxx',
                     'soqt_wrap.cxx',
                     'sogtk_wrap.cxx',
                     'soxt_wrap.cxx')

    def remove_coin_headers(self):
        "remove the coin headers from the pivy Inventor directory"
        
        for root, dirs, files in os.walk("Inventor"):
            if 'CVS' in dirs:
                dirs.remove('CVS')

            for file_name in files:
                if file_name[-2:] == ".h":
                    print blue("removing %s" % os.path.join(root, file_name))
                    os.remove(os.path.join(root, file_name))
        
    def run(self):
        "the entry point for the distutils clean class"
        self.remove_coin_headers()
        # remove the SWIG generated wrappers
        for wrapper_file in self.WRAPPER_FILES:
            if os.path.isfile(wrapper_file):
                print blue("removing %s" % wrapper_file)
                os.remove(wrapper_file)
        clean.run(self)

setup(name = "Pivy",
      version = VERSION,
      description = "A Python binding for Coin/Open Inventor",
      long_description = __doc__,
      author = "Tamer Fahmy",
      author_email = "tamer@tammura.at",
      download_url="http://www.tammura.at/cvs.html",
      url = "http://pivy.tammura.at/",
      cmdclass = {'build' : pivy_build,
                  'clean' : pivy_clean},
      ext_modules = pivy_build.ext_modules,
      py_modules  = pivy_build.py_modules,
      classifiers = filter(None, classifiers.split("\n")),
      license = "BSD License",
      platforms = ['Any']
      )


