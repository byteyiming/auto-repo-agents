#!/usr/bin/env python3
"""
Test script to compare Gemini 2.5 Pro vs 2.0 Flash for document improvement
Tests the quality improvement loop with both models
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.agents.document_improver_agent import DocumentImproverAgent
from src.agents.quality_reviewer_agent import QualityReviewerAgent
from src.quality.document_type_quality_checker import DocumentTypeQualityChecker
from src.context.shared_context import AgentType
from src.utils.file_manager import FileManager
from src.rate_limit.queue_manager import RequestQueue


def test_model_improvement(model_name: str, test_doc_type: str = "technical_documentation"):
    """Test document improvement with a specific model"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing {model_name} for {test_doc_type} improvement")
    print(f"{'='*80}\n")
    
    # Create temporary directory for test
    temp_dir = Path(tempfile.mkdtemp())
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    
    try:
        # Initialize context manager and coordinator with specific model
        context_manager = ContextManager(db_path=temp_db_path)
        
        # Set environment variable to use specific model
        os.environ['GEMINI_DEFAULT_MODEL'] = model_name
        
        coordinator = WorkflowCoordinator(
            context_manager=context_manager,
            provider_name="gemini"
        )
        
        # Create a simple test document (low quality)
        test_doc = f"""# {test_doc_type.replace('_', ' ').title()}

## Overview
This is a test document with low quality.

## Section 1
Some basic content here.

## Section 2
More content.

## Conclusion
That's it.
"""
        
        # Check initial quality
        document_type_checker = DocumentTypeQualityChecker()
        quality_result_v1 = document_type_checker.check_quality_for_type(
            test_doc,
            document_type=test_doc_type
        )
        v1_score = quality_result_v1.get("overall_score", 0)
        
        print(f"📊 Initial Quality Score: {v1_score:.2f}/100")
        print(f"   - Word Count: {quality_result_v1.get('word_count', {}).get('word_count', 0)}")
        print(f"   - Sections: {quality_result_v1.get('sections', {}).get('found_count', 0)}/{quality_result_v1.get('sections', {}).get('required_count', 0)}")
        print(f"   - Readability: {quality_result_v1.get('readability', {}).get('readability_score', 0):.1f}")
        
        # Generate quality feedback
        print(f"\n🔍 Generating quality feedback with {model_name}...")
        quality_reviewer = QualityReviewerAgent(
            provider_name="gemini",
            model_name=model_name
        )
        
        feedback_report = quality_reviewer.generate({test_doc_type: test_doc})
        print(f"✅ Quality feedback generated: {len(feedback_report)} characters")
        
        # Improve document
        print(f"\n🔧 Improving document with {model_name}...")
        document_improver = DocumentImproverAgent(
            provider_name="gemini",
            model_name=model_name
        )
        
        start_time = datetime.now()
        improved_doc = document_improver.improve_document(
            original_document=test_doc,
            document_type=test_doc_type,
            quality_feedback=feedback_report,
            quality_score=v1_score,
            quality_details={
                "word_count": quality_result_v1.get("word_count", {}),
                "sections": quality_result_v1.get("sections", {}),
                "readability": quality_result_v1.get("readability", {})
            }
        )
        end_time = datetime.now()
        improvement_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Document improved in {improvement_time:.2f} seconds")
        print(f"   - Original length: {len(test_doc)} characters")
        print(f"   - Improved length: {len(improved_doc)} characters")
        print(f"   - Length increase: {len(improved_doc) - len(test_doc)} characters ({((len(improved_doc) - len(test_doc)) / len(test_doc) * 100):.1f}%)")
        
        # Check improved quality
        quality_result_v2 = document_type_checker.check_quality_for_type(
            improved_doc,
            document_type=test_doc_type
        )
        v2_score = quality_result_v2.get("overall_score", 0)
        improvement = v2_score - v1_score
        
        print(f"\n📊 Improved Quality Score: {v2_score:.2f}/100")
        print(f"   - Word Count: {quality_result_v2.get('word_count', {}).get('word_count', 0)}")
        print(f"   - Sections: {quality_result_v2.get('sections', {}).get('found_count', 0)}/{quality_result_v2.get('sections', {}).get('required_count', 0)}")
        print(f"   - Readability: {quality_result_v2.get('readability', {}).get('readability_score', 0):.1f}")
        print(f"\n📈 Improvement: {improvement:+.2f} points ({improvement/v1_score*100 if v1_score > 0 else 0:+.1f}%)")
        
        # Check if missing sections were added
        v1_missing = quality_result_v1.get("sections", {}).get("missing_sections", [])
        v2_missing = quality_result_v2.get("sections", {}).get("missing_sections", [])
        sections_added = len(v1_missing) - len(v2_missing)
        
        if sections_added > 0:
            print(f"✅ Added {sections_added} missing section(s)")
        elif len(v2_missing) < len(v1_missing):
            print(f"✅ Reduced missing sections from {len(v1_missing)} to {len(v2_missing)}")
        else:
            print(f"⚠️  Still missing {len(v2_missing)} section(s)")
        
        # Save results
        results = {
            "model": model_name,
            "document_type": test_doc_type,
            "v1_score": v1_score,
            "v2_score": v2_score,
            "improvement": improvement,
            "improvement_percent": improvement/v1_score*100 if v1_score > 0 else 0,
            "improvement_time": improvement_time,
            "v1_length": len(test_doc),
            "v2_length": len(improved_doc),
            "length_increase": len(improved_doc) - len(test_doc),
            "sections_added": sections_added,
            "v1_word_count": quality_result_v1.get("word_count", {}).get("word_count", 0),
            "v2_word_count": quality_result_v2.get("word_count", {}).get("word_count", 0),
            "v1_sections": quality_result_v1.get("sections", {}).get("found_count", 0),
            "v2_sections": quality_result_v2.get("sections", {}).get("found_count", 0),
            "v1_readability": quality_result_v1.get("readability", {}).get("readability_score", 0),
            "v2_readability": quality_result_v2.get("readability", {}).get("readability_score", 0),
        }
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Cleanup
        context_manager.close()
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def compare_models():
    """Compare Gemini 2.0 Flash vs 2.5 Pro"""
    print("="*80)
    print("🔬 Gemini Model Comparison Test")
    print("="*80)
    print("\nThis test will compare:")
    print("  - gemini-2.0-flash (fast, balanced)")
    print("  - gemini-2.5-pro (slower, highest quality)")
    print("\nTesting document improvement quality and speed...")
    
    models = ["gemini-2.0-flash", "gemini-2.5-pro"]
    test_doc_type = "technical_documentation"
    
    results = {}
    
    for model in models:
        try:
            result = test_model_improvement(model, test_doc_type)
            if result:
                results[model] = result
        except Exception as e:
            print(f"❌ Failed to test {model}: {e}")
            import traceback
            traceback.print_exc()
    
    # Compare results
    if len(results) == 2:
        print("\n" + "="*80)
        print("📊 Comparison Results")
        print("="*80)
        
        flash_result = results.get("gemini-2.0-flash")
        pro_result = results.get("gemini-2.5-pro")
        
        if flash_result and pro_result:
            print(f"\n{'Metric':<30} {'2.0-flash':<20} {'2.5-pro':<20} {'Winner':<10}")
            print("-"*80)
            
            # Quality improvement
            flash_improvement = flash_result["improvement"]
            pro_improvement = pro_result["improvement"]
            winner_improvement = "2.5-pro" if pro_improvement > flash_improvement else "2.0-flash"
            print(f"{'Quality Improvement':<30} {flash_improvement:>+8.2f} points      {pro_improvement:>+8.2f} points      {winner_improvement:<10}")
            
            # Final score
            flash_score = flash_result["v2_score"]
            pro_score = pro_result["v2_score"]
            winner_score = "2.5-pro" if pro_score > flash_score else "2.0-flash"
            print(f"{'Final Quality Score':<30} {flash_score:>8.2f}/100        {pro_score:>8.2f}/100        {winner_score:<10}")
            
            # Improvement time
            flash_time = flash_result["improvement_time"]
            pro_time = pro_result["improvement_time"]
            winner_time = "2.0-flash" if flash_time < pro_time else "2.5-pro"
            print(f"{'Improvement Time':<30} {flash_time:>8.2f}s          {pro_time:>8.2f}s          {winner_time:<10}")
            
            # Length increase
            flash_length = flash_result["length_increase"]
            pro_length = pro_result["length_increase"]
            winner_length = "2.5-pro" if pro_length > flash_length else "2.0-flash"
            print(f"{'Length Increase':<30} {flash_length:>8} chars      {pro_length:>8} chars      {winner_length:<10}")
            
            # Sections added
            flash_sections = flash_result["sections_added"]
            pro_sections = pro_result["sections_added"]
            winner_sections = "2.5-pro" if pro_sections > flash_sections else "2.0-flash"
            print(f"{'Sections Added':<30} {flash_sections:>8}           {pro_sections:>8}           {winner_sections:<10}")
            
            # Word count increase
            flash_words = pro_result["v2_word_count"] - flash_result["v1_word_count"]
            pro_words = pro_result["v2_word_count"] - pro_result["v1_word_count"]
            winner_words = "2.5-pro" if pro_words > flash_words else "2.0-flash"
            print(f"{'Word Count Increase':<30} {flash_words:>8} words      {pro_words:>8} words      {winner_words:<10}")
            
            print("\n" + "="*80)
            print("📝 Summary")
            print("="*80)
            
            if pro_improvement > flash_improvement:
                print(f"✅ gemini-2.5-pro shows BETTER quality improvement (+{pro_improvement - flash_improvement:.2f} points)")
            else:
                print(f"✅ gemini-2.0-flash shows BETTER quality improvement (+{flash_improvement - pro_improvement:.2f} points)")
            
            if flash_time < pro_time:
                print(f"⚡ gemini-2.0-flash is FASTER ({pro_time - flash_time:.2f}s faster)")
            else:
                print(f"⚡ gemini-2.5-pro is FASTER ({flash_time - pro_time:.2f}s faster)")
            
            if pro_score > flash_score:
                print(f"🏆 gemini-2.5-pro achieves HIGHER final quality score ({pro_score - flash_score:.2f} points higher)")
            else:
                print(f"🏆 gemini-2.0-flash achieves HIGHER final quality score ({flash_score - pro_score:.2f} points higher)")
            
            # Recommendation
            print("\n" + "="*80)
            print("💡 Recommendation")
            print("="*80)
            
            if pro_improvement > flash_improvement * 1.2:  # 20% better improvement
                print("✅ RECOMMEND: gemini-2.5-pro for document improvement")
                print("   - Significantly better quality improvement")
                print("   - Worth the extra time for higher quality")
            elif flash_improvement > pro_improvement * 1.1:  # 10% better improvement
                print("✅ RECOMMEND: gemini-2.0-flash for document improvement")
                print("   - Better quality improvement")
                print("   - Faster execution")
            else:
                if pro_score > flash_score:
                    print("✅ RECOMMEND: gemini-2.5-pro for document improvement")
                    print("   - Higher final quality score")
                    print("   - Better for critical documents")
                else:
                    print("✅ RECOMMEND: gemini-2.0-flash for document improvement")
                    print("   - Good quality improvement")
                    print("   - Faster execution")
                    print("   - Better cost/performance ratio")
        else:
            print("❌ Missing results for comparison")
    else:
        print(f"⚠️  Only {len(results)} model(s) tested successfully. Cannot compare.")
    
    return results


if __name__ == "__main__":
    print("🚀 Starting Gemini Model Comparison Test")
    print("="*80)
    print("\n⚠️  This test requires:")
    print("   - GEMINI_API_KEY environment variable")
    print("   - Active internet connection")
    print("   - May take several minutes to complete")
    print("\n" + "="*80)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("   Please set it in your .env file or environment")
        sys.exit(1)
    
    # Run comparison
    try:
        results = compare_models()
        print("\n✅ Test completed!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

