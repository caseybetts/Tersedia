# Tersedia - Calibration

## Description
This tool produces outputs which contain the current orders available to collect on the given satellite on a given day. The user has the option for the results to be output to their local geodatabase or to a shapefile in a shared location or both. Output to a local database will automatically add the data to the map and with the symbology of the input layer. Output to the shared location will replace
the current files so that layer source connections will not be broken. The tool will output one layer for each satellite layer provided.

## How to use
In the ArcPro Catalog pane create a file connection to the folder. Open the toolbox dropdown and double click the tool. When the tool opens in the Geoprocessing pane the user must add one order layer which may or may not be pre-filtered.
At least one satellite ONV layer is also required. Whatever filter the onv layer has will be used, for example the user can input today's onv, or tomorrow's onv, or any other criteria the layer is able to be filtered by.
The user has the option of where to output the data (output to defalut geodatabase) or SharePoint (output to the shared folder location) or both. By default it will output to the SharePoint location. Then click 'Run'.

## Requirements
The tool will require inputs of the orders layer and the satellite onv layers. Once this is loaded, no other input is needed, but be sure to make sure the layers are functional. 

