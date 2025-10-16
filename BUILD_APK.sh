#!/bin/bash

echo "================================================"
echo "🚀 POOKIE4U APK BUILD SCRIPT"
echo "================================================"
echo ""

# Navigate to frontend
cd /app/frontend

echo "Step 1: Checking if you're logged in to Expo..."
if eas whoami > /dev/null 2>&1; then
    echo "✅ Already logged in as: $(eas whoami)"
else
    echo "❌ Not logged in to Expo"
    echo ""
    echo "Please run: eas login"
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "Step 2: Configuring EAS build..."
eas build:configure -p android --non-interactive || echo "Already configured"

echo ""
echo "Step 3: Starting Android APK build..."
echo "⏱️  This will take 20-30 minutes..."
echo ""

eas build --profile preview --platform android --non-interactive

echo ""
echo "================================================"
echo "✅ BUILD COMPLETE!"
echo "================================================"
echo ""
echo "Check the output above for:"
echo "  - Build URL (to monitor progress)"
echo "  - APK Download URL (to share with friends)"
echo ""
echo "Or check your builds at:"
echo "  https://expo.dev/accounts/$(eas whoami)/projects/pookie4u/builds"
echo ""
