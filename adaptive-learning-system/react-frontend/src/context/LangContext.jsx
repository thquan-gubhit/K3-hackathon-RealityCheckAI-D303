import { createContext, useContext, useState } from 'react';
import vi from '../i18n/vi';
import en from '../i18n/en';

const LangContext = createContext();

const STRINGS = { vi, en };

export function LangProvider({ children }) {
  const [lang, setLang] = useState('vi');
  const t = (key) => STRINGS[lang][key] || key;
  const fmt = (key, vars = {}) => {
    let str = t(key);
    for (const [k, v] of Object.entries(vars)) {
      str = str.replace(`{${k}}`, v);
    }
    return str;
  };
  return (
    <LangContext.Provider value={{ lang, setLang, t, fmt }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLang() {
  return useContext(LangContext);
}
