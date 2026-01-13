# Phase 4: Intelligent Enhancement (Hybrid AI + Rule-Based)

**Status**: Proposal / Design Phase
**Version**: 1.0 Draft
**Date**: 2026-01-13
**Estimated Timeline**: 2-3 weeks (after Phase 3 complete)

---

## Executive Summary

Phase 4 adds intelligent enhancement capabilities to Xenocrates using a **two-tier hybrid approach**:

1. **Tier 1: Rule-Based Intelligence** (Default, always available)
   - Zero cost, privacy-preserving, deterministic
   - Keyword-based categorization
   - Co-occurrence cross-reference detection
   - Heuristic-based primary identification

2. **Tier 2: AI-Powered Review** (Optional, explicit opt-in)
   - Local-first architecture (Ollama/llama.cpp)
   - Cloud API support (Anthropic Claude) with consent
   - Review mode only (never auto-applies)
   - Cost estimation and privacy warnings

**Critical Design Principle**: AI is an **optional assistant**, not a replacement for user judgment.

---

## Problem Statement

### Current State (Post Phase 1-3)

Users manually specify:
- **Categories**: Hierarchical organization
- **SeeAlso**: Cross-references to related terms
- **Primary**: Which page is the main reference

**Pain Points:**
- Large indexes (1000+ entries): Manual tagging is time-consuming
- Consistency: Hard to maintain uniform categorization
- Discovery: Users might miss valuable cross-references
- Updates: Revising categories across many entries is tedious

### Proposed Solution

**Intelligent suggestions** that:
1. Analyze existing entries
2. Suggest categories, cross-references, primary markings
3. Output recommendations for user review
4. User manually applies accepted suggestions

**Non-Goals:**
- ❌ Auto-modify user's index without review
- ❌ Replace user's domain expertise
- ❌ Require internet/API for basic functionality
- ❌ Send proprietary/sensitive data without explicit consent

---

## Critical Challenges & Concerns

### 1. Privacy & Security 🔒

**The Big Problem**: GIAC exam notes may contain:
- Proprietary SANS course material references
- Company-specific security information
- Personal study strategies
- Exam-related content (potential policy violations)

**Risk**: Sending to external APIs violates:
- SANS copyright policies
- Corporate NDAs
- Certification exam policies
- Privacy expectations

**Mitigation Strategy**:

```python
# Privacy Tiers (user selects)

Tier 1: Local Only (Default)
- All processing on user's machine
- Ollama/llama.cpp with local models
- Zero data leaves system
- Slower but 100% private

Tier 2: Anonymized Cloud
- Strip descriptions, keep only titles/structure
- Send minimal metadata for analysis
- User reviews what's sent before transmission
- Clear consent dialog with examples

Tier 3: Full Cloud (Requires explicit consent)
- Send full content for deep analysis
- Show exact data being transmitted
- Warning about proprietary content
- Confirmation: "I own this content and consent to share"
```

**Implementation**:

```python
def require_ai_consent():
    """
    Display privacy policy and require explicit consent.
    """
    print("""
    ⚠️  AI ENHANCEMENT PRIVACY NOTICE

    You are about to send index data to an external AI service.

    Data being sent:
    - Entry titles: Yes
    - Descriptions: [Yes/No - configurable]
    - Book/page references: Yes
    - Your IP address: Yes (API requirement)

    This data will be:
    - Processed by: Anthropic Claude API
    - Stored: Per Anthropic's policy (30 days for abuse detection)
    - Used for: Enhancement suggestions only

    ⚠️  DO NOT proceed if your notes contain:
    - Proprietary course material
    - Company confidential information
    - Content under NDA

    Alternative: Use --ai-provider=local for offline processing

    Type 'I CONSENT' to proceed:
    """)

    consent = input().strip()
    if consent != "I CONSENT":
        print("AI enhancement cancelled. Use --smart-suggestions for offline analysis.")
        sys.exit(0)
```

### 2. Cost Analysis 💰

**Anthropic Claude API Pricing** (2025):
- Sonnet 4: $3/M input tokens, $15/M output tokens
- Haiku: $0.25/M input, $1.25/M output

**Index Cost Estimation**:

```python
Typical Index (500 entries):
- Input: ~250K tokens (titles + descriptions)
- Output: ~25K tokens (suggestions)
- Cost (Sonnet): $0.75 + $0.38 = $1.13
- Cost (Haiku): $0.06 + $0.03 = $0.09

Large Index (5000 entries):
- Input: ~2.5M tokens (may need chunking)
- Output: ~250K tokens
- Cost (Sonnet): $7.50 + $3.75 = $11.25
- Cost (Haiku): $0.63 + $0.31 = $0.94

Context window limits:
- Claude Sonnet 4: 200K tokens input
- Need chunking for indexes >5K entries
```

**Cost Control Implementation**:

```python
def estimate_cost(index, model='sonnet-4'):
    """
    Estimate API cost before running.
    """
    token_count = estimate_tokens(index)

    pricing = {
        'sonnet-4': {'input': 3.0, 'output': 15.0},
        'haiku': {'input': 0.25, 'output': 1.25}
    }

    cost = calculate_cost(token_count, pricing[model])

    print(f"""
    Estimated Cost:
    - Entries: {len(index)}
    - Tokens: ~{token_count:,} input, ~{token_count//10:,} output
    - Model: {model}
    - Cost: ${cost:.2f}

    Continue? [y/N]:
    """)

    return input().strip().lower() == 'y'
```

