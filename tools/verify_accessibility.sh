#!/bin/bash

# Accessibility Features Verification Script
# This script verifies that key accessibility features are present in the code

echo "🔍 Verifying Accessibility Features in Sentio Dashboard"
echo "============================================================"
echo ""

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DASHBOARD_DIR="dashboard/src"
PASS_COUNT=0
FAIL_COUNT=0

check_feature() {
    local description=$1
    local file=$2
    local pattern=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: $description"
        ((PASS_COUNT++))
    else
        echo -e "${RED}❌ FAIL${NC}: $description"
        ((FAIL_COUNT++))
    fi
}

echo "1️⃣  Checking ARIA Labels..."
check_feature "ARIA labels in navigation" "$DASHBOARD_DIR/App.js" "aria-label="
check_feature "ARIA selected attribute" "$DASHBOARD_DIR/App.js" "aria-selected="
check_feature "ARIA controls attribute" "$DASHBOARD_DIR/App.js" "aria-controls="
check_feature "ARIA live regions" "$DASHBOARD_DIR/App.js" "aria-live="
echo ""

echo "2️⃣  Checking Semantic HTML Roles..."
check_feature "Navigation role" "$DASHBOARD_DIR/App.js" "role=\"navigation\""
check_feature "Main role" "$DASHBOARD_DIR/App.js" "role=\"main\""
check_feature "Banner role" "$DASHBOARD_DIR/App.js" "role=\"banner\""
check_feature "Tabpanel role" "$DASHBOARD_DIR/App.js" "role=\"tabpanel\""
check_feature "Dialog role" "$DASHBOARD_DIR/components/Onboarding.js" "role=\"dialog\""
echo ""

echo "3️⃣  Checking Keyboard Navigation..."
check_feature "Skip to main content link" "$DASHBOARD_DIR/App.js" "skip-to-main"
check_feature "Focus indicators in CSS" "$DASHBOARD_DIR/App.css" "outline:"
check_feature "Keyboard event handlers" "$DASHBOARD_DIR/components/Onboarding.js" "onKeyDown="
check_feature "Escape key handler" "$DASHBOARD_DIR/components/NotificationPreferences.js" "Escape"
echo ""

echo "4️⃣  Checking Form Accessibility..."
check_feature "Form labels with htmlFor" "$DASHBOARD_DIR/App.js" "htmlFor="
check_feature "Input IDs matching labels" "$DASHBOARD_DIR/App.js" "id=\"tier-select\""
check_feature "ARIA required attribute" "$DASHBOARD_DIR/App.js" "aria-required="
echo ""

echo "5️⃣  Checking New Components..."
check_feature "Onboarding component exists" "$DASHBOARD_DIR/components/Onboarding.js" "const Onboarding"
check_feature "NotificationPreferences exists" "$DASHBOARD_DIR/components/NotificationPreferences.js" "const NotificationPreferences"
check_feature "Onboarding CSS exists" "$DASHBOARD_DIR/components/Onboarding.css" ".onboarding-overlay"
check_feature "Preferences CSS exists" "$DASHBOARD_DIR/components/NotificationPreferences.css" ".preferences-overlay"
echo ""

echo "6️⃣  Checking Component Integration..."
check_feature "Onboarding imported in App" "$DASHBOARD_DIR/App.js" "import Onboarding"
check_feature "NotificationPreferences imported" "$DASHBOARD_DIR/App.js" "import NotificationPreferences"
check_feature "Settings button in header" "$DASHBOARD_DIR/App.js" "btn-preferences"
echo ""

echo "7️⃣  Checking Accessibility Features..."
check_feature "Toggle switches with role" "$DASHBOARD_DIR/components/NotificationPreferences.js" "role=\"switch\""
check_feature "Progress indicators" "$DASHBOARD_DIR/components/Onboarding.js" "role=\"progressbar\""
check_feature "Table scope attributes" "$DASHBOARD_DIR/App.js" "scope=\"col\""
check_feature "Status role for badges" "$DASHBOARD_DIR/App.js" "role=\"status\""
echo ""

echo "8️⃣  Checking Documentation..."
if [ -f "ACCESSIBILITY.md" ]; then
    echo -e "${GREEN}✅ PASS${NC}: ACCESSIBILITY.md exists"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}: ACCESSIBILITY.md exists"
    ((FAIL_COUNT++))
fi

if [ -f "UX_ACCESSIBILITY_SUMMARY.md" ]; then
    echo -e "${GREEN}✅ PASS${NC}: UX_ACCESSIBILITY_SUMMARY.md exists"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}: UX_ACCESSIBILITY_SUMMARY.md exists"
    ((FAIL_COUNT++))
fi
echo ""

echo "9️⃣  Checking Build Configuration..."
if grep -q "i18next" "dashboard/package.json" 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: i18next dependency installed"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}: i18next dependency installed"
    ((FAIL_COUNT++))
fi

if grep -q "i18next-browser-languagedetector" "dashboard/package.json" 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}: i18next-browser-languagedetector installed"
    ((PASS_COUNT++))
else
    echo -e "${RED}❌ FAIL${NC}: i18next-browser-languagedetector installed"
    ((FAIL_COUNT++))
fi
echo ""

# Summary
echo "============================================================"
echo "📊 Summary"
echo "============================================================"
echo -e "Total Checks: $((PASS_COUNT + FAIL_COUNT))"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 All accessibility features verified successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed. Please review the output above.${NC}"
    exit 1
fi
