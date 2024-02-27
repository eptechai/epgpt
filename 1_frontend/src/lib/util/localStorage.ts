import { browser } from '$app/environment';

export function setLocalStorageItem(key: string, value: { [key: string]: any }) {
  if (browser) {
    localStorage.setItem(key, JSON.stringify(value));
  }
}

export function getLocalStorageItem(key: string) {
  if (browser) {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  }
}

export function removeLocalStorageItem(key: string) {
  if (browser) {
    localStorage.removeItem(key);
  }
}
