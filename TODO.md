# Notification Feature Implementation

## Steps
- [x] 1. Add `Notification` model to `admin_panel/models.py`
- [x] 2. Add `NotificationForm` to `admin_panel/forms.py`
- [x] 3. Add CRUD views to `admin_panel/views.py`
- [x] 4. Add URLs to `admin_panel/urls.py`
- [x] 5. Create `templates/notification_list_form.html`
- [x] 6. Create `admin_panel/context_processors.py`
- [x] 7. Register context processor in `publication_portal/settings.py`
- [x] 8. Update `templates/adminheader.html` (real notifications + sidebar link)
- [x] 9. Update `templates/customerheader.html` (remove dummy override)
- [x] 10. Update `templates/agentheader.html` (remove empty override)
- [x] 11. Run makemigrations and migrate

## Summary
- **Model**: `Notification` with fields `agent` (FK, nullable), `message` (50 chars), `notification_date`, `status` (15 chars)
- **Admin CRUD**: `/admin-panel/notification/` — add, edit, delete notifications
- **Context Processor**: Automatically injects relevant notifications into every template
- **Visibility**:
  - Admin: sees all active notifications
  - Agent: sees general (agent=null) + agent-specific notifications
  - Customer: sees general (agent=null) notifications only
- **UI**: Bell icon in topbar shows real notifications; red dot appears when there are notifications

