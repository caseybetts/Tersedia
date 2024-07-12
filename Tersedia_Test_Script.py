# Author: Casey Betts, 2024
# This file contains the function for isolating the available orders on a given rev

import arcpy

# Find applicable spacecraft
def onv_dict(all_onvs):
    """ Returns a dictionary with spacecraft as keys and onv files as values """

    onv_dict = dict()

    for onv in all_onvs:

        try:

            with arcpy.da.SearchCursor(onv, "sensor") as cursor:
                
                for row in cursor:
                    if len(row) != 1:
                        arcpy.AddMessage("The onv file does not contain exactly one spacecraft")
                    else:
                        onv_dict[str(row[0]).lower()] = onv 
        except:
            
            pass

    return onv_dict
            
# Create feature class of available orders
def available_orders(prod, all_onvs):
    """ Select orders accessable on a given rev based on the order's max ONA vlaue """

    arcpy.AddMessage("Running available_orders.....")

    # Definition query values
    ona_values = [35, 30, 25, 20, 15]
    order_file_names = []

    for spacecraft in all_onvs:

        # Export the onv as a new feature class
        # arcpy.conversion.ExportFeatures(all_onvs[spacecraft], "Tersedia_" + spacecraft + "_ONV")

        # Select orders intersecting the 45deg segments of the rev (max selection)
        arcpy.management.SelectLayerByLocation(prod, "INTERSECT", all_onvs[spacecraft], None, "NEW_SELECTION")

        # Select only the orders that are avaialble based on their max ONA value    
        for ona in ona_values:

            # Deselect orders with ONA under current value
            arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", "max_ona < " + str(ona + 1), None)

            # Create an onv feature
            feature_layer = arcpy.management.MakeFeatureLayer(all_onvs[spacecraft], "FeatureLayer", f"ona = {ona}")

            # Select orders intersecting the current onv feature layer
            arcpy.management.SelectLayerByLocation(prod, "INTERSECT", feature_layer, None, "ADD_TO_SELECTION")

        # Deselect orders that do not use the spacecraft consitant with the onv
        arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", spacecraft + " = 0", None)

        # File name
        order_file_names.append( "Available_orders_on_" + spacecraft )

        # Export the order layer
        arcpy.management.MultipartToSinglepart(prod, "Available_orders_on_" + spacecraft)

        arcpy.AddMessage("Done Creating Order File")

    return order_file_names

# Add given feature class to the map
def add_layer_to_map(source_layer_name, layer1):
    """ Will add the desired layers to the map and symbolize them """

    arcpy.AddMessage("Running add_layers_to_map.....")

    # Get the active map document and data frame
    project = arcpy.mp.ArcGISProject("CURRENT")
    map = project.activeMap

    # Add the feature layer to the map
    map.addDataFromPath(layer1)

    # Save the layer just added to the map in a variable
    orders = map.listLayers()[0]

    # Find the source layer by name in the list of layers (or raise and error if not found)
    for layer in map.listLayers():
        if layer.name == source_layer_name:
            source_layer = layer
            break
    else:
        raise Exception(f"Source layer '{source_layer_name}' not found in the TOC.")
    
    # Apply the symbology to the target layer
    orders.symbology = source_layer.symbology

    arcpy.AddMessage("Done")

def clean_layer_name(layer):
    """ Returns the name of the given layer file with the preceding group path removed """

    name = ""

    for i in range(1,len(layer)):

        # Grab each character until a '\' is found
        if layer[-i] != '\\':
            name = layer[-i] + name
        else:
            return name


# Function to be called by the Clear Order Value tool
def run(prod, prod_name, all_onvs):
    """ This function controls what is run by the tool """
    
    # Get current workspace
    current_Workspace = arcpy.env.workspace

    # Create dictionary of {spacecraft: onv_file,...}
    spacecraft_dict = onv_dict(all_onvs)

    # Create all the layers and add to the geodatabase
    order_files = available_orders(prod, spacecraft_dict)

    # Add each file to the map and symbolize it
    for file_name in order_files:
        add_layer_to_map(clean_layer_name(prod_name), current_Workspace + "\\" + file_name)





 
