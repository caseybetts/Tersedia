# Author: Casey Betts, 2024
# This file contains the function for isolating the available orders on a given rev

import arcpy

# Create feature class of available orders
def available_orders(prod, onv, rev, respect_ona = True):
    """ Select orders accessable on a given rev based on the order's max ONA vlaue """

    arcpy.AddMessage("Running available_orders.....")

    # File names
    onv_rev = "onv_rev_" + rev
    prod_layer = "Available_orders_on_rev_" + rev

    # Definition query values
    onv_values = [35, 30, 25, 20, 15]

    # Select and export the given rev
    selection = f"\"rev_num\" = {rev} And days = 0"
    arcpy.conversion.ExportFeatures(onv, onv_rev, selection)

    # Select orders intersecting the 45deg segments of the rev (max selection)
    arcpy.management.SelectLayerByLocation(prod, "INTERSECT", onv_rev, None, "NEW_SELECTION")

    # Only include orders that are avaialble based on their max ONA value
    if respect_ona:

        for ona in onv_values:

            # Deselect orders with ONA under current value
            arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", "max_ona < " + str(ona + 1), None)

            # Create an onv feature
            feature_layer = arcpy.management.MakeFeatureLayer(onv_rev, "FeatureLayer", f"ona = {ona}")

            # Select orders intersecting the current onv feature layer
            arcpy.management.SelectLayerByLocation(prod, "INTERSECT", feature_layer, None, "ADD_TO_SELECTION")

    # Export the order layer (strip overlay does not seem to work without an exported feature)
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

    arcpy.AddMessage("\b Done")


# Function to be called by the Clear Order Value tool
def run(prod, onv, rev):
    """ This function controls what is run by the tool """

    # Get current workspace
    current_Workspace = arcpy.env.workspace
    
    # Create all the layers and add to the geodatabase
    orders = available_orders(prod, onv, rev)

    add_layers_to_map(current_Workspace + "\\" + orders)




 
