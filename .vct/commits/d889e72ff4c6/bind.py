"""
Bind - Multi-Language Build Tool
File Extension: .st
Supports: C, C++, Rust, Python, Go
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

# Language Templates
TEMPLATES = {
    "c": """# Bind Build File - C Project
# Generated for: {name}

[project]
name = {name}
type = executable
language = c

[output]
name = {name}.exe
directory = ./build

[compiler]
c_compiler = gcc
flags = -Wall -O2 -mconsole

[sources]
files = main.c
include_dirs = 

[linking]
libraries = 
lib_dirs = 
""",
    
    "cpp": """# Bind Build File - C++ Project
# Generated for: {name}

[project]
name = {name}
type = executable
language = cpp

[output]
name = {name}.exe
directory = ./build

[compiler]
cpp_compiler = g++
flags = -Wall -O2 -std=c++17 -mconsole

[sources]
files = main.cpp
include_dirs = 

[linking]
libraries = 
lib_dirs = 
""",
    
    "rust": """# Bind Build File - Rust Project
# Generated for: {name}

[project]
name = {name}
type = executable
language = rust

[output]
name = {name}.exe
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
""",
    
    "python": """# Bind Build File - Python Project
# Generated for: {name}

[project]
name = {name}
type = executable
language = python

[output]
name = {name}.exe
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
""",
    
    "go": """# Bind Build File - Go Project
# Generated for: {name}

[project]
name = {name}
type = executable
language = go

