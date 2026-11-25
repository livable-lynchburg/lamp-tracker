#!/usr/bin/env python3
"""Import lamps from GeoJSON file into the database."""

import json
import sqlite3
import argparse
from datetime import datetime

DB_PATH = "lamp_tracker.db"


def parse_geojson_file(filepath):
    """Parse a GeoJSON file and return features."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data.get('features', [])


def get_address_from_properties(props):
    """Extract address fields from properties."""
    address = {}
    for key in ['addr_housenumber', 'addr_street', 'addr_city', 'addr_state', 'addr_postcode']:
        if key in props:
            address[key] = props[key]
    return address


def insert_lamps(conn, features, change_dtm=None):
    """Insert lamp features into the database."""
    cursor = conn.cursor()
    
    if change_dtm is None:
        change_dtm = datetime.now().strftime("%Y-%m-%d")
    
    inserted_count = 0
    for feature in features:
        # Skip if a lamp with this osm_object_id already exists
        cursor.execute(
            "SELECT id FROM Lamps WHERE osm_object_id = ?",
            (feature['properties'].get('@id'),)
        )
        if cursor.fetchone():
            continue
        
        # Extract coordinates from geometry
        geometry = feature.get('geometry', {})
        if geometry.get('type') != 'Point':
            continue
        
        coordinates = geometry.get('coordinates', [])
        if len(coordinates) < 2:
            continue
        
        longitude = coordinates[0]
        latitude = coordinates[1]
        
        # Extract properties
        props = feature.get('properties', {})
        osm_object_id = props.get('@id', '')
        # Use ref field as AppCo pole ID (common in OSM data)
        ref = props.get('ref', '')
        
        # Extract address
        addr = get_address_from_properties(props)
        
        # Insert into database
        try:
            cursor.execute(
                """INSERT INTO Lamps 
                   (change_dtm, latitude, longitude, osm_object_id, 
                    verizon_pole_id, apco_pole_id, lynchburg_id,
                    addr_housenumber, addr_street, addr_city, 
                    addr_state, addr_postcode)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    change_dtm,
                    latitude,
                    longitude,
                    osm_object_id,
                    props.get('verizon_pole_id'),
                    ref if ref else None,
                    props.get('lynchburg_id'),
                    addr.get('addr_housenumber'),
                    addr.get('addr_street'),
                    addr.get('addr_city'),
                    addr.get('addr_state'),
                    addr.get('addr_postcode'),
                )
            )
            inserted_count += 1
        except sqlite3.IntegrityError as e:
            print(f"Skipping feature: {osm_object_id} - {e}")
            continue
    
    conn.commit()
    print(f"Inserted {inserted_count} lamps")


def main():
    parser = argparse.ArgumentParser(description="Import lamps from GeoJSON")
    parser.add_argument('--input', '-i', required=True, help='Input GeoJSON file')
    args = parser.parse_args()
    
    print(f"Reading {args.input}...")
    features = parse_geojson_file(args.input)
    print(f"Found {len(features)} features")
    
    conn = sqlite3.connect(DB_PATH)
    insert_lamps(conn, features)
    conn.close()
    
    print("Done!")


if __name__ == "__main__":
    main()
