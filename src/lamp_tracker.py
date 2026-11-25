#!/usr/bin/env python3
"""Lamp Tracker - A Bottle web app for tracking street light outages."""

import os
import sqlite3
import json
from bottle import route, run, response, request, redirect
from urllib.parse import parse_qs

DB_PATH = os.path.join(os.path.dirname(__file__), "lamp_tracker.db")
IMPORTER_SCRIPT = os.path.join(os.path.dirname(__file__), "import_lamps.py")


def build_lamp_html(lamps, outage_status, title="Lamp Tracker"):
    """Build HTML for a list of lamps.
    
    Args:
        lamps: List of lamp tuples from database
        outage_status: Dict mapping lamp_id to status
        title: HTML title for the page
    
    Returns:
        HTML string with all lamps listed
    """
    html_parts = []
    html_parts.append(f"<h1>{title}</h1>")
    html_parts.append("<ul>")
    
    for lamp in lamps:
        # Handle both formats: with distance prefix or without
        if isinstance(lamp, tuple) and len(lamp) > 0:
            # If first element is a float (distance), extract lamp data
            if isinstance(lamp[0], float):
                # Format with distance prefix: (distance, lamp_id, lat, lon, ...)
                lamp_id = lamp[1]
                latitude = lamp[2]
                longitude = lamp[3]
                addr_housenumber = lamp[4]
                addr_street = lamp[5]
                addr_city = lamp[6]
                addr_state = lamp[7]
                addr_postcode = lamp[8]
                apco_pole_id = lamp[9]
                verizon_pole_id = lamp[10]
                lynchburg_id = lamp[11]
                osm_object_id = lamp[12]
            else:
                # Original format: (id, lat, lon, ...)
                lamp_id = lamp[0]
                latitude = lamp[1]
                longitude = lamp[2]
                addr_housenumber = lamp[8]
                addr_street = lamp[9]
                addr_city = lamp[10]
                addr_state = lamp[11]
                addr_postcode = lamp[12]
                apco_pole_id = lamp[4]
                verizon_pole_id = lamp[5]
                lynchburg_id = lamp[6]
                osm_object_id = lamp[4]
        
        # Build address
        address = []
        if addr_housenumber:
            address.append(f"{addr_housenumber}")
        if addr_street:
            address.append(addr_street)
        if addr_city:
            address.append(addr_city)
        if addr_state:
            address.append(addr_state)
        if addr_postcode:
            address.append(f"{addr_postcode}")
        
        address_str = ", ".join(address) if address else "Unknown"
        
        # Determine status - check if lamp has any unfixed outages
        if lamp_id in outage_status:
            status = outage_status[lamp_id]
        else:
            # No outages recorded for this lamp, so it's working
            status = "working"
        
        # Status badge
        if status == "working":
            status_html = '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;">Working</span>'
        else:
            status_html = '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;">Broken</span>'
        
        # Build IDs and GPS link
        ids_str = []
        if apco_pole_id:
            ids_str.append(f"AppCo: {apco_pole_id}")
        if verizon_pole_id:
            ids_str.append(f"Verizon: {verizon_pole_id}")
        if lynchburg_id:
            ids_str.append(f"Lynchburg: {lynchburg_id}")
        if not ids_str:
            ids_str.append(f"AppCo: {osm_object_id.split('/')[-1] if '/' in osm_object_id else osm_object_id}")
        ids_html = ", ".join(ids_str) if ids_str else "N/A"
        
        # GPS coordinates as clickable link
        if latitude and longitude:
            osm_id = osm_object_id.split('/')[-1] if osm_object_id else ""
            if osm_id:
                geo_url = f"https://www.openstreetmap.org/node/{osm_id}"
                gps_link = f'<a href="{geo_url}" target="_blank">📍 {osm_id}</a>'
            else:
                gps_link = "No GPS data"
        else:
            gps_link = "No GPS data"
        
        # Item HTML
        item_html = f"""<li>
    <span style="font-weight: bold; margin-right: 15px;">#{lamp_id}</span>
    <span style="margin-right: 15px;">{address_str}</span>
    {status_html}
    <span style="margin-left: 15px; color: #666;">{ids_html}</span>
    <a href="/lamp/{lamp_id}" style="margin-left: 15px;">View details</a>
    {gps_link}
</li>"""
        
        html_parts.append(item_html)
    
    html_parts.append("</ul>")
    
    return "\n".join(html_parts)