### 3. Context Window Management 🪟

**Problem**: Large indexes exceed model context limits

**Example**:
```
Claude Sonnet 4: 200K token limit
Average entry: ~50 tokens (title + description + metadata)
Maximum entries: ~4,000 per request
```

**Chunking Strategy**:

```python
def chunk_index_for_ai(index, max_tokens=100000):
    """
    Split large indexes into processable chunks while maintaining context.

    Strategy:
    1. Group by alphabetical section (Aa, Bb, Cc...)
    2. Include overlap for cross-references
    3. Maintain global context summary
    """
    chunks = []
    current_chunk = []
    current_tokens = 0

    # Sort entries alphabetically
    sorted_entries = sorted(index.items())

    # Build global context summary (sent with each chunk)
    global_summary = build_summary(sorted_entries)  # ~500 tokens

    for title, refs in sorted_entries:
        entry_tokens = estimate_entry_tokens(title, refs)

        if current_tokens + entry_tokens > max_tokens:
            # Finalize current chunk
            chunks.append({
                'context': global_summary,
                'entries': current_chunk,
                'overlap': get_overlap_context(current_chunk[-10:])  # Last 10 for continuity
            })

            # Start new chunk with overlap
            current_chunk = get_overlap_entries(current_chunk[-10:])
            current_tokens = sum(estimate_entry_tokens(e) for e in current_chunk)

        current_chunk.append((title, refs))
        current_tokens += entry_tokens

    # Add final chunk
    if current_chunk:
        chunks.append({
            'context': global_summary,
            'entries': current_chunk,
            'overlap': []
        })

    return chunks

def process_chunks_with_ai(chunks):
    """
    Process each chunk and merge results.
    """
    all_suggestions = {
        'categories': {},
        'cross_references': {},
        'primary_refs': {}
    }

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")

        suggestions = ai_analyze_chunk(chunk)
        merge_suggestions(all_suggestions, suggestions)

        # Rate limiting
        time.sleep(1)  # Be respectful to API

    return all_suggestions
```

### 4. Quality & Reliability 🎯

**Challenge**: AI outputs are non-deterministic and may hallucinate

**Quality Metrics Required**:

```python
# Testing framework for AI suggestions

def test_ai_suggestion_quality():
    """
    Test AI suggestions against known-good dataset.
    """
    test_cases = load_test_index('tests/ai/known_good_index.tsv')

    # Known ground truth
    expected_categories = load_expected('tests/ai/expected_categories.json')
    expected_crossrefs = load_expected('tests/ai/expected_crossrefs.json')

    # Get AI suggestions
    ai_suggestions = ai_enhance(test_cases)

    # Measure accuracy
    metrics = {
        'category_accuracy': measure_accuracy(
            ai_suggestions['categories'],
            expected_categories
        ),
        'crossref_precision': measure_precision(
            ai_suggestions['cross_references'],
            expected_crossrefs
        ),
        'crossref_recall': measure_recall(
            ai_suggestions['cross_references'],
            expected_crossrefs
        ),
        'false_positive_rate': measure_false_positives(
            ai_suggestions,
            expected_categories
        )
    }

    # Quality thresholds
    assert metrics['category_accuracy'] > 0.80  # 80% correct
    assert metrics['crossref_precision'] > 0.85  # 85% relevant
    assert metrics['false_positive_rate'] < 0.10  # <10% wrong

    return metrics
```

---

## Tier 1: Rule-Based Intelligence (Recommended Default)

**Goal**: Provide 80% of the value with 0% cost and 100% privacy

### Feature 1: Keyword-Based Categorization

**Implementation**:

```python
# User-configurable keyword mapping
DEFAULT_CATEGORY_KEYWORDS = {
    'Cryptography': {
        'keywords': ['encryption', 'cipher', 'aes', 'rsa', 'des', 'hash',
                     'cryptography', 'symmetric', 'asymmetric', 'key'],
        'subcategories': {
            'Symmetric': ['aes', 'des', '3des', 'symmetric'],
            'Asymmetric': ['rsa', 'ecc', 'dsa', 'asymmetric'],
            'Hashing': ['sha', 'md5', 'hash', 'digest']
        }
    },
    'Network Security': {
        'keywords': ['firewall', 'ids', 'ips', 'network', 'packet',
                     'snort', 'suricata', 'acl'],
        'subcategories': {
            'Prevention': ['firewall', 'ips', 'prevention'],
            'Detection': ['ids', 'detection', 'monitoring']
        }
    },
    'Web Security': {
        'keywords': ['xss', 'sql injection', 'csrf', 'web', 'owasp',
                     'cors', 'http', 'https', 'ssl', 'tls'],
        'subcategories': {
            'Injection': ['sql', 'xss', 'injection'],
            'Authentication': ['session', 'cookie', 'jwt', 'oauth']
        }
    }
}

def suggest_categories_rule_based(index, keyword_map=DEFAULT_CATEGORY_KEYWORDS):
    """
    Suggest categories based on keyword matching.

    Returns: dict of {title: [(category, confidence), ...]}
    """
    suggestions = {}

    for title, refs in index.items():
        # Analyze title and descriptions
        text = f"{title} {' '.join(r['description'] for r in refs)}".lower()

        category_scores = defaultdict(float)
        subcategory_scores = defaultdict(lambda: defaultdict(float))

        for category, config in keyword_map.items():
            # Main category scoring
            for keyword in config['keywords']:
                if keyword in text:
                    # Weight by keyword length (longer = more specific)
                    weight = len(keyword.split())
                    category_scores[category] += weight

            # Subcategory scoring
            for subcategory, subkeywords in config.get('subcategories', {}).items():
                for keyword in subkeywords:
                    if keyword in text:
                        weight = len(keyword.split())
                        subcategory_scores[category][subcategory] += weight

        # Build suggestions if confident
        title_suggestions = []
        for category, score in sorted(category_scores.items(),
                                     key=lambda x: x[1],
                                     reverse=True):
            if score > 0:
                confidence = min(score / 5.0, 1.0)  # Cap at 1.0

                # Find best subcategory
                if category in subcategory_scores:
                    best_sub = max(subcategory_scores[category].items(),
                                  key=lambda x: x[1])[0]
                    suggested_category = f"{category} > {best_sub}"
                else:
                    suggested_category = category

                title_suggestions.append((suggested_category, confidence))

        if title_suggestions:
            suggestions[title] = title_suggestions

    return suggestions
```

