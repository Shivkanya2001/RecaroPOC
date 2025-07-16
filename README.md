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



Bmide deploy using tem.bat
 
"D:\apps\siemens\tc_root\install\tem.bat" -update -templates=t5recaro -full -pf="D:\apps\siemens\tc_root\security\config1_infodba.pwf" -verbose -path="D:\apps\siemens\tc_root\bmide\workspace\t5recaro\output\wntx64\packaging\full_update\t5recaro_wntx64_1.0_2412_2025_07_15_10-17-52" -fullkit="D:\tc2412_wntx64
