import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_r5_resolution():
    os.makedirs('reports', exist_ok=True)
    
    # 1. Load R4 records
    r4_file = 'data/ground_truth/external_evidence/incident_master_record_r4.csv'
    df = pd.read_csv(r4_file)
    
    # STEP 1: Audit existing incidents
    audit_md = "# Phase 16GT-R5: Existing Incident Audit\n\n"
    for _, row in df.iterrows():
        audit_md += f"### {row['incident_id']}\n"
        audit_md += f"- **Date**: {row['incident_date']}\n"
        audit_md += f"- **Facility**: {row['facility_name']} ({row['facility_type']})\n"
        audit_md += f"- **Location**: {row['reported_location_text']}, {row['city']}, {row['district']}, {row['state']}\n"
        audit_md += f"- **Existing Anchor**: {row['anchor_lat']}, {row['anchor_lon']} ({row['anchor_precision']})\n"
        audit_md += f"- **Anchor Source**: {row['anchor_source']}\n"
        audit_md += f"- **Sources**: {row['external_source_1']}, {row['external_source_2']}\n"
        audit_md += f"- **Status**: {row['evidence_status']}\n\n"
        
    with open('reports/phase16gtr5_existing_incident_audit.md', 'w') as f:
        f.write(audit_md)

    # STEP 2 & 3: Facility Identity & Geospatial Resolution
    identity_md = "# Phase 16GT-R5: Facility Identity Audit\n\n"
    geo_md = "# Phase 16GT-R5: Authoritative Geospatial Audit\n\n"
    
    resolved_records = []
    
    for _, row in df.iterrows():
        rec = row.to_dict()
        
        # Identity Resolution
        fac_name = str(rec['facility_name']).lower()
        if "unknown" in fac_name:
            rec['facility_identity_confidence'] = 'UNRESOLVED'
            identity_md += f"- **{rec['incident_id']}**: UNRESOLVED (Generic facility name)\n"
        else:
            rec['facility_identity_confidence'] = 'HIGH'
            identity_md += f"- **{rec['incident_id']}**: HIGH (Explicitly named: {rec['facility_name']})\n"
            
        # Geospatial Resolution
        rec['geocoder_lat'] = rec['anchor_lat']
        rec['geocoder_lon'] = rec['anchor_lon']
        rec['geocoder_source'] = rec['anchor_source']
        rec['geocoder_confidence'] = rec['anchor_confidence']
        
        if rec['incident_id'] == 'INC-2026-06-30-HALDIA':
            rec['anchor_precision'] = 'FACILITY_POINT_VERIFIED'
            rec['radius_m'] = 1500
            rec['radius_source'] = 'Assumed based on estate acreage'
            rec['radius_source_type'] = 'ASSUMPTION'
            rec['radius_confidence'] = 'LOW'
            rec['radius_is_assumption'] = True
            rec['evidence_status'] = 'PENDING_GEOSPATIAL_VERIFICATION' # Cannot be complete if radius is assumed and boundaries are missing
            geo_md += f"- **{rec['incident_id']}**: Authoritative point exists, but radius is ASSUMED_SPATIAL_ENVELOPE. Retaining point as supporting, but strict polygon boundary is missing.\n"
        else:
            # We searched for Eximchem and Hazelo but found only survey numbers and plot numbers, no verifiable exact coordinates in official docs.
            rec['anchor_precision'] = 'PENDING_GEOSPATIAL_VERIFICATION'
            rec['radius_m'] = 'None'
            rec['radius_source'] = 'None'
            rec['radius_source_type'] = 'NONE'
            rec['radius_confidence'] = 'NONE'
            rec['radius_is_assumption'] = True
            
            if rec['facility_identity_confidence'] == 'HIGH':
                geo_md += f"- **{rec['incident_id']}**: Placed in PENDING_GEOSPATIAL_VERIFICATION. Geocoder coordinates retained as SUPPORTING_EVIDENCE only. Official point/polygon missing.\n"
            else:
                geo_md += f"- **{rec['incident_id']}**: Skipped (Identity Unresolved).\n"
                
        resolved_records.append(rec)
        
    with open('reports/phase16gtr5_facility_identity_audit.md', 'w') as f:
        f.write(identity_md)
        
    with open('reports/phase16gtr5_authoritative_geospatial_audit.md', 'w') as f:
        f.write(geo_md)
        
    # STEP 4: Haldia Geometry Correction
    with open('reports/phase16gtr5_haldia_geometry_correction.md', 'w') as f:
        f.write("# Phase 16GT-R5: Haldia Geometry Correction\n\nThe 1,500m radius previously utilized for Haldia is hereby permanently downgraded to `ASSUMED_SPATIAL_ENVELOPE`. It is not an authoritative facility boundary. Consequently, Haldia cannot be upgraded to REAL_GOLD using this assumed radius, preventing hallucinations of spatial inclusion.\n")
        
    out_df = pd.DataFrame(resolved_records)
    out_df.to_csv('data/ground_truth/external_evidence/incident_master_record_r5.csv', index=False)
    logging.info("R5 Identity and Geospatial Resolution complete.")

if __name__ == "__main__":
    run_r5_resolution()
