export type ValidationRule = {
  test: (value: any) => boolean;
  message: string;
};

export type FieldValidation = {
  [key: string]: ValidationRule[];
};

export const validators = {
  required: (message = 'This field is required'): ValidationRule => ({
    test: (value: any) => value !== undefined && value !== null && value !== '',
    message,
  }),
  email: (message = 'Please enter a valid email'): ValidationRule => ({
    test: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message,
  }),
  minLength: (
    length: number,
    message = `Must be at least ${length} characters`
  ): ValidationRule => ({
    test: (value: string) => value.length >= length,
    message,
  }),
  url: (message = 'Please enter a valid URL'): ValidationRule => ({
    test: (value: string) => {
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    },
    message,
  }),
};

export function validateField(value: any, rules: ValidationRule[]): string | null {
  for (const rule of rules) {
    if (!rule.test(value)) {
      return rule.message;
    }
  }
  return null;
}

export function validateForm(values: Record<string, any>, validation: FieldValidation) {
  const errors: Record<string, string> = {};

  for (const [field, rules] of Object.entries(validation)) {
    const error = validateField(values[field], rules);
    if (error) {
      errors[field] = error;
    }
  }

  return errors;
}
