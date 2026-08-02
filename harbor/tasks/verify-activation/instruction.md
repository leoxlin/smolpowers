This is a read-only activation classification task.

Read `/app/activation-cases.json`. For each case, use the installed Smol Activate instructions and the repository
configuration to decide if Smolpowers must activate for that request.

Write `/app/activation-results.json` with this structure:

```json
{
  "decisions": [
    {"id": "case-id", "activate": true}
  ]
}
```

Return one decision for each input case. Do not perform any described request. Do not start a lifecycle phase. Do not
change another file.
