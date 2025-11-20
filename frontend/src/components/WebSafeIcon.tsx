/**
 * Web-Safe Icon Component
 * Wraps Ionicons to prevent setNativeProps errors on web
 */

import React, { Component } from 'react';
import { Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Override Ionicons to be web-safe
const OriginalIonicons = Ionicons as any;

class WebSafeIonicons extends Component<any> {
  _icon: any = null;

  setNativeProps(props: any) {
    // On web, safely check if setNativeProps exists before calling
    if (Platform.OS === 'web') {
      if (this._icon && typeof this._icon.setNativeProps === 'function') {
        this._icon.setNativeProps(props);
      }
      // On web, if setNativeProps doesn't exist, just ignore (no error)
    } else {
      // On native, call normally
      if (this._icon) {
        this._icon.setNativeProps(props);
      }
    }
  }

  render() {
    return (
      <OriginalIonicons
        {...this.props}
        ref={(ref: any) => {
          this._icon = ref;
          // Call original ref if provided
          if (this.props.ref && typeof this.props.ref === 'function') {
            this.props.ref(ref);
          }
        }}
      />
    );
  }
}

// Export as default to replace Ionicons
export default WebSafeIonicons;
export { WebSafeIonicons as Ionicons };