**Usage**:

```bash
python xenocrates.py notes.xlsx index.html --smart-suggestions

# Output: smart-suggestions.json
{
  "categories": {
    "AES ENCRYPTION": [
      {"category": "Cryptography > Symmetric", "confidence": 0.95},
      {"category": "Encryption", "confidence": 0.80}
    ],
    "FIREWALL": [
      {"category": "Network Security > Prevention", "confidence": 0.90}
    ]
  },
  "statistics": {
    "entries_analyzed": 500,
    "categories_suggested": 450,
    "avg_confidence": 0.87
  }
}
```

### Feature 2: Co-Occurrence Cross-Reference Detection

**Algorithm**:

```python
def suggest_crossrefs_cooccurrence(index):
    """
    Suggest cross-references based on:
    1. Entries that appear on same pages
    2. Titles mentioned in descriptions
    3. Shared book/course references
    """
    suggestions = defaultdict(set)

    # Build page co-occurrence matrix
    page_entries = defaultdict(set)
    for title, refs in index.items():
        for ref in refs:
            page_key = (ref['book'], ref['page'])
            page_entries[page_key].add(title)

    # Find co-occurring entries
    for page_key, titles in page_entries.items():
        if len(titles) > 1:
            # All entries on same page are potentially related
            for title in titles:
                suggestions[title].update(titles - {title})

    # Find mentions in descriptions
    for title, refs in index.items():
        for other_title in index.keys():
            if other_title != title:
                # Check if other_title mentioned in this entry's descriptions
                for ref in refs:
                    if other_title.lower() in ref['description'].lower():
                        suggestions[title].add(other_title)
                        suggestions[other_title].add(title)  # Bidirectional

    # Calculate confidence scores
    scored_suggestions = {}
    for title, related_titles in suggestions.items():
        scored = []
        for related in related_titles:
            # Score based on multiple signals
            score = calculate_relationship_score(
                index[title],
                index[related],
                page_entries
            )
            if score > 0.3:  # Confidence threshold
                scored.append((related, score))

        if scored:
            scored_suggestions[title] = sorted(scored,
                                              key=lambda x: x[1],
                                              reverse=True)[:5]  # Top 5

    return scored_suggestions

def calculate_relationship_score(entry1_refs, entry2_refs, page_entries):
    """
    Calculate relationship score between two entries.
    """
    score = 0.0

    # Same page appearances
    pages1 = {(r['book'], r['page']) for r in entry1_refs}
    pages2 = {(r['book'], r['page']) for r in entry2_refs}
    shared_pages = pages1 & pages2
    score += len(shared_pages) * 0.3

    # Same book
    books1 = {r['book'] for r in entry1_refs}
    books2 = {r['book'] for r in entry2_refs}
    shared_books = books1 & books2
    score += len(shared_books) * 0.1

    # Description mentions (already checked by caller)
    # This is the strongest signal
    score += 0.5

    return min(score, 1.0)
```

### Feature 3: Primary Reference Heuristics

**Logic**:

```python
def suggest_primary_refs(index):
    """
    Suggest which references should be marked as primary.

    Heuristics:
    1. Longest description = likely most detailed
    2. First occurrence in book = likely introduction
    3. Explicit keywords ("definition", "main", "primary")
    """
    suggestions = {}

    for title, refs in index.items():
        if len(refs) <= 1:
            continue  # Only one ref, already primary by default

        scored_refs = []

        for ref in refs:
            score = 0.0
            desc = ref['description'].lower()

            # Length score (longer = more detailed)
            desc_length = len(desc.split())
            score += min(desc_length / 50.0, 0.4)  # Max 0.4 for length

            # Keyword score
            primary_keywords = ['definition', 'introduction', 'overview',
                               'main', 'primary', 'fundamentals']
            for keyword in primary_keywords:
                if keyword in desc:
                    score += 0.3

            # First occurrence in book (lower page = higher score)
            # Normalize page to 0-1 range (assume max page 999)
            try:
                page_num = int(ref['page'])
                first_occurrence_score = max(0, 1 - (page_num / 999.0)) * 0.3
                score += first_occurrence_score
            except ValueError:
                pass  # Non-numeric page

            scored_refs.append((ref, min(score, 1.0)))

        # Suggest highest scoring ref as primary
        best_ref, best_score = max(scored_refs, key=lambda x: x[1])

        if best_score > 0.5:  # Confidence threshold
            suggestions[title] = {
                'suggested_primary': best_ref,
                'confidence': best_score,
                'reasoning': explain_primary_choice(best_ref, best_score)
            }

    return suggestions
```