@route('/', method='POST')
def import_lamps():
    """CLI route to import lamps from GeoJSON."""
    try:
        input_file = request.get_header('X-Input-File')
        if not input_file:
            return "Error: Missing X-Input-File header\n"  # type: ignore
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        features = data.get('features', [])
        
        conn = sqlite3.connect(DB_PATH)
        try:
            from datetime import datetime
            cursor = conn.cursor()
            change_dtm = datetime.now().strftime("%Y-%m-%d")
            
            for feature in features:
                props = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                if geometry.get('type') != 'Point':
                    continue
                
                coordinates = geometry.get('coordinates', [])
                if len(coordinates) < 2:
                    continue
                
                longitude = coordinates[0]
                latitude = coordinates[1]
                osm_object_id = props.get('@id', '')
                
                cursor.execute(
                    "SELECT id FROM Lamps WHERE osm_object_id = ?",
                    (osm_object_id,)
                )
                if cursor.fetchone():
                    continue
                
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
                            props.get('apco_pole_id'),
                            props.get('lynchburg_id'),
                            props.get('addr_housenumber'),
                            props.get('addr_street'),
                            props.get('addr_city'),
                            props.get('addr_state'),
                            props.get('addr_postcode'),
                        )
                    )
                except sqlite3.IntegrityError:
                    continue
            
            conn.commit()
            return f"Imported {len(features)} features"  # type: ignore
        finally:
            conn.close()
    except Exception as e:
        return f"Error: {str(e)}"  # type: ignore


