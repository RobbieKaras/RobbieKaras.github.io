---
title: Defend-Check
summary: A Linux blue-team audit tool — checks firewall, privileged users, listening ports, and auth logs, then scores the risk and emits structured JSON.
tech: [Python, Linux, JSON]
repo: https://github.com/RobbieKaras
status: Active
order: 2
---

Defend-Check is a Linux blue-team audit tool. It checks firewall status,
privileged users, listening ports, and auth logs, applies automated risk
scoring, and emits structured JSON. It does baseline comparison to detect
configuration drift over time, and every finding maps to a blue-team
fundamental — hardening, least privilege, attack-surface reduction — with a
per-finding recommendation.
