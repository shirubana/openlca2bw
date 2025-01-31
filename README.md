## OLCA2BW package

This is a Python package to import OpenLCA database to the brightway python environment

To install:
Direct from github

> pip install git+https://github.com/cyrillefrancois/openlca2bw

If folder downloaded 

> pip install path_to_setup_folder

for exemple C:/user/userprofile/document/openlca2bw

the main functions to import olca database to brightway are load_openLCA_IPC() (to import from IPC protocol) or load_openLCA_Json() (to import from a .zip json extraction)

## IPC protocol importation

The IPC connection is made by the OpenLCA software and allows ather software to access the database.
To import with IPC protocol, you need to lauch OpenLCA, to open your database and activate the IPC protocol from the OpenLCA software (Tool/Developer tools/IPC server)
The default port value is 8080

The load_openLCA_IPC() function has default values and can be run without entries, nontheless all processes will be stored in one unique bw2 database ('EcoInvent').
To split OpenLCA into several database you need to specify the databases you want to create and the OpenLCA folders related.
The format of "user_databases" entry is a dictionnary :

> user_databases = {'FirstDatabase': ['Folder1','Folder2',...],'SecondDatabase': 'Folder3','ThirdDatabase': List or single name}

With this example you will three databases in brightway that contains the processes contain in the specified folders.

Others options are available in this function:
- port: integer -> to specified the IPC port value if it is different than 8080
- project_name: string -> the name of the brightway project that will contain your openlca database
- overwrite: boolean -> True to overwrite an existing brightway project with the same name
- nonuser_db_name: string -> the name of the brightway database that will contain the nonuser database (processes that are not specified in the user_databases folders)
- check_nonuser_exc: boolean -> if True the program will check if all nonuser processes' exchanges have correct connexion, especially regarding unit conversion
- user_databases: dictionnary -> a dictionnary with keys representing the brightway databases names and the values for each key representing the list of openLCA folders related
- excluded_folders: list -> a list of openLCA folders names that will not be imported
- exclude_S: boolean -> if True the program will not import nonuser processes that are System process (LCI) if a corresponding Unit process is available, the importation of a full System process databse is long (3 hours for EcoInvent) 
- selected_methods: list or all -> a list of LCIA methods in OpenLCA that will be imported. The default value is 'all' to import all methods present, an empty list not will import any method

> load_openLCA_IPC(port = 8080, project_name="Open_imports",overwrite=False, 
>                     nonuser_db_name = 'EcoInvent',check_nonuser_exc=False,
>                     user_databases={},excluded_folders=[], exclude_S=False, selected_methods= all)
                     
example to run function:
> import openlca2bw
>
> my_dict = {'FirstDatabase': ['Folder1','Folder2'],'SecondDatabase': 'Folder3'}
>
> #after activating IPC server from OpenLCA
>
> load_openLCA_IPC(project_name="Example_Name",user_databases=my_dict)
                     
The update_openLCA_IPC() function only import specified elements to an existing brightway project.
The update_databases dictionnary allows the user to specified the brightway databases that will be replaced.
It seems complicated to only import modification, so the program delete the previous database and load the new one with specified openLCA folders.

> update_openLCA_IPC(port = 8080, project_name="Open_imports",update_biosphere=False,update_methods=[],
>                     update_databases={}, exclude_S=False)

- port: integer -> to specified the IPC port value if it is different than 8080
- project_name: string -> the name of the brightway project that will be updated
- update_biosphere: boolean -> if True the program import all elementary flows and replace the existing 'biosphere3' database in brightway
- update_methods: list -> indicate in a list LCIA methods to be imported or updated. To import no method specify an empty list.The program will import LCIA methods and write the new methods or replace old ones if some differents are presents
- update_databases: dictionnary -> a dictionnary with keys representing the brightway databases names and the values for each key representing the list of openLCA folders related (see previous user_databases format)
- exclude_S: boolean -> if True the program will not import nonuser processes that are System process (LCI) if a corresponding Unit process is available, the importation of a full System process databse is long (3 hours for EcoInvent) 

