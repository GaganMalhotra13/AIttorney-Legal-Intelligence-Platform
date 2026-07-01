"use client";
import { createContext, useContext, useState, ReactNode } from "react";

type Lang = "en" | "hi";

interface LangContextType {
  lang:    Lang;
  setLang: (l: Lang) => void;
  t:       (en: string, hi: string) => string;
}

const LanguageContext = createContext<LangContextType>({
  lang:    "en",
  setLang: () => {},
  t:       (en) => en,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("aittorney-lang") as Lang) || "en";
    }
    return "en";
  });

  const setLang = (l: Lang) => {
    setLangState(l);
    if (typeof window !== "undefined") {
      localStorage.setItem("aittorney-lang", l);
    }
  };

  const t = (en: string, hi: string) => lang === "hi" ? hi : en;

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export const useLang = () => useContext(LanguageContext);