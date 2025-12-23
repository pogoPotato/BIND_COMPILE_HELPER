"""
Bind - Simple C/C++ Build Tool
File Extension: .st
"""

import os
import subprocess
import sys
from pathlib import Path
import shutil

#basic template u get

TEMPLATE = """# Bind Build File
# Generated for: {name}

[project]
name = {name}
type = executable

[output]
name =
directory = ./build

[compiler]
c_compiler =
cpp_compiler =
flags = -Wall -O2 -mconsole

[sources]
files =
include_dirs =

[linking]
libraries =
lib_dirs =
"""

#phrasing things 

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
        if "files" not in self.config["sources"]:
            raise ValueError("No source files specified")
        if "name" not in self.config["output"]:
            raise ValueError("No output name specified")

#building shit

class BindBuilder:
    def __init__(self, config):
        self.cfg = config
        self.objects = []

    def q(self, p):
        return f"\"{p}\""

    def get_compiler(self, src):
        ext = Path(src).suffix.lower()
        if ext == ".c":
            return self.cfg["compiler"].get("c_compiler") or "gcc"
        return self.cfg["compiler"].get("cpp_compiler") or "g++"

    def compile(self, src):
        if not os.path.exists(src):
            print(f"✗ Missing source: {src}")
            return None

        compiler = self.q(self.get_compiler(src))
        flags = self.cfg["compiler"].get("flags", "")

        includes = self.cfg["sources"].get("include_dirs", [])
        if isinstance(includes, str):
            includes = [includes]

        inc_flags = " ".join(f"-I{self.q(i)}" for i in includes)

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

    def link(self):
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

        lib_flags = " ".join(f"-l{l}" for l in libs)
        lib_dir_flags = " ".join(f"-L{self.q(d)}" for d in lib_dirs)

        objs = " ".join(self.q(o) for o in self.objects)

        cmd = f"{linker} {objs} -o {output} {lib_dir_flags} {lib_flags}"
        print("CMD:", cmd)

        r = subprocess.run(cmd, shell=True, text=True)
        if r.returncode != 0:
            return False

        print(f"  ✓ {output}")
        print("\n✓ Build successful!")
        return True

    def build(self):
        print(f"Building: {self.cfg['project']['name']}\n")

        files = self.cfg["sources"]["files"]
        if isinstance(files, str):
            files = [files]

        for f in files:
            obj = self.compile(f)
            if not obj:
                return False
            self.objects.append(obj)

        return self.link()

#commands to use
def create_new(name):
    file = f"{name}.st"
    if os.path.exists(file):
        print("✗ File already exists")
        return
    with open(file, "w") as f:
        f.write(TEMPLATE.format(name=name))
    print(f"✓ Created {file}")

def build_project(name):
    file = f"{name}.st"
    if not os.path.exists(file):
        print("✗ Build file not found")
        return

    parser = BindParser(file)
    cfg = parser.parse()
    parser.validate()

    BindBuilder(cfg).build()

def clean_project(name):
    file = f"{name}.st"
    if not os.path.exists(file):
        print("✗ Build file not found")
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
bind new <name>
bind <name>
bind clean <name>
bind help
""")

#main shit
def main():
    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1]

    if cmd == "help":
        show_help()
    elif cmd == "new":
        create_new(sys.argv[2])
    elif cmd == "clean":
        clean_project(sys.argv[2])
    else:
        build_project(cmd)

if __name__ == "__main__":
    main()
