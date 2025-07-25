#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <tc/tc_startup.h>
#include <tcinit/tcinit.h>
#include <tc/emh.h>

#include<tccore/aom.h>
#include<tccore/aom_prop.h>
#include<ae/ae.h>
#include<tccore/grm.h>

using namespace std;

int isUnique();
int findDataset();

#define CHECK_ITK_STATUS(status) \
if (status != ITK_ok) { \
char* message = nullptr; \
EMH_ask_error_text(status, &message); \
cout<< "Error:"<< message<< endl; \
if (message != nullptr) MEM_free(message); \
return status; \
}

int isUnique()
{
int status = ITK_ok;
char* message = NULL;

//UniqueTestDT - 2Dtatastes
//TestDataset - 1 dataset
logical isunique;
status = AE_is_dataset_unique2("TestDataset", &isunique);

if (isunique) {
tag_t dataset;
status = AE_find_dataset2("TestDataset", &dataset);
char* value;
status = AOM_ask_value_string(dataset, "object_name", &value);
cout << value;
}
return status;
}
int findDataset()
{
int status = ITK_ok;
char* message = NULL;

// UniqueTestDT - 2Dtatastes
// TestDataset - 1 dataset
tag_t dataset = NULLTAG;
char* value = NULL;

// Find the dataset
status = AE_find_dataset2("TestDataset", &dataset);
if (status != ITK_ok || dataset == NULLTAG) {
cerr << "Failed to find dataset. Status: " << status << endl;
return status;
}

// Get the object name
status = AOM_ask_value_string(dataset, "object_name", &value);
if (status == ITK_ok && value != NULL) {
cout << "Object Name: " << value << endl;
MEM_free(value); // Free the allocated string
}
else {
cerr << "Failed to get object_name. Status: " << status << endl;
return status;
}

/* Uncomment and use the below code if needed
char* desvalue = NULL;
status = AOM_ask_value_string(dataset, "object_desc", &desvalue);
if (status == ITK_ok && desvalue != NULL) {
cout << "Object Description: " << desvalue << endl;
MEM_free(desvalue); // Free the allocated string
} else {
cerr << "Failed to get object_desc. Status: " << status << endl;
}
*/

return ITK_ok;
}
int main(int argc, char* argv[])
{
int iFail = 0;
char* message = NULL;
iFail = ITK_init_module("infodba", "infodba", "dba");
if (iFail == ITK_ok)
{
cout << "Login successful" << endl;

//findDataset();
}
else
{
EMH_ask_error_text(iFail, &message);
cout << "The error is :" << message << endl;
}
return iFail;
}