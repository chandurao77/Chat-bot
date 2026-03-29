import { useState, useEffect } from "react"
import type { Theme } from "../types"

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const s = localStorage.getItem("jarvis-theme") as Theme | null
    if (s) return s
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
  })
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark")
    localStorage.setItem("jarvis-theme", theme)
  }, [theme])
  const toggle = () => setTheme((t: Theme) => t === "dark" ? "light" : "dark")
  return { theme, toggle }
}
