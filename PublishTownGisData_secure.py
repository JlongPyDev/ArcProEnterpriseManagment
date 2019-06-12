import arcpy, os
print ("INITIALIZING SCRIPT EXECUTION")

arcpy.env.overwriteOutput= 1

arcpy.SignInToPortal('https://www.arcgis.com', '#', '#')

direct = r"C:\Users\Jlong\Documents\ArcGIS\Projects\PublishDataAGOL"
mapdoc = r"C:\Users\Jlong\Documents\ArcGIS\Projects\PublishDataAGOL/PublishDataAGOL.aprx"


def create_service_definition(map_proj,sname,mpname,proj_dir,weblyrname):
    agol_serv_con = 'My Hosted Services'
    aprx = arcpy.mp.ArcGISProject(map_proj)
    outServiceDefinition = os.path.join(proj_dir,"{}.sd".format(sname))

    sddraft_output_filename = os.path.join(proj_dir,"{}.sddraft".format(sname))
    mplyrs = aprx.listMaps(mpname)[0]
    print (mplyrs)
    arcpy.mp.CreateWebLayerSDDraft(mplyrs, sddraft_output_filename, weblyrname, 'MY_HOSTED_SERVICES',
                                   'FEATURE_ACCESS', overwrite_existing_service=1)

    arcpy.StageService_server(sddraft_output_filename, outServiceDefinition)

    print("Uploading {} Services to AGOL".format(sname))
    arcpy.UploadServiceDefinition_server(outServiceDefinition, agol_serv_con, in_override=1, in_public=0,
                                         in_organization=1,
                                         in_groups=["Town of Apex Authoritative GIS Data"])
    print ("-------Web Service Succesfully Published--------")


create_service_definition(map_proj=mapdoc, sname="PLServiceDef",mpname="PL", proj_dir=direct,
                          weblyrname="PlanningBounds")

#create_service_definition(map_proj=mapdoc, sname="WCDServiceDef",mpname="WCD", proj_dir=direct,
 #                         weblyrname="ApexNetworks")

create_service_definition(map_proj=mapdoc, sname="WRServiceDef",mpname="WR", proj_dir=direct,
                          weblyrname="WaterUtilityData")

create_service_definition(map_proj=mapdoc, sname="ELServiceDef",mpname="EL", proj_dir=direct,
                          weblyrname="ElectricUtilityData")

create_service_definition(map_proj=mapdoc, sname="PRServiceDef",mpname="PR", proj_dir=direct,
                          weblyrname="ParksAndRecreationData")


