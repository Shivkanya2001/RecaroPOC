# RecaroPOC

RecaroPOC

Preferenece command

python .\\prefrencesDeploymentScript.py preferences_manager.exe -u infodba -g dba -scope SITE -mode import -action OVERRIDE -pf "config1_infodba.pwf" --xml-files "preferences_override.xml" "preferences_2.xml" --folder C:\RecaroPythonProject\RecaroPOC\preferences

stylesheet command

python .\stylesheet.py -target-path "C:\RecaroPythonProject\RecaroPOC\stylesheet" -pwf-file "config1_infodba.pwf" -install-user "infodba" -install-group "dba" -tc-bat "D:\apps\siemens\tc_root\tc_menu\tc_DEVBOX.bat"

AWS Bulid
python .\awcDeploymentScript.py -target_path "C:\Users\infodba\Downloads\stage\stage" -tc_bat "D:\apps\siemens\tc_root\tc_menu\tc_DEVBOX.bat"

BMIDE Package generate

bmide_generate_package
-projectLocation="D:\apps\siemens\tc_root\bmide\workspace\t5recaro"
-packageLocation=D:\apps\siemens\tc_root\bmide\workspace\t5recaro\output
-dependencyTemplateFolder=D:\apps\siemens\tc_data\model
-codeGenerationFolder="D:\apps\siemens\tc_root\bmide\workspace\t5recaro\output\wntx64"
-softwareVersion=2412
-buildVersion=1
-allPlatform
-log=test.log

scipt for generate package

python .\Bmide_generate_package.py bmide_generate_package -tc_bat "D:\apps\siemens\tc_root\tc_menu\tc_DEVBOX.bat" -workspace_folder_name t5recaro -softwareVersion 2412 -buildVersion 1 -allPlatform

Bmide deploy using tem.bat

"D:\apps\siemens\tc_root\install\tem.bat" -update -templates=t5recaro -full -pf="D:\apps\siemens\tc_root\security\config1_infodba.pwf" -verbose -path="D:\apps\siemens\tc_root\bmide\workspace\t5recaro\output\wntx64\packaging\full_update\t5recaro_wntx64_1.0_2412_2025_07_15_10-17-52" -fullkit="D:\tc2412_wntx64

python .\Bmide_generate_deploy.py -tc_bat "D:\apps\siemens\tc_root\tc_menu\tc_DEVBOX.bat" -template "b2testpoc" -pf_file "config1_infodba.pwf" -version "1.0_2412" -fullkit_path "D:\tc2412_wntx64" --path "D:\apps\siemens\tc_root\bmide\workspace\b2testpoc\output\wntx64\packaging\full_update\b2testpoc_wntx64_1.0_1_2412_2025_07_15_13-50-30"

---

itk

D:\apps\siemens\tc_root\tc_menu>C:\Users\infodba\source\repos\ConsoleApplication1\x64\Release\ConsoleApplication1.exe
Login successful

D:\apps\siemens\tc_root\tc_menu>
