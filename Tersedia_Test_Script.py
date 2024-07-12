# Author: Casey Betts, 2024
# This file contains the function for isolating the available orders on a given rev

import arcpy

# Find applicable spacecraft
def onv_dict(all_onvs):
    """ Returns a dictionary with spacecraft as keys and onv files as values """

    # Initialize a dictionary
    onv_dict = dict()

    # Add a dictionary item for each onv in given list
    for onv in all_onvs:

        # Test if the list element is a onv file or not (if not do nothing)
        try:

            with arcpy.da.SearchCursor(onv, ["sensor", "days"]) as cursor:
                
                for row in cursor:

                    # Make sure onv file contains a single spacecraft
                    if row[0] not in ["WV01", "WV02", "WV03", "GE01", "LG01", "LG02", "LG03", "LG04", "LG05", "LG06"]:
                        arcpy.AddMessage("The onv file does not contain exactly one spacecraft")
                    
                    # Make sure the days is a single digit
                    elif row[1] > 10:
                        arcpy.AddMessage("ONV files greater than 9 days in the future or past are not supported")
                    
                    # Create a dictionary item: key = "scid_dayNumber", value = onv layer
                    else:
                        onv_dict[str(row[0]).lower() + "_" + str(int(row[1]))] = onv
                        break 
        except:
            
            pass

    return onv_dict
            
# Create feature class of available orders
def available_orders(prod, spacecraft_dict, sharepoint_location, current_workspace):
    """ Select orders accessable on a given rev based on the order's max ONA vlaue """

    arcpy.AddMessage("Running available_orders.....")

    # Definition query values
    ona_values = [35, 30, 25, 20, 15]
    order_file_names = []

    for spacecraft_day in spacecraft_dict:

        arcpy.AddMessage("spacecraft_day: " + spacecraft_day)

        # Select orders intersecting the 45deg segments of the rev (max selection)
        arcpy.management.SelectLayerByLocation(prod, "INTERSECT", spacecraft_dict[spacecraft_day], None, "NEW_SELECTION")

        # Select only the orders that are avaialble based on their max ONA value    
        for ona in ona_values:

            # Deselect orders with ONA under current value
            arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", "max_ona < " + str(ona + 1), None)

            # Create an onv feature
            feature_layer = arcpy.management.MakeFeatureLayer(spacecraft_dict[spacecraft_day], "FeatureLayer", f"ona = {ona}")

            # Select orders intersecting the current onv feature layer
            arcpy.management.SelectLayerByLocation(prod, "INTERSECT", feature_layer, None, "ADD_TO_SELECTION")

        # Deselect orders that do not use the spacecraft consitant with the onv
        arcpy.management.SelectLayerByAttribute(prod, "REMOVE_FROM_SELECTION", spacecraft_day[:4] + " = 0", None)

        # File name
        if spacecraft_day[-1] == "0":
            file_name = "Available_orders_on_" + spacecraft_day[:4] + "_today"
        elif spacecraft_day[-1] == "1":
            file_name = "Available_orders_on_" + spacecraft_day[:4] + "_tomorrow"
        else:
            file_name = "Available_orders_on_" + spacecraft_day[:4] + "_today+" + spacecraft_day[-1]

        # Export the order layer to the sharepoint location
        if sharepoint_location:
            arcpy.conversion.ExportFeatures(prod, sharepoint_location + "\\" + file_name)
            arcpy.AddMessage("Outputing Shapefile to: " + sharepoint_location + "\\" + file_name)

        # Create a feature class in the default geo-database
        if current_workspace:
            arcpy.conversion.ExportFeatures(prod, current_workspace + "\\" + file_name)
            arcpy.AddMessage("Outputing Shapefile to: " + current_workspace + "\\" + file_name)

        # Append file name to list
        order_file_names.append( file_name)

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
def run(prod, prod_name, all_onvs, local, sharepoint):
    """ This function controls what is run by the tool """

    # Get current workspace
    if local:
        current_workspace = arcpy.env.workspace
    else:
        current_workspace = None
    
    # Define output location
    if sharepoint:
        sharepoint_location = r"C:\Users\ca003927\Maxar Technologies Holdings Inc\BR-Collection Planning - ArcGIS Pro\Planning Tools\Homegrown Tools\Tersedia - Available Orders\Shapefile_Output"
    else:
        sharepoint_location = None
        current_workspace = arcpy.env.workspace

    # Create dictionary of {spacecraft: onv_file,...}
    spacecraft_dict = onv_dict(all_onvs)

    # Create all the layers and add to the geodatabase
    order_files = available_orders(prod, spacecraft_dict, sharepoint_location, current_workspace)

    # If local output was selected 
    if local:

        # Add each file to the map and symbolize it
        for file_name in order_files:
            arcpy.AddMessage("Loading from: " + current_workspace + "\\" + file_name)
            add_layer_to_map(clean_layer_name(prod_name), current_workspace + "\\" + file_name)





 
