
"""
Bind - Simple C/C++ Build Tool
File Extension: .st

Usage:
    bind new <name>      - Create a new .st build file
    bind <name>          - Build project using <name>.st file
    bind clean <name>    - Clean build artifacts
    bind help            - Show help
"""

import os
import subprocess
import sys
from pathlib import Path

TEMPLATE = """# Bind Build File - May the compile gods be with you
# Generated for: {name}

[project]
name = {name}
type = executable  # or 'library' if you're feeling fancy

[output]
name =  # what do we call this masterpiece?
directory = ./build  # where the magic happens

[compiler]
c_compiler =  # gcc go brrr
cpp_compiler =  # g++ go brrr harder
flags = -Wall -O2 -mconsole # because warnings are just suggestions, right?

[sources]
files =  # throw your .c and .cpp files here (comma separated, don't be shy)
include_dirs =  # where your headers are hiding

[linking]
libraries =  # external libs we're mooching off of
lib_dirs =  # where those libs live (probably /usr/lib but who knows)

#MAKE SURE TO REMOVE ALL COMMENTS BEFORE RUNNING -- bind <name>
"""


#
#
#
   # it took me hours to add a supported icon ✓✓✓✓✓✓✓-->>  this shit 
   # also use -mconsole for windows 
#
#
#


class BindParser:
    def __init__(self, build_file):
        self.build_file = build_file
        self.config = {
            'project': {},
            'output': {},
            'compiler': {},
            'sources': {},
            'linking': {}
        }
    
    def parse(self):
        """Parse the .st file"""
        current_section = None
        
        with open(self.build_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    continue
                
                if '=' in line and current_section:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    #skip empty values
                    if not value:
                        continue
                    
                    #handle comma-separated lists
                    if ',' in value:
                        value = [v.strip() for v in value.split(',') if v.strip()]
                    
                    self.config[current_section][key] = value
        
        return self.config
    
    def validate(self):
        """Validate required fields"""
        if 'name' not in self.config['project']:
            raise ValueError("Missing project name")
        
        if 'type' not in self.config['project']:
            raise ValueError("Missing project type")
        
        if self.config['project']['type'] not in ['executable', 'library']:
            raise ValueError(f"Invalid project type: {self.config['project']['type']}")
        
        if 'files' not in self.config['sources']:
            raise ValueError("No source files specified")
        
        if 'name' not in self.config['output']:
            raise ValueError("No output name specified")

class BindBuilder:
    def __init__(self, config):
        self.config = config
        self.obj_files = []
    
    def get_compiler(self, source_file):
        """Determine compiler based on file extension"""
        ext = Path(source_file).suffix.lower()
        
        if ext in ['.cpp', '.cc', '.cxx', '.c++']:
            compiler = self.config['compiler'].get('cpp_compiler')
            if not compiler:
                compiler = 'g++'
            return compiler
        elif ext == '.c':
            compiler = self.config['compiler'].get('c_compiler')
            if not compiler:
                compiler = 'gcc'
            return compiler
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    
    def compile_source(self, source_file):
        """Compile a single source file"""
        #check if the file exist or not 
        if not os.path.exists(source_file):
            print(f"Error: Source file '{source_file}' not found")
            return None
        
        compiler = self.get_compiler(source_file)
        flags = self.config['compiler'].get('flags', '')
        
        #grab all the include paths because headers are everywhere apparently
        include_dirs = self.config['sources'].get('include_dirs', [])
        if isinstance(include_dirs, str):
            include_dirs = [include_dirs]
        
        include_flags = ' '.join([f'-I{d}' for d in include_dirs])
        
        #to dump our object files
        output_dir = self.config['output'].get('directory', './build')
        os.makedirs(output_dir, exist_ok=True)
        
        obj_file = Path(output_dir) / (Path(source_file).stem + '.o')
        
        #let's compile this bad boy
        cmd = f"{compiler} {flags} {include_flags} -c {source_file} -o {obj_file}"
        
        print(f"Compiling: {source_file}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Error compiling {source_file}:")
            print(result.stderr)
            return None
        
        print(f"  ✓ {obj_file}")
        return str(obj_file)
    
    def link(self):
        """Link object files"""
        #do we need C++ linker or not,,,,,  we probably do!
        sources = self.config['sources']['files']
        if isinstance(sources, str):
            sources = [sources]
        
        has_cpp = any(Path(s).suffix.lower() in ['.cpp', '.cc', '.cxx', '.c++'] for s in sources)
        
        if has_cpp:
            linker = self.config['compiler'].get('cpp_compiler', 'g++')
        else:
            linker = self.config['compiler'].get('c_compiler', 'gcc')
        
        output_name = self.config['output']['name']
        output_dir = self.config['output'].get('directory', './build')
        project_type = self.config['project']['type']
        
        print(f"\nLinking... (this is where dreams come true or segfaults happen)")
        
        if project_type == 'library':
            #making a library - basically fancy object file collection
            output_file = Path(output_dir) / f"lib{output_name}.a"
            cmd = f"ar rcs {output_file} {' '.join(self.obj_files)}"
        else:
            #making an executable
            output_file = Path(output_dir) / output_name
            
            #collect all the libraries we're borrowing from
            libraries = self.config['linking'].get('libraries', [])
            if isinstance(libraries, str):
                libraries = [libraries]
            lib_flags = ' '.join([f'-l{lib}' for lib in libraries if lib])
            
            #here are those libraries hiding?
            lib_dirs = self.config['linking'].get('lib_dirs', [])
            if isinstance(lib_dirs, str):
                lib_dirs = [lib_dirs]
            lib_dir_flags = ' '.join([f'-L{d}' for d in lib_dirs if d])
            
            cmd = f"{linker} {' '.join(self.obj_files)} -o {output_file} {lib_dir_flags} {lib_flags}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Error linking:")
            print(result.stderr)
            return False
        
        print(f"  ✓ {output_file}")
        print(f"\n✓ Build successful!")
        return True
    
    def build(self):
        """Execute build"""
        print(f"Building: {self.config['project']['name']}")
        print(f"Type: {self.config['project']['type']}\n")
        
        sources = self.config['sources']['files']
        if isinstance(sources, str):
            sources = [sources]
        
        for source in sources:
            obj_file = self.compile_source(source)
            if obj_file:
                self.obj_files.append(obj_file)
            else:
                print("\n✗ Build failed")
                return False
        
        return self.link()

