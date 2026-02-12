# Bind - Multi-Language Build Tool

A lightweight, no-nonsense CLI build tool for C, C++, Rust, Python, and Go projects. Because makefiles are so last century.

## Features

- 🚀 Simple .st file format (way easier than makefiles)
- 🎯 Multi-language support (C, C++, Rust, Python, Go)
- 🎨 Interactive language selection with numbered menu
- 📦 Builds final release executables
- 🧹 Built-in clean command
- 😎 One tool for all your projects

## Installation

### Option 1: Use the Python Script

```bash
python bind.py <command>
```

### Option 2: Build as Executable (Recommended)

```bash
pip install pyinstaller
pyinstaller --onefile --name bind bind.py
```

Then move `dist/bind.exe` to a folder in your PATH (e.g., `C:\tools\`)

## Usage

### Create a New Project

```bash
bind new <name>
```

Example:

```bash
bind new myproject
```

This will show an interactive menu:

```
=== Creating new project: myproject ===

Select a language:
1. C
2. C++
3. Rust
4. Python
5. Go

Enter your choice (1-5):
```

Select your language by entering a number (1-5). This creates `myproject.st` with the appropriate template.

### Build Your Project (Release)

```bash
bind build <name>
```

Example:

```bash
bind build myproject
```

This compiles your code and creates a final release executable in the `./build` directory.

### Clean Build Artifacts

```bash
bind clean <name>
```

### Get Help

```bash
bind help
```

## File Format (.st)

The `.st` format varies slightly by language, but follows the same structure:

### C/C++ Example

```ini
# Bind Build File - C++ Project
# May the compile gods be with you

[project]
name = myproject
type = executable
language = cpp

[output]
name = myproject.exe
directory = ./build

[compiler]
cpp_compiler = g++
flags = -Wall -O2 -std=c++17 -mconsole

[sources]
files = main.cpp, utils.cpp, helper.c
include_dirs = ./include, ./src

[linking]
libraries = m, pthread
lib_dirs = /usr/local/lib
```

### Rust Example

```ini
[project]
name = myapp
type = executable
language = rust

[output]
name = myapp.exe
directory = ./build

[compiler]
rustc_compiler = rustc
flags = -O

[sources]
files = main.rs
include_dirs = 

[linking]
libraries = 
lib_dirs = 
```

### Python Example

```ini
[project]
name = calculator
type = executable
language = python

[output]
name = calculator.exe
directory = ./build

[compiler]
python_compiler = pyinstaller
flags = --onefile --console

[sources]
files = main.py
include_dirs = 

[linking]
libraries = 
lib_dirs = 
```

### Go Example

```ini
[project]
name = server
type = executable
language = go

[output]
name = server.exe
directory = ./build

[compiler]
go_compiler = go
flags = 

[sources]
files = main.go
include_dirs = 

[linking]
libraries = 
lib_dirs = 
```

## Sections Explained

### [project]
- **name**: Your project name
- **type**: Either `executable` or `library`
- **language**: `c`, `cpp`, `rust`, `python`, or `go`

### [output]
- **name**: Name of the output file (e.g., `program.exe`, `mylib`)
- **directory**: Where to put build artifacts (default: `./build`)

### [compiler]
- **c_compiler**: Path to C compiler (default: `gcc`)
- **cpp_compiler**: Path to C++ compiler (default: `g++`)
- **rustc_compiler**: Path to Rust compiler (default: `rustc`)
- **python_compiler**: Python packager (default: `pyinstaller`)
- **go_compiler**: Path to Go compiler (default: `go`)
- **flags**: Compiler/build flags

### [sources]
- **files**: Comma-separated list of source files
- **include_dirs**: Comma-separated list of include directories

### [linking]
- **libraries**: External libraries to link (e.g., `m`, `pthread`)
- **lib_dirs**: Directories to search for libraries

## Common Flags

### C/C++ - Windows (MinGW/Clang)

```ini
flags = -Wall -O2 -mconsole
```

The `-mconsole` flag is important on Windows to create console applications.

### C/C++ - Linux/Mac

```ini
flags = -Wall -O2
```

### C/C++ - Debug Build

```ini
flags = -Wall -g
```

### C/C++ - Release Build (Optimized)

```ini
flags = -Wall -O3 -DNDEBUG
```

### Rust - Release Build

```ini
flags = -O
```

### Python - GUI Application

```ini
flags = --onefile --windowed
```

## Examples

### Simple Hello World (C++)

```bash
bind new hello
# Select: 2 (C++)
```

Edit `hello.st`:

```ini
[project]
name = hello
type = executable
language = cpp

[output]
name = hello.exe
directory = ./build

[compiler]
cpp_compiler = g++
flags = -Wall -O2 -mconsole

[sources]
files = main.cpp
include_dirs = 

[linking]
libraries = 
lib_dirs =
```

Create `main.cpp`:

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
```

Build and run:

```bash
bind build hello
./build/hello.exe
```

### Rust CLI Tool

```bash
bind new mytool
# Select: 3 (Rust)
```

Create `main.rs`:

```rust
fn main() {
    println!("Hello from Rust!");
}
```

Build:

```bash
bind build mytool
./build/mytool.exe
```

### Python Desktop App

```bash
bind new calculator
# Select: 4 (Python)
```

Edit `calculator.st` for GUI:

```ini
[compiler]
python_compiler = pyinstaller
flags = --onefile --windowed --name Calculator
```

Create `main.py` with your GUI code, then:

```bash
bind build calculator
# Creates standalone Calculator.exe!
```

### Multi-File C Project

```ini
[sources]
files = main.c, math_utils.c, string_utils.c
include_dirs = ./include
```

### Using External Libraries

```ini
[linking]
libraries = curl, ssl, crypto
lib_dirs = C:\libs\curl\lib, C:\libs\openssl\lib
```

## Language Requirements

| Language | Required Tools |
|----------|---------------|
| C | gcc or clang |
| C++ | g++ or clang++ |
| Rust | rustc (install from rustup.rs) |
| Python | pyinstaller (`pip install pyinstaller`) |
| Go | Go toolchain (golang.org) |

## Troubleshooting

### C/C++: "undefined symbol: WinMain"
Add `-mconsole` to your compiler flags:

```ini
flags = -Wall -O2 -mconsole
```

### "No such file or directory" for source files
Make sure your source files exist and the paths are correct. Paths are relative to where you run bind.

### Compiler not found
Either:
1. Add compiler to your PATH, or
2. Specify full path in .st file:

```ini
cpp_compiler = C:\MinGW\bin\g++.exe
```

### Python: "pyinstaller not found"
Install PyInstaller:

```bash
pip install pyinstaller
```

### Rust: "rustc not found"
Install Rust from https://rustup.rs

### Only .o files, no executable (C/C++)
Check if linking failed. Look for error messages. Make sure you set `output name =` in your .st file.

## Tips

- **Comments**: Use `#` for comments on their own lines. Don't put comments after values.
- **Empty fields**: Leave fields blank if not needed (e.g., `libraries =`)
- **Quotes**: Use quotes for paths with spaces: `"C:\Program Files\..."`
- **Multiple files**: Separate with commas: `file1.cpp, file2.cpp, file3.c`
- **Language templates**: Each language gets the right template automatically
- **Release builds**: `bind build` always creates optimized release executables

## Building a Library (C/C++)

```ini
[project]
name = mylib
type = library
language = cpp

[output]
name = mylib
directory = ./lib

[sources]
files = math.cpp, string.cpp
include_dirs = ./include
```

This creates `lib/libmylib.a` (static library).

## Why "Bind"?

Because it **binds** your source files together into an executable. Also, it's short and sounds cool. 😎

Now supports binding code in multiple languages!

## License

Do whatever you want with it. May your builds always succeed! 🚀

---

Made with ☕ and a healthy dose of compiler errors.