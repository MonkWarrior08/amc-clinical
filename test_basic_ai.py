#!/usr/bin/env python3
"""
Basic AI System Test - Core functionality only

This script tests the core AI functionality without complex feedback generation.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from simulation.models import Case
from simulation.ai_core.patient_agent import PatientAgent
from simulation.ai_core.examiner_workflow import ExaminerWorkflow

def test_patient_agent():
    """Test the patient agent"""
    print("Testing Patient Agent...")
    
    # Get a test case
    case = Case.objects.first()
    if not case:
        print("No cases found in database")
        return False
    
    print(f"Using case: {case.case_id}")
    
    # Create patient agent
    agent = PatientAgent(case.instructions_for_patient or "You are a patient.", "test_session")
    
    # Test interactions
    test_inputs = [
        "Hello, how are you feeling today?",
        "What brought you in today?",
        "How long have you been experiencing these symptoms?",
        "Are you taking any medications?",
        "Do you have any allergies?"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n--- Test {i} ---")
        print(f"Doctor: {user_input}")
        
        is_examiner, response = agent.process_user_input(user_input)
        
        if is_examiner:
            print("Patient: [EXAMINER REQUEST DETECTED]")
        else:
            print(f"Patient: {response}")
    
    print("\n✓ Patient Agent test completed successfully!")
    return True

def test_examiner_workflow():
    """Test the examiner workflow"""
    print("\nTesting Examiner Workflow...")
    
    # Get a test case
    case = Case.objects.first()
    if not case:
        print("No cases found in database")
        return False
    
    print(f"Using case: {case.case_id}")
    
    # Create examiner workflow
    workflow = ExaminerWorkflow(case)
    
    # Test examiner requests
    test_requests = [
        "Examiner: I would like to examine the patient's vital signs",
        "Examiner: Show me the blood test results",
        "Examiner: I need to check the patient's physical examination findings",
        "Examiner: What are the lab results?"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n--- Examiner Test {i} ---")
        print(f"Doctor: {request}")
        
        response = workflow.process_examiner_request(request)
        print(f"Examiner: {response}")
    
    print("\n✓ Examiner Workflow test completed successfully!")
    return True

def test_integration():
    """Test integrated workflow"""
    print("\nTesting Integrated Workflow...")
    
    # Get a test case
    case = Case.objects.first()
    if not case:
        print("No cases found in database")
        return False
    
    print(f"Using case: {case.case_id}")
    
    # Create both agents
    patient_agent = PatientAgent(case.instructions_for_patient or "You are a patient.", "test_session")
    examiner_workflow = ExaminerWorkflow(case)
    
    # Test mixed interactions
    interactions = [
        ("Hello, how are you feeling?", False),
        ("What's your main concern today?", False),
        ("Examiner: I need to check your vital signs", True),
        ("How long have you had this problem?", False),
        ("Examiner: Show me the examination findings", True),
        ("Thank you for coming in today", False)
    ]
    
    for i, (user_input, is_examiner_expected) in enumerate(interactions, 1):
        print(f"\n--- Integration Test {i} ---")
        print(f"Doctor: {user_input}")
        
        if is_examiner_expected:
            # Test examiner workflow
            response = examiner_workflow.process_examiner_request(user_input)
            print(f"Examiner: {response}")
        else:
            # Test patient agent
            is_examiner, response = patient_agent.process_user_input(user_input)
            if is_examiner:
                print("Patient: [EXAMINER REQUEST DETECTED]")
            else:
                print(f"Patient: {response}")
    
    print("\n✓ Integrated Workflow test completed successfully!")
    return True

def main():
    """Main test function"""
    print("Clinical AI ExamPro - Basic AI System Test")
    print("=" * 50)
    
    tests = [
        test_patient_agent,
        test_examiner_workflow,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All core AI tests passed! The system is ready for use.")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
