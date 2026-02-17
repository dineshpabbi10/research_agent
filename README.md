# Research Agent

An agent that analysis given topic. Internally does critique and generates
a blog article for you. It researches internet for similar articles, does
keyword research, undertsands the structure of top ranked articles and keywords an finally
optimizes for content length.

Additionally, Add links. Content without proper internal and external links is one of the main things that scream "AI GENERATED". Think of internal links as your opportunity to show off how well you know your content, and external links as an opportunity to show off how well you know your field.

Optimize other resources. The prompt adds keywords to headers and body text, but you should also optimize any additional elements you would add afterward (e.g., internal links, captions below videos, alt values for images, etc.).

Add citations of relevant, authoritative sources to enhance credibility (if applicable).

## Flow

```mermaid
flowchart TD
    A[User provides topic] --> B{Is topic specific enough?}

    B -- No --> C[Ask user for clarification]
    C --> A

    B -- Yes --> D[Generate 5 search queries]

    D --> E[Search internet for related articles]

    E --> F[Collect article URLs]

    F --> G[Parallel: Open each article]
    G --> H[Extract markdown text]

    H --> I[Keyword extraction agent]

    I --> J[Summarize articles]

    J --> K["Generate 5 SEO article ideas (topic + keywords + summaries)"]

    K --> L[User selects one idea]

    L --> M[Article Writer Agent]

    M --> N[SEO Expert Agent 1]
    M --> O[SEO Expert Agent 2]
    M --> P[SEO Expert Agent 3]
    M --> Q[SEO Expert Agent 4]
    M --> R[SEO Expert Agent 5]

    N --> S[Aggregate Feedback]
    O --> S
    P --> S
    Q --> S
    R --> S

    S --> T{All approve?}

    T -- Yes --> U[Final Article]
    T -- No --> V[Revise Article using feedback]
    V --> M
```
