import { neobrutalism } from '@clerk/themes';

export function createClerkAppearance() {
  return {
    baseTheme: neobrutalism,
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
