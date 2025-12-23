# Bind - Simple C/C++ Build Tool

A lightweight, no-nonsense CLI build tool for C/C++ projects. Because makefiles are so last century.

## Features

- 🚀 Simple .st file format (way easier than makefiles)
- 🎯 Automatic compiler detection (C vs C++)
- 📦 Support for executables and static libraries
- 🧹 Built-in clean command
- 😎 Funny comments to keep you sane during builds

## Installation

### Option 1: Use the Python Script

bash
python bind.py <command>


### Option 2: Build as Executable (Recommended)

bash
pip install pyinstaller
pyinstaller --onefile --name bind bind.py


Then move dist/bind.exe to a folder in your PATH (e.g., C:\tools\)

## Usage

### Create a New Build File

bash
bind new <name>

Example:

bash
bind new myproject

This creates myproject.st with a template ready to fill out.

### Build Your Project

bash
bind <name>

Example:

bash
bind myproject


### Clean Build Artifacts

bash
bind clean <name>


### Get Help

bash
bind help


## File Format (.st)

Here's what a typical .st file looks like:


ini
# Bind Build File - May the compile gods be with you

[project]
name = myproject
type = executable

[output]
name = myproject.exe
directory = ./build

[compiler]
c_compiler = gcc
cpp_compiler = g++
flags = -Wall -O2 -mconsole

[sources]
files = main.cpp, utils.c, helper.cpp
include_dirs = ./include, ./src

[linking]
libraries = m, pthread
lib_dirs = /usr/local/lib


### Sections Explained

#### [project]
- **name**: Your project name
- **type**: Either executable or library

#### [output]
- **name**: Name of the output file (e.g., program.exe, mylib)
- **directory**: Where to put build artifacts (default: ./build)

#### [compiler]
- **c_compiler**: Path to C compiler (default: gcc)
- **cpp_compiler**: Path to C++ compiler (default: g++)
- **flags**: Compiler flags (e.g., -Wall -O2 -mconsole)

#### [sources]
- **files**: Comma-separated list of .c and .cpp files
- **include_dirs**: Comma-separated list of include directories

#### [linking]
- **libraries**: External libraries to link (e.g., m, pthread)
- **lib_dirs**: Directories to search for libraries

## Common Flags

### Windows (MinGW/Clang)

ini
flags = -Wall -O2 -mconsole

The -mconsole flag is important on Windows to create console applications.

### Linux/Mac

ini
flags = -Wall -O2


### Debug Build

ini
flags = -Wall -g


### Release Build (Optimized)

ini
flags = -Wall -O3 -DNDEBUG


## Examples

### Simple Hello World

bash
bind new hello


Edit hello.st:

ini
[project]
name = hello
type = executable

[output]
name = hello.exe
directory = ./build

[compiler]
c_compiler = gcc
cpp_compiler = g++
flags = -Wall -O2 -mconsole

[sources]
files = main.cpp
include_dirs = 

[linking]
libraries = 
lib_dirs =


Create main.cpp:

cpp
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}


Build and run:

bash
bind hello
./build/hello.exe


### Multi-File Project

ini
[sources]
files = main.cpp, math_utils.cpp, string_utils.c
include_dirs = ./include


### Using External Libraries

ini
[linking]
libraries = curl, ssl, crypto
lib_dirs = C:\libs\curl\lib, C:\libs\openssl\lib


## Troubleshooting

### "undefined symbol: WinMain"
Add -mconsole to your compiler flags:

ini
flags = -Wall -O2 -mconsole


### "No such file or directory" for source files
Make sure your source files exist and the paths are correct. Paths are relative to where you run bind.

### Compiler not found
Either:
1. Add compiler to your PATH, or
2. Specify full path in .st file:

ini
c_compiler = C:\MinGW\bin\gcc.exe
cpp_compiler = C:\MinGW\bin\g++.exe


### Only .o files, no executable
Check if linking failed. Look for error messages. Make sure you set output name = in your .st file.

## Tips

- **Comments**: Use # for comments on their own lines. Don't put comments after values.
- **Empty fields**: Leave fields blank if not needed (e.g., libraries = )
- **Quotes**: Use quotes for paths with spaces: "C:\Program Files\..."
- **Multiple files**: Separate with commas: file1.cpp, file2.cpp, file3.c

## Building a Library


ini
[project]
name = mylib
type = library

[output]
name = mylib
directory = ./lib

[sources]
files = math.cpp, string.cpp
include_dirs = ./include


This creates lib/libmylib.a (static library).

## Why "Bind"?

Because it **binds** your source files together into an executable. Also, it's short and sounds cool. 😎

## License

Do whatever you want with it. May your builds always succeed! 🚀

---

Made with ☕ and a healthy dose of compiler errors. this update 