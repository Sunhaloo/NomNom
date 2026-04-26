# Agent Guide for the NomNom Django Project

This document describes how automated coding agents should work in this repository: how to run commands, how to structure code, and how to handle errors and data.

There are currently no repo-specific Cursor rules (`.cursor/rules/`, `.cursorrules`) or Copilot instructions (`.github/copilot-instructions.md`), so this file is the primary agent guideline.

---

## 1. Project Overview

- Framework: Django (5.x) with the built-in test runner (no pytest configuration present).
- Apps: `landing`, `about_us`, `login`, `contact`, `cart`, `pastry`, `orders`, `payments`, `review`, `delivery`, `profile_page`, `api`.
- Custom user model: `login.User` (set via `AUTH_USER_MODEL = "login.User"`).
- Database: SQLite (`db.sqlite3`).
- Env management: `python-dotenv` used in `NomNom/settings.py`.
 - API: Django REST Framework is installed and configured via `REST_FRAMEWORK` in `NomNom/settings.py` for authenticated API access using both token-based and session-based authentication.
- Admin: All core domain models are registered in the Django admin and visible to superusers:
   - Users (`login.User`)
   - Deliveries (`delivery.Delivery`)
   - Pastries (`pastry.Pastry`)
   - Cart and items (`cart.Cart`, `cart.CartItem`)
   - Orders and order details (`orders.Order`, `orders.OrderDetail`)
   - Payments (`payments.Payment`)
   - Reviews (`review.Review`)
   - Contact messages (`contact.ContactMessage`)

---

## 2. Environment Setup

- Preferred Python: 3.11+ (compatible with Django 5).
- Install dependencies from the root of the repo:

```bash
pip install -r requirements.txt
# or, if you are inside the NomNom/ subdirectory:
pip install -r NomNom/requirements.txt
```

- Make sure `DJANGO_SETTINGS_MODULE` is `NomNom.settings` (this is already done in `NomNom/manage.py` and `NomNom/sync_products.py`).

---

## 3. Running the Application

From the repository root (`/home/azmaan/Desktop/Django Assignment/NomNom`):

```bash
python NomNom/manage.py migrate
python NomNom/manage.py runserver
```

- Do not introduce new run scripts unless explicitly requested.
- Use Django’s management commands (via `NomNom/manage.py`) rather than shelling into Python manually.

---

## 4. Tests: Commands and Conventions

There is no pytest configuration; use Django’s test runner.

### 4.1 Run the full test suite

From the repo root:

```bash
python NomNom/manage.py test
```

### 4.2 Run tests for a single app

```bash
python NomNom/manage.py test cart
python NomNom/manage.py test orders
python NomNom/manage.py test login
```

### 4.3 Run a single test module

Use the Python path to the module (relative to the `NomNom` package):

```bash
python NomNom/manage.py test cart.tests
python NomNom/manage.py test orders.tests
```

### 4.4 Run a single test case or test method

If you create tests like `class CartViewTests(TestCase)` in `cart/tests.py`:

```bash
python NomNom/manage.py test cart.tests.CartViewTests
python NomNom/manage.py test cart.tests.CartViewTests.test_add_to_cart_authenticated
```

- When adding tests, follow Django’s default `unittest.TestCase` style unless the repo is explicitly migrated to pytest.

---

## 5. Linting and Formatting

There are no explicit linting/formatting configs (`pyproject.toml`, `.flake8`, etc.) in this repo. Treat the following as soft guidelines for agents:

- Use 4 spaces for indentation (Django default).
- Keep lines under ~88–100 characters where practical.
- Prefer double quotes for new string literals in Python (`"like this"`), except when the string itself contains double quotes.
- When adding third-party tools (e.g., `black`, `ruff`, `flake8`), do not commit new dependencies or config files unless the user explicitly requests it.

If you need to quickly lint for internal reasoning:

- You may conceptually apply `ruff`/`flake8` rules, but do not assume these tools exist in the environment or add them to `requirements.txt` without user approval.

---

## 6. Imports and Module Structure

### 6.1 Import ordering

For new or edited files, group imports in this order:

