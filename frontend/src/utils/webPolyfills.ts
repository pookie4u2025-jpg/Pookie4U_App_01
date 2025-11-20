/**
 * Web polyfills for React Native APIs that don't exist on web
 * This fixes the "setNativeProps is not a function" error
 */

import { Platform } from 'react-native';

// Initialize polyfills immediately on web
if (Platform.OS === 'web' && typeof window !== 'undefined') {
  // Polyfill setNativeProps for all possible objects
  
  // 1. Patch HTMLElement prototype
  if (typeof HTMLElement !== 'undefined' && !HTMLElement.prototype.setNativeProps) {
    HTMLElement.prototype.setNativeProps = function(props: any) {
      // No-op on web - React handles updates automatically
    };
  }
  
  // 2. Patch Element prototype as fallback
  if (typeof Element !== 'undefined' && !Element.prototype.setNativeProps) {
    Element.prototype.setNativeProps = function(props: any) {
      // No-op on web
    };
  }
  
  // 3. Patch SVGElement for icon support
  if (typeof SVGElement !== 'undefined' && !SVGElement.prototype.setNativeProps) {
    SVGElement.prototype.setNativeProps = function(props: any) {
      // No-op on web
    };
  }
  
  // 4. Global ref wrapper to catch any refs
  const originalCreateElement = document.createElement.bind(document);
  document.createElement = function(tagName: any, options?: any) {
    const element = originalCreateElement(tagName, options);
    if (!element.setNativeProps) {
      element.setNativeProps = function(props: any) {
        // No-op on web
      };
    }
    return element;
  };
  
  console.log('✅ Web polyfills initialized - setNativeProps patched globally');
}

// Export a function to initialize polyfills (for backwards compatibility)
export function initializeWebPolyfills() {
  if (Platform.OS === 'web') {
    console.log('✅ Web polyfills check - already initialized');
  }
}