[output]
name = {name}.exe
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
"""
}

# Parsing
class BindParser:
    def __init__(self, build_file):
        self.build_file = build_file
        self.config = {
            "project": {},
            "output": {},
            "compiler": {},
            "sources": {},
            "linking": {}
        }

    def parse(self):
        current = None
        last_key = None

        with open(self.build_file, "r", encoding="utf-8") as f:
            for raw in f:
                if not raw.strip() or raw.lstrip().startswith("#"):
                    continue

                indented = raw.startswith((" ", "\t"))
                line = raw.strip()

                if line.startswith("[") and line.endswith("]"):
                    current = line[1:-1]
                    last_key = None
                    continue

                if indented and current and last_key:
                    val = line.rstrip(",")
                    if not val:
                        continue
                    existing = self.config[current].get(last_key)
                    if existing is None:
                        self.config[current][last_key] = val
                    elif isinstance(existing, list):
                        existing.append(val)
                    else:
                        self.config[current][last_key] = [existing, val]
                    continue

                if "=" in line and current:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.split("#", 1)[0].strip().rstrip(",")

                    last_key = k
                    if not v:
                        continue

                    if "," in v:
                        v = [x.strip() for x in v.split(",") if x.strip()]

                    self.config[current][k] = v

        return self.config

    def validate(self):
        if "name" not in self.config["project"]:
            raise ValueError("Missing project name")
        if "type" not in self.config["project"]:
            raise ValueError("Missing project type")
        if "language" not in self.config["project"]:
            raise ValueError("Missing project language")
        if "files" not in self.config["sources"]:
            raise ValueError("No source files specified")
        if "name" not in self.config["output"]:
            raise ValueError("No output name specified")

# Building
class BindBuilder:
    def __init__(self, config):
        self.cfg = config
        self.objects = []
        self.language = self.cfg["project"].get("language", "c")

    def q(self, p):
        return f"\"{p}\""

    def get_compiler(self, src):
        ext = Path(src).suffix.lower()
        if ext == ".c":
            return self.cfg["compiler"].get("c_compiler") or "gcc"
        elif ext in [".cpp", ".cc", ".cxx"]:
            return self.cfg["compiler"].get("cpp_compiler") or "g++"
        elif ext == ".rs":
            return self.cfg["compiler"].get("rustc_compiler") or "rustc"
        elif ext == ".go":
            return self.cfg["compiler"].get("go_compiler") or "go"
        return "gcc"

    def build_c_cpp(self):
        print(f"Building {self.language.upper()} project: {self.cfg['project']['name']}\n")

        files = self.cfg["sources"]["files"]
        if isinstance(files, str):
            files = [files]

        # Compile each source file
        for f in files:
            obj = self.compile_c_cpp(f)
            if not obj:
                return False
            self.objects.append(obj)

        return self.link_c_cpp()

    def compile_c_cpp(self, src):
        if not os.path.exists(src):
            print(f"✗ Missing source: {src}")
            return None

        compiler = self.q(self.get_compiler(src))
        flags = self.cfg["compiler"].get("flags", "")

        includes = self.cfg["sources"].get("include_dirs", [])
        if isinstance(includes, str):
            includes = [includes]

        inc_flags = " ".join(f"-I{self.q(i)}" for i in includes if i)

        out_dir = self.cfg["output"].get("directory", "./build")
        os.makedirs(out_dir, exist_ok=True)

        obj = Path(out_dir) / (Path(src).stem + ".o")

        cmd = f"{compiler} {flags} {inc_flags} -c {self.q(src)} -o {self.q(obj)}"
        print("CMD:", cmd)

        r = subprocess.run(cmd, shell=True, text=True)
        if r.returncode != 0:
            return None

        print(f"  ✓ {obj}")
        return str(obj)

    def link_c_cpp(self):
        files = self.cfg["sources"]["files"]
        if isinstance(files, str):
            files = [files]

        has_cpp = any(Path(f).suffix != ".c" for f in files)
        linker = self.cfg["compiler"].get("cpp_compiler" if has_cpp else "c_compiler") or "g++"
        linker = self.q(linker)

        out_name = self.cfg["output"]["name"]
        out_dir = self.cfg["output"].get("directory", "./build")
        output = self.q(str(Path(out_dir) / out_name))

        libs = self.cfg["linking"].get("libraries", [])
        if isinstance(libs, str):
            libs = [libs]

        lib_dirs = self.cfg["linking"].get("lib_dirs", [])
        if isinstance(lib_dirs, str):
            lib_dirs = [lib_dirs]

        lib_flags = " ".join(f"-l{l}" for l in libs if l)
        lib_dir_flags = " ".join(f"-L{self.q(d)}" for d in lib_dirs if d)

        objs = " ".join(self.q(o) for o in self.objects)

        cmd = f"{linker} {objs} -o {output} {lib_dir_flags} {lib_flags}"
        print("CMD:", cmd)

        r = subprocess.run(cmd, shell=True, text=True)
        if r.returncode != 0:
            return False

        print(f"  ✓ {output}")
        print("\n✓ Build successful!")
        return True

    def build_rust(self):
        print(f"Building Rust project: {self.cfg['project']['name']}\n")

        files = self.cfg["sources"]["files"]
        if isinstance(files, str):
            files = [files]

        rustc = self.cfg["compiler"].get("rustc_compiler", "rustc")
        flags = self.cfg["compiler"].get("flags", "")

        out_dir = self.cfg["output"].get("directory", "./build")
        os.makedirs(out_dir, exist_ok=True)

        out_name = self.cfg["output"]["name"]
        output = str(Path(out_dir) / out_name)

        for src in files:
            if not os.path.exists(src):
                print(f"✗ Missing source: {src}")
                return False

            cmd = f"{self.q(rustc)} {flags} {self.q(src)} -o {self.q(output)}"
            print("CMD:", cmd)

            r = subprocess.run(cmd, shell=True, text=True)
            if r.returncode != 0:
                return False

        print(f"  ✓ {output}")
        print("\n✓ Build successful!")
        return True

    def build_python(self):
        print(f"Building Python project: {self.cfg['project']['name']}\n")

        files = self.cfg["sources"]["files"]
        if isinstance(files, str):
            files = [files]

        pyinstaller = self.cfg["compiler"].get("python_compiler", "pyinstaller")
        flags = self.cfg["compiler"].get("flags", "--onefile --console")

        out_dir = self.cfg["output"].get("directory", "./build")
        os.makedirs(out_dir, exist_ok=True)

        out_name = self.cfg["output"]["name"]

        for src in files:
            if not os.path.exists(src):
                print(f"✗ Missing source: {src}")
                return False

            cmd = f"{pyinstaller} {flags} --distpath {self.q(out_dir)} --name {Path(out_name).stem} {self.q(src)}"
            print("CMD:", cmd)

            r = subprocess.run(cmd, shell=True, text=True)
            if r.returncode != 0:
                return False

        print(f"  ✓ {Path(out_dir) / out_name}")
        print("\n✓ Build successful!")
        return True

    def build_go(self):
        print(f"Building Go project: {self.cfg['project']['name']}\n")

        files = self.cfg["sources"]["files"]
        if isinstance(files, str):
            files = [files]

        go_compiler = self.cfg["compiler"].get("go_compiler", "go")
        flags = self.cfg["compiler"].get("flags", "")

        out_dir = self.cfg["output"].get("directory", "./build")
        os.makedirs(out_dir, exist_ok=True)

        out_name = self.cfg["output"]["name"]
        output = str(Path(out_dir) / out_name)

        for src in files:
            if not os.path.exists(src):
                print(f"✗ Missing source: {src}")
                return False

            cmd = f"{go_compiler} build {flags} -o {self.q(output)} {self.q(src)}"
            print("CMD:", cmd)

            r = subprocess.run(cmd, shell=True, text=True)
            if r.returncode != 0:
                return False

        print(f"  ✓ {output}")
        print("\n✓ Build successful!")
        return True

    def build(self):
        if self.language in ["c", "cpp"]:
            return self.build_c_cpp()
        elif self.language == "rust":
            return self.build_rust()
        elif self.language == "python":
            return self.build_python()
        elif self.language == "go":
            return self.build_go()
        else:
            print(f"✗ Unsupported language: {self.language}")
            return False

# Commands
def create_new(name):
    print(f"\n=== Creating new project: {name} ===\n")
    print("Select a language:")
    print("1. C")
    print("2. C++")
    print("3. Rust")
    print("4. Python")
    print("5. Go")
    print()

    choice = input("Enter your choice (1-5): ").strip()

    language_map = {
        "1": "c",
        "2": "cpp",
        "3": "rust",
        "4": "python",
        "5": "go"
    }

    if choice not in language_map:
        print("✗ Invalid choice")
        return

    lang = language_map[choice]
    file = f"{name}.st"

    if os.path.exists(file):
        print(f"✗ File {file} already exists")
        return

    with open(file, "w") as f:
        f.write(TEMPLATES[lang].format(name=name))

    print(f"✓ Created {file} for {lang.upper()} project")
    print(f"✓ Edit {file} to configure your build")

def build_project(name):
    file = f"{name}.st"
    if not os.path.exists(file):
        print(f"✗ Build file {file} not found")
        return

    parser = BindParser(file)
    cfg = parser.parse()
    
    try:
        parser.validate()
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return

    success = BindBuilder(cfg).build()
    if not success:
        print("\n✗ Build failed!")
        sys.exit(1)

def clean_project(name):
    file = f"{name}.st"
    if not os.path.exists(file):
        print(f"✗ Build file {file} not found")
        return

    parser = BindParser(file)
    cfg = parser.parse()
    out = cfg["output"].get("directory", "./build")

    if os.path.exists(out):
        shutil.rmtree(out)
        print(f"✓ Cleaned {out}")
    else:
        print("Nothing to clean")

def show_help():
    print("""
Bind - Multi-Language Build Tool

Usage:
  bind new <name>         Create a new project (interactive language selection)
  bind build <name>       Build the project and create release executable
  bind clean <name>       Clean build artifacts
  bind help               Show this help message

Supported Languages:
  - C
  - C++
  - Rust
  - Python
  - Go

Example:
  bind new myproject      # Creates myproject.st with language selection
  bind build myproject    # Builds final release executable
  bind clean myproject    # Removes build directory
""")

# Main
def main():
    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1]

    if cmd == "help":
        show_help()
    elif cmd == "new":
        if len(sys.argv) < 3:
            print("✗ Usage: bind new <name>")
            return
        create_new(sys.argv[2])
    elif cmd == "build":
        if len(sys.argv) < 3:
            print("✗ Usage: bind build <name>")
            return
        build_project(sys.argv[2])
    elif cmd == "clean":
        if len(sys.argv) < 3:
            print("✗ Usage: bind clean <name>")
            return
        clean_project(sys.argv[2])
    else:
        # For backward compatibility, treat as build command
        build_project(cmd)

if __name__ == "__main__":
    main()