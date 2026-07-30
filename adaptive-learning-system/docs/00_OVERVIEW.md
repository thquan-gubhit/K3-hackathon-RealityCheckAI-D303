# Adaptive Learning System — Overview

> **Delivery status:** Phase 1 (project foundation) is complete. This document defines the target MVP; PDF processing, question/evaluation, adaptive learning, and Tutor Agent capabilities remain pending in Phases 2–5.

## Problem

Reading a document is not reliable evidence that a learner can recall, explain, or apply its ideas. Learners need a short feedback loop that turns source material into testable units, evaluates free-text answers against evidence prepared in advance, and chooses an appropriate next activity.

## Target users

- A self-directed learner studying a text-based PDF locally.
- An instructor or demo operator who wants to inspect the knowledge map and learning history.
- A developer who configures an OpenAI-compatible model and runs the local MVP.

## Pain points

- Long documents do not expose clear, testable learning objectives.
- Passive rereading creates weak signals of understanding.
- Generic quiz generation often leaks answers, asks out-of-scope questions, or uses an unstable rubric.
- A single score hides missing ideas, incorrect claims, and recurring misconceptions.
- An unconstrained agent is difficult to test, audit, and operate safely.

## Proposed solution

The application will:

1. Extract page-level text from one PDF.
2. organize the document into 3–10 meaningful Knowledge Units;
3. build Recall, Explain, and Apply questions with reference answers and immutable rubrics;
4. evaluate free-text answers into correct, missing, incorrect, and misconception evidence;
5. update mastery using deterministic rules;
6. select the next question or remediation action through a predefined workflow; and
7. invoke a bounded Tutor Agent only for configured exceptions.

The governing design principle is:

```text
Workflow as the backbone
+ deterministic rules for control
+ LLMs for semantic tasks
+ a bounded agent for exceptional tutoring
```

## Phase roadmap

| Phase | Outcome | Status |
| --- | --- | --- |
| 1 — Project foundation | Python project, configuration, SQLite bootstrap, health API, Streamlit home, baseline tests and docs | **Completed** |
| 2 — Document processing | PDF upload/parsing, Knowledge Units, split/merge validation, Knowledge Map | Pending |
| 3 — Question and evaluation | Questions, reference answers, rubrics, answer evaluation, feedback | Pending |
| 4 — Adaptive learning | Sessions, next-question rules, mastery, remediation, dashboard | Pending |
| 5 — Tutor Agent | Bounded tools, triggers, trace, disabled mode | Pending |
| 6 — Hardening | Full tests, error handling, logging, demo data, documentation polish | Pending |

## MVP scope

- Local Python 3.11 application with FastAPI, Streamlit, SQLite, SQLAlchemy, and Pydantic.
- One PDF per upload, maximum size controlled by configuration.
- Page-level extraction with PyMuPDF; no advanced OCR.
- Three to ten Knowledge Units with source-page traceability.
- Recall, Explain, and Apply questions, plus supporting remediation types.
- Reference answer and rubric created before the learner answers.
- Structured answer evaluation, learning history, mastery, and progress dashboard.
- Optional Tutor Agent controlled through `.env` and limited to `AGENT_MAX_STEPS`.
- OpenAI, OpenRouter, other OpenAI-compatible APIs, or a compatible local server through one adapter.

## Phase 1 boundary

Phase 1 supplies only the runnable foundation and design contracts. It does **not** claim that PDF parsing, Knowledge Unit generation, question generation, answer scoring, adaptive routing, or Tutor Agent execution is implemented.

## Non-goals

- Production deployment, payments, or a complete identity system.
- Video processing or advanced OCR.
- A separate vector database, fine-tuning, or advanced spaced repetition.
- Multi-agent orchestration.
- An unrestricted agent or an agent that owns the normal application workflow.
- Evaluation based only on cosine similarity.

## MVP success signals

- A sample PDF produces at least three valid, source-grounded Knowledge Units.
- Each unit can generate Recall, Explain, and Apply questions.
- Three answer qualities produce distinguishable rubric-based feedback.
- Mastery changes after each accepted answer but never becomes `MASTERED` from one answer alone.
- A repeated misconception can trigger the Tutor Agent when enabled.
- The same core learning flow remains usable when the Tutor Agent is disabled.

