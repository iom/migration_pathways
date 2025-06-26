# test_crew_ai.py - Test script for CrewAI integration

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from crew_ai.crew import MigrationAssistanceCrew
from crew_ai.config import CrewAIConfig

def test_crew_ai_basic():
    """Basic test of CrewAI functionality"""
    
    print("🚀 Testing CrewAI Migration Assistant Integration...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Validate configuration
        print("📋 Validating CrewAI configuration...")
        CrewAIConfig.validate_config()
        print("✅ Configuration validation passed")
        
        # Initialize crew
        print("🤖 Initializing Migration Assistance Crew...")
        migration_crew = MigrationAssistanceCrew()
        print("✅ Crew initialized successfully")
        
        # Test simple query
        print("💬 Testing simple migration query...")
        test_query = "I want to migrate from Senegal to Canada for work. What are my options?"
        test_context = {
            "source_country": "Senegal",
            "destination_country": "Canada"
        }
        
        response = migration_crew.process_migration_query(test_query, test_context)
        print("✅ Query processed successfully")
        print(f"📝 Response length: {len(response)} characters")
        print(f"📄 Response preview: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

# def test_crew_ai_tools():
#     """Test individual CrewAI tools"""
    
#     print("\n🔧 Testing CrewAI Tools...")
    
#     try:
#         from crew_ai.tools import get_migration_tools
        
#         tools = get_migration_tools()
#         print(f"✅ Loaded {len(tools)} tools successfully")
        
#         for tool in tools:
#             print(f"   - {tool.name}: {tool.description[:50]}...")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Tools test failed: {str(e)}")
#         return False

# def test_crew_complexity_detection():
#     """Test crew complexity detection"""
    
#     print("\n🧠 Testing Crew Complexity Detection...")
    
#     try:
#         migration_crew = MigrationAssistanceCrew()
        
#         # Test simple query
#         simple_query = "What is IOM?"
#         complexity = migration_crew.determine_crew_complexity(simple_query, {})
#         print(f"✅ Simple query complexity: {complexity}")
        
#         # Test complex query
#         complex_query = "I need comprehensive information about work visa documentation, cultural integration, and employment opportunities for migrating from India to Germany"
#         complexity = migration_crew.determine_crew_complexity(complex_query, {"source_country": "India", "destination_country": "Germany"})
#         print(f"✅ Complex query complexity: {complexity}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Complexity detection test failed: {str(e)}")
#         return False

def main():
    """Run all tests"""
    
    print("🧪 CrewAI Migration Assistant Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 1
    
    # Run tests
    if test_crew_ai_basic():
        tests_passed += 1
    
    # if test_crew_ai_tools():
    #     tests_passed += 1
        
    # if test_crew_complexity_detection():
    #     tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! CrewAI integration is working correctly.")
        return True
    else:
        print(f"⚠️  {total_tests - tests_passed} test(s) failed. Please check configuration and dependencies.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)