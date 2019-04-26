import arcpy, os, getpass, timeit, sys, json
#print sys.executable
print("INITIALIZING SCRIPT EXECUTION FROM BAT")
# USER MUST HAVE ARC PRO OPENED AND BE LOGGED INTO PORTAL
start = timeit.default_timer()

username = getpass.getuser()
print(username)
dir = r'C:\Users\{}\AppData\Roaming\ESRI\ArcGISPro\Favorites'.format(username)
arcpy.env.workspace = r'C:\Users\{}\AppData\Roaming\ESRI\ArcGISPro\Favorites'.format(username)

sde_dbs = ["APEXPR", "APEXWCD", "APEXPL", "APEXFD",
           "APEXEL", "APEXWR", "APEXPWT", "APEXFN", "APEXPD"]

sde_direct = r'C:\Users\{}\AppData\Roaming\ESRI\ArcGISPro\Favorites'.format(username)

workspaces = [os.path.splitext(os.path.basename(sdedb))[0] for sdedb in arcpy.ListWorkspaces("*", "SDE")]

# create dict for favorites then check for existing favs and add to dict if necessary
favs = {}
favs['Items'] = []
files = os.listdir(dir)

if 'Favorites.json' in files:
    with open(dir + "\Favorites.json", "r") as json_file:
        data = json.load(json_file)
        for p in data['Items']:
            favs['Items'].append(p)
        json_file.close()

for e,db in enumerate(sde_dbs):
    cred = db.split('APEX')[1]

    if db+"Viewer" in workspaces:
        print("SDE DATABASE CONNECTION FOR -->{}<-- ALREADY ESTABLISHED".format(db),"\n")
        continue
    else:
        print("Making db connection to --{}--".format(db), "\n")
        un, pw = login_cred = cred+"Viewer", cred+"Viewer123"
        dbv = db + 'Viewer.sde'
        arcpy.CreateDatabaseConnection_management(sde_direct,
                                                  dbv,
                                                  "SQL_SERVER",
                                                  "APEXGIS",
                                                  "DATABASE_AUTH",
                                                  un,
                                                  pw,
                                                  "SAVE_USERNAME")
        favs['Items'].append({"TypeId": "database_egdb",
                              "Path": "C:\\Users\\{0}\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\{1}".format(username, dbv),
                              "Id": "", "url": "", "name": "{0}".format(dbv),
                              "persistFavorite": "false"})

with open(dir + "\Favorites.json", "w") as write_file:
    json.dump(favs, write_file)

write_file.close()

stop = timeit.default_timer()
total_time = stop - start

# output running time in a nice format.
mins, secs = divmod(total_time, 60)
hours, mins = divmod(mins, 60)

sys.stdout.write("Total running time: %d:%d:%d\n" % (hours, mins, secs))

print("Script Has Successfully Executed --- All town SDE database connections have been established in ArcGIS Pro Favorites folder.")