1. Standard library (`os`, `json`, `pathlib.Path`, `datetime`, etc.).
2. Third-party packages (`django`, `dotenv`, etc.).
3. Django apps in this project (`cart.models`, `pastry.models`, `orders.models`, etc.).
4. Local relative imports (e.g., `.forms`, `.models`).

Example:

```python
import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cart.models import Cart
from .models import Order, OrderDetail
```

- Avoid wildcard imports (`from x import *`).
- Prefer absolute imports from the project root (`from cart.models import Cart`) over deep relative imports when reasonable.

### 6.2 Django management scripts

- Follow the pattern in `NomNom/sync_products.py` when writing standalone scripts:
  - Set `DJANGO_SETTINGS_MODULE`.
  - Call `django.setup()` before importing models.

---

## 7. Naming Conventions

### 7.1 Python

- Modules and packages: `snake_case` (as already used: `profile_page`, `order_confirmation` view etc.).
- Classes (models, forms, views): `PascalCase` (e.g., `Pastry`, `User`, `EditProfileForm`).
- Functions and methods: `snake_case` (e.g., `login_view`, `add_to_cart_ajax`, `format_pastry_name`).
- Variables:
  - Local variables: `snake_case` (`cart_items`, `order_details`, `delivery_address`).
  - Booleans: `is_...` / `has_...` (`is_custom`, `has_ordered`, `is_available`).

### 7.2 Django models

- Model class names: singular (e.g., `Pastry`, `Order`, `Review`).
- Field names:
  - Use descriptive `snake_case` (`pastry_name`, `pastry_category`, `total_amount`).
  - For choices: define an iterable in the model (`CATEGORY_CHOICES`) and reference it in the field as in `pastry.models.Pastry`.

### 7.3 URLs and view names

- URL names should be descriptive and namespaced (e.g., `orders:order_confirmation`, `cart:cart`, `login:login`).
- View functions: use verbs that describe actions (`checkout`, `order_confirmation`, `add_review`, `clear_profile_pic`).

---

## 8. Error Handling and Responses

### 8.1 HTTP views (HTML responses)

- Use Django messages framework for user-facing feedback, consistent with existing code:

```python
from django.contrib import messages

messages.success(request, "Profile updated successfully.")
messages.error(request, "Please fix the errors below.")
messages.warning(request, "Your cart is empty.")
```

- Prefer `redirect(...)` after POSTs (Post/Redirect/Get), as seen in `contact.views.index` and `orders.views.checkout`.
 - Put validation logic in forms (e.g., `ContactForm.clean_email` in `contact.forms`) rather than relying on view-level try/except. This keeps invalid input from ever reaching side effects like `send_mail` and surfaces field-level errors alongside any global toast messages.

### 8.2 JSON views / AJAX endpoints

- Use `JsonResponse` with a predictable structure:

  - Include `success: bool`.
  - For failure, include a human-readable message or `error` field.
  - Set appropriate HTTP status codes (400, 401, 404, 500).

Examples from `cart.views.add_to_cart_ajax` and `review.views.add_review`:

```python
return JsonResponse(
    {"success": False, "message": "Authentication required"},
    status=401,
)

return JsonResponse(
    {"success": False, "error": "Invalid rating value."},
    status=400,
)
```

- When catching broad exceptions, log or print a concise error and return a sanitized message to the client. Do not expose stack traces or sensitive data.

### 8.3 Database and concurrency

- Use `select_for_update()` inside transactions when preventing duplicates, as in `review.views.add_review`.
- Guard against `DoesNotExist` and `MultipleObjectsReturned` where applicable (see `cart.views.add_to_cart_ajax` and `review.views.get_reviews`).

### 8.4 Toast notifications

The project uses toast-style notifications in several places instead of inline alerts:

- Landing page: `.order-toast` for order success, driven by `order_success` and `order_id` query params.
- Cart and checkout: `.toast` with `showToast(message)` in `cart/static/cart/cart.js` and `orders/static/orders/checkout.js`.
- Pastry customization: `.toast` with `showToast(message)` in `pastry/templates/pastry/customize_pastry.html`.
- Payments: `.toast` with `showToast(message)` in `payments/static/payments/payment.js`.
- Contact: `.toast` in `contact/templates/contact/contact.html`, with `contact/static/contact/contact.js` mapping Django messages to toasts on page load.