### Feature 4: Smart Duplicate Detection

**Beyond exact matching**:

```python
def detect_smart_duplicates(index):
    """
    Find near-duplicates and suggest merges.

    - Levenshtein distance
    - Plural forms
    - Acronym expansions
    """
    from difflib import SequenceMatcher

    suggestions = []
    titles = list(index.keys())

    for i, title1 in enumerate(titles):
        for title2 in titles[i+1:]:
            similarity = SequenceMatcher(None, title1, title2).ratio()

            if similarity > 0.85:  # Very similar
                # Check if one is plural of other
                if is_plural_form(title1, title2):
                    suggestions.append({
                        'type': 'plural_merge',
                        'titles': [title1, title2],
                        'suggestion': f"Merge '{title1}' and '{title2}' (plural forms)",
                        'confidence': 0.95
                    })
                # Check if one is acronym
                elif is_acronym_expansion(title1, title2):
                    suggestions.append({
                        'type': 'acronym_link',
                        'titles': [title1, title2],
                        'suggestion': f"Add cross-reference between acronym and expansion",
                        'confidence': 0.90
                    })
                else:
                    # Generic similar title
                    suggestions.append({
                        'type': 'similar',
                        'titles': [title1, title2],
                        'suggestion': f"Review for potential duplicate/merge",
                        'confidence': similarity
                    })

    return suggestions

def is_plural_form(str1, str2):
    """Check if one string is plural of another."""
    return (str1 + 'S' == str2 or str2 + 'S' == str1 or
            str1 + 'ES' == str2 or str2 + 'ES' == str1)
```

### Output Format

**smart-suggestions.json**:

```json
{
  "metadata": {
    "generated": "2026-01-13T10:30:00Z",
    "index_file": "notes.xlsx",
    "entries_analyzed": 500,
    "suggestions_generated": 450,
    "tier": "rule-based"
  },
  "categories": {
    "AES ENCRYPTION": [
      {
        "category": "Cryptography > Symmetric",
        "confidence": 0.95,
        "reasoning": "Keywords: encryption(3), cipher(2), symmetric(1)"
      }
    ]
  },
  "cross_references": {
    "FIREWALL": [
      {
        "see_also": "IDS",
        "confidence": 0.88,
        "reasoning": "Co-occurs on SEC503 p.89-91"
      },
      {
        "see_also": "IPS",
        "confidence": 0.85,
        "reasoning": "Mentioned in description"
      }
    ]
  },
  "primary_references": {
    "KERBEROS": {
      "suggested_primary": {"book": "SEC505", "page": "201"},
      "confidence": 0.87,
      "reasoning": "Longest description (145 words), contains 'definition'"
    }
  },
  "duplicates": [
    {
      "type": "plural_merge",
      "titles": ["FIREWALL", "FIREWALLS"],
      "suggestion": "Merge plural forms",
      "confidence": 0.95
    }
  ]
}
```

---

## Tier 2: AI-Powered Review (Optional)

**For users who want deeper analysis and have consented to data sharing**

### Architecture: Local-First Design

```python
# Priority order for AI providers
AI_PROVIDERS = {
    'local': LocalAIProvider,      # Default, uses Ollama/llama.cpp
    'anthropic': AnthropicProvider,  # Claude API
    'openai': OpenAIProvider,        # Future expansion
    'azure': AzureOpenAIProvider     # Enterprise users
}

def get_ai_provider(provider_name='local'):
    """
    Factory method for AI providers.

    Local provider doesn't require API keys or internet.
    """
    if provider_name == 'local':
        return LocalAIProvider()
    elif provider_name == 'anthropic':
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set.\n"
                "Get your API key at: https://console.anthropic.com/\n"
                "Or use --ai-provider=local for offline processing."
            )
        return AnthropicProvider(api_key)
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")
```

### Local AI Provider Implementation

```python
class LocalAIProvider:
    """
    Uses local models via Ollama or llama.cpp.
    No data leaves the machine.
    """

    def __init__(self):
        self.check_local_model_availability()

    def check_local_model_availability(self):
        """Check if Ollama is installed and has usable models."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True
            )

            models = result.stdout
            if 'llama' not in models.lower():
                print("""
                Warning: No suitable local model found.

                Install Ollama and pull a model:
                  curl https://ollama.ai/install.sh | sh
                  ollama pull llama2

                Or use --ai-provider=anthropic (requires API key)
                """)
                sys.exit(1)

        except FileNotFoundError:
            print("""
            Ollama not found. Install it to use local AI:
              https://ollama.ai/

            Or use --ai-provider=anthropic (requires API key)
            """)
            sys.exit(1)

    def analyze_index(self, index_data, analysis_type):
        """
        Send data to local Ollama model.
        """
        prompt = self.build_prompt(index_data, analysis_type)

        # Call Ollama API (localhost:11434)
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',  # Or user-configured
                'prompt': prompt,
                'stream': False
            }
        )

        return self.parse_response(response.json())
```

### Anthropic Claude Provider Implementation

