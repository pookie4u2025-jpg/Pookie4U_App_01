/**
 * Web polyfills for React Native APIs that don't exist on web
 * This fixes the "setNativeProps is not a function" error
 * 
 * ROOT CAUSE: @expo/vector-icons calls setNativeProps on refs, which don't exist on web
 * SOLUTION: Patch React.createElement to add setNativeProps to all ref callbacks
 */

import React from 'react';
import { Platform } from 'react-native';

// Store original createElement
const originalCreateElement = React.createElement;

if (Platform.OS === 'web' && typeof window !== 'undefined') {
  console.log('🔧 Applying web polyfills for setNativeProps...');
  
  // 1. Patch all DOM element prototypes
  if (typeof HTMLElement !== 'undefined') {
    HTMLElement.prototype.setNativeProps = function(props: any) {
      // No-op on web - React handles updates automatically
    };
  }
  
  if (typeof Element !== 'undefined') {
    Element.prototype.setNativeProps = function(props: any) {
      // No-op on web
    };
  }
  
  if (typeof SVGElement !== 'undefined') {
    SVGElement.prototype.setNativeProps = function(props: any) {
      // No-op on web
    };
  }
  
  // 2. CRITICAL FIX: Patch React.createElement to intercept ALL ref callbacks
  // This catches refs BEFORE they're stored by icon libraries
  (React as any).createElement = function(type: any, props: any, ...children: any[]) {
    // If props has a ref, wrap it to add setNativeProps
    if (props && props.ref) {
      const originalRef = props.ref;
      
      // Handle ref callbacks
      if (typeof originalRef === 'function') {
        props.ref = function(node: any) {
          if (node && typeof node === 'object' && !node.setNativeProps) {
            node.setNativeProps = function(props: any) {
              // No-op on web
            };
          }
          return originalRef(node);
        };
      }
      // Handle ref objects (useRef, createRef)
      else if (originalRef && typeof originalRef === 'object' && 'current' in originalRef) {
        // Wrap in a callback to patch when assigned
        const refObject = originalRef;
        props.ref = function(node: any) {
          if (node && typeof node === 'object' && !node.setNativeProps) {
            node.setNativeProps = function(props: any) {
              // No-op on web
            };
          }
          refObject.current = node;
        };
      }
    }
    
    return originalCreateElement.call(React, type, props, ...children);
  };
  
  // 3. Also patch document.createElement as a safety net
  const originalDocCreateElement = document.createElement.bind(document);
  document.createElement = function(tagName: any, options?: any) {
    const element = originalDocCreateElement(tagName, options);
    if (!element.setNativeProps) {
      element.setNativeProps = function(props: any) {
        // No-op on web
      };
    }
    return element;
  };
  
  console.log('✅ Web polyfills initialized - setNativeProps patched at React level');
}

// Export a function to initialize polyfills (for backwards compatibility)
export function initializeWebPolyfills() {
  if (Platform.OS === 'web') {
    console.log('✅ Web polyfills verified - setNativeProps available');
  }
}
