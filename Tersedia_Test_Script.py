# Author: Casey Betts, 2024
# This file contains the function for isolating the available orders on a given rev

import arcpy

# Find applicable spacecraft
def applicable_spacecraft(onv):
    """ Returns a list of applicable spacecraft from the given onv file """

    with arcpy.da.SearchCursor(onv, "sensor") as cursor:
        
        for row in cursor:
            if len(row) != 1:
                arcpy.AddMessage("The onv file does not contain exactly one spacecraft")
            else:
                return row[0]    
            

# Create feature class of available orders
def available_orders(prod, onv, rev, respect_ona = True):
    """ Select orders accessable on a given rev based on the order's max ONA vlaue """

    arcpy.AddMessage("Running available_orders.....")

    # Definition query values
    onv_values = [35, 30, 25, 20, 15]
    spacecraft = applicable_spacecraft(onv).lower()

    # File names
    # onv_rev = "onv_" + spacecraft + "rev_" + rev
    prod_layer = "Available_orders_on_rev_" + rev

    # Select and export the given rev
    # selection = f"\"rev_num\" = {rev}"
    arcpy.conversion.ExportFeatures(onv, "Tersedia_ONV")

    # Select orders intersecting the 45deg segments of the rev (max selection)
    arcpy.management.SelectLayerByLocation(prod, "INTERSECT", onv, None, "NEW_SELECTION")

    # Only include orders that are avaialble based on their max ONA value
    if respect_ona:

        for ona in onv_values:

            # Deselect orders with ONA under current value
            arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", "max_ona < " + str(ona + 1), None)

            # Create an onv feature
            feature_layer = arcpy.management.MakeFeatureLayer("Tersedia_ONV", "FeatureLayer", f"ona = {ona}")

            # Select orders intersecting the current onv feature layer
            arcpy.management.SelectLayerByLocation(prod, "INTERSECT", feature_layer, None, "ADD_TO_SELECTION")

    # Deselect orders that do not use the spacecraft consitant with the onv
    arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", spacecraft + " = 0", None)

    # Export the order layer
    arcpy.management.MultipartToSinglepart(prod, prod_layer)

    arcpy.AddMessage("\b Done")

    return prod_layer


# Add given feature class to the map
def add_layers_to_map(layer1):
    """ Will add the desired layers to the map and symbolize them """

    arcpy.AddMessage("Running add_layers_to_map.....")

    # Get the active map document and data frame
    project = arcpy.mp.ArcGISProject("CURRENT")
    map = project.activeMap

    # Add the feature layer to the map
    map.addDataFromPath(layer1)

    # Get the symbology from the symbology template layer
    orders = map.listLayers()[0]
    source_layer_name = r"Tersedia Symbology Template"

    for layer in map.listLayers():
        if layer.name == source_layer_name:
            source_layer = layer
            break
    else:
        raise Exception(f"Source layer '{source_layer_name}' not found in the TOC.")
    
    # Apply the symbology to the target layer
    orders.symbology = source_layer.symbology

    arcpy.AddMessage("\b Done")


# Function to be called by the Clear Order Value tool
def run(prod, onv, rev):
    """ This function controls what is run by the tool """

    # Get current workspace
    current_Workspace = arcpy.env.workspace
    
    # Create all the layers and add to the geodatabase
    orders = available_orders(prod, onv, rev)

    add_layers_to_map(current_Workspace + "\\" + orders)





 
