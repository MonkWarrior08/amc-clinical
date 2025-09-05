#!/usr/bin/env python3
"""
Test script to verify the medical cases database structure and data
"""

import sqlite3

def test_database():
    """Test the database with various queries"""
    conn = sqlite3.connect("medical_cases.db")
    cursor = conn.cursor()
    
    print("=== DATABASE STRUCTURE TEST ===\n")
    
    # Test 1: Check all categories
    print("1. All Categories:")
    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    for i, (category,) in enumerate(categories, 1):
        print(f"   {i:2d}. {category}")
    
    # Test 2: Cases per category
    print(f"\n2. Cases per Category:")
    cursor.execute("""
        SELECT c.name, COUNT(cases.case_id) as case_count
        FROM categories c
        LEFT JOIN cases ON c.id = cases.category_id
        GROUP BY c.id, c.name
        ORDER BY case_count DESC
    """)
    for category, count in cursor.fetchall():
        print(f"   {category}: {count} cases")
    
    # Test 3: Sample case with all sections
    print(f"\n3. Sample Case - Erin_Campbell:")
    cursor.execute("""
        SELECT s.section_type, s.content
        FROM sections s
        WHERE s.case_id = 'Erin_Campbell'
        ORDER BY s.id
    """)
    sections = cursor.fetchall()
    for section_type, content in sections:
        print(f"   Section: {section_type}")
        print(f"   Content preview: {content[:100]}...")
        print()
    
    # Test 4: Sample subsections
    print(f"4. Sample Subsections for Erin_Campbell - Suggested_approach:")
    cursor.execute("""
        SELECT ss.subsection_type, ss.content
        FROM sections s
        JOIN subsections ss ON s.id = ss.section_id
        WHERE s.case_id = 'Erin_Campbell' 
        AND s.section_type = 'Suggested_approach'
        ORDER BY ss.id
    """)
    subsections = cursor.fetchall()
    for sub_type, content in subsections:
        print(f"   {sub_type}: {content[:150]}...")
        print()
    
    # Test 5: Search for specific content
    print(f"5. Search for cases containing 'acne':")
    cursor.execute("""
        SELECT DISTINCT s.case_id, s.section_type
        FROM sections s
        WHERE s.content LIKE '%acne%'
        ORDER BY s.case_id
    """)
    acne_cases = cursor.fetchall()
    for case_id, section_type in acne_cases:
        print(f"   {case_id} - {section_type}")
    
    # Test 6: Count subsections by type
    print(f"\n6. Subsection Types Count:")
    cursor.execute("""
        SELECT subsection_type, COUNT(*) as count
        FROM subsections
        GROUP BY subsection_type
        ORDER BY count DESC
    """)
    sub_counts = cursor.fetchall()
    for sub_type, count in sub_counts:
        print(f"   {sub_type}: {count}")
    
    # Test 7: Complex query - Get all cardiovascular cases with their management plans
    print(f"\n7. Cardiovascular Cases with Management Plans:")
    cursor.execute("""
        SELECT c.case_id, s.content
        FROM cases c
        JOIN categories cat ON c.category_id = cat.id
        JOIN sections s ON c.case_id = s.case_id
        WHERE cat.name = 'Cardiovascular_system'
        AND s.section_type = 'Suggested_approach'
        AND s.content LIKE '%MANAGEMENT%'
        ORDER BY c.case_id
    """)
    cv_cases = cursor.fetchall()
    for case_id, content in cv_cases:
        print(f"   {case_id}: Management content found")
    
    conn.close()
    print("\n=== DATABASE TEST COMPLETED ===")

if __name__ == "__main__":
    test_database()