def create_new(name):
    """Create a new .st file"""
    filename = f"{name}.st"
    
    #already exists? shit!!
    if os.path.exists(filename):
        print(f"Error: '{filename}' already exists")
        return False
    
    content = TEMPLATE.format(name=name)
    
    #yeeeeeeeeet the template into a file
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✓ Created '{filename}' (now go fill it out, you got this)")
    print(f"\nEdit the file to configure your build, then run:")
    print(f"  bind {name}")
    return True

def build_project(name):
    """Build a project"""
    filename = f"{name}.st"
    
    #file not found
    if not os.path.exists(filename):
        print(f"Error: '{filename}' not found")
        print(f"\nCreate it first with:")
        print(f"  bind new {name}")
        return False
    
    try:
        #phrase things
        parser = BindParser(filename)
        config = parser.parse()
        parser.validate()
        
        #let's build this sucker
        builder = BindBuilder(config)
        return builder.build()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("(something went horribly wrong)")
        return False

def clean_project(name):
    """Clean build artifacts"""
    filename = f"{name}.st"
    
    if not os.path.exists(filename):
        print(f"Error: '{filename}' not found")
        return False
    
    try:
        parser = BindParser(filename)
        config = parser.parse()
        
        output_dir = config['output'].get('directory', './build')
        
        #nuclear option----> delete everything
        if os.path.exists(output_dir):
            import shutil
            shutil.rmtree(output_dir)
            print(f"✓ Cleaned '{output_dir}' (wiped it off the face of the earth)")
        else:
            print(f"Nothing to clean (it's already spotless)")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        print("(couldn't clean, files are probably cursed)")
        return False

def show_help():
    """Show help message"""
    print("""
Bind - Simple C/C++ Build Tool

Usage:
    bind new <name>      Create a new .st build file
    bind <name>          Build project using <name>.st
    bind clean <name>    Clean build artifacts
    bind help            Show this help message

Examples:
    bind new build       Creates build.st
    bind build           Builds project using build.st
    bind clean build     Removes build directory

File Format (.st):
    [project]
    name = MyProject
    type = executable

    [output]
    name = my_program
    directory = ./build

    [compiler]
    c_compiler = gcc
    cpp_compiler = g++
    flags = -Wall -O2 -mconsole

    [sources]
    files = main.cpp, utils.c
    include_dirs = ./include

    [linking]
    libraries = m, pthread
    lib_dirs = /usr/local/lib
    """)

def main():
    if len(sys.argv) < 2:
        print("Usage: bind <command> [args]")
        print("Run 'bind help' for more information")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "help":
        show_help()
        sys.exit(0)
    
    elif command == "new":
        if len(sys.argv) < 3:
            print("Error: Missing name")
            print("Usage: bind new <name>")
            sys.exit(1)
        
        name = sys.argv[2]
        success = create_new(name)
        sys.exit(0 if success else 1)
    
    elif command == "clean":
        if len(sys.argv) < 3:
            print("Error: Missing name")
            print("Usage: bind clean <name>")
            sys.exit(1)
        
        name = sys.argv[2]
        success = clean_project(name)
        sys.exit(0 if success else 1)
    
    else:
        #assume it's a build command
        name = command
        success = build_project(name)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()