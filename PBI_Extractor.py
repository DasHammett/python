import glob
import os
import shutil

#mypath = "C:\\Users\\Jordi\\Roca Group\\IT - Business Analytics Team - Documents\\11- PBI Reports\\"
mypath = r"\\tsclient\Multimedia\PBIX"

files = glob.glob(mypath + '/**/*.pbix', recursive=True)
#[print(x) for x in files]

pbix_tool_path = r"C:\Users\Jordi\Downloads\pbi-tools.1.0.0-rc.4\pbi-tools.exe"
destination_folder = r"C:\Users\Jordi\Desktop\Metadata"
script_location = r"C:\Users\Jordi\Desktop\Metadata\MetadataExport.cs"

for i in files:
    pbix_folder = i.split("\\")[-1].split(".")[0]
    dest_dir = f"{destination_folder}\\{pbix_folder}"
    
    print(f"Extracting database.json for {pbix_folder}")
    os.system(f"{pbix_tool_path} extract \"{i}\" -modelSerialization Raw -extractFolder \"{dest_dir}\" > NUL 2>&1")
    
    # Remove all files and directories we do not need
    for root, dirs, files in os.walk(dest_dir,topdown = False):
        for file in files:
            file_path = os.path.join(root,file)
            if not file_path.endswith("database.json"):
                 os.remove(file_path)
        for directory in dirs:
            dir_path = os.path.join(root,directory)
            if not dir_path.endswith("Model"):
                shutil.rmtree(dir_path)

    print(f"Extracting metadata for {pbix_folder}")            
    os.system(f"start /wait /d \"C:\\Program Files (x86)\\Tabular Editor\" TabularEditor.exe \"{dest_dir}\\Model\database.json\" -S {destination_folder}\\MetadataExport.cs")
   # os.remove(i)
print("Done")
