# Bulk Task Operations

## Goal

Allow agents to operate on multiple tasks at once — batch complete, batch flag, batch move. Reduces round-trips for common multi-task workflows.

## API

### `bulk_edit`

Accepts an array of task IDs and a set of changes to apply to all of them.

```json
{
  "task_ids": ["id1", "id2", "id3"],
  "changes": {
    "flagged": true,
    "dueDate": "2026-04-01"
  }
}
```

### `bulk_complete`

Mark multiple tasks as complete in a single call.

```json
{
  "task_ids": ["id1", "id2", "id3"]
}
```

## Behavior

- Changes are applied atomically — if one task fails, none are updated
- The response includes a summary of what changed
- Tags can be added via `addTags` in the changes object
- Maximum 50 tasks per call

## Success Criteria

- Agent can complete multiple tasks at once
- Agent can flag and move tasks in bulk
- Performance is acceptable for batches up to 50 tasks