@route('/nearby')
def get_nearby_lamps():
    """Get lamps near a GPS location, sorted by distance, displayed as HTML."""
    try:
        query_string = request.query_string
        if not query_string:
            return "Error: Missing lat or lon query parameters\n"
        params = parse_qs(query_string)
        lat = float(params['lat'][0]) if params.get('lat') else None
        lon = float(params['lon'][0]) if params.get('lon') else None
        if lat is None or lon is None:
            return "Error: Missing lat or lon query parameters\n"
        
        # Get all lamps with their coordinates
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""SELECT id, latitude, longitude, 
                           addr_housenumber, addr_street, addr_city, addr_state, addr_postcode,
                           apco_pole_id, verizon_pole_id, lynchburg_id, osm_object_id 
                           FROM Lamps""")
        lamps = cursor.fetchall()
        
        # Build outage status - lamp is broken if ANY outage is unfixed
        outage_status = {}
        # Group outages by lamp_id
        lamps_with_outages = {}
        cursor.execute("SELECT lamp_id, fixed_dtm FROM Outages")
        outages = cursor.fetchall()
        for outage in outages:
            lamp_id = outage[0]
            fixed_dtm = outage[1]
            if lamp_id not in lamps_with_outages:
                lamps_with_outages[lamp_id] = []
            lamps_with_outages[lamp_id].append(outage)
        
        # For each lamp that has outages, determine status
        for lamp_id, outages_for_lamp in lamps_with_outages.items():
            # Check if all outages for this lamp are fixed
            all_fixed = True
            for o in outages_for_lamp:
                if not o[1]:  # o[1] is fixed_dtm
                    all_fixed = False
                    break
            if all_fixed:
                outage_status[lamp_id] = "working"
            else:
                outage_status[lamp_id] = "broken"
        conn.close()
        
        # Calculate distance for each lamp using simple cartesian distance
        # Distance = sqrt((x1-x2)^2 + (y1-y2)^2)
        # Using a simplified approach: (lat1-lat2)^2 + (lon1-lon2)^2
        results = []
        for lamp in lamps:
            lamp_id = lamp[0]
            lamp_lat = lamp[1]
            lamp_lon = lamp[2]
            addr_housenumber = lamp[3]
            addr_street = lamp[4]
            addr_city = lamp[5]
            addr_state = lamp[6]
            addr_postcode = lamp[7]
            apco_pole_id = lamp[8]
            verizon_pole_id = lamp[9]
            lynchburg_id = lamp[10]
            osm_object_id = lamp[11]
            
            # Calculate squared distance (avoiding sqrt for performance)
            # Use simple cartesian: (lat1 - lat2)^2 + (lon1 - lon2)^2
            distance_sq = (lat - lamp_lat) ** 2 + (lon - lamp_lon) ** 2
            
            results.append((distance_sq, lamp_id, lamp_lat, lamp_lon, 
                           addr_housenumber, addr_street, addr_city, addr_state, 
                           addr_postcode, apco_pole_id, verizon_pole_id, 
                           lynchburg_id, osm_object_id))
        
        # Sort by distance (ascending) and take top 10
        results.sort(key=lambda x: x[0])
        nearby = results[:10]
        
        # Build HTML using shared function
        return build_lamp_html(nearby, outage_status, title="Lamps Near You")
    except Exception as e:
        return f"Error: {str(e)}"


@route('/lamp/<lamp_id>')
def lamp_detail(lamp_id):
    """Display detailed information about a specific lamp."""
    try:
        # Get the lamp data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, change_dtm, latitude, longitude, osm_object_id, \
                       verizon_pole_id, apco_pole_id, lynchburg_id, \
                       addr_housenumber, addr_street, addr_city, \
                       addr_state, addr_postcode FROM Lamps WHERE id = ?", (lamp_id,))
        lamp = cursor.fetchone()
        
        if not lamp:
            return f"<h1>Lamp {lamp_id} Details</h1><p>No lamp found with ID {lamp_id}</p>"
        
        lamp_id, change_dtm, latitude, longitude, osm_object_id, \
            verizon_pole_id, apco_pole_id, lynchburg_id, \
            addr_housenumber, addr_street, addr_city, \
            addr_state, addr_postcode = lamp
        
        conn.close()
        
        # Build address
        address = []
        if addr_housenumber:
            address.append(f"{addr_housenumber}")
        if addr_street:
            address.append(addr_street)
        if addr_city:
            address.append(addr_city)
        if addr_state:
            address.append(addr_state)
        if addr_postcode:
            address.append(f"{addr_postcode}")
        
        address_str = ", ".join(address) if address else "Unknown"
        
        # Build IDs and GPS link
        ids_str = []
        if apco_pole_id:
            ids_str.append(f"AppCo: {apco_pole_id}")
        if verizon_pole_id:
            ids_str.append(f"Verizon: {verizon_pole_id}")
        if lynchburg_id:
            ids_str.append(f"Lynchburg: {lynchburg_id}")
        if not ids_str:
            ids_str.append(f"AppCo: {osm_object_id.split('/')[-1] if '/' in osm_object_id else osm_object_id}")
        ids_html = ", ".join(ids_str) if ids_str else "N/A"
        
        # GPS coordinates as clickable link
        if latitude and longitude:
            osm_id = osm_object_id.split('/')[-1] if osm_object_id else ""
            if osm_id:
                geo_url = f"https://www.openstreetmap.org/node/{osm_id}"
                gps_link = f'<a href="{geo_url}" target="_blank">📍 {osm_id}</a>'
            else:
                gps_link = "No GPS data"
        else:
            gps_link = "No GPS data"
        
        # Get outage history for this lamp
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT lamp_id, found_dtm, report_dtm, checked_dtm, fixed_dtm FROM Outages WHERE lamp_id = ? ORDER BY found_dtm DESC", (lamp_id,))
        outages = cursor.fetchall()
        
        # Determine current status
        # If there's no outage record, lamp is working
        # If there's an outage with a fixed_dtm, lamp is working
        # If there's an outage without a fixed_dtm, lamp is broken
        outage_status = "working"
        if outages:
            latest_outage = outages[0]
            if not latest_outage[4]:  # No fixed_dtm
                outage_status = "broken"
        
        # Build outage history HTML
        outage_html_parts = []
        for outage in outages:
            lamp_id_outage, found_dtm, report_dtm, checked_dtm, fixed_dtm = outage
            if fixed_dtm:
                outage_html_parts.append(f"<li><span>Outage #{lamp_id_outage}</span> - Found: {found_dtm}, Fixed: {fixed_dtm}</li>")
            else:
                outage_html_parts.append(f"<li><span>Outage #{lamp_id_outage}</span> - Found: {found_dtm}, Status: <span style='background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 4px;'>Still Out</span></li>")
        
        outage_html = "".join(outage_html_parts) if outage_html_parts else "<p>No outages recorded for this lamp.</p>"
        
        # Build status badge
        if outage_status == "working":
            status_html = '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;">Working</span>'
        else:
            status_html = '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;">Broken</span>'
        
        # Build detailed HTML
        detail_html = f"""<h1>Lamp {lamp_id} Details</h1>

<h2>Current Status</h2>
{status_html}

<h2>Location</h2>
<p><strong>Address:</strong> {address_str}</p>
{gps_link}

<h2>Additional Information</h2>
<p><strong>AppCo Pole ID:</strong> {ids_html}</p>

<h2>Outage History</h2>
<ul>
    {outage_html}
</ul>

