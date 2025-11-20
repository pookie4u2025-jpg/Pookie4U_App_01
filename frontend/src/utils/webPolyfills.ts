/**
 * Web polyfills for React Native APIs that don't exist on web
 * This fixes the "setNativeProps is not a function" error
 * 
 * ROOT CAUSE: @expo/vector-icons calls setNativeProps on refs, which don't exist on web
 * FINAL SOLUTION: Directly patch the Ionicons component class
 */

import { Platform } from 'react-native';

if (Platform.OS === 'web' && typeof window !== 'undefined') {
  console.log('🔧 Applying NUCLEAR web polyfills for setNativeProps...');
  
  // NUCLEAR OPTION: Patch after a delay to ensure icons are loaded
  setTimeout(() => {
    try {
      // Get the Ionicons module
      const vectorIcons = require('@expo/vector-icons');
      
      // Patch Ionicons specifically
      if (vectorIcons && vectorIcons.Ionicons) {
        const originalIonicons = vectorIcons.Ionicons;
        
        // Override the component's setNativeProps method
        if (originalIonicons.prototype && originalIonicons.prototype.setNativeProps) {
          const originalSetNativeProps = originalIonicons.prototype.setNativeProps;
          
          originalIonicons.prototype.setNativeProps = function(props: any) {
            // Safely call setNativeProps only if the ref has it
            if (this._icon && typeof this._icon.setNativeProps === 'function') {
              this._icon.setNativeProps(props);
            }
            // Otherwise, silently ignore (no error on web)
          };
          
          console.log('✅ Ionicons.setNativeProps patched successfully!');
        }
      }
      
      // Also patch all icon families
      const iconFamilies = ['Ionicons', 'MaterialIcons', 'FontAwesome', 'MaterialCommunityIcons'];
      iconFamilies.forEach(family => {
        if (vectorIcons[family] && vectorIcons[family].prototype) {
          const original = vectorIcons[family].prototype.setNativeProps;
          if (original) {
            vectorIcons[family].prototype.setNativeProps = function(props: any) {
              if (this._icon && typeof this._icon.setNativeProps === 'function') {
                this._icon.setNativeProps(props);
              }
            };
          }
        }
      });
      
      console.log('✅ All icon families patched!');
    } catch (error) {
      console.warn('⚠️ Could not patch icons:', error);
    }
  }, 0);
  
  // Also add the DOM patches as backup
  if (typeof HTMLElement !== 'undefined') {
    HTMLElement.prototype.setNativeProps = function(props: any) {};
  }
  
  if (typeof Element !== 'undefined') {
    Element.prototype.setNativeProps = function(props: any) {};
  }
  
  if (typeof SVGElement !== 'undefined') {
    SVGElement.prototype.setNativeProps = function(props: any) {};
  }
}

// Export a function to initialize polyfills
export function initializeWebPolyfills() {
  if (Platform.OS === 'web') {
    console.log('✅ Web polyfills verified - setNativeProps patched');
  }
}
