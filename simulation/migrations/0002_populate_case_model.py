"""
Data migration to populate Case model with data from medical_cases.db
"""

from django.db import migrations
import sqlite3
import os

def populate_case_model(apps, schema_editor):
    """Populate Case model with data from medical_cases.db"""
    Case = apps.get_model('simulation', 'Case')
    
    # Path to the medical cases database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'medical_cases.db')
    
    if not os.path.exists(db_path):
        print(f"Warning: Medical cases database not found at {db_path}")
        return
    
    # Connect to the medical cases database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all cases with their content
        cursor.execute("""
            SELECT c.case_id, cat.name as category_name
            FROM cases c
            LEFT JOIN categories cat ON c.category_id = cat.id
            ORDER BY c.case_id
        """)
        cases = cursor.fetchall()
        
        for case_row in cases:
            case_id = case_row['case_id']
            category = case_row['category_name'] or 'Unknown'
            
            # Get all sections for this case
            cursor.execute("""
                SELECT s.id, s.section_type, s.content
                FROM sections s
                WHERE s.case_id = ?
                ORDER BY s.id
            """, (case_id,))
            sections = cursor.fetchall()
            
            # Initialize case data
            case_data = {
                'case_id': case_id,
                'category': category,
                'scenario': '',
                'instructions_for_patient': '',
                'gender': '',
                'age': '',
                'occupation': '',
                'instruction_for_doc': '',
                'case_type': '',
                'examination_details': '',
                'info_for_facilitator_exam_findings': '',
                'specific_questions': '',
                'management_plan': '',
                'case_commentary': '',
                'pitfalls': '',
                'summary': ''
            }
            
            # Process each section
            for section in sections:
                section_id, section_type, content = section
                
                # Get subsections for this section
                cursor.execute("""
                    SELECT subsection_type, content
                    FROM subsections
                    WHERE section_id = ?
                    ORDER BY id
                """, (section_id,))
                subsections = cursor.fetchall()
                
                # Store section content based on type
                if section_type == 'Instruction_for_doc':
                    case_data['instruction_for_doc'] = content
                    
                    # Extract subsections
                    for sub in subsections:
                        sub_type, sub_content = sub
                        if sub_type == 'CASE_TYPE':
                            case_data['case_type'] = sub_content
                        elif sub_type == 'INSTRUCTION':
                            case_data['specific_questions'] = sub_content
                        elif sub_type == 'SCENARIO':
                            case_data['scenario'] = sub_content
                            # Extract patient info from scenario
                            case_data.update(_extract_patient_info(sub_content))
                        elif sub_type == 'SUMMARY':
                            case_data['summary'] = sub_content
                        elif sub_type == 'EXAMINATION':
                            case_data['examination_details'] = sub_content
                        elif sub_type == 'MANAGEMENT':
                            case_data['management_plan'] = sub_content
                        elif sub_type == 'COMMENTARY':
                            case_data['case_commentary'] = sub_content
                        elif sub_type == 'PITFALL':
                            case_data['pitfalls'] = sub_content
                
                elif section_type == 'Instructions_for_patient':
                    case_data['instructions_for_patient'] = content
                    
                    # Extract subsections
                    for sub in subsections:
                        sub_type, sub_content = sub
                        if sub_type == 'SCENARIO':
                            if not case_data['scenario']:  # Only if not already set
                                case_data['scenario'] = sub_content
                        elif sub_type == 'SUMMARY':
                            if not case_data['summary']:  # Only if not already set
                                case_data['summary'] = sub_content
                
                elif section_type == 'Examination_findings':
                    case_data['info_for_facilitator_exam_findings'] = content
            
            # Create Case object
            Case.objects.update_or_create(
                case_id=case_id,
                defaults=case_data
            )
            
            print(f"Created/updated case: {case_id}")
        
        print(f"Successfully populated {len(cases)} cases")
        
    finally:
        conn.close()

def _extract_patient_info(scenario_text):
    """Extract patient information from scenario text"""
    import re
    
    info = {'gender': '', 'age': '', 'occupation': ''}
    
    # Extract age
    age_patterns = [
        r'(\d+)-year-old',
        r'aged (\d+)',
        r'(\d+) years old',
        r'(\d+) year old'
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, scenario_text, re.IGNORECASE)
        if match:
            info['age'] = match.group(1) + " years"
            break
    
    # Extract gender
    gender_found = False
    
    # Look for explicit gender terms
    gender_patterns = [
        r'\b(girl|boy)\b',
        r'\b(lady|woman|man)\b',
        r'\b(female|male)\b'
    ]
    
    for pattern in gender_patterns:
        match = re.search(pattern, scenario_text, re.IGNORECASE)
        if match:
            gender_word = match.group(1).lower()
            if gender_word in ['girl', 'woman', 'lady', 'female']:
                info['gender'] = 'Female'
                gender_found = True
                break
            elif gender_word in ['boy', 'man', 'male']:
                info['gender'] = 'Male'
                gender_found = True
                break
    
    # If no explicit gender found, look for pronouns
    if not gender_found:
        he_count = len(re.findall(r'\b(he|him|his)\b', scenario_text, re.IGNORECASE))
        she_count = len(re.findall(r'\b(she|her|hers)\b', scenario_text, re.IGNORECASE))
        
        if he_count > she_count and he_count > 0:
            info['gender'] = 'Male'
        elif she_count > he_count and she_count > 0:
            info['gender'] = 'Female'
    
    # Extract occupation
    occupation_patterns = [
        r'is a \d+-year-old ([^.]+?)(?:\.|,|$)',
        r'is a (\d+)-year-old ([^.]+?)(?:\.|,|$)',
        r'works as a ([^.]+?)(?:\.|,|$)',
        r'is a ([^.]+?)(?:\.|,|$)',
        r'is an ([^.]+?)(?:\.|,|$)',
        r'is a retired ([^.]+?)(?:\.|,|$)',
        r'is a former ([^.]+?)(?:\.|,|$)'
    ]
    
    for pattern in occupation_patterns:
        match = re.search(pattern, scenario_text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                occupation = match.group(2).strip()
            else:
                occupation = match.group(1).strip()
            
            # Clean up the occupation text
            occupation = re.sub(r'\s+', ' ', occupation)
            occupation = re.sub(r'\s+(who|that|with|and|but|aged \d+|\d+ years old).*$', '', occupation, flags=re.IGNORECASE)
            occupation = re.sub(r'\d+-year-old\s*', '', occupation, flags=re.IGNORECASE)
            occupation = re.sub(r'\d+\s*years?\s*old\s*', '', occupation, flags=re.IGNORECASE)
            occupation = re.sub(r'aged\s+\d+\s*', '', occupation, flags=re.IGNORECASE)
            
            if len(occupation) > 50:
                occupation = occupation[:50] + "..."
            
            if (occupation and 
                occupation.lower() not in ['patient', 'person', 'individual', 'girl', 'boy', 'lady', 'man', 'woman'] and
                not re.match(r'^\d+', occupation.strip())):
                info['occupation'] = occupation.title()
                break
    
    return info

def reverse_populate_case_model(apps, schema_editor):
    """Reverse migration - delete all Case objects"""
    Case = apps.get_model('simulation', 'Case')
    Case.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('simulation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_case_model, reverse_populate_case_model),
    ]