Guidelines for agents:

- For new HTML views that use Django messages, prefer toast notifications over inline alert boxes if they fit the UX.
- Reuse the existing pattern: a fixed `.toast` element in the template and a per-page JS `showToast(message, level)` function in the app’s `static/<app>/` JS.
- When using the messages framework with JS-heavy pages, expose messages via a hidden container (e.g. `#django-messages` with data attributes) and let JS trigger corresponding toasts after DOM ready.

---

## 9. Data and Serialization Patterns

The project uses a couple of recurring patterns that agents should follow.

### 9.1 Serializing cart/order items

- Use helper functions to encapsulate formatting logic (e.g., `format_pastry_name`, `resolve_image`, `serialize_cart_items` in `orders/views.py`).
- When augmenting cart/order JSON:

  - Keep field names consistent (`name`, `price`, `quantity`, `image`, `is_custom`, `flavour`, `pickup_date`, etc.).
  - Use `float()` for Decimal fields when serializing to JSON.
  - Convert `date`/`datetime` to strings, not raw objects.

### 9.2 Address formatting

- Follow the pattern in `orders.views.checkout`:

  - Collect field parts (`first_name`, `last_name`, `street_address`, `city`, `zip_code`, `country`).
  - Fallback to user profile fields (e.g., `user.street`, `user.region`) when form values are empty.
  - Join non-empty components with `", "`.

### 9.3 Time and dates

- Use `django.utils.timezone.now()` for timestamps.
- For simple date arithmetic, use `datetime.timedelta` with timezone-aware datetimes, as in the delivery date computation.

---

## 10. Authentication and Permissions

- Use `@login_required` for views that operate on user-specific state (profile, cart, orders, reviews).
- For AJAX endpoints, explicitly check `request.user.is_authenticated` and return 401 with a JSON error, as in `cart.views.add_to_cart_ajax`.
- Do not assume an authenticated user in context processors, but handle both cases (see `cart.context_processors.cart_item_count`).

### 10.1 DRF configuration and authentication

- The REST API uses Django REST Framework, configured in `NomNom/settings.py` as:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

- This means:
  - Browser / web usage (including the DRF browsable API) authenticates via Django sessions and CSRF, using the normal login views (`/login/`, `/admin/`).
  - Mobile and other external clients should authenticate using DRF tokens, sent with an `Authorization: Token <token>` header.
  - All API endpoints under `/api/v1/` require authentication by default.

---

## 11. Templates and Context

- Use context processors for values needed across many templates (e.g., `cart_item_count`).
- For JSON blobs passed into templates (cart and checkout):

  - Pre-serialize to JSON in the view (`json.dumps(cart_data)`) and pass as a string.
  - Ensure data is safe to expose and does not contain secrets or internal IDs beyond what the template needs.
 - JavaScript for page-specific behaviour should live in the corresponding app’s `static/<app>/` directory, and be included via `{% block extra_js %}` in templates (e.g., `cart/cart.js`, `orders/checkout.js`, `payments/payment.js`, `contact/contact.js`). Avoid inlining large JS blocks directly into templates when a static file is appropriate.

---

## 12. Custom User Model

- Always use `django.contrib.auth.get_user_model()` or `settings.AUTH_USER_MODEL` rather than importing `auth.User` directly.
- Do not create new models that duplicate fields already on `login.User` (e.g., profile fields like `first_name`, `last_name`, `profile_pic`, `region`, `street`).
- When updating `User.save()`, preserve the existing behavior where admin/staff roles override the default `role`.

---

## 13. Static Files and Media

- Static files:

  - `STATIC_URL = "static/"`
  - `STATICFILES_DIRS = [BASE_DIR / "static"]`

- Media:

  - `MEDIA_URL = "/media/"`
  - `MEDIA_ROOT = BASE_DIR / "media"`

- For image fields:

  - Custom pastries may require using `.url` when rendering (see `orders.views.resolve_image` and `cart.views.view_cart`).
  - Standard pastries may be stored as string paths; convert to `str()` if needed.

---

## 14. Adding New Code

When agents introduce new code:

- Prefer extending existing patterns and helpers instead of duplicating logic.
- Keep views thin; move formatting and transformation logic into helper functions where it is shared (e.g., between `cart` and `orders`).
- Make minimal, focused changes that preserve current behavior unless the user explicitly requests refactoring or new features.
- Do not introduce new frameworks or major dependencies (e.g., switching test runners, adding async stack) without explicit user approval.

---

## 15. Summary for Agents

- Use `python NomNom/manage.py test` and app/module paths for running tests; no pytest is configured.
- Model your code after patterns in `login.views`, `cart.views`, and `orders.views`.
- Follow Django’s conventions for views, models, and templates, with the additional naming and error-handling rules described here.
- Be conservative with new tools/configs; this guide is the effective style contract for automated agents working in this repo.

---

## 16. Orders, Delivery, and Payments Lifecycle

- Checkout flow (`orders.views.checkout`):
  - On POST, creates an `Order` for the logged-in user with `total_amount` derived from the cart and an initial `order_status="Pending"`.
  - Creates related `OrderDetail` rows for each cart item.
  - Builds a formatted delivery address from the checkout form and/or user profile fields and creates a `Delivery` row with `status="Pending"` and an appropriate `date`.
  - Immediately records a `Payment` row for the order with:
    - `payment_method="Card"`
    - `amount=order.total_amount`
    - `payment_status="Paid"`
  - Updates the order to `order_status="Paid"` to reflect successful payment, then clears the cart and redirects to the order confirmation page.

- Status enums (current semantics):
  - `orders.Order.order_status`:
    - `"Pending"` – created and not yet paid (transient; in the current checkout flow this is immediately moved to `"Paid"`).
    - `"Paid"` – order has a successful payment recorded.
    - `"Cancelled"` – reserved for future cancellation flows (e.g. via mobile API); agents should not set this without also updating delivery/payment appropriately.
  - `delivery.Delivery.status`:
    - `"Pending"` – delivery is scheduled or awaiting fulfilment.
    - `"Done"` – delivery completed.
    - `"Failed"` – delivery attempted but did not succeed.
    - `"Cancelled"` – reserved for orders that are cancelled before delivery; keep this in sync with `Order.order_status` when implementing cancellation.
  - `payments.Payment.payment_status`:
    - `"Pending"` – payment initiated but not confirmed.
    - `"Paid"` – payment captured successfully (used by the current checkout flow).
    - `"Failed"` – payment attempt failed.
    - `"Refunded"` – represent refunded payments when an order is cancelled; cancellation logic should update this status when implemented.

- Each order currently has exactly one associated delivery created at checkout and may have one or more payments. When introducing order cancellation or refund logic (e.g. via the `api` app), always:
  - Update `Order.order_status` and `Delivery.status` together so they remain consistent.
  - Consider whether related `Payment` rows need their `payment_status` moved from `"Paid"` to `"Refunded"` according to the desired business rules.

---

## 17. Deliveries API Usage

- API app and routing:
  - The `api` app exposes REST endpoints under the `/api/v1/` prefix via Django REST Framework.
  - `api/urls.py` registers two viewsets on a `DefaultRouter`:
    - `OrderViewSet` → `/api/v1/orders/` and `/api/v1/orders/<id>/`.
    - `DeliveryViewSet` → `/api/v1/deliveries/` and `/api/v1/deliveries/<id>/`.

- Delivery listing behaviour (`DeliveryViewSet.get_queryset`):
  - All queries are scoped to the authenticated user: `Delivery.objects.filter(order__user=request.user)`.
  - By default, `GET /api/v1/deliveries/` returns only deliveries with `status="Pending"` (customer "pending deliveries" view).
  - Passing a `status` query parameter overrides the default filter, for example:
    - `GET /api/v1/deliveries/?status=Cancelled` → all cancelled deliveries for the current user.
    - `GET /api/v1/deliveries/?status=Done` → all confirmed/completed deliveries.

- Delivery serializer structure (`DeliverySerializer`):
  - Fields: `id`, `address`, `date`, `status`, `order`.
  - `order` is a nested `OrderSummaryForDeliverySerializer` exposing `id`, `order_date`, `order_status`, `total_amount`.