```python
class AnthropicProvider:
    """
    Uses Anthropic Claude API for analysis.
    Requires explicit user consent.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
        self.usage_stats = {'input_tokens': 0, 'output_tokens': 0}

    def analyze_index(self, index_data, analysis_type):
        """
        Send data to Claude API with safety checks.
        """
        # Estimate cost first
        estimated_cost = self.estimate_cost(index_data)
        if not self.confirm_cost(estimated_cost):
            return None

        # Build prompt
        prompt = self.build_prompt(index_data, analysis_type)

        # Make API call with safety limits
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",  # Latest model
                max_tokens=8000,
                temperature=0.3,  # Lower for more consistent results
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track usage
            self.usage_stats['input_tokens'] += message.usage.input_tokens
            self.usage_stats['output_tokens'] += message.usage.output_tokens

            return self.parse_response(message.content[0].text)

        except anthropic.APIError as e:
            print(f"API Error: {e}")
            return None

    def estimate_cost(self, index_data):
        """Estimate API cost before running."""
        token_count = self.estimate_tokens(index_data)

        # Pricing for Sonnet 4
        input_cost = (token_count / 1_000_000) * 3.0
        output_cost = (token_count / 10 / 1_000_000) * 15.0  # Assume 10:1 ratio

        return input_cost + output_cost

    def confirm_cost(self, estimated_cost):
        """Ask user to confirm cost."""
        response = input(f"""
        Estimated API cost: ${estimated_cost:.2f}

        Proceed? [y/N]:
        """)
        return response.strip().lower() == 'y'

    def get_final_cost_report(self):
        """Report actual costs after completion."""
        input_cost = (self.usage_stats['input_tokens'] / 1_000_000) * 3.0
        output_cost = (self.usage_stats['output_tokens'] / 1_000_000) * 15.0
        total_cost = input_cost + output_cost

        return f"""
        API Usage Summary:
        - Input tokens: {self.usage_stats['input_tokens']:,}
        - Output tokens: {self.usage_stats['output_tokens']:,}
        - Total cost: ${total_cost:.2f}
        """
```

### Prompt Engineering & Testing

**Critical: Prompts must be rigorously tested**

```python
# Prompt templates for different analysis types

CATEGORY_ANALYSIS_PROMPT = """
You are an expert indexer helping categorize entries for a {domain} examination index.

Context:
- This is a study index for {exam_name} certification
- Entries reference course materials: {books}
- Index contains {entry_count} entries

Task: Suggest hierarchical categories for these entries.

Requirements:
1. Categories should be 2-3 levels deep (Main > Sub > Subsub)
2. Use standard domain terminology
3. Keep categories broad enough to group 5-10 related entries
4. Return ONLY valid JSON, no markdown formatting

Entries to categorize:
{entries}

Output format (JSON only):
{{
  "categories": {{
    "ENTRY_TITLE": {{
      "category": "Main Category > Subcategory",
      "confidence": 0.95,
      "reasoning": "Brief explanation"
    }}
  }}
}}
"""

CROSSREF_ANALYSIS_PROMPT = """
You are an expert indexer identifying cross-references for a {domain} examination index.

Task: Identify related entries that should reference each other.

Criteria for cross-references:
1. Conceptually related topics (e.g., Firewall ↔ IDS)
2. Prerequisite relationships (e.g., TCP ↔ Three-way handshake)
3. Comparison pairs (e.g., AES ↔ RSA)
4. Part-whole relationships (e.g., OSI Model ↔ Network Layer)

Do NOT suggest cross-references for:
- Unrelated topics
- Overly broad connections
- Entries already linked via categories

Entries:
{entries}

Output format (JSON only):
{{
  "cross_references": {{
    "ENTRY_1": [
      {{"see_also": "RELATED_ENTRY", "confidence": 0.88, "reasoning": "Why related"}},
    ]
  }}
}}
"""
```

### Testing Framework

```python
# tests/ai/test_prompt_quality.py

class TestPromptQuality(unittest.TestCase):
    """
    Test AI prompt responses against known-good dataset.
    """

    def setUp(self):
        """Load test data."""
        self.test_index = load_test_index('tests/ai/security_index_sample.tsv')
        self.expected_categories = load_json('tests/ai/expected_categories.json')
        self.expected_crossrefs = load_json('tests/ai/expected_crossrefs.json')

    def test_category_accuracy_anthropic(self):
        """Test category suggestions meet accuracy threshold."""
        provider = AnthropicProvider(os.environ['ANTHROPIC_TEST_API_KEY'])

        results = provider.analyze_index(self.test_index, 'categories')

        accuracy = calculate_accuracy(
            results['categories'],
            self.expected_categories
        )

        self.assertGreater(accuracy, 0.80,
                          "Category accuracy below 80% threshold")

    def test_crossref_precision(self):
        """Test cross-reference suggestions are relevant."""
        provider = AnthropicProvider(os.environ['ANTHROPIC_TEST_API_KEY'])

        results = provider.analyze_index(self.test_index, 'cross_references')

        precision = calculate_precision(
            results['cross_references'],
            self.expected_crossrefs
        )

        self.assertGreater(precision, 0.85,
                          "Cross-reference precision below 85%")

    def test_false_positive_rate(self):
        """Ensure AI doesn't suggest too many incorrect links."""
        provider = AnthropicProvider(os.environ['ANTHROPIC_TEST_API_KEY'])

        results = provider.analyze_index(self.test_index, 'cross_references')

        false_positive_rate = calculate_false_positive_rate(
            results['cross_references'],
            self.test_index
        )

        self.assertLess(false_positive_rate, 0.10,
                       "False positive rate above 10% threshold")

    def test_local_vs_cloud_consistency(self):
        """Test local model gives similar results to cloud API."""
        local = LocalAIProvider()
        cloud = AnthropicProvider(os.environ['ANTHROPIC_TEST_API_KEY'])

        local_results = local.analyze_index(self.test_index, 'categories')
        cloud_results = cloud.analyze_index(self.test_index, 'categories')

        similarity = calculate_result_similarity(local_results, cloud_results)

        # We expect some variance, but should be >60% similar
        self.assertGreater(similarity, 0.60,
                          "Local and cloud results too divergent")
```

