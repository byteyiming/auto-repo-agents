#!/bin/bash
# Quick test script for file organization

echo "🧪 Quick File Organization Test"
echo "================================"
echo ""

# Test 1: Check if all expected folders exist
echo "Test 1: Checking folder structure..."
expected_folders=("requirements" "charter" "pm" "user_stories" "technical" "database" "api" "setup" "developer" "stakeholder" "test" "quality")

missing_folders=()
for folder in "${expected_folders[@]}"; do
    if [ ! -d "docs/$folder" ]; then
        missing_folders+=("$folder")
    fi
done

if [ ${#missing_folders[@]} -eq 0 ]; then
    echo "✅ All expected folders exist"
else
    echo "⚠️  Missing folders: ${missing_folders[*]}"
fi
echo ""

# Test 2: Check format completeness
echo "Test 2: Checking format completeness..."
incomplete=()
for folder in "${expected_folders[@]}"; do
    if [ -d "docs/$folder" ]; then
        md_count=$(ls docs/$folder/*.md 2>/dev/null | wc -l | tr -d ' ')
        html_count=$(ls docs/$folder/*.html 2>/dev/null | wc -l | tr -d ' ')
        pdf_count=$(ls docs/$folder/*.pdf 2>/dev/null | wc -l | tr -d ' ')
        docx_count=$(ls docs/$folder/*.docx 2>/dev/null | wc -l | tr -d ' ')
        
        if [ "$md_count" -eq 0 ] || [ "$html_count" -eq 0 ] || [ "$pdf_count" -eq 0 ] || [ "$docx_count" -eq 0 ]; then
            incomplete+=("$folder")
            echo "⚠️  $folder: md=$md_count html=$html_count pdf=$pdf_count docx=$docx_count"
        else
            echo "✅ $folder: All formats present"
        fi
    fi
done

if [ ${#incomplete[@]} -eq 0 ]; then
    echo "✅ All folders have complete formats"
else
    echo "⚠️  Incomplete folders: ${incomplete[*]}"
fi
echo ""

# Test 3: Check for misplaced files in user_stories
echo "Test 3: Checking for misplaced files..."
if [ -d "docs/user_stories" ]; then
    user_stories_files=$(ls docs/user_stories/*.md 2>/dev/null | xargs -n1 basename 2>/dev/null || echo "")
    misplaced=0
    for file in $user_stories_files; do
        if [ "$file" != "user_stories.md" ] && [ -n "$file" ]; then
            echo "⚠️  Found unexpected file in user_stories/: $file"
            misplaced=$((misplaced + 1))
        fi
    done
    if [ $misplaced -eq 0 ]; then
        echo "✅ user_stories/ folder only contains correct files"
    fi
fi

echo ""
echo "✅ Quick check complete!"
echo ""
echo "For detailed test, run:"
echo "  uv run python test_file_organization.py --quick-check"
echo ""
echo "For full test with generation, run:"
echo "  uv run python test_file_organization.py"

