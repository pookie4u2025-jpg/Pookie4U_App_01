/**
 * CRITICAL FIX for setNativeProps error on web
 * This MUST be imported BEFORE any other imports in the app
 * 
 * Patches @expo/vector-icons to NOT call setNativeProps on web
 */

import { Platform } from 'react-native';

if (Platform.OS === 'web') {
  // Monkey-patch the createIconSet function BEFORE it's used
  const Module = require('module');
  const originalRequire = Module.prototype.require;

  Module.prototype.require = function(id) {
    const module = originalRequire.apply(this, arguments);

    // Intercept @expo/vector-icons
    if (id === '@expo/vector-icons/build/createIconSet' || id.includes('createIconSet')) {
      // Wrap the exported function
      const originalCreateIconSet = module.default || module;
      
      module.default = function(...args) {
        const IconComponent = originalCreateIconSet.apply(this, args);
        
        // Patch the component's setNativeProps method
        if (IconComponent && IconComponent.prototype) {
          const originalSetNativeProps = IconComponent.prototype.setNativeProps;
          
          IconComponent.prototype.setNativeProps = function(props) {
            // On web, check if _icon exists and has setNativeProps
            if (this._icon && typeof this._icon.setNativeProps === 'function') {
              this._icon.setNativeProps(props);
            } else if (this._icon) {
              // If _icon exists but doesn't have setNativeProps, just ignore
              // This prevents the error on web
              console.log('📱 Skipping setNativeProps on web (not supported)');
            }
          };
        }
        
        return IconComponent;
      };
    }

    return module;
  };

  console.log('✅ Icon patch applied - setNativeProps will be safe on web');
}