---

## Security Best Practices

### 1. API Key Management

```python
# ❌ NEVER do this:
API_KEY = "sk-ant-api03-..."

# ✅ Always use environment variables:
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# ✅ Support multiple sources:
def get_api_key():
    """
    Get API key from multiple sources in order of preference.
    """
    # 1. Environment variable
    key = os.environ.get('ANTHROPIC_API_KEY')
    if key:
        return key

    # 2. Config file (encrypted)
    config_file = os.path.expanduser('~/.xenocrates/config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            key = config.get('anthropic_api_key')
            if key:
                # Decrypt if stored encrypted
                return decrypt_api_key(key)

    # 3. Prompt user (don't store)
    print("Anthropic API key not found.")
    print("Get your API key at: https://console.anthropic.com/")
    key = getpass.getpass("Enter API key (input hidden): ")

    # Ask if user wants to save (encrypted)
    save = input("Save key for future use? [y/N]: ")
    if save.lower() == 'y':
        save_encrypted_api_key(key, config_file)

    return key

def save_encrypted_api_key(key, config_file):
    """
    Save API key encrypted (not plaintext).
    Uses system keyring if available.
    """
    try:
        import keyring
        keyring.set_password('xenocrates', 'anthropic_api_key', key)
        print("API key saved securely in system keyring.")
    except ImportError:
        # Fallback: Save with basic encryption
        print("Warning: keyring module not found. Using basic encryption.")
        encrypted = basic_encrypt(key)
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump({'anthropic_api_key': encrypted}, f)
        os.chmod(config_file, 0o600)  # Owner read/write only
```

### 2. Input Sanitization

```python
def sanitize_for_ai(entry):
    """
    Sanitize entry before sending to external API.
    Remove PII, limit size, validate structure.
    """
    sanitized = {}

    # Keep only essential fields
    sanitized['title'] = entry['title'][:200]  # Limit length

    # Optional: Strip descriptions for privacy
    if PRIVACY_MODE == 'anonymized':
        sanitized['description'] = '[REDACTED]'
    else:
        # Remove potential PII patterns
        desc = entry['description']
        desc = remove_email_addresses(desc)
        desc = remove_ip_addresses(desc)
        desc = remove_names(desc)  # Use NER if available
        sanitized['description'] = desc[:500]  # Limit length

    # Validate no secrets leaked
    if contains_api_key_pattern(sanitized['description']):
        raise ValueError("Entry contains pattern resembling API key!")

    return sanitized

def remove_email_addresses(text):
    """Remove email addresses from text."""
    import re
    return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                  '[EMAIL]', text)

def remove_ip_addresses(text):
    """Remove IP addresses from text."""
    import re
    return re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                  '[IP]', text)
```

### 3. Rate Limiting & Retry Logic

```python
class RateLimitedAPIClient:
    """
    Wrapper for API clients with rate limiting and retry logic.
    """

    def __init__(self, provider, requests_per_minute=50):
        self.provider = provider
        self.rpm_limit = requests_per_minute
        self.request_times = []

    def call_api(self, *args, **kwargs):
        """
        Make API call with rate limiting and retries.
        """
        # Rate limiting
        self.wait_if_needed()

        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                result = self.provider.analyze_index(*args, **kwargs)
                self.record_request()
                return result

            except anthropic.RateLimitError:
                if attempt < max_retries - 1:
                    print(f"Rate limited. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise

            except anthropic.APIError as e:
                if attempt < max_retries - 1 and e.status_code >= 500:
                    # Server error, retry
                    print(f"Server error. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise

    def wait_if_needed(self):
        """Wait if we've hit rate limit."""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.rpm_limit:
            # Wait until oldest request is >60s old
            oldest = min(self.request_times)
            wait_time = 60 - (now - oldest) + 1
            print(f"Rate limit reached. Waiting {wait_time:.0f}s...")
            time.sleep(wait_time)

    def record_request(self):
        """Record timestamp of successful request."""
        self.request_times.append(time.time())
```

### 4. Data Validation

```python
def validate_ai_response(response, expected_schema):
    """
    Validate AI response against expected schema.
    Prevents injection attacks and ensures data integrity.
    """
    import jsonschema

    try:
        jsonschema.validate(response, expected_schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"AI response validation failed: {e}")

    # Additional checks
    for title in response.get('categories', {}).keys():
        # Ensure title exists in our index (no hallucinated entries)
        if title not in original_index:
            print(f"Warning: AI suggested category for non-existent entry '{title}'")

    return True

CATEGORY_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "categories": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "maxLength": 200},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "reasoning": {"type": "string", "maxLength": 500}
                    },
                    "required": ["category", "confidence"]
                }
            }
        }
    },
    "required": ["categories"]
}
```

---

## Command-Line Interface

### Phase 4 Commands

