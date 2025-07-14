# RecaroPOC

RecaroPOC

Preferenece command

python .\\prefrencesDeploymentScript.py preferences_manager.exe -u infodba -g dba -scope SITE -mode import -action OVERRIDE -pf "config1_infodba.pwf" --xml-files "preferences_override.xml" "preferences_2.xml" --folder C:\RecaroPythonProject\RecaroPOC\preferences

stylesheet command

python .\stylesheet.py -target-path "C:\RecaroPythonProject\RecaroPOC\stylesheet" -pwf-file "config1_infodba.pwf" -install-user "infodba" -install-group "dba" -tc-bat "D:\apps\siemens\tc_root\tc_menu\tc_DEVBOX.bat"