## JSON files importation

The JSON format is a commun format for same database and OpenLCA allows the exportation of database in this format (JSON-LD).
Compare the the IPC protocol, the JSON importation require export from OpenLCA that add significantly more time than IPC connexion, but JSON zip file can be send to others users.

The load_openLCA_Json() function work similarly than load_openLCA_IPC but the path to the zip file containing all JSON file need to be specified (path_zip)
To create a all new brightway project you need to export from OpenLCA all the flows, the processes, the LCIA methods and properties (unit, flows properties and locations)

Others options are available in this function:
- path_zip: string -> the complete path to your zip file or to the directory with all extrated folders. 
- project_name: string -> the name of the brightway project that will contain your openlca database
- overwrite: boolean -> True to overwrite an existing brightway project with the same name
- nonuser_db_name: string -> the name of the brightway database that will contain the nonuser database (processes that are not specified in the user_databases folders)
- check_nonuser_exc: boolean -> if True the program will check if all nonuser processes' exchanges have correct connexion, especially regarding unit conversion
- user_databases: dictionnary -> a dictionnary with keys representing the brightway databases names and the values for each key representing the list of openLCA folders related
- excluded_folders: list -> a list of openLCA folders names that will not be imported
- exclude_S: boolean -> if True the program will not import nonuser processes that are System process (LCI) if a corresponding Unit process is available, the importation of a full System process databse is long (3 hours for EcoInvent) 
- selected_methods: list or all -> a list of LCIA methods in OpenLCA that will be imported. The default value is 'all' to import all methods present, an empty list not will import any method

>load_openLCA_Json(path_zip=str, project_name="Open_imports",overwrite=False, 
>                     nonuser_db_name = 'EcoInvent',check_nonuser_exc=False,
>                     user_databases={},excluded_folders=[], exclude_S=False, selected_methods = all) 

example to run function:
> import openlca2bw
>
> my_dict = {'FirstDatabase': ['Folder1','Folder2'],'SecondDatabase': 'Folder3'}
>
> #after exporting json zip from OpenLCA
>
> load_openLCA_Json(path_zip=r'C:\user\userprofile\document\olcaJSON.zip',user_databases=my_dict)

The update_openLCA_Json() function only import specified elements to an existing brightway project.
The update_databases dictionnary allows the user to specified the brightway databases that will be replaced.
It seems complicated to only import modification, so the program delete the previous database and load the new one with specified openLCA folders.
With this function no need to export the all database from OpenLCA, only modified element con be exported

> update_openLCA_Json(path_zip=str, project_name="Open_imports",update_biosphere=False,update_methods=[],
>                     update_databases={}, exclude_S=False)

- path_zip: string -> the complete path to your zip file
- project_name: string -> the name of the brightway project that will be updated
- update_biosphere: boolean -> if True the program import all elementary flows and replace the existing 'biosphere3' database in brightway
- update_methods: list -> indicate in a list LCIA methods to be imported or updated. To import no method specify an empty list.The program will import LCIA methods and write the new methods or replace old ones if some differents are presents
- update_databases: dictionnary -> a dictionnary with keys representing the brightway databases names and the values for each key representing the list of openLCA folders related (see previous user_databases format)
- exclude_S: boolean -> if True the program will not import nonuser processes that are System process (LCI) if a corresponding Unit process is available, the importation of a full System process databse is long (3 hours for EcoInvent) 


OpenLCA has many specificities and this package may not handle all of them.
For instance, a technological exchange without a specified provider that can be satisfy by several activities is deleted frmo the activity (a single provider is retrieve). LCA model in OpenLCA need to be completly defined. 

                 
OpenLCA database has many exceptions and depending on your database some errors may araise. Feel free to share issues and potential correction.

Next steps for this package :
- Apply allocation factors when importing
- Write processes and data from brightway2 to OpenLCA
- Errors and exceptions corrections
- Computing and coding optimization