```bash
# Tier 1: Rule-based (default, always available)
python xenocrates.py notes.xlsx index.html --smart-suggestions
# Output: smart-suggestions.json

# Apply suggestions interactively
python xenocrates.py notes.xlsx --apply-suggestions smart-suggestions.json
# Interactive: Review each suggestion, accept/reject

# Tier 2: AI-powered (opt-in)

# Local AI (privacy-first, no cost)
python xenocrates.py notes.xlsx index.html --ai-review --ai-provider=local
# Requires Ollama installed

# Cloud AI (requires API key and consent)
python xenocrates.py notes.xlsx index.html \
    --ai-review \
    --ai-provider=anthropic \
    --ai-consent-privacy-policy
# Shows cost estimate, requires confirmation

# Advanced options
python xenocrates.py notes.xlsx index.html \
    --ai-review \
    --ai-provider=anthropic \
    --ai-model=sonnet-4 \
    --ai-analyze=categories,crossrefs,primary \
    --ai-privacy-mode=anonymized

# Specific analysis types
python xenocrates.py notes.xlsx --ai-suggest-categories
python xenocrates.py notes.xlsx --ai-suggest-crossrefs
python xenocrates.py notes.xlsx --ai-suggest-primary
```

### Configuration File

**~/.xenocrates/config.yml**:

```yaml
# AI Enhancement Configuration

# Provider settings
ai:
  default_provider: local  # local, anthropic, openai

  # Local AI settings
  local:
    model: llama2
    endpoint: http://localhost:11434

  # Anthropic settings
  anthropic:
    model: claude-sonnet-4-20250514
    max_tokens: 8000
    temperature: 0.3

  # Privacy settings
  privacy_mode: anonymized  # full, anonymized, minimal

  # Cost controls
  max_cost_per_run: 5.00  # USD
  confirm_before_api_call: true

  # Analysis preferences
  enable_categories: true
  enable_crossrefs: true
  enable_primary: true

  # Confidence thresholds
  thresholds:
    category_min: 0.7
    crossref_min: 0.8
    primary_min: 0.7

# Rule-based settings
smart_suggestions:
  # Custom keyword mappings
  category_keywords:
    "Network Security":
      - firewall
      - ids
      - ips
      - packet
    "Cryptography":
      - encryption
      - cipher
      - hash
      - key
```

---

## Implementation Timeline

**Estimated: 2-3 weeks** (after Phase 3 complete)

### Week 1: Rule-Based Intelligence (Tier 1)

**Days 1-2: Keyword-based categorization**
- Implement DEFAULT_CATEGORY_KEYWORDS
- Add suggest_categories_rule_based()
- Create smart-suggestions.json output format
- Test with sample security index

**Days 3-4: Co-occurrence cross-reference detection**
- Implement page co-occurrence matrix
- Add description mention detection
- Calculate relationship scores
- Test accuracy on known-good data

**Day 5: Primary reference heuristics**
- Implement scoring algorithm
- Add explanation generation
- Test with multi-reference entries

**Days 6-7: Smart duplicate detection**
- Implement Levenshtein distance
- Add plural/acronym detection
- Create merge suggestions
- Integration testing

### Week 2: AI Infrastructure (Tier 2)

**Days 8-9: Local AI provider**
- Implement Ollama integration
- Create LocalAIProvider class
- Test with llama2 model
- Benchmark performance vs cloud

**Days 10-11: Anthropic Claude provider**
- Implement AnthropicProvider class
- Add API key management (secure)
- Implement cost estimation
- Add consent workflow

**Days 12-13: Prompt engineering**
- Design category analysis prompt
- Design cross-reference prompt
- Create test dataset
- Run accuracy tests (target: >80%)

**Day 14: Testing & refinement**
- Run full test suite
- Measure accuracy metrics
- Refine prompts based on results
- Document best practices

### Week 3: Integration & Polish

**Days 15-16: CLI integration**
- Add --smart-suggestions flag
- Add --ai-review flag
- Add --ai-provider option
- Implement interactive apply mode

**Days 17-18: Documentation**
- Update README with Phase 4 features
- Create AI_USAGE_GUIDE.md
- Add privacy policy
- Create video tutorial

**Day 19: Security review**
- API key storage audit
- Input sanitization verification
- Rate limiting testing
- Privacy mode validation

**Days 20-21: Beta testing**
- Recruit 5-10 users
- Gather feedback
- Fix bugs
- Optimize performance

---

## Success Metrics

### Tier 1 (Rule-Based) Success Criteria

- ✅ Category suggestions: >75% accuracy on test dataset
- ✅ Cross-reference suggestions: >80% precision, >60% recall
- ✅ Primary reference identification: >70% accuracy
- ✅ Duplicate detection: >90% detection of known duplicates
- ✅ Performance: <5 seconds for 1000-entry index
- ✅ Zero external dependencies (stdlib only)

### Tier 2 (AI-Powered) Success Criteria

- ✅ Category suggestions: >80% accuracy (better than rule-based)
- ✅ Cross-reference suggestions: >85% precision, >70% recall
- ✅ Local AI: Works offline, <30 seconds for 1000 entries
- ✅ Cloud API: Cost < $2 per 1000-entry index (Sonnet 4)
- ✅ Privacy: Zero data leaks in anonymized mode
- ✅ Security: API keys never logged or transmitted insecurely
- ✅ User consent: 100% explicit opt-in, clear warnings

### Quality Thresholds

**Will NOT ship if:**
- False positive rate >15% (too many wrong suggestions)
- API key leak vulnerability found
- Privacy mode can be bypassed
- Cost exceeds $5 per typical index

