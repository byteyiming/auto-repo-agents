#!/usr/bin/env python3
"""
Analyze why Gemini 2.5 Pro performed poorly in the improvement test
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except:
    pass

from src.agents.document_improver_agent import DocumentImproverAgent
from src.agents.quality_reviewer_agent import QualityReviewerAgent
from src.quality.document_type_quality_checker import DocumentTypeQualityChecker
from src.rate_limit.queue_manager import RequestQueue

def analyze_model_output(model_name: str):
    """Analyze model output to understand the issue"""
    print(f"\n{'='*80}")
    print(f"🔍 Analyzing {model_name} output")
    print(f"{'='*80}\n")
    
    os.environ['GEMINI_DEFAULT_MODEL'] = model_name
    
    # Test document
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
    
    rate_limiter = RequestQueue(max_rate=1000, period=60)
    document_type_checker = DocumentTypeQualityChecker()
    
    # Check initial
    quality_result_v1 = document_type_checker.check_quality_for_type(test_doc, test_doc_type)
    v1_score = quality_result_v1.get("overall_score", 0)
    
    print(f"📊 Initial Quality: {v1_score:.2f}/100")
    print(f"   Sections found: {quality_result_v1.get('sections', {}).get('found_count', 0)}/{quality_result_v1.get('sections', {}).get('required_count', 0)}")
    
    # Generate feedback
    print(f"\n🔍 Generating feedback...")
    quality_reviewer = QualityReviewerAgent(
        provider_name="gemini",
        model_name=model_name,
        rate_limiter=rate_limiter
    )
    feedback_report = quality_reviewer.generate({test_doc_type: test_doc})
    
    # Improve document
    print(f"\n🔧 Improving document...")
    document_improver = DocumentImproverAgent(
        provider_name="gemini",
        model_name=model_name,
        rate_limiter=rate_limiter
    )
    
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
    
    # Check improved
    quality_result_v2 = document_type_checker.check_quality_for_type(improved_doc, test_doc_type)
    v2_score = quality_result_v2.get("overall_score", 0)
    
    print(f"\n📊 Improved Quality: {v2_score:.2f}/100")
    print(f"   Sections found: {quality_result_v2.get('sections', {}).get('found_count', 0)}/{quality_result_v2.get('sections', {}).get('required_count', 0)}")
    
    # Analyze document structure
    print(f"\n📄 Document Analysis:")
    print(f"   Length: {len(improved_doc)} characters")
    print(f"   First 500 characters:")
    print("   " + "-" * 76)
    print("   " + improved_doc[:500].replace("\n", "\n   "))
    print("   " + "-" * 76)
    
    # Check for section headers
    import re
    headers = re.findall(r'^#+\s+(.+)$', improved_doc, re.MULTILINE)
    print(f"\n📋 Found {len(headers)} section headers:")
    for i, header in enumerate(headers[:10], 1):
        print(f"   {i}. {header}")
    
    # Check required sections
    required_sections = [
        r"^#+\s+System\s+Architecture",
        r"^#+\s+Technical\s+Stack",
        r"^#+\s+Database\s+Design",
        r"^#+\s+API\s+Design",
        r"^#+\s+Security"
    ]
    
    print(f"\n🔍 Required Sections Check:")
    for pattern in required_sections:
        found = bool(re.search(pattern, improved_doc, re.MULTILINE | re.IGNORECASE))
        section_name = pattern.replace('^#+\\s+', '').replace('\\s+', ' ')
        status = "✅" if found else "❌"
        print(f"   {status} {section_name}: {'Found' if found else 'Missing'}")
        if not found:
            # Try to find similar headers
            similar = [h for h in headers if section_name.lower().replace(' ', '') in h.lower().replace(' ', '')]
            if similar:
                print(f"      Similar headers found: {', '.join(similar[:3])}")
    
    return improved_doc

if __name__ == "__main__":
    print("="*80)
    print("🔬 Analyzing Gemini 2.5 Pro Output Issue")
    print("="*80)
    
    # Test both models
    for model in ["gemini-2.0-flash", "gemini-2.5-pro"]:
        try:
            doc = analyze_model_output(model)
            # Save to file for inspection
            output_file = f"test_output_{model.replace('-', '_').replace('.', '_')}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc)
            print(f"\n💾 Saved output to: {output_file}")
        except Exception as e:
            print(f"❌ Error analyzing {model}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)

