"""
Created on 
"""
import os
import requests as req

try:
    os.mkdir("bioact")
except FileExistsError:
    pass

base = 'https://phytochem.nal.usda.gov'
mid ='/biological-activities-chemicals-csv-export/'

for bio in range(1,100):
	if os.path.isfile("bioact/"+str(bio)+".csv"):
		print(str(bio)+"already downloaded")
	else:
		
		res = req.get(base+mid+str(bio)+'/all?page&_format=csv')
		csv = open("bioact/"+str(bio)+".csv","wb")
		csv.write(res.content)
		csv.close()
		print("file download"+str(bio))
		
		
import pubchempy as pcp
import pandas as pd
import glob
import os
from pandas.errors import EmptyDataError
import time

# Create the SDFS folder if it doesn't exist
try:
    os.mkdir("SDFS")
except FileExistsError:
    pass

# Get list of CSV files
csv_files = glob.glob('bioact/*.csv')

lig = []

# Read each CSV file and append to lig
for files in csv_files:
    try:
        temp_df = pd.read_csv(files, sep=',')
        lig.append(temp_df)
        print(f"Loaded: {files}")
    except EmptyDataError:
        print(f"{files} is an empty csv file")
    except pd.errors.ParserError as e:
        print(f"Error reading {files}: {e}")

# Check if lig is not empty before concatenating
if lig:
    df = pd.concat(lig, axis=0, ignore_index=True)
    print("Concatenation successful!")
else:
    print("No data to concatenate!")
    df = pd.DataFrame()

# Ensure 'Chemical Name' exists before processing
if not df.empty and 'Chemical Name' in df.columns:
    for name in df['Chemical Name']:
        try:
            compounds = pcp.get_compounds(name, 'name')
            if compounds:
                for compound in compounds:
                    cid = compound.cid
                    print(f"Downloading SDF for CID {cid}")
                    pcp.download('SDF', f'SDFS/{cid}.sdf', cid, 'cid')
                    print(f"Downloading {cid}...")
                time.sleep(1)  # Sleep to avoid hitting API too quickly
            else:
                print(f"No compounds found for {name}")
        except Exception as e:
            print(f"Error fetching compound for {name}: {e}")
else:
    print("No data to process or 'Chemical Name' column is missing.")

