/**
 * Web polyfills for React Native APIs that don't exist on web
 * This fixes the "setNativeProps is not a function" error
 */

import { Platform } from 'react-native';

if (Platform.OS === 'web') {
  // Polyfill setNativeProps for web
  // This is a no-op on web since we don't have native props
  if (typeof Element !== 'undefined' && !Element.prototype.setNativeProps) {
    Element.prototype.setNativeProps = function(props: any) {
      // No-op on web
      // On web, React handles prop updates automatically
    };
  }

  // Also patch React refs to prevent setNativeProps calls
  const originalCreateElement = React.createElement;
  
  // @ts-ignore
  React.createElement = function(...args) {
    const element = originalCreateElement.apply(this, args);
    
    // If element has a ref callback, wrap it to add setNativeProps
    if (element && element.ref && typeof element.ref === 'function') {
      const originalRef = element.ref;
      element.ref = function(node: any) {
        if (node && !node.setNativeProps) {
          node.setNativeProps = function() {
            // No-op on web
          };
        }
        return originalRef(node);
      };
    }
    
    return element;
  };
}

// Export a function to initialize polyfills
export function initializeWebPolyfills() {
  if (Platform.OS === 'web') {
    console.log('✅ Web polyfills initialized');
  }
}
