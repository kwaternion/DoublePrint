import traceback
import sys
import datetime as dtime
import os

from IPython import get_ipython
from IPython.core import magic_arguments
from IPython.core.magic import line_magic, cell_magic, line_cell_magic, Magics, magics_class
# https://subscription.packtpub.com/book/big_data_and_business_intelligence/9781785888632/1/ch01lvl1sec14/creating-an-ipython-extension-with-custom-magic-commands
# Context manager that copies stdout and any exceptions to a log file
class DoublePrint(object):
    """Context Manager used to save output to sdtout and file.
    Usage: 
    with DoublePrint(filepath):
        print("Print stdout + Write to file")
    print("Print to stdout")
    
    """ 
    def __init__(self, filepath=None):  
        if filepath == None:
            cwd = os.getcwd()
            d = dtime.datetime.today()
            filepath = d.strftime(cwd +"/%Y-%M-%d_%H-%M-%S-%m_log.txt")          
        print("Saving logs to file:", filepath)
        self.stdout = sys.stdout
        self.filepath = filepath
        base_dir = os.path.dirname(self.filepath)
        if base_dir in [".", ""]:
            pass
        else:
            try:
                os.mkdir(base_dir)
            except: pass
        self.file = open(self.filepath, 'w')
    
    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = self.stdout
        if exc_type is not None:
            self.file.write(traceback.format_exc())
        self.file.close()

    def write(self, data):
        self.stdout.write(data)
        if data.strip() != "":
            self.file.write(self.stamp() + data[:1000] + "\n")
            self.file.flush()

    def flush(self):
        pass
    
    def stamp(self):
        d = dtime.datetime.today()
        string = d.strftime("[%Y-%M-%d %H:%M:%S] ")
        return string

@magics_class
class MagicDoublePrint(Magics):
    
    @line_cell_magic
    def doubleprint(self, line, cell=None):
        """Magic function used to stream output of std.out to log file.
        This magic can be used as line_magic or cell_magic.
        In case of cell magic, an additional parameter defining log file path can be passed.
        As a parameter path str or variable (pointing at string path) can be used.
        Otherwise file (with current timestamp name) in the current directory will be created.
        This function is especially useful, when performing long calculations on Jupyter notebook.
        Often connection is close, and regular output is lost. In that case doubleprint allows to 
        check current status of the output by reading content of the log file.
        Usage:
        %%doubleprint "myLogFile.txt"
        print("log printed to stdout and to myLogFile.txt")

        Importing as a module:
        from modules.doubleprint import MagicDoublePrint
        ipy = get_ipython()
        ipy.register_magics(MagicDoublePrint)
        """
        if cell is None:
            with DoublePrint():
                self.shell.run_cell(line)
        else:
            line = line.strip()
            if len(line):
                if (line[0] in ["'", '"']) and (line[-1] in ["'", '"']):
                    filepath = line[1:-1]
                elif line in self.shell.user_ns.keys():
                    filepath = self.shell.user_ns[line]
                else: filepath = None 
            else: 
                filepath = None        
            with DoublePrint(filepath):
                self.shell.run_cell(cell)
                
ipy = get_ipython()
ipy.register_magics(MagicDoublePrint)
