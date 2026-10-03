# 👥 TeamFlow — a Team-Management CRM for Operations Leaders

> A lightweight, no-login CRM that puts a team lead's whole world in one place: roster, performance, coaching, leave, and tasks. Built with Streamlit, ships with synthetic demo data, runs free on Streamlit Community Cloud.

**Built by:** [Mohammed Abdul Najeeb](https://github.com/Najeeb-AI-bots) · Operations Manager → AI-Transformation builder

---

## Why

Operations leaders juggle their team across five tools — a roster here, a metrics dashboard there, coaching notes in a doc, leave in email, tasks in a tracker. **TeamFlow** brings those into one clean workspace, so a 1x1, a quality dip, and an upcoming leave are all one click apart.

## Modules

| Module | What it does |
|--------|--------------|
| 📊 **Dashboard** | Team health at a glance — active headcount, avg OA%/IR%, open tasks, quality-by-member and ACHT-trend charts, upcoming leave |
| 👥 **Team Roster** | Add, view, and manage members (role, tier, start date, status) |
| 📈 **Performance** | Weekly **OA% · IR% · NRR% · ACHT** per member with trend lines; log new weekly metrics |
| 🗒️ **1x1 & Coaching** | Log coaching conversations, capture action items, track open vs. done |
| 🌴 **Attendance & Leave** | Leave requests with type, dates, and approval status |
| ✅ **Tasks** | Assign and track tasks / escalations by priority, due date, and status |

## Design notes

- **No login, no key, no cost** — pure Streamlit, deploys on the free Community Cloud tier.
- **CSV-backed** — all data lives in `data/*.csv`; the app seeds them on first run and persists edits within the session.
- **Synthetic data only** — the sample roster and metrics are fictional. Never commit real employee data to a public repo.
- **Ops-metric native** — tracks the quality metrics real contact-center teams live by (OA / IR controllable accuracy, No-Resolution-Rate, Average Contact Handle Time).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project layout

```
teamflow/
├── app.py              # Streamlit UI — 6 modules
├── data.py             # CSV-backed data layer + synthetic seed data
├── data/               # auto-created CSVs (roster, metrics, 1x1s, leave, tasks)
├── requirements.txt
└── README.md
```

## Roadmap ideas

- Export a team's weekly scorecard to PDF
- Role-based views (lead vs. associate)
- Wire the metrics module to a live data source (QuickSight / CSV upload)
- Bring-your-own-key AI summary of a member's quarter

## License

MIT.