<p><a href="/">← Back to Lamp List</a></p>
"""
        
        # Add "Mark as broken" button if lamp is working
        if outage_status == "working":
            detail_html += f"\n<p><a href='/lamp/{lamp_id}/mark-broken' style='background-color: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 4px; text-decoration: none; cursor: pointer;'>Mark as broken</a></p>"
        # Add "Mark as fixed" button if lamp is broken
        elif outage_status == "broken":
            detail_html += f"\n<p><a href='/lamp/{lamp_id}/mark-fixed' style='background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; text-decoration: none; cursor: pointer;'>Mark as fixed</a></p>"
        
        return detail_html
    except Exception as e:
        return f"<h1>Error</h1><p>Error displaying lamp details: {str(e)}</p>"

@route('/lamp/<lamp_id>/mark-broken', method=['GET', 'POST'])
def mark_as_broken(lamp_id):
    """Mark a lamp as broken by creating a new outage with unset fixed_dtm."""
    try:
        from datetime import datetime
        
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get the lamp data
            cursor.execute("SELECT id FROM Lamps WHERE id = ?", (lamp_id,))
            lamp = cursor.fetchone()
            
            if not lamp:
                return f"<h1>Mark as broken</h1><p>No lamp found with ID {lamp_id}</p>"
            
            # Create a new outage record with all fields set to current datetime
            # but fixed_dtm set to empty string (marking lamp as broken)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                """INSERT INTO Outages (lamp_id, found_dtm, report_dtm, checked_dtm,
                    most_recent_contact_dtm, work_order_id, fixed_dtm)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (lamp_id, now, now, now, now, '', '')
            )
            
            conn.commit()
            
            count = cursor.execute('SELECT count(*) FROM Outages WHERE lamp_id = ?', (lamp_id,))
            count = count.fetchone()[0]
            
            return f"<h1>Lamp {lamp_id} marked as broken</h1><p>All {count} outages updated.</p><p><a href='/lamp/{lamp_id}'>View lamp details</a></p>"
        except Exception as e:
            return f"<h1>Error</h1><p>Error marking lamp as broken: {str(e)}</p>"
        finally:
            if conn:
                conn.close()
                cursor = None
    except Exception as e:
        return f"<h1>Error</h1><p>Error marking lamp as broken: {str(e)}</p>"
@route('/lamp/<lamp_id>/mark-fixed', method=['GET', 'POST'])
def mark_as_fixed(lamp_id):
    """Mark a lamp as fixed by updating all unfixed outages."""
    try:
        from datetime import datetime
        
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get the lamp data
            cursor.execute("SELECT id FROM Lamps WHERE id = ?", (lamp_id,))
            lamp = cursor.fetchone()
            
            if not lamp:
                return f"<h1>Mark as fixed</h1><p>No lamp found with ID {lamp_id}</p>"
            
            # Update all unfixed outages for this lamp to current datetime
            found_dtm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                "UPDATE Outages SET fixed_dtm = ? WHERE lamp_id = ? AND fixed_dtm = ''",
                (found_dtm, lamp_id)
            )
            
            conn.commit()
            
            count = cursor.execute('SELECT count(*) FROM Outages WHERE lamp_id = ?', (lamp_id,))
            count = count.fetchone()[0]
            
            return f"<h1>Lamp {lamp_id} marked as fixed</h1><p>All {count} outages updated.</p><p><a href='/lamp/{lamp_id}'>View lamp details</a></p>"
        except Exception as e:
            return f"<h1>Error</h1><p>Error marking lamp as fixed: {str(e)}</p>"
        finally:
            if conn:
                conn.close()
                cursor = None
    except Exception as e:
        return f"<h1>Error</h1><p>Error marking lamp as fixed: {str(e)}</p>"




@route('/')
def index():
    """Display list of lamps as HTML."""
    conn = sqlite3.connect(DB_PATH)
    
    # Get all lamps
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lamps")
    lamps = cursor.fetchall()
    
    # Get all outages
    cursor.execute("SELECT * FROM Outages")
    outages = cursor.fetchall()
    
    conn.close()
    
    # Build lookup for outages by lamp_id - lamp is broken if ANY outage is unfixed
    outage_status = {}
    # Group outages by lamp_id
    lamps_with_outages = {}
    for outage in outages:
        lamp_id = outage[0]
        fixed_dtm = outage[4]
        if lamp_id not in lamps_with_outages:
            lamps_with_outages[lamp_id] = []
        lamps_with_outages[lamp_id].append(outage)
    
    # For each lamp that has outages, determine status
    for lamp_id, outages_for_lamp in lamps_with_outages.items():
        # Check if all outages for this lamp are fixed
        all_fixed = True
        for o in outages_for_lamp:
            if not o[4]:  # o[4] is fixed_dtm
                all_fixed = False
                break
        if all_fixed:
            outage_status[lamp_id] = "working"
        else:
            outage_status[lamp_id] = "broken"
    
    # Build HTML using shared function
    return build_lamp_html(lamps, outage_status, title="Lamp Tracker")


if __name__ == "__main__":
    run(host='0.0.0.0', port=8082)
