#!/usr/bin/env python3
"""
Test script to compare document improvement quality with different Gemini models
Tests the quality improvement loop with gemini-2.0-flash vs gemini-2.5-pro
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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env file from {env_path}")
    else:
        print(f"⚠️  .env file not found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, skipping .env loading")
except Exception as e:
    print(f"⚠️  Error loading .env: {e}")

def test_improvement_with_model(model_name: str):
    """Test document improvement with a specific model"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing {model_name}")
    print(f"{'='*80}\n")
    
    # Set model in environment
    os.environ['GEMINI_DEFAULT_MODEL'] = model_name
    
    from src.agents.document_improver_agent import DocumentImproverAgent
    from src.agents.quality_reviewer_agent import QualityReviewerAgent
    from src.quality.document_type_quality_checker import DocumentTypeQualityChecker
    from src.context.shared_context import AgentType
    from src.rate_limit.queue_manager import RequestQueue
    
    # Create a low-quality test document (technical_documentation)
    test_doc = """# Technical Documentation

## Overview
This is a test document.

## System Architecture
Basic architecture.

## Technical Stack
Python, FastAPI.

## Database Design
Some database info.

## API Design
REST API.

## Security
Basic security.
"""
    
    test_doc_type = "technical_documentation"
    agent_type = AgentType.TECHNICAL_DOCUMENTATION
    
    try:
        # Initialize components
        rate_limiter = RequestQueue(max_rate=1000, period=60)
        
        document_type_checker = DocumentTypeQualityChecker()
        
        # Check V1 quality
        print("📊 Checking initial quality...")
        quality_result_v1 = document_type_checker.check_quality_for_type(
            test_doc,
            document_type=test_doc_type
        )
        v1_score = quality_result_v1.get("overall_score", 0)
        v1_word_count = quality_result_v1.get("word_count", {}).get("word_count", 0)
        v1_sections = quality_result_v1.get("sections", {}).get("found_count", 0)
        v1_required = quality_result_v1.get("sections", {}).get("required_count", 0)
        v1_missing = quality_result_v1.get("sections", {}).get("missing_sections", [])
        v1_readability = quality_result_v1.get("readability", {}).get("readability_score", 0)
        
        print(f"   Initial Score: {v1_score:.2f}/100")
        print(f"   Word Count: {v1_word_count} words")
        print(f"   Sections: {v1_sections}/{v1_required} found")
        if v1_missing:
            missing_clean = [s.replace('^#+\\s+', '').replace('\\s+', ' ') for s in v1_missing[:3]]
            print(f"   Missing: {', '.join(missing_clean)}")
        print(f"   Readability: {v1_readability:.1f}")
        
        # Generate quality feedback
        print(f"\n🔍 Generating quality feedback with {model_name}...")
        quality_reviewer = QualityReviewerAgent(
            provider_name="gemini",
            model_name=model_name,
            rate_limiter=rate_limiter
        )
        
        feedback_start = datetime.now()
        feedback_report = quality_reviewer.generate({test_doc_type: test_doc})
        feedback_time = (datetime.now() - feedback_start).total_seconds()
        print(f"   ✅ Feedback generated in {feedback_time:.2f}s ({len(feedback_report)} chars)")
        
        # Improve document
        print(f"\n🔧 Improving document with {model_name}...")
        document_improver = DocumentImproverAgent(
            provider_name="gemini",
            model_name=model_name,
            rate_limiter=rate_limiter
        )
        
        improve_start = datetime.now()
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
        improve_time = (datetime.now() - improve_start).total_seconds()
        total_time = feedback_time + improve_time
        
        print(f"   ✅ Improved in {improve_time:.2f}s (total: {total_time:.2f}s)")
        print(f"   Length: {len(test_doc)} → {len(improved_doc)} chars ({len(improved_doc) - len(test_doc):+d})")
        
        # Check V2 quality
        print(f"\n📊 Checking improved quality...")
        quality_result_v2 = document_type_checker.check_quality_for_type(
            improved_doc,
            document_type=test_doc_type
        )
        v2_score = quality_result_v2.get("overall_score", 0)
        v2_word_count = quality_result_v2.get("word_count", {}).get("word_count", 0)
        v2_sections = quality_result_v2.get("sections", {}).get("found_count", 0)
        v2_missing = quality_result_v2.get("sections", {}).get("missing_sections", [])
        v2_readability = quality_result_v2.get("readability", {}).get("readability_score", 0)
        
        improvement = v2_score - v1_score
        word_increase = v2_word_count - v1_word_count
        sections_added = len(v1_missing) - len(v2_missing)
        readability_improvement = v2_readability - v1_readability
        
        print(f"   Improved Score: {v2_score:.2f}/100")
        print(f"   Word Count: {v2_word_count} words (+{word_increase})")
        print(f"   Sections: {v2_sections}/{v1_required} found ({sections_added:+d})")
        if v2_missing:
            missing_clean = [s.replace('^#+\\s+', '').replace('\\s+', ' ') for s in v2_missing[:3]]
            print(f"   Still Missing: {', '.join(missing_clean)}")
        print(f"   Readability: {v2_readability:.1f} ({readability_improvement:+.1f})")
        print(f"\n📈 Quality Improvement: {improvement:+.2f} points ({improvement/v1_score*100 if v1_score > 0 else 0:+.1f}%)")
        
        return {
            "model": model_name,
            "v1_score": v1_score,
            "v2_score": v2_score,
            "improvement": improvement,
            "improvement_percent": improvement/v1_score*100 if v1_score > 0 else 0,
            "total_time": total_time,
            "feedback_time": feedback_time,
            "improve_time": improve_time,
            "v1_word_count": v1_word_count,
            "v2_word_count": v2_word_count,
            "word_increase": word_increase,
            "v1_sections": v1_sections,
            "v2_sections": v2_sections,
            "sections_added": sections_added,
            "v1_readability": v1_readability,
            "v2_readability": v2_readability,
            "readability_improvement": readability_improvement,
            "v1_length": len(test_doc),
            "v2_length": len(improved_doc),
            "length_increase": len(improved_doc) - len(test_doc),
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main test function"""
    print("="*80)
    print("🔬 Gemini Model Comparison: Document Improvement Quality")
    print("="*80)
    print("\nThis test compares:")
    print("  - gemini-2.0-flash (fast, balanced quality)")
    print("  - gemini-2.5-pro (slower, highest quality)")
    print("\nTesting document improvement with quality metrics...")
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\n❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("   Please set it in your .env file:")
        print("   export GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    print(f"\n✅ GEMINI_API_KEY found")
    
    models = ["gemini-2.0-flash", "gemini-2.5-pro"]
    results = {}
    
    for model in models:
        try:
            result = test_improvement_with_model(model)
            if result:
                results[model] = result
            print("\n" + "="*80)
        except KeyboardInterrupt:
            print(f"\n⚠️  Test interrupted during {model}")
            break
        except Exception as e:
            print(f"❌ Failed to test {model}: {e}")
            import traceback
            traceback.print_exc()
    
    # Compare results
    if len(results) >= 2:
        print("\n" + "="*80)
        print("📊 COMPARISON RESULTS")
        print("="*80)
        
        flash = results.get("gemini-2.0-flash")
        pro = results.get("gemini-2.5-pro")
        
        if flash and pro:
            print(f"\n{'Metric':<35} {'2.0-flash':<20} {'2.5-pro':<20} {'Difference':<15}")
            print("-"*90)
            
            # Quality improvement
            flash_imp = flash["improvement"]
            pro_imp = pro["improvement"]
            diff_imp = pro_imp - flash_imp
            print(f"{'Quality Improvement':<35} {flash_imp:>+8.2f} points    {pro_imp:>+8.2f} points    {diff_imp:>+8.2f} ({'✅' if diff_imp > 0 else '❌'})")
            
            # Final score
            flash_score = flash["v2_score"]
            pro_score = pro["v2_score"]
            diff_score = pro_score - flash_score
            print(f"{'Final Quality Score':<35} {flash_score:>8.2f}/100      {pro_score:>8.2f}/100      {diff_score:>+8.2f} ({'✅' if diff_score > 0 else '❌'})")
            
            # Time
            flash_time = flash["total_time"]
            pro_time = pro["total_time"]
            diff_time = pro_time - flash_time
            print(f"{'Total Time':<35} {flash_time:>8.2f}s        {pro_time:>8.2f}s        {diff_time:>+8.2f}s ({'✅' if diff_time < 0 else '❌'})")
            
            # Word increase
            flash_words = flash["word_increase"]
            pro_words = pro["word_increase"]
            diff_words = pro_words - flash_words
            print(f"{'Word Count Increase':<35} {flash_words:>8} words    {pro_words:>8} words    {diff_words:>+8} ({'✅' if diff_words > 0 else '❌'})")
            
            # Sections added
            flash_sec = flash["sections_added"]
            pro_sec = pro["sections_added"]
            diff_sec = pro_sec - flash_sec
            print(f"{'Sections Added':<35} {flash_sec:>8}           {pro_sec:>8}           {diff_sec:>+8} ({'✅' if diff_sec > 0 else '❌'})")
            
            # Readability improvement
            flash_read = flash["readability_improvement"]
            pro_read = pro["readability_improvement"]
            diff_read = pro_read - flash_read
            print(f"{'Readability Improvement':<35} {flash_read:>+8.1f}        {pro_read:>+8.1f}        {diff_read:>+8.1f} ({'✅' if diff_read > 0 else '❌'})")
            
            print("\n" + "="*80)
            print("💡 RECOMMENDATION")
            print("="*80)
            
            # Analyze results
            pro_better_quality = pro_imp > flash_imp * 1.1  # 10% better
            pro_better_score = pro_score > flash_score
            flash_faster = flash_time < pro_time * 0.8  # 20% faster
            
            if pro_better_quality and pro_better_score:
                print("✅ RECOMMEND: gemini-2.5-pro")
                print("   - Significantly better quality improvement")
                print("   - Higher final quality score")
                if not flash_faster:
                    print("   - Worth the extra time for better quality")
            elif flash_better_quality := (flash_imp > pro_imp * 1.1):
                print("✅ RECOMMEND: gemini-2.0-flash")
                print("   - Better quality improvement")
                print("   - Faster execution")
                print("   - Better cost/performance ratio")
            else:
                if pro_better_score:
                    print("✅ RECOMMEND: gemini-2.5-pro for critical documents")
                    print("   - Higher final quality score")
                    print("   - Better for important documentation")
                else:
                    print("✅ RECOMMEND: gemini-2.0-flash for general use")
                    print("   - Good quality improvement")
                    print("   - Faster execution")
                    print("   - More cost-effective")
            
            print(f"\n📈 Quality Improvement: {'2.5-pro wins' if pro_imp > flash_imp else '2.0-flash wins'} ({abs(diff_imp):.2f} points difference)")
            print(f"⚡ Speed: {'2.0-flash wins' if flash_faster else '2.5-pro wins'} ({abs(diff_time):.2f}s difference)")
            print(f"🏆 Final Score: {'2.5-pro wins' if pro_score > flash_score else '2.0-flash wins'} ({abs(diff_score):.2f} points difference)")
        else:
            print("❌ Missing results for comparison")
    elif len(results) == 1:
        model = list(results.keys())[0]
        result = results[model]
        print(f"\n✅ Tested {model} successfully")
        print(f"   Quality Improvement: {result['improvement']:+.2f} points")
        print(f"   Final Score: {result['v2_score']:.2f}/100")
        print(f"   Time: {result['total_time']:.2f}s")
    else:
        print("❌ No models tested successfully")
    
    print("\n" + "="*80)
    print("✅ Test completed!")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

