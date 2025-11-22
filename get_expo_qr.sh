#!/bin/bash

echo "🔍 Getting Expo Go connection info..."
echo ""

# The tunnel subdomain from .env
TUNNEL_SUBDOMAIN="bug-buster"

# Check if tunnel is active
if curl -s --max-time 5 "https://${TUNNEL_SUBDOMAIN}-22.ngrok.io" > /dev/null 2>&1; then
    TUNNEL_URL="https://${TUNNEL_SUBDOMAIN}-22.ngrok.io"
    echo "✅ Tunnel is ACTIVE at: $TUNNEL_URL"
    echo ""
    echo "📱 To open in Expo Go:"
    echo "   1. Open Expo Go app on your phone"
    echo "   2. Scan this QR code or enter the URL manually"
    echo ""
    echo "   Expo URL: exp://${TUNNEL_SUBDOMAIN}-22.ngrok.io:443"
    echo ""
    
    # Generate QR code
    echo "Generating QR code..."
    qrencode -t UTF8 "exp://${TUNNEL_SUBDOMAIN}-22.ngrok.io:443"
    
else
    echo "❌ Tunnel is OFFLINE at: https://${TUNNEL_SUBDOMAIN}-22.ngrok.io"
    echo ""
    echo "🔧 Fixing tunnel connection..."
    
    # Restart expo service
    sudo supervisorctl restart expo
    
    echo "⏳ Waiting for tunnel to connect (20 seconds)..."
    sleep 20
    
    # Check again
    if curl -s --max-time 5 "https://${TUNNEL_SUBDOMAIN}-22.ngrok.io" > /dev/null 2>&1; then
        echo "✅ Tunnel is now ACTIVE!"
        echo ""
        echo "📱 Expo URL: exp://${TUNNEL_SUBDOMAIN}-22.ngrok.io:443"
        qrencode -t UTF8 "exp://${TUNNEL_SUBDOMAIN}-22.ngrok.io:443"
    else
        echo "❌ Tunnel still offline. Checking alternative methods..."
        
        # Try localhost with ngrok info
        echo ""
        echo "🌐 Web Preview URL (works in browser):"
        echo "   https://bug-buster-22.preview.emergentagent.com"
        echo ""
        echo "📱 For Expo Go, you may need to:"
        echo "   1. Use LAN connection instead of tunnel"
        echo "   2. Or use the web preview URL in mobile browser"
    fi
fi
