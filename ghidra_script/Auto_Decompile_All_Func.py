#@author WuLearn
# Automatically decompile all functions.
#@category Analysis
#@keybinding 
#@menupath 
#@toolbar 

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os

wufuzz_path = '/home/wulearn/Desktop/Cheng-fuzz'# Cheng-fuzz path

base_folder_path = '/home/wulearn/Desktop/wufuzztmp' # same as $pwd/Cheng-fuzz/config/wufuzz.cfg base_folder_path


program = getCurrentProgram()

path = base_folder_path + '/' + 'out_decompiler_' + str(program)[0:str(program).find(' ')].replace('.' ,'_') + '.txt'
f = open(path,'w')

ifc = DecompInterface()
ifc.openProgram(program)

func = getFirstFunction()
while func is not None:
	try:
		function = getGlobalFunctions(func.getName())[0]

		# decompile the function and print the pseudo C
		results = ifc.decompileFunction(function, 0, ConsoleTaskMonitor())
		print(results.getDecompiledFunction().getC())
		f.write(results.getDecompiledFunction().getC())
	except:
		print("Can't decompler! FUNC NAME:"+func.getName())
	func = getFunctionAfter(func)
f.close()

xml_file_name = 'parse_out_decompiler_hedwig_cgi.xml' # same as $pwd/Cheng-fuzz/config/wufuzz.cfg xml_file_name
os.system("python3 " + wufuzz_path + "/parse_txt.py" + " -i "+ path + " -o " + base_folder_path)
