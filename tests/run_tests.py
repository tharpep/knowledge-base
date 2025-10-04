#!/usr/bin/env python3
"""
Test runner script for Personal AI Assistant
Runs all tests with proper configuration and reporting
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Run all tests with pytest"""
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Change to project root
    os.chdir(project_root)
    
    print("🧪 Running Personal AI Assistant Tests")
    print("=" * 50)
    
    # Test categories
    test_categories = [
        ("API Tests", "tests/tests_api"),
        ("AI Provider Tests", "tests/tests_ai_providers"), 
        ("RAG Tests", "tests/tests_rag"),
        ("Tuning Tests", "tests/tests_tuning")
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category_name, test_path in test_categories:
        print(f"\n📋 {category_name}")
        print("-" * 30)
        
        if not Path(test_path).exists():
            print(f"⚠️  {test_path} not found, skipping...")
            continue
            
        try:
            # Run pytest for this category
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_path, 
                "-v", 
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print(f"✅ {category_name} - PASSED")
                total_passed += 1
            else:
                print(f"❌ {category_name} - FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                total_failed += 1
                
        except Exception as e:
            print(f"❌ {category_name} - ERROR: {e}")
            total_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test category(ies) failed")
        return 1

def run_specific_tests(test_pattern=None):
    """Run specific tests matching a pattern"""
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
    
    if test_pattern:
        cmd.append(test_pattern)
    else:
        cmd.append("tests/")
    
    print(f"🧪 Running tests: {' '.join(cmd)}")
    print("=" * 50)
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific tests
        pattern = sys.argv[1]
        exit_code = run_specific_tests(pattern)
    else:
        # Run all tests by category
        exit_code = run_tests()
    
    sys.exit(exit_code)
