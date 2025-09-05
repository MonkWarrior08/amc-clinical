"""
Database utilities for the simulation app
"""

import sqlite3
import os
from typing import List, Dict, Optional

class MedicalCasesQuery:
    def __init__(self, db_path=None):
        if db_path is None:
            # Get the database path relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            db_path = os.path.join(project_root, 'database', 'medical_cases.db')
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def get_cases_by_category(self, category_name: str) -> List[Dict]:
        """Get all cases for a specific category with basic info"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.case_id, c.category_id, cat.name as category_name
            FROM cases c
            JOIN categories cat ON c.category_id = cat.id
            WHERE cat.name = ?
            ORDER BY c.case_id
        """, (category_name,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_case_with_content(self, case_id: str) -> Optional[Dict]:
        """Get case details including SCENARIO, CASE_TYPE, INSTRUCTION and other content"""
        cursor = self.conn.cursor()
        
        # Get case basic info
        cursor.execute("""
            SELECT c.case_id, cat.name as category_name
            FROM cases c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.case_id = ?
        """, (case_id,))
        case_info = cursor.fetchone()
        
        if not case_info:
            return None
        
        # Get all sections for this case
        cursor.execute("""
            SELECT s.id, s.section_type, s.content
            FROM sections s
            WHERE s.case_id = ?
            ORDER BY s.id
        """, (case_id,))
        sections = cursor.fetchall()
        
        # Initialize result
        result = {
            'case_id': case_info[0],
            'category_name': case_info[1],
            'scenario': "",
            'instruction_for_doc': "",
            'case_type': "",
            'instruction': "",
            'summary': "",
            'instructions_for_patient': "",
            'gender': "",
            'age': "",
            'occupation': ""
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
            
            # Store section content
            if section_type == 'Instruction_for_doc':
                result['instruction_for_doc'] = content
                
                # Extract subsections
                for sub in subsections:
                    sub_type, sub_content = sub
                    if sub_type == 'CASE_TYPE':
                        result['case_type'] = sub_content
                    elif sub_type == 'INSTRUCTION':
                        result['instruction'] = sub_content
                    elif sub_type == 'SCENARIO':
                        result['scenario'] = sub_content
                        # Extract gender, age, and presenting complaint from scenario
                        self._extract_patient_info(sub_content, result)
                    elif sub_type == 'SUMMARY':
                        result['summary'] = sub_content
                        
            elif section_type == 'Instructions_for_patient':
                result['instructions_for_patient'] = content
                
                # Extract subsections
                for sub in subsections:
                    sub_type, sub_content = sub
                    if sub_type == 'SCENARIO':
                        result['scenario'] = sub_content
                    elif sub_type == 'SUMMARY':
                        result['summary'] = sub_content
        
        return result
    
    def _extract_patient_info(self, scenario_text: str, result: Dict):
        """Extract gender, age, and occupation from scenario text"""
        import re
        
        # Extract age (look for patterns like "14-year-old", "aged 76", "76 years old")
        age_patterns = [
            r'(\d+)-year-old',
            r'aged (\d+)',
            r'(\d+) years old',
            r'(\d+) year old'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, scenario_text, re.IGNORECASE)
            if match:
                result['age'] = match.group(1) + " years"
                break
        
        # Extract gender - first try explicit terms, then pronouns
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
                    result['gender'] = 'Female'
                    gender_found = True
                    break
                elif gender_word in ['boy', 'man', 'male']:
                    result['gender'] = 'Male'
                    gender_found = True
                    break
        
        # If no explicit gender found, look for pronouns
        if not gender_found:
            # Count occurrences of "he/him/his" vs "she/her/hers"
            he_count = len(re.findall(r'\b(he|him|his)\b', scenario_text, re.IGNORECASE))
            she_count = len(re.findall(r'\b(she|her|hers)\b', scenario_text, re.IGNORECASE))
            
            if he_count > she_count and he_count > 0:
                result['gender'] = 'Male'
            elif she_count > he_count and she_count > 0:
                result['gender'] = 'Female'
        
        # Extract occupation (look for patterns like "is a 50-year-old taxi driver", "works as a", "is a retired")
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
                # Handle patterns with age and occupation
                if len(match.groups()) == 2:
                    occupation = match.group(2).strip()
                else:
                    occupation = match.group(1).strip()
                
                # Clean up the occupation text
                occupation = re.sub(r'\s+', ' ', occupation)
                # Remove common trailing words and age references
                occupation = re.sub(r'\s+(who|that|with|and|but|aged \d+|\d+ years old).*$', '', occupation, flags=re.IGNORECASE)
                # Remove age patterns
                occupation = re.sub(r'\d+-year-old\s*', '', occupation, flags=re.IGNORECASE)
                occupation = re.sub(r'\d+\s*years?\s*old\s*', '', occupation, flags=re.IGNORECASE)
                occupation = re.sub(r'aged\s+\d+\s*', '', occupation, flags=re.IGNORECASE)
                
                if len(occupation) > 50:
                    occupation = occupation[:50] + "..."
                
                # Filter out non-occupation words
                if (occupation and 
                    occupation.lower() not in ['patient', 'person', 'individual', 'girl', 'boy', 'lady', 'man', 'woman'] and
                    not re.match(r'^\d+', occupation.strip())):
                    result['occupation'] = occupation.title()
                    break
    
    def get_cases_with_content_by_category(self, category_name: str) -> List[Dict]:
        """Get all cases for a category with their content"""
        cases = self.get_cases_by_category(category_name)
        cases_with_content = []
        
        for case in cases:
            case_id = case['case_id']
            case_content = self.get_case_with_content(case_id)
            if case_content:
                cases_with_content.append(case_content)
        
        return cases_with_content
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
