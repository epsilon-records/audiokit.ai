import type { Theme } from '@clerk/themes';
import { dark, neobrutalism } from '@clerk/themes';

export interface ClerkConfig {
  baseTheme: Theme;
  variables: {
    spacingUnit: string;
    colorPrimary: string;
    colorBackground: string;
    colorText: string;
    colorDanger: string;
    colorSuccess: string;
    colorWarning: string;
    colorInputText: string;
    colorInputBackground: string;
    colorInputBorder: string;
    fontFamily: string;
    fontSize: string;
    fontWeight: {
      normal: string;
      medium: string;
      bold: string;
    };
    borderRadius: string;
    boxShadow: string;
  };
  elements: {
    formButtonPrimary: {
      backgroundColor: string;
      '&:hover': {
        backgroundColor: string;
      };
    };
    formFieldInput: {
      borderColor: string;
      '&:focus': {
        borderColor: string;
        boxShadow: string;
      };
    };
    card: {
      border: string;
      boxShadow: string;
      borderRadius: string;
    };
    headerTitle: {
      fontSize: string;
      fontWeight: string;
      color: string;
    };
    headerSubtitle: {
      fontSize: string;
      color: string;
    };
    footer: {
      fontSize: string;
      color: string;
    };
    footerActionLink: {
      color: string;
      '&:hover': {
        textDecoration: string;
      };
    };
    alert: {
      backgroundColor: string;
      borderColor: string;
      color: string;
    };
  };
}

export function createClerkAppearance(mode: 'light' | 'dark'): ClerkConfig {
  return {
    baseTheme: mode === 'dark' ? dark : neobrutalism,
    variables: {
      spacingUnit: '16px',
      colorPrimary: '#0E4FFF',
      colorBackground: '#ffffff',
      colorText: '#1F1F1F',
      colorDanger: '#FF4E4E',
      colorSuccess: '#22C55E',
      colorWarning: '#F59E0B',
      colorInputText: '#1F1F1F',
      colorInputBackground: '#F3F4F6',
      colorInputBorder: '#E5E7EB',
      fontFamily: 'ui-sans-serif, system-ui, sans-serif',
      fontSize: '16px',
      fontWeight: {
        normal: '400',
        medium: '500',
        bold: '600',
      },
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    },
    elements: {
      formButtonPrimary: {
        backgroundColor: '#0E4FFF',
        '&:hover': {
          backgroundColor: '#0036D9',
        },
      },
      formFieldInput: {
        borderColor: '#E5E7EB',
        '&:focus': {
          borderColor: '#0E4FFF',
          boxShadow: '0 0 0 3px rgba(14,79,255,0.1)',
        },
      },
      card: {
        border: '1px solid #E5E7EB',
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
        borderRadius: '12px',
      },
      headerTitle: {
        fontSize: '24px',
        fontWeight: '600',
        color: '#1F1F1F',
      },
      headerSubtitle: {
        fontSize: '16px',
        color: '#6B7280',
      },
      footer: {
        fontSize: '14px',
        color: '#6B7280',
      },
      footerActionLink: {
        color: '#0E4FFF',
        '&:hover': {
          textDecoration: 'underline',
        },
      },
      alert: {
        backgroundColor: '#FEF3C7',
        borderColor: '#F59E0B',
        color: '#92400E',
      },
    },
  };
}

export interface ClerkNavConfig {
  baseTheme: Theme;
  variables: {
    colorPrimary: string;
    colorBackground: string;
    colorText: string;
    colorInputBackground: string;
    colorInputText: string;
  };
  elements: {
    card: {
      backgroundColor: string;
      borderColor: string;
    };
    organizationSwitcherTrigger: {
      color: string;
      '&:hover': {
        backgroundColor: string;
      };
    };
    userButtonTrigger: {
      color: string;
      '&:hover': {
        backgroundColor: string;
      };
    };
    userButtonPopoverCard: {
      backgroundColor: string;
      borderColor: string;
    };
    organizationSwitcherPopoverCard: {
      backgroundColor: string;
      borderColor: string;
    };
  };
}

export function createClerkNavAppearance(mode: 'light' | 'dark'): ClerkNavConfig {
  return {
    baseTheme: mode === 'dark' ? dark : neobrutalism,
    variables: {
      colorPrimary: mode === 'dark' ? '#818CF8' : '#4F46E5',
      colorBackground: mode === 'dark' ? '#1F2937' : '#FFFFFF',
      colorText: mode === 'dark' ? '#F3F4F6' : '#111827',
      colorInputBackground: mode === 'dark' ? '#374151' : '#F3F4F6',
      colorInputText: mode === 'dark' ? '#F3F4F6' : '#111827',
    },
    elements: {
      card: {
        backgroundColor: mode === 'dark' ? '#1F2937' : '#FFFFFF',
        borderColor: mode === 'dark' ? '#374151' : '#E5E7EB',
      },
      organizationSwitcherTrigger: {
        color: mode === 'dark' ? '#F3F4F6' : '#111827',
        '&:hover': {
          backgroundColor: 'transparent',
        },
      },
      userButtonTrigger: {
        color: mode === 'dark' ? '#F3F4F6' : '#111827',
        '&:hover': {
          backgroundColor: mode === 'dark' ? '#374151' : '#F3F4F6',
        },
      },
      userButtonPopoverCard: {
        backgroundColor: mode === 'dark' ? '#1F2937' : '#FFFFFF',
        borderColor: mode === 'dark' ? '#374151' : '#E5E7EB',
      },
      organizationSwitcherPopoverCard: {
        backgroundColor: mode === 'dark' ? '#1F2937' : '#FFFFFF',
        borderColor: mode === 'dark' ? '#374151' : '#E5E7EB',
      },
    },
  };
}
