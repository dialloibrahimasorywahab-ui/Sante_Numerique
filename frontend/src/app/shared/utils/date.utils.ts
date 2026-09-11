const FRENCH_DATE_FORMAT: Intl.DateTimeFormatOptions = {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric'
};

const FRENCH_LONG_DATE_FORMAT: Intl.DateTimeFormatOptions = {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric'
};

export function parseDate(value?: string | Date | null): Date | null {
  if (!value) return null;
  const date = value instanceof Date ? new Date(value.getTime()) : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(value?: string | Date | null, fallback = '—'): string {
  const date = parseDate(value);
  if (!date) return fallback;
  return date.toLocaleDateString('fr-FR', FRENCH_DATE_FORMAT);
}

export function formatLongDate(value?: string | Date | null, fallback = '—'): string {
  const date = parseDate(value);
  if (!date) return fallback;
  return date.toLocaleDateString('fr-FR', FRENCH_LONG_DATE_FORMAT);
}

export function toIsoDate(value: Date = new Date()): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, '0');
  const day = String(value.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function addDays(value: Date | string, days: number): Date {
  const date = parseDate(value) || new Date();
  date.setDate(date.getDate() + days);
  return date;
}

export function calculateAge(value?: string | Date | null, fallback = 'N/D'): number | string {
  const birthDate = parseDate(value);
  if (!birthDate) return fallback;

  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const beforeBirthday = today.getMonth() < birthDate.getMonth() ||
    (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate());
  if (beforeBirthday) age--;
  return age;
}

export function isSameIsoDate(value: string | Date, reference: Date = new Date()): boolean {
  return toIsoDate(parseDate(value) || reference) === toIsoDate(reference);
}

export function combineDateAndTime(date: string, time: string): Date | null {
  return parseDate(`${date}T${time.substring(0, 5)}`);
}

export function isDateTimePast(date: string, time?: string, reference = new Date()): boolean {
  const value = time ? combineDateAndTime(date, time) : parseDate(date);
  return value ? value.getTime() <= reference.getTime() : true;
}