- Delivery actions (`DeliveryViewSet`):
  - `POST /api/v1/deliveries/<id>/confirm/`:
    - Only allowed when the delivery belongs to the current user and `status == "Pending"`.
    - Updates `Delivery.status` to `"Done"` and returns `{ "success": true, "delivery_id": ..., "new_status": "Done" }`.
    - Does not modify the related `Order` or `Payment` rows.
  - `POST /api/v1/deliveries/<id>/cancel/`:
    - Only allowed when the delivery belongs to the current user and `status == "Pending"`.
    - Runs inside a transaction and performs all of the following:
      - Sets `Delivery.status = "Cancelled"`.
      - Sets the related `Order.order_status = "Cancelled"`.
      - Updates all `Payment` rows for that order with `payment_status="Paid"` to `payment_status="Refunded"`.
    - Returns a JSON payload of the form `{ "success": true, "delivery_id": ..., "order_id": ..., "order_status": "Cancelled", "delivery_status": "Cancelled" }`.

- Calling the deliveries API via the DRF browsable interface (session auth):
  - Log in through the normal web UI (e.g. `/login/` or `/admin/`) so the browser holds a valid session and CSRF cookies.
  - Visit `/api/v1/deliveries/` in the same browser to see the browsable API list view.
  - Click through to `/api/v1/deliveries/<id>/` for a specific delivery.
  - Manually navigate to `/api/v1/deliveries/<id>/confirm/` or `/api/v1/deliveries/<id>/cancel/` (note the required trailing `/`).
  - Use the POST form rendered by DRF on those pages; the form includes a CSRF token, so no extra work is needed.

- Token-based access for Postman and mobile clients:
  - Obtain a token by calling the built-in DRF token endpoint:

    - `POST /api/v1/auth/token/`
    - Body (form or JSON): `{"username": "<username>", "password": "<password>"}`.
    - On success, you receive `{ "token": "<token>" }`.

  - Use the token on subsequent API calls, for example:

    - `GET /api/v1/deliveries/`
    - `POST /api/v1/deliveries/<id>/confirm/`
    - `POST /api/v1/deliveries/<id>/cancel/`

    with the header:

    - `Authorization: Token <token>`

  - When using token auth, you do not need cookies or CSRF headers.

- Logging out / revoking tokens:
  - The project exposes a simple logout endpoint for mobile/external clients:

    - `POST /api/v1/auth/logout/`
    - Requires authentication (typically via `Authorization: Token <token>`).
    - Deletes all auth tokens for the current user and returns `{ "success": true }`.
    - After this call, previously issued tokens will fail with 401.

---

## 18. Users API

- Endpoint and routing:
  - The `api` app exposes a read-only profile endpoint for the current user under the `/api/v1/` prefix.
  - `api/urls.py` wires this as:
    - `GET /api/v1/users/me/` → `CurrentUserView`.

- Serializer structure (`UserProfileSerializer`):
  - Backed by the custom `login.User` model via `get_user_model()`.
  - Fields: `id`, `first_name`, `last_name`, `street`, `region`.

- Behaviour:
  - `GET /api/v1/users/me/`:
    - Requires authentication (`IsAuthenticated`).
    - Returns a minimal JSON profile for the logged-in user only.
    - Intended for clients (e.g. mobile apps) to construct human-readable addresses such as `"<street>, <region>"` for features like Google Maps integration.

 - Authentication:
  - For the browsable API in a browser:
    - Log in via the normal web UI so the browser holds valid `sessionid` and `csrftoken` cookies, then visit `/api/v1/users/me/`.
  - For Postman and mobile/external clients:
    - First obtain a token via `POST /api/v1/auth/token/`.
    - Then call `GET /api/v1/users/me/` with the header `Authorization: Token <token>`.
    - No CSRF header is required when using token authentication.

---

## 19. Frontend JavaScript and AJAX

