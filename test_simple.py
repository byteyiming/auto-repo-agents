#!/usr/bin/env python3
"""
Simple test script - Generate one document to verify file organization works
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager

def quick_test():
    """Quick test - just generate and check basic structure"""
    print("🧪 Quick Test: File Organization")
    print("=" * 60)
    print()
    
    # Small test idea
    test_idea = "Create a simple todo app"
    
    print(f"📝 Test Idea: {test_idea}")
    print()
    print("⏳ Starting generation...")
    print("   (This may take a few minutes)")
    print()
    
    try:
        context_manager = ContextManager()
        coordinator = WorkflowCoordinator(context_manager=context_manager)
        
        # Generate
        results = coordinator.generate_all_docs(test_idea)
        
        print()
        print("=" * 60)
        print("✅ Generation Complete!")
        print("=" * 60)
        print()
        
        # Check files
        files = results.get("files", {})
        print(f"📊 Generated {len(files)} document types:")
        for doc_type, file_path in files.items():
            if doc_type != "format_conversions" and doc_type != "quality_review":
                exists = "✅" if Path(file_path).exists() else "❌"
                print(f"   {exists} {doc_type}: {Path(file_path).name}")
        
        print()
        
        # Check format conversions
        format_results = files.get("format_conversions", {})
        if format_results:
            print(f"📄 Format Conversions: {len(format_results)} documents")
            for doc_name, formats in list(format_results.items())[:5]:  # Show first 5
                formats_present = [f for f, p in formats.items() if p]
                print(f"   - {doc_name}: {', '.join(formats_present)}")
            if len(format_results) > 5:
                print(f"   ... and {len(format_results) - 5} more")
        else:
            print("⚠️  No format conversions found")
        
        print()
        print("✅ Test complete! Check the docs/ folder to verify files.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)

