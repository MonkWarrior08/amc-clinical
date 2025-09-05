#!/usr/bin/env python3
"""
Medical Cases Database Creator

This script creates a SQLite database to store medical case information from text files.
The database structure includes:
- Categories (SECTION_ID)
- Cases (CASE_ID) 
- Sections (different types like Instruction_for_doc, etc.)
- Subsections (SCENARIO, SUMMARY, etc.)
"""

import sqlite3
import re
import os
from typing import Dict, List, Tuple, Optional

class MedicalCasesDatabase:
    def __init__(self, db_path: str = "medical_cases.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def create_tables(self):
        """Create the database tables"""
        cursor = self.conn.cursor()
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        # Cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """)
        
        # Sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                section_type TEXT NOT NULL,
                content TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (case_id)
            )
        """)
        
        # Subsections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subsections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section_id INTEGER NOT NULL,
                subsection_type TEXT NOT NULL,
                content TEXT,
                FOREIGN KEY (section_id) REFERENCES sections (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_category ON cases(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_case ON sections(case_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subsections_section ON subsections(section_id)")
        
        self.conn.commit()
        
    def parse_text_file(self, file_path: str) -> List[Dict]:
        """Parse a text file and extract structured data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content by case blocks
        case_blocks = re.split(r'\[CASE_ID: ([^\]]+)\]', content)
        
        cases = []
        for i in range(1, len(case_blocks), 2):
            if i + 1 < len(case_blocks):
                case_id = case_blocks[i].strip()
                case_content = case_blocks[i + 1]
                
                # Extract category
                category_match = re.search(r'\[SECTION_ID: ([^\]]+)\]', case_content)
                category = category_match.group(1) if category_match else None
                
                # Extract sections
                sections = self._extract_sections(case_content)
                
                cases.append({
                    'case_id': case_id,
                    'category': category,
                    'sections': sections
                })
        
        return cases
    
    def _extract_sections(self, case_content: str) -> List[Dict]:
        """Extract sections and their subsections from case content"""
        sections = []
        
        # Find all section markers
        section_pattern = r'\[SECTION: ([^\]]+)\](.*?)(?=\[SECTION:|$)'
        section_matches = re.finditer(section_pattern, case_content, re.DOTALL)
        
        for match in section_matches:
            section_type = match.group(1).strip()
            section_content = match.group(2).strip()
            
            # Extract subsections
            subsections = self._extract_subsections(section_content)
            
            sections.append({
                'section_type': section_type,
                'content': section_content,
                'subsections': subsections
            })
        
        return sections
    
    def _extract_subsections(self, section_content: str) -> List[Dict]:
        """Extract subsections from section content"""
        subsections = []
        
        # Common subsection patterns
        subsection_patterns = [
            r'\[INSTRUCTION\](.*?)(?=\[|$)',
            r'\[SCENARIO\](.*?)(?=\[|$)',
            r'\[SUMMARY\](.*?)(?=\[|$)',
            r'\[EXAMINATION_FINDINGS\](.*?)(?=\[|$)',
            r'\[SPECIFIC_QUESTIONS\](.*?)(?=\[|$)',
            r'\[EXAMINATION\](.*?)(?=\[|$)',
            r'\[DIAGNOSIS\](.*?)(?=\[|$)',
            r'\[INVESTIGATION\](.*?)(?=\[|$)',
            r'\[TREATMENT\](.*?)(?=\[|$)',
            r'\[MANAGEMENT\](.*?)(?=\[|$)',
            r'\[COMMENTARY\](.*?)(?=\[|$)',
            r'\[PITFALL\](.*?)(?=\[|$)',
        ]
        
        for pattern in subsection_patterns:
            matches = re.finditer(pattern, section_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                subsection_type = match.group(0).split(']')[0][1:]  # Extract type from [TYPE]
                content = match.group(1).strip()
                if content:  # Only add if there's content
                    subsections.append({
                        'subsection_type': subsection_type,
                        'content': content
                    })
        
        # Special handling for CASE_TYPE which has a different format
        case_type_matches = re.finditer(r'\[CASE_TYPE:([^\]]+)\]', section_content)
        for match in case_type_matches:
            content = match.group(1).strip()
            if content:
                subsections.append({
                    'subsection_type': 'CASE_TYPE',
                    'content': content
                })
        
        return subsections
    
    def insert_data(self, cases: List[Dict]):
        """Insert parsed data into the database"""
        cursor = self.conn.cursor()
        
        for case in cases:
            # Insert category
            if case['category']:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                    (case['category'],)
                )
                
                # Get category ID
                cursor.execute(
                    "SELECT id FROM categories WHERE name = ?",
                    (case['category'],)
                )
                category_id = cursor.fetchone()[0]
            else:
                category_id = None
            
            # Insert case
            cursor.execute(
                "INSERT OR REPLACE INTO cases (case_id, category_id) VALUES (?, ?)",
                (case['case_id'], category_id)
            )
            
            # Insert sections
            for section in case['sections']:
                cursor.execute(
                    "INSERT INTO sections (case_id, section_type, content) VALUES (?, ?, ?)",
                    (case['case_id'], section['section_type'], section['content'])
                )
                
                section_id = cursor.lastrowid
                
                # Insert subsections
                for subsection in section['subsections']:
                    cursor.execute(
                        "INSERT INTO subsections (section_id, subsection_type, content) VALUES (?, ?, ?)",
                        (section_id, subsection['subsection_type'], subsection['content'])
                    )
        
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function to create the database"""
    # Initialize database
    db = MedicalCasesDatabase("medical_cases.db")
    db.connect()
    db.create_tables()
    
    # Parse and insert data from both files
    files_to_process = ["source_info/cases/case1.txt", "source_info/cases/cases2.txt"]
    
    for filename in files_to_process:
        if os.path.exists(filename):
            print(f"Processing {filename}...")
            cases = db.parse_text_file(filename)
            db.insert_data(cases)
            print(f"Processed {len(cases)} cases from {filename}")
        else:
            print(f"Warning: {filename} not found")
    
    # Print summary
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cases")
    total_cases = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sections")
    total_sections = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subsections")
    total_subsections = cursor.fetchone()[0]
    
    print(f"\nDatabase created successfully!")
    print(f"Total cases: {total_cases}")
    print(f"Total categories: {total_categories}")
    print(f"Total sections: {total_sections}")
    print(f"Total subsections: {total_subsections}")
    
    # Show some sample data
    print("\nSample categories:")
    cursor.execute("SELECT name FROM categories LIMIT 10")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    print("\nSample cases:")
    cursor.execute("""
        SELECT c.case_id, cat.name 
        FROM cases c 
        LEFT JOIN categories cat ON c.category_id = cat.id 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]})")
    
    db.close()

if __name__ == "__main__":
    main()
