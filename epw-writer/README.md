# epw-writer
The workflow generates EPW files from MesoWest historical weather data.
 
1. `1_pre_process_raw` parses MesoWest data in raw format to annual hourly CSV format. The script also includes the workflow of (1) time series interpolation and (2) filling missing local weather station data with the nearest airport values.
2. `2_write_epw` takes a base airport EPW file, and use the previous generated hourly CSV file to overwrite the corresponding fields in the EPW file to generate local EPW file

Note: raw historical local weather data can be downloaded from the [Synoptic Data website](https://download.synopticdata.com/), and the station ID can be queried from the [MesoWest website](https://mesowest.utah.edu/cgi-bin/droman/mesomap.cgi).
