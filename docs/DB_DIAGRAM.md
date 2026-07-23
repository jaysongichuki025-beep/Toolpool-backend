# ToolPool — Database Diagram (ER)

> Paste the Mermaid block into [mermaid.live](https://mermaid.live) to export PNG/SVG for your whiteboard submission.

## Entity Relationship Diagram

```mermaid
erDiagram
  User ||--|| Profile : has
  User ||--o{ Tool : owns
  Category ||--o{ Tool : categorizes
  Tool ||--o{ ToolImage : has
  Tool ||--o{ RentalRequest : receives
  User ||--o{ RentalRequest : borrows
  RentalRequest ||--o| Dispute : may_have

  User {
    bigint id PK
    string email UK
    string password
    string role
    bool is_active
    bool is_staff
    datetime created_at
  }

  Profile {
    bigint id PK
    bigint user_id FK
    string full_name
    string neighborhood
    string phone
    text bio
  }

  Category {
    bigint id PK
    string name UK
    string slug UK
    text description
    bool is_active
  }

  Tool {
    bigint id PK
    bigint owner_id FK
    bigint category_id FK
    string title
    text description
    string condition
    decimal daily_fee
    string status
    text pickup_instructions
    string neighborhood
    datetime created_at
  }

  ToolImage {
    bigint id PK
    bigint tool_id FK
    string image
    bool is_primary
    datetime uploaded_at
  }

  RentalRequest {
    bigint id PK
    bigint tool_id FK
    bigint borrower_id FK
    date start_date
    date end_date
    string status
    decimal total_fee
    text message
    datetime created_at
  }

  Dispute {
    bigint id PK
    bigint rental_id FK
    bigint flagged_by_id FK
    text reason
    string status
    datetime created_at
  }
```

## Relationship Summary (plain English)

1. **User ↔ Profile** — One-to-one. Every account has one profile (name, neighborhood).
2. **User → Tool** — One-to-many. A lender can list many tools.
3. **Category → Tool** — One-to-many. Each tool belongs to one category.
4. **Tool → ToolImage** — One-to-many. A tool can have many photos.
5. **Tool → RentalRequest** — One-to-many. Neighbors request a tool for date ranges.
6. **User → RentalRequest** — One-to-many. A borrower can make many requests.
7. **RentalRequest ↔ Dispute** — One-to-one (optional). Admins monitor flagged rentals.

## ASCII sketch

```
┌──────────┐ 1:1 ┌─────────┐
│   User   │─────│ Profile │
└────┬─────┘     └─────────┘
     │ 1
     │ owns
     │ *
┌────┴─────┐ *    1 ┌──────────┐
│   Tool   │────────│ Category │
└────┬─────┘        └──────────┘
     │ 1
     ├──────── * ToolImage
     │
     │ 1
     │ *
┌────┴──────────┐
│ RentalRequest │──── 0..1 Dispute
└───────────────┘
```
