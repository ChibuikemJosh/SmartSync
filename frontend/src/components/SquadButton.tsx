/**
 * SquadButton Component
 * Reusable button styled for Squad payment interface
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';

export interface SquadButtonProps {
  onPress: () => void;
  title: string;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

const SquadButton: React.FC<SquadButtonProps> = ({
  onPress,
  title,
  loading = false,
  disabled = false,
  variant = 'primary',
  size = 'medium',
  style,
  textStyle,
}) => {
  const getButtonStyle = (): ViewStyle => {
    const baseStyle = [styles.button, styles[`button_${variant}`]];

    if (size === 'small') {
      baseStyle.push(styles.button_small);
    } else if (size === 'large') {
      baseStyle.push(styles.button_large);
    }

    if (disabled || loading) {
      baseStyle.push(styles.button_disabled);
    }

    return Object.assign({}, ...baseStyle, style);
  };

  const getTextStyle = (): TextStyle => {
    const baseStyle = [styles.text, styles[`text_${variant}`]];

    if (size === 'small') {
      baseStyle.push(styles.text_small);
    } else if (size === 'large') {
      baseStyle.push(styles.text_large);
    }

    return Object.assign({}, ...baseStyle, textStyle);
  };

  return (
    <TouchableOpacity
      style={getButtonStyle()}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator color="white" size="small" />
      ) : (
        <Text style={getTextStyle()}>{title}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
  },
  button_primary: {
    backgroundColor: '#1F2937',
  },
  button_secondary: {
    backgroundColor: '#E5E7EB',
  },
  button_danger: {
    backgroundColor: '#EF4444',
  },
  button_small: {
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  button_large: {
    paddingVertical: 16,
    paddingHorizontal: 32,
  },
  button_disabled: {
    opacity: 0.5,
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  text_primary: {
    color: '#FFFFFF',
  },
  text_secondary: {
    color: '#1F2937',
  },
  text_danger: {
    color: '#FFFFFF',
  },
  text_small: {
    fontSize: 12,
  },
  text_large: {
    fontSize: 18,
  },
});

export default SquadButton;