- jQuery loading and usage:
  - jQuery 3.7.1 is loaded globally in `templates/base.html` via CDN and is available on all pages that extend it.
  - jQuery is actively used in:
    - `cart/static/cart/cart.js` for cart item quantity updates.
    - `orders/static/orders/checkout.js` for checkout quantity updates and address helpers.
    - `pastry/static/pastry/script.js` for add-to-cart buttons and the reviews modal.
  - Other JS under `static/global/` (login popup, cart helpers, progress bar) and some app scripts (`payments/payment.js`, `contact/contact.js`, `pastry/customize_pastry.html`) use plain JavaScript; when changing a page, match the style already used there.

- Cart AJAX endpoints:
  - Adding items to cart:
    - Endpoint: `POST /cart/add/` handled by `cart.views.add_to_cart_ajax` (URL name `cart:add_to_cart_ajax`).
    - Called from:
      - `pastry/static/pastry/script.js` using jQuery `$.ajax` for category product cards.
      - `landing/templates/landing/landing.html` using `fetch` for the hero "Fudgy McFudgecake" call-to-action.
    - Request body is JSON with at least `name`, `price`, `image`, `quantity` and optionally `category`.
    - Response shape:
      - On success: `{"success": true, "message": "<text>", "cart_count": <int>}`.
      - On failure: `{"success": false, "message": "<error>"}` with status `400`, `401`, or `404`.
    - Authentication: manual `request.user.is_authenticated` check returns a JSON 401; frontend uses the global `showLoginPrompt()` helper for 401/403 cases.

  - Updating cart quantities:
    - Endpoint: `POST /cart/update/` handled by `cart.views.update_cart_quantity` (URL name `cart:update_cart_quantity`).
    - Called from:
      - `cart/static/cart/cart.js` on the cart page.
      - `orders/static/orders/checkout.js` on the checkout page.
    - Request body is JSON: `{"index": <int>, "quantity": <int>}`, where `index` is the zero-based index of the item in `cart.items.all()` on the server.
    - Response shape:
      - On success: `{"success": true, "message": "Quantity updated", "cart_count": <int>}`.
      - On failure: `{"success": false, "message": "<error>"}` with status `400`, `401`, or `404`.
    - Both scripts update their local `cartData` array, re-render the item list, and update the navbar `#cart-count` badge using the shared `updateCartCount` helper from `static/global/cart_helpers.js`.

- Review AJAX flows:
  - Listing reviews:
    - Endpoint: `GET /review/get/<pastry_id>/` handled by `review.views.get_reviews`.
    - Called from `pastry/static/pastry/script.js` using `$.getJSON`.
    - Response: `{"reviews": [{"user": "<username>", "rating": <int>, "comment": "<text>", "date": "MMM DD, YYYY"}, ...]}`.
    - The JS computes average rating, populates the modal summary, and renders the list. On failure it falls back to cached data in `reviewsData`.

  - Submitting reviews:
    - Endpoint: `POST /review/add/<pastry_id>/` handled by `review.views.add_review`.
    - Decorated with `@login_required` and `@require_POST` and enforces "must have ordered this pastry" plus "one review per user/pastry" using `select_for_update()` inside a transaction.
    - Called from `pastry/static/pastry/script.js` via `$.ajax` with JSON body `{"rating": <1–5>, "comment": "<text>"}`.
    - Response:
      - Success: `{"success": true, "message": "Review submitted successfully!"}`.
      - Failure: `{"success": false, "error": "<reason>"}` with status `400` or `500`.
    - The form in `pastry/category.html` has a `data-user-authenticated` attribute. JS uses this to prevent unauthenticated submissions and shows `showLoginPrompt()` before attempting AJAX.

- Checkout behaviour:
  - The checkout page (`orders/templates/orders/checkout.html`) is driven by `orders/static/orders/checkout.js`:
    - Uses jQuery to manage the multi-step UI and calls `window.updateProgress` from `static/global/progress.js`.
    - Validates contact, address, and card fields on the client.
    - Uses the shared `POST /cart/update/` endpoint to adjust item quantities during checkout.
    - Loads a static `city_zip.json` via `$.getJSON('/static/orders/data/city_zip.json')` to auto-fill the `#zip` field from the chosen city.
  - Placing an order is not done via AJAX:
    - `checkout.js` creates a plain `<form method="POST" action=current_url>`, injects a `csrfmiddlewaretoken` from the `csrftoken` cookie, and submits it.
    - `orders.views.checkout` then creates the `Order`, `OrderDetail`, `Delivery`, and `Payment`, marks the order as `"Paid"`, clears the cart, and redirects to the confirmation page.

