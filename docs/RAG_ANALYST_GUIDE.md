# RAG AI Analyst Guide (Multi-Provider Architecture)

## Übersicht

Der RAG (Retrieval-Augmented Generation) KI-Analyst ist eine conversational AI für die CoffeeStudio-Plattform. Nutzer können in natürlicher Sprache (Deutsch/Englisch) Fragen über Kooperativen, Röstereien, Marktdaten und Sourcing stellen.

**NEU in v2.0:** Multi-Provider-Architektur mit Ollama als Standard – **funktioniert ohne API Key!**

## Installation & Setup

### Option 1: Ollama (Standard, kein API Key)

1. **Ollama installieren:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Ollama starten:**
   ```bash
   ollama serve
   ```

3. **Modell herunterladen:**
   ```bash
   ollama pull llama3.1:8b
   ```

4. **CoffeeStudio konfigurieren (.env):**
   ```bash
   RAG_PROVIDER=ollama
   RAG_LLM_MODEL=llama3.1:8b
   ```

Weitere Details siehe vollständige Dokumentation im Repository.

---

**Version:** 2.0.0  
**Letzte Aktualisierung:** 2026-02-13
