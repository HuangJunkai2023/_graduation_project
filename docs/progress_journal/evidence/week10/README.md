# Week 10 evidence — recorded through 10 November 2026

This package records actual preparation and review, not completion of the planned T05/T06 work. The week covers 9–15 November; no work on 11–15 November is pre-recorded.

| ID | Activity date / record | Method and observation | Limitation |
| --- | --- | --- | --- |
| E10-01 | 9 November; Git `f1ebd28`; [visual deck](../../../../outputs/proposal-defense/v7-5min-visual/OCS_Proposal_Defense_EN_5min_SWJTU_Visual.pptx), [modification summary](../../../../outputs/proposal-defense/v7-5min-visual/Modification_Summary.md) | Assistant-supported preparation of a university-template defence deck: 15 main slides, five backups; answer/citation/refusal interface concepts and a question-tile diagram. | Illustrations are planned interface states. They are not screenshots of a validated live RAG workflow. No new application implementation or performance result is inferred. |
| E10-02 | Retained checks from 9 November; read-only audit on 10 November: [artifact_audit.json](artifact_audit.json), [audit script](verify_week10.py) | Retained report has 12/12 presentation checks passed and zero PowerPoint overflow flags. Current ZIP/XML inspection finds 20 slides and 20 note parts, with 19/20 exact bilingual matches to the content JSON. Slide 5's English opening is abbreviated in the PPT notes. Hashes identify files actually reviewed. | Retained checks were read, not rerun as a new performance test. The new exact-text mismatch is recorded rather than hidden by the older pass report. No PPT or script is changed by this journal audit. Allocated 300 seconds is not a measured rehearsal. |
| E10-03 | 10 November conversation and preparation of [Week 10](../../WEEK_10.md) | Student requested a plain-language explanation for defence questions; assistant explained the document-assistant purpose, RQ1–3, five configurations, evaluation and limitations against the report. | Supports preparation, not confirmed mastery, completed rehearsal or supervisor feedback. No new literature reading, experiment or formal meeting is claimed. |

## Recheck

From the repository root:

```powershell
python docs/progress_journal/evidence/week10/verify_week10.py
```

This reads the presentation package, its content JSON and existing validation files. It makes no model API request, ingests no documents, and performs no formal QA benchmark. The snapshot preserves full SHA-256 values, commit metadata and readback counts; it must not be described as new retrieval verification.

Actual student working hours and API cost were not recorded. The untracked `演讲稿.docx` is left untouched and excluded because its authorship/completion was not independently checked. Student requests concerning clarity and emphasis are not attributed to a supervisor. No Minerva posting, Teams message, defence attendance or Review Document approval is inferred.


## 10 November clarification — revised journal basis

- **E10-04:** The student explicitly confirmed that the project is largely complete and asked for a journal organised around `Proposal_English_Final.pdf`, rather than inferred from repository files. This supports the broad completion context, not specific test figures or dates of past implementation.
- **E10-05:** Proposal pp.2–5 and 7 were reviewed on 10 November. T05 covers Weeks 9–10, T06 Weeks 9–11, and M2 is Week 11. [proposal_alignment.json](proposal_alignment.json) retains the source fingerprint and mapping.
- The revised Week 10 body reviews document processing, chunking, source tracing and edition metadata against that plan. It does not describe all components as newly implemented this week. The earlier assertion that presentation work displaced unfinished engineering is withdrawn: missing repository evidence does not establish non-completion.
- E10-01–03 and the presentation audit remain supporting preparation records. Presentation checks and the slide-5 note discrepancy are not the technical focus of the revised journal.
- The added Week 10 deviation checkpoint was removed from WEEKLY_PLAN.md; the original schedule is retained. No milestone, Proposal or prior-week journal was changed.
