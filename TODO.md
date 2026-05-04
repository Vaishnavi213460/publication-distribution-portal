# Delivery Rounds & Delivery Stock — Implementation Plan

## Information Gathered
- **Project**: Django Publication Distribution Portal with admin, agent, customer, and login apps.
- **Agent Models**: Currently only `AgentSupp` exists in `agent/models.py`.
- **Agent Views**: Dashboard, delivery list, payment report, complaints, supplier mapping.
- **UI Pattern**: Agent pages extend `agentheader.html` which has a sidebar with collapsible sub-menus.
- **CRUD Pattern**: List + Create/Update combined in one template (form at top, list below), delete as separate URL.
- **Agent FK**: `Agent` model is in `login/models.py`, linked via `login` (OneToOne to User).
- **Product FK**: `Product` model is in `admin_panel/models.py`.

## Plan

### 1. Models (`agent/models.py`)
- **`DeliveryRound`**
  - `id` (PK, AutoField)
  - `agent` (FK → `login.Agent`, on_delete=CASCADE)
  - `start_place` (CharField, max_length=20, not null)
  - `end_place` (CharField, max_length=20, not null)

- **`DeliveryStock`**
  - `id` (PK, AutoField)
  - `delivery_round` (FK → `DeliveryRound`, on_delete=CASCADE)
  - `product` (FK → `admin_panel.Product`, on_delete=CASCADE)
  - `no_of_copies` (IntegerField, not null)

### 2. Forms (`agent/forms.py`)
- **`DeliveryRoundForm`** (ModelForm, exclude=[])
- **`DeliveryStockForm`** (ModelForm, exclude=[])
- Widget customizations for selects and number inputs with Bootstrap classes.

### 3. Views (`agent/views.py`)
- **`agent_delivery_rounds(request)`** — Combined single-template view:
  - Shows the logged-in agent’s delivery rounds and their stocks.
  - Allows adding/editing a delivery round.
  - Allows adding/editing a delivery stock linked to a round.
  - Uses `delivery_round_id` and `delivery_stock_id` GET params to populate edit forms.
- **`delivery_round_delete(request, id)`** — Deletes a round (and cascades its stocks).
- **`delivery_stock_delete(request, id)`** — Deletes a stock item.

### 4. URLs (`agent/urls.py`)
- `path('delivery-rounds/', views.agent_delivery_rounds, name='agent_delivery_rounds')`
- `path('delivery-rounds/<int:id>/delete/', views.delivery_round_delete, name='delivery_round_delete')`
- `path('delivery-stocks/<int:id>/delete/', views.delivery_stock_delete, name='delivery_stock_delete')`

### 5. Template (`templates/agent_delivery_stock.html`)
- Extends `agentheader.html`.
- **Top section**: Form to add/edit a Delivery Round (Start Place, End Place).
- **Middle section**: Table listing agent’s Delivery Rounds with Edit/Delete actions.
- **Bottom section**: Form to add/edit a Delivery Stock (select Round, select Product, No. of Copies).
- **Stock table**: Lists all stocks grouped by or alongside rounds with Edit/Delete actions.
- Styled consistently with existing agent templates (cards, chips, action buttons).

### 6. Sidebar Update (`templates/agentheader.html`)
- Update the "Delivery Rounds" sub-menu links:
  - `Add/View Delivery Rounds` → `{% url 'agent_delivery_rounds' %}`
- Update the "Stock" sub-menu links:
  - `Manage Delivery Stocks` → `{% url 'agent_delivery_rounds' %}`
  - `Manage Agent Stocks` → `{% url 'agent_delivery_rounds' %}`

### 7. Migrations
- `python manage.py makemigrations agent`
- `python manage.py migrate`

## Dependent Files to Edit
1. `agent/models.py`
2. `agent/forms.py`
3. `agent/views.py`
4. `agent/urls.py`
5. `templates/agent_delivery_stock.html` (new)
6. `templates/agentheader.html`

## Follow-up Steps
- Run migrations.
- Test CRUD flows for delivery rounds and stocks.
- Verify sidebar navigation highlights correctly.

