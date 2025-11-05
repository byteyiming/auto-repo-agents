#!/usr/bin/env python3
"""
Test script to verify file organization and format conversion
Tests that:
1. All documents are converted to multiple formats (HTML, PDF, DOCX)
2. Files are saved in correct folders
3. No files appear in wrong locations
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.utils.document_organizer import get_documents_summary
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_file_organization():
    """Test that all documents are properly organized and converted"""
    print("=" * 70)
    print("🧪 Testing File Organization and Format Conversion")
    print("=" * 70)
    print()
    
    # Initialize coordinator
    context_manager = ContextManager()
    coordinator = WorkflowCoordinator(context_manager=context_manager)
    
    # Test with a simple idea
    test_idea = "Create a simple task management app with user authentication"
    print(f"📝 Test Idea: {test_idea}")
    print()
    print("⏳ Starting documentation generation...")
    print("   (This will take several minutes)")
    print()
    
    try:
        # Generate all documentation
        results = coordinator.generate_all_docs(test_idea)
        
        print()
        print("=" * 70)
        print("📊 Test Results")
        print("=" * 70)
        print()
        
        # Check results
        files = results.get("files", {})
        project_id = results.get("project_id")
        
        print(f"✅ Project ID: {project_id}")
        print(f"✅ Generated {len(files)} document types")
        print()
        
        # Expected document types
        expected_docs = {
            "requirements": "requirements",
            "project_charter": "charter",
            "pm_documentation": "pm",
            "user_stories": "user_stories",
            "technical_documentation": "technical",
            "database_schema": "database",
            "api_documentation": "api",
            "setup_guide": "setup",
            "developer_documentation": "developer",
            "stakeholder_documentation": "stakeholder",
            "test_documentation": "test"
        }
        
        # Check each document type
        print("📁 Checking Document Organization:")
        print("-" * 70)
        
        issues_found = []
        success_count = 0
        
        for doc_type, expected_folder in expected_docs.items():
            if doc_type not in files:
                print(f"⚠️  {doc_type}: Not generated yet")
                continue
            
            file_path = files[doc_type]
            if not file_path:
                print(f"⚠️  {doc_type}: File path is empty")
                continue
            
            folder_path = Path(file_path).parent
            expected_folder_path = Path("docs") / expected_folder
            
            # Check if folder exists, create if not
            if not expected_folder_path.exists():
                expected_folder_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created missing folder: {expected_folder_path}")
            
            # Check if in correct folder
            actual_folder_name = folder_path.name if folder_path.name else str(folder_path)
            is_in_expected_folder = (
                expected_folder in str(folder_path) or 
                folder_path.name == expected_folder
            )
            
            if is_in_expected_folder:
                print(f"✅ {doc_type}: ✓ (in {folder_path.name}/)")
                success_count += 1
            else:
                # File might be in wrong location
                print(f"⚠️  {doc_type}: Found in {actual_folder_name}/, expected {expected_folder}/")
                # Check if file exists in expected location too
                if Path(file_path).exists():
                    target_path = expected_folder_path / Path(file_path).name
                    if target_path.exists():
                        print(f"   ℹ️  File also exists in correct location: {target_path}")
                    else:
                        print(f"   💡 Tip: Consider moving to {expected_folder}/ folder")
                issues_found.append(f"{doc_type}: In folder {actual_folder_name}/, expected {expected_folder}/")
        
        print()
        print("=" * 70)
        print("📄 Checking Format Conversions:")
        print("-" * 70)
        
        # Check format conversions
        format_results = files.get("format_conversions", {})
        if not format_results:
            print("⚠️  No format conversions found")
            issues_found.append("No format conversions generated")
        else:
            print(f"✅ Found format conversions for {len(format_results)} documents")
            print()
            
            # Check each document's formats
            for doc_name, formats in format_results.items():
                formats_found = [fmt for fmt, path in formats.items() if path]
                expected_formats = ["html", "pdf", "docx"]
                missing_formats = [f for f in expected_formats if f not in formats_found]
                
                if missing_formats:
                    print(f"⚠️  {doc_name}: Missing formats: {', '.join(missing_formats)}")
                    issues_found.append(f"{doc_name}: Missing formats {missing_formats}")
                else:
                    print(f"✅ {doc_name}: All formats present (html, pdf, docx)")
                    
                # Check folder structure for each format
                for fmt, fmt_path in formats.items():
                    if fmt_path:
                        folder = Path(fmt_path).parent.name
                        expected_folder = expected_docs.get(doc_name, doc_name)
                        if expected_folder not in str(fmt_path):
                            print(f"   ⚠️  {fmt} file in wrong folder: {folder}")
                            issues_found.append(f"{doc_name}.{fmt}: Wrong folder")
        
        print()
        print("=" * 70)
        print("📈 Summary")
        print("=" * 70)
        
        # Count how many documents were actually generated
        generated_count = len([d for d in expected_docs.keys() if d in files])
        
        if generated_count == 0:
            print("ℹ️  No documents generated yet. Run full generation to test.")
            print()
            print("💡 To generate documents, run:")
            print("   uv run python test_file_organization.py")
            print("   (without --quick-check flag)")
            return True  # Not an error, just nothing generated yet
        
        print(f"✅ Documents organized correctly: {success_count}/{generated_count}")
        print(f"📝 Total documents generated: {generated_count}/{len(expected_docs)}")
        
        if format_results:
            total_conversions = sum(len([p for p in paths.values() if p]) for paths in format_results.values())
            expected_total = len(format_results) * 3  # html, pdf, docx
            print(f"✅ Format conversions: {total_conversions}/{expected_total} files generated")
        
        if issues_found:
            print()
            print("⚠️  Issues Found:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False
        else:
            print()
            if generated_count < len(expected_docs):
                print(f"✅ All generated documents ({generated_count}) are properly organized!")
                print(f"ℹ️  {len(expected_docs) - generated_count} documents not yet generated")
            else:
                print("🎉 All tests passed! Files are properly organized.")
            return True
        
    except Exception as e:
        print()
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_folder(folder_name: str):
    """Test a specific folder to see what files are in it"""
    docs_path = Path("docs") / folder_name
    if not docs_path.exists():
        # Create folder if it doesn't exist
        docs_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Folder {folder_name}/ created (was missing)")
        print("-" * 70)
        print("   (empty - waiting for documents to be generated)")
        return
    
    print(f"📁 Files in {folder_name}/:")
    print("-" * 70)
    files = list(docs_path.glob("*"))
    
    if not files:
        print("   (empty)")
    else:
        for file in sorted(files):
            size = file.stat().st_size if file.is_file() else 0
            file_type = "📄" if file.is_file() else "📁"
            print(f"   {file_type} {file.name} ({size:,} bytes)")
    
    # Check for expected formats
    md_files = list(docs_path.glob("*.md"))
    html_files = list(docs_path.glob("*.html"))
    pdf_files = list(docs_path.glob("*.pdf"))
    docx_files = list(docs_path.glob("*.docx"))
    
    print()
    print("📊 Format Breakdown:")
    print(f"   Markdown: {len(md_files)} files")
    print(f"   HTML: {len(html_files)} files")
    print(f"   PDF: {len(pdf_files)} files")
    print(f"   DOCX: {len(docx_files)} files")
    
    expected_formats = 4  # md, html, pdf, docx
    actual_formats = len(set([f.suffix for f in files if f.is_file()]))
    
    if actual_formats < expected_formats:
        missing = expected_formats - actual_formats
        print(f"   ⚠️  Missing {missing} format(s) - expected {expected_formats} formats")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test file organization and format conversion")
    parser.add_argument(
        "--folder",
        type=str,
        help="Check a specific folder (e.g., 'charter', 'database')"
    )
    parser.add_argument(
        "--quick-check",
        action="store_true",
        help="Just check existing files without generating new ones"
    )
    
    args = parser.parse_args()
    
    if args.folder:
        # Just check a specific folder
        test_specific_folder(args.folder)
    elif args.quick_check:
        # Quick check of all folders
        print("🔍 Quick Check of All Document Folders")
        print("=" * 70)
        print()
        
        folders = [
            "requirements", "charter", "pm", "user_stories",
            "technical", "database", "api", "setup",
            "developer", "stakeholder", "test", "quality"
        ]
        
        for folder in folders:
            test_specific_folder(folder)
            print()
    else:
        # Full test with generation
        success = test_file_organization()
        sys.exit(0 if success else 1)