- Pastry customization:
  - The custom cake designer (`pastry/templates/pastry/customize_pastry.html`) uses vanilla `fetch` to submit a `FormData` payload to `POST /pastry/customize/`.
  - `pastry.views.customize_pastry`:
    - Manually checks `request.user.is_authenticated` and redirects to `login:login` with a Django message if not.
    - Validates `pickup_date` and creates a `Pastry` with `is_custom=True`.
    - Adds the custom pastry to both the DB-backed `Cart/CartItem` and a legacy session cart.
  - The frontend treats non-JSON responses as redirects (`response.redirected`) and navigates accordingly; there is no JSON contract for this endpoint.

- CSRF handling:
  - There is no global `$.ajaxSetup` for CSRF; each bundle handles it explicitly:
    - Pages with a rendered `{% csrf_token %}` read the token from a hidden `input[name="csrfmiddlewaretoken"]` and send it as an `X-CSRFToken` header (for example, add-to-cart and reviews in `pastry/script.js`, hero add-to-cart in `landing.html`, and the customize pastry form).
    - `cart.js` and `checkout.js` read the `csrftoken` value from cookies via a local `getCookie` helper and use it for AJAX (`/cart/update/`) and for building the checkout POST form.
  - When adding new AJAX POST endpoints, follow the existing pattern in that area (hidden input vs cookie) and always set the `X-CSRFToken` header so Django’s CSRF checks pass.

- Toasts and login prompts:
  - Each major page defines its own toast structure (`#toast` or `.order-toast`) and a local `showToast` or `showNotification` helper; there is no single global toast API.
  - For login-required flows, use the global `showLoginPrompt(message?)` from `static/global/login_popup.js` instead of custom modals. This is already used by cart add-to-cart handlers, review submission, and cart access when not authenticated.

- JSON response conventions:
  - For classic Django JSON views (not DRF), follow these conventions:
    - Include a top-level `success: bool` field when modelling an action (cart add/update, review submit, etc.).
    - On success, include a human-readable `message` and any extra data (`cart_count`, etc.).
    - On failure, include a top-level `error` or `message` describing the problem and set the appropriate HTTP status code (`400` for validation, `401` for auth, `404` for not found, `500` for unexpected errors).
  - For read-only endpoints that just return data (like `review.get_reviews`), returning a structured payload without `success` (for example `{"reviews": [...]}`) is acceptable as long as the pattern is consistent within that module.

- Index-based cart operations:
   - Cart item updates and removals are index-based rather than ID-based: the frontend adds a `data-index` attribute to each cart item, and `/cart/update/` and `/cart/remove/<index>/` operate on that index within `cart.items.all()` on the server.
   - If you change how cart items are ordered or filtered in the backend, make sure the `cartData` array and `data-index` attributes remain aligned with `cart.items.all()` so that updates and removals still affect the correct items.

---

## 20. Mobile App Implementation (Flet)

The mobile app is a customer-facing delivery management application built with Flet. It enables customers to:
- Sign in/up via API
- View homepage with business statistics and top reviews
- Track orders and deliveries
- Confirm deliveries with photo proof and QR code validation
- Calculate distance and ETA based on geolocation

### 20.1 Project Structure

```
mobile-app/
├── src/
│   ├── main.py                    # App entry point and router
│   ├── config.py                  # API URLs and constants
│   ├── auth/
│   │   ├── auth_service.py        # Login/signup/logout logic
│   │   └── screens/
│   │       ├── login_screen.py
│   │       └── register_screen.py
│   ├── home/
│   │   ├── home_screen.py         # Homepage with stats/reviews
│   │   └── home_service.py        # Fetch stats, reviews, profile
│   ├── orders/
│   │   ├── orders_screen.py       # Orders list
│   │   └── orders_service.py      # Fetch orders
│   ├── deliveries/
│   │   ├── deliveries_screen.py   # Deliveries list
│   │   ├── delivery_detail_screen.py
│   │   ├── delivery_confirmation_screen.py
│   │   ├── deliveries_service.py  # Fetch deliveries, upload photos
│   │   ├── geolocation.py         # Distance/ETA calculation
│   │   └── camera_scanner.py      # Photo capture & QR validation
│   ├── common/
│   │   ├── api_client.py          # HTTP request wrapper
│   │   ├── storage.py             # Token/cache management
│   │   ├── error_handler.py       # Standardized error messages
│   │   └── navigation.py          # Navigation utilities
│   ├── shared/
│   │   ├── navigation.py          # Bottom navigation template
│   │   └── base_layout.py         # Page wrapper with navigation
│   └── assets/
│       ├── icons/
│       └── images/
├── pyproject.toml
└── README.md
```

