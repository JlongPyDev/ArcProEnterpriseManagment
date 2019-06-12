import arcpy, os
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
print("INITIALIZING SCRIPT EXECUTION")

arcpy.env.overwriteOutput=1

#port = 'https://www.arcgis.com'
port = arcpy.GetParameterAsText(0)
#user = 'mgriffin_apexnc'
user = arcpy.GetParameterAsText(1)
#passw = 'Apex2019'
passw = arcpy.GetParameterAsText(2)


arcpy.SignInToPortal(port, user, passw)
gis = GIS(port, user, passw)

open_data = gis.groups.search('title:Apex Open Data')
group = open_data[0]


direct = arcpy.GetParameterAsText(3)
#direct = r"C:\Users\Jlong\Documents\ArcGIS\Projects\PublishAGOLdata"
mapdoc = arcpy.GetParameterAsText(4)
#mapdoc = r"C:\Users\Jlong\Documents\ArcGIS\Projects/PublishAGOLdata/PublishAGOLdata.aprx"

agol_serv_con = 'My Hosted Services'
aprx = arcpy.mp.ArcGISProject(mapdoc)

'''
data_items = Dictionary of items to be published, dictionary value[0] is the name of the map in ArcGIS Pro and will
be used as a tag for the new feature layer. This tag will also be used to categorize the data for the open data site.
Value[1] will be the service definition name. Value[2] is the name of the new hosted feature layer or the 
feature layer already in AGOL to be overwritten.
'''

data_items = {'Planning': ['PL', 'PLServiceDef', 'PlanBounds1'], 'Parks': ['PR','PRServiceDef','ParksAndRecreationData1'],
              'Electric': ['EL', 'ELServiceDef', 'ElectricData']}

# look for data items already in AGOL and create a list to test
existing_maps = []

for t in data_items.values():
    result = gis.content.search(query='title: {}'.format(t[2]), item_type='Feature Layer')
    if len(result) > 0:
        item = result[0]
        item_title = item.title
        existing_maps.append(item_title)


def create_service_definition(sname, mpname, weblyrname):
    global outServiceDefinition
    outServiceDefinition = os.path.join(direct, "{}.sd".format(sname))

    sddraft_output_filename = os.path.join(direct, "{}.sddraft".format(sname))
    mplyrs = aprx.listMaps(mpname)[0]
    print("Service definition for {} created.".format(weblyrname))

    # Create FeatureSharingDraft and set service properties
    sharing_draft = mplyrs.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", weblyrname)
    sharing_draft.tags = mpname
    sharing_draft.allowExporting = True
    sharing_draft.portalFolder = 'HubContent'

    # Create Service Definition Draft file
    sharing_draft.exportToSDDraft(sddraft_output_filename)

    arcpy.StageService_server(sddraft_output_filename, outServiceDefinition)


def overwrite_service(weblyrname, service_def):
    item1 = gis.content.search('title: {}'.format(weblyrname))
    web_item = item1[0]
    update_FLcollection = FeatureLayerCollection.fromitem(web_item)

    print("Overwriting {}".format(weblyrname))
    update_FLcollection.manager.overwrite(service_def)


def new_service(sname, mpname, weblyrname):
    # upload service definition, sharing set to everyone
    print("Uploading {} Services to AGOL.".format(sname))
    arcpy.UploadServiceDefinition_server(outServiceDefinition, agol_serv_con, in_override=1,
                                         in_public=True, in_organization=True)

    print("-------Web Service Successfully Published--------", "Adding new services to Open Data Group.\n")

    # use GIS module to add new services to Open Data folder
    new_data = gis.content.search(query="tags:{}".format(mpname), item_type='Feature Layer')
    l = len(new_data)
    for x in range(0, 1):
        data = new_data[x]
        data.share(groups=group.groupid)

    print("{} Services added to Open Data Group".format(weblyrname))


def mark_authoritative(layername):
    ma_item = gis.content.search(query='title: {}'.format(layername), item_type='Feature Layer')
    ma_item_id = ma_item[0]
    ma_result = ma_item_id.id
    id_result = gis.content.get(ma_result)
    id_result.content_status='authoritative'
    print('{} marked as authoritative!\n'.format(layername))


def check_authoritative(layername):
    ma_item = gis.content.search(query='title: {}'.format(layername), item_type='Feature Layer')
    ma_item_id = ma_item[0]
    ma_result = ma_item_id.id
    id_result = gis.content.get(ma_result)
    global stat
    stat = id_result.content_status

# test to see if map is existing, then create service definition and publish appropriately

for map in data_items.values():

    res = any(ele in map[2] for ele in existing_maps)

    if res:
        check_authoritative(map[2])
        if stat == 'org_authoritative':
            ans = input(
                '{} map is an already an authoritative dataset in AGOL. Are you sure you want to overwrite? (y/n)'.format(map[2]))
            if ans == "y":
                create_service_definition(sname=map[1], mpname=map[0], weblyrname=map[2])
                overwrite_service(weblyrname=map[2], service_def=outServiceDefinition)
            else:
                print('{} will be skipped.\n'.format(map[2]))
        else:
            ans = input(
                '{} map is already in AGOL. Do you want to overwrite? (y/n)'.format(map[2]))
            if ans == "y":
                create_service_definition(sname=map[1], mpname=map[0], weblyrname=map[2])
                overwrite_service(weblyrname=map[2], service_def=outServiceDefinition)
                ans1 = input('Would you like to mark {} as authoritative? (y/n)'.format(map[2]))
                if ans1 == "y":
                    mark_authoritative(layername=map[2])
            else:
                print('{} will be skipped.\n'.format(map[2]))

    else:
        print('{} map is not in AGOL and will be published now.'.format(map[2]))
        create_service_definition(sname=map[1], mpname=map[0], weblyrname=map[2])
        new_service(sname=map[1], mpname=map[0], weblyrname=map[2])
        ans2 = input('Would you like to mark {} as authoritative? (y/n)'.format(map[2]))
        if ans2 == "y":
            mark_authoritative(layername=map[2])