---

## Risks & Mitigation

### High-Risk Areas

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Privacy violation** | Critical | Local-first design; anonymized mode; explicit consent |
| **API key theft** | Critical | Never hardcode; use keyring; encrypt at rest |
| **Cost runaway** | High | Estimate + confirm before call; hard limits; user approval |
| **Poor quality suggestions** | High | Rigorous testing; confidence thresholds; user review required |
| **Dependency hell** | Medium | Optional feature; graceful degradation; clear error messages |

### Fallback Strategy

**If AI features cause problems:**
1. Can be completely disabled with no impact on Phases 1-3
2. Rule-based suggestions work standalone
3. User can always manually add metadata
4. No breaking changes to core functionality

---

## Alternatives Considered

### Option A: YOLO Mode (Auto-apply suggestions)

**Rejected because:**
- Too risky for exam preparation
- Could corrupt carefully prepared indexes
- Users lose control over their data
- False positives would be applied automatically

**Could add later if:**
- Extensive testing shows >95% accuracy
- User explicitly enables with multiple warnings
- Undo/rollback mechanism in place

### Option B: Multiple AI Providers from Day 1

**Deferred because:**
- Each provider has different API conventions
- Increases testing burden significantly
- Start with one (Claude) and expand based on demand

**Will add later if:**
- Users request specific providers
- Claude API has issues/limitations
- Cost comparison shows significant savings

### Option C: Real-time AI during indexing

**Rejected because:**
- Slows down index generation significantly
- Ties basic functionality to external service
- Not necessary - batch analysis is fine

### Option D: AI-generated descriptions

**Out of scope:**
- Too risky (hallucinations)
- Users should write descriptions based on study notes
- Could suggest edits, but not generate from scratch

---

## Future Enhancements (Post-Phase 4)

1. **Custom keyword training**
   - Let users train on their own indexes
   - Build domain-specific models

2. **Collaborative suggestions**
   - Share anonymized suggestion datasets
   - Community-improved categorization

3. **Visual category builder**
   - GUI for reviewing/editing AI suggestions
   - Drag-and-drop category organization

4. **Batch processing**
   - Process multiple indexes
   - Compare/merge suggestions across indexes

5. **Integration with study tools**
   - Anki flashcard generation
   - Quiz question suggestions
   - Study schedule optimization

---

## Conclusion

Phase 4 adds powerful intelligence to Xenocrates while respecting user privacy and maintaining simplicity. The **two-tier hybrid approach** gives users choice:

- **Tier 1 (Rule-Based)**: Fast, free, private, deterministic
- **Tier 2 (AI-Powered)**: Smarter, opt-in, local-first, reviewed

**Critical principles maintained:**
- ✅ Privacy-first design
- ✅ Local models supported from day 1
- ✅ Explicit user consent for cloud APIs
- ✅ Review mode only (no auto-apply by default)
- ✅ Optional feature (Phases 1-3 work standalone)
- ✅ Secure API key management
- ✅ Cost transparency and controls

**Recommendation**: Implement Tier 1 first (Week 1), then evaluate user feedback before committing to Tier 2.

---

## Appendix: Example Workflow

### User Story: Processing a Large GSE Index

**Scenario**: User has 2,000 entries for GSE Security Expert certification

**Step 1: Generate index with rule-based suggestions**
```bash
$ python xenocrates.py gse-notes.xlsx gse-index.html --smart-suggestions

Processing: 2000 entries
Analyzing patterns...
Generated smart-suggestions.json

Smart Suggestions Summary:
- Categories: 1,847 suggestions (92% coverage)
- Cross-references: 3,521 suggestions
- Primary references: 456 suggestions
- Duplicates: 23 potential merges

Review suggestions: smart-suggestions.json
```

**Step 2: Review and apply suggestions**
```bash
$ python xenocrates.py gse-notes.xlsx --apply-suggestions smart-suggestions.json

Interactive Review Mode

[1/1847] Category suggestion for "AES ENCRYPTION"
  Suggested: Cryptography > Symmetric
  Confidence: 0.95
  Reasoning: Keywords: encryption(3), cipher(2), symmetric(1)

  Accept? [y/n/skip-rest]: y  ✓ Applied

[2/1847] Category suggestion for "FIREWALL"
  Suggested: Network Security > Prevention
  Confidence: 0.88
  Reasoning: Keywords: firewall(4), packet(2), network(1)

  Accept? [y/n/skip-rest]: y  ✓ Applied

...

Summary:
- Accepted: 1,654 (89.6%)
- Rejected: 193 (10.4%)
- Time saved: ~3 hours
```

**Step 3 (Optional): Use AI for remaining entries**
```bash
$ python xenocrates.py gse-notes.xlsx --ai-review \
    --ai-provider=local \
    --ai-analyze=categories

Using local AI (Ollama - llama2)
No data will leave your machine.

Processing 346 uncategorized entries...
[==============>              ] 50% (173/346)

Completed! Generated ai-suggestions.json

AI Suggestions Summary:
- Additional categories: 298 suggestions
- Avg confidence: 0.82
- Processing time: 4m 32s
- Cost: $0.00
```

**Final result**: User categorized 2,000 entries in ~30 minutes (vs. 4-5 hours manually)

---

**Questions? Feedback?**
Open an issue: https://github.com/bioless/Xenocrates/issues

**Last Updated**: 2026-01-13
**Document Version**: 1.0 Draft