### 20.2 Core Services

**API Client (`common/api_client.py`)**
- Wraps all HTTP requests to backend
- Handles token injection in headers
- Provides `get()` and `post()` methods
- Returns standardized response or raises `APIError`

**Token Storage (`common/storage.py`)**
- Manages auth token persistence
- Caches statistics locally with timestamp
- Methods: `save_token()`, `get_token()`, `clear_token()`, `cache_stats()`, `get_cached_stats()`

**Auth Service (`auth/auth_service.py`)**
- `login(username, password)` → Stores token on success
- `signup(user_data)` → Creates user via `/api/v1/auth/signup/`
- `logout()` → Revokes tokens and clears local token
- `is_authenticated()` → Checks if valid token exists

**Service Pattern**
- Each screen has an associated service (e.g., `HomeService`, `OrdersService`, `DeliveriesService`)
- Services use `APIClient` to fetch data
- Services handle caching where appropriate
- All API errors are caught and re-raised as `APIError`

### 20.3 Screen Structure

All screens follow a consistent pattern:
1. Accept `page` (Flet Page object) and callback functions
2. Return a `Container` or `PageLayout` with UI
3. Fetch data in `load_data()` or similar function
4. Display loading indicators and errors
5. Update UI based on API responses

**Navigation:**
- Home, Orders, Deliveries tabs via bottom navigation
- Login/Signup handled separately
- Auth guards prevent unauthenticated access

### 20.4 API Integration for Mobile

**Authentication Flow:**
1. User signup/login via `/api/v1/auth/signup/` or `/api/v1/auth/token/`
2. App stores token in local storage
3. All subsequent requests include `Authorization: Token <token>` header
4. Token cleared on logout via `/api/v1/auth/logout/`

**Data Fetching:**
- Homepage: Fetches `/api/v1/stats/`, `/api/v1/users/me/`, `/api/v1/reviews/top-rated/`
- Orders: Fetches `/api/v1/orders/`
- Deliveries: Fetches `/api/v1/deliveries/?status=<status>`
- All responses cached locally where appropriate

**Delivery Confirmation:**
- User captures photo via camera (Flet `Image` picker)
- Mobile app validates QR code in photo using `pyzbar`
- If valid, uploads photo to `/api/v1/deliveries/<id>/confirm-with-photo/`
- Backend stores binary photo and marks delivery as Done
- User sees success message

### 20.5 Mobile Dependencies

Core dependencies (in `pyproject.toml`):
- `flet>=0.84.0` - UI framework
- `requests>=2.31.0` - HTTP client
- `pyzbar>=0.1.9` - QR code detection
- `pillow>=10.0.0` - Image processing

Optional (for advanced features):
- Geolocation libraries for distance calculation
- Camera integration (platform-specific)

### 20.6 Development Guidelines for Mobile Team

**When extending screens:**
1. Follow the service pattern (each screen has a service)
2. Use `APIClient` for all API calls (do not use requests directly)
3. Always handle `APIError` exceptions
4. Show loading indicators while fetching
5. Cache appropriate data using `LocalStorage`
6. Call `page.update()` after UI changes

**When modifying services:**
1. Ensure all API calls go through `APIClient`
2. Use consistent error handling
3. Log errors with Python `logging` module
4. Handle both successful and error responses

**When adding new endpoints:**
1. Add to `config.py` if URL or constant
2. Create service method in appropriate service file
3. Call service from screen, not API directly
4. Update documentation


