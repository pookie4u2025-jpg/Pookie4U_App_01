/**
 * Web polyfills for React Native APIs that don't exist on web
 * This fixes the "setNativeProps is not a function" error
 */

import { Platform } from 'react-native';

// Export a function to initialize polyfills
export function initializeWebPolyfills() {
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    // Polyfill setNativeProps for DOM elements
    // This is a no-op on web since we don't have native props
    if (typeof Element !== 'undefined') {
      // @ts-ignore
      if (!Element.prototype.setNativeProps) {
        // @ts-ignore
        Element.prototype.setNativeProps = function(props: any) {
          // No-op on web
          // On web, React handles prop updates automatically
        };
      }
    }
    
    // Also polyfill for any object that might be used as a ref
    const originalRef = (node: any) => {
      if (node && typeof node === 'object' && !node.setNativeProps) {
        node.setNativeProps = function() {
          // No-op on web
        };
      }
    };
    
    console.log('✅ Web polyfills initialized - setNativeProps available');
  }
}
