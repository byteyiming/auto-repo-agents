# Ollama Token Limit Fix

## Problem

Ollama models were generating only ~2,300 characters while Gemini generates 8,000-10,000 characters. This was because:

1. **Ollama's default `num_predict` (output token limit) is very low** - typically around 512 tokens
2. **Gemini's default output limit is much higher** - 8,192 tokens
3. When `max_tokens` is not explicitly provided, Ollama uses its low default, resulting in short outputs

## Solution

Updated `OllamaProvider.generate()` to set a default of **8,192 tokens** when `max_tokens` is not provided, matching Gemini's default behavior.

### Changes Made

1. **Modified `src/llm/ollama_provider.py`**:
   - Added logic to set `max_tokens = 8192` when not provided
   - Added support for `OLLAMA_MAX_TOKENS` environment variable
   - This allows ~32,000 characters of output (4 chars per token average)

2. **Updated environment files**:
   - Added `OLLAMA_MAX_TOKENS` configuration option to `.env`, `.env.example`, `.env.production`, `.env.test`
   - Documented the new option with usage instructions

## Configuration

### Default Behavior

By default, Ollama will now use **8,192 tokens** for output, matching Gemini's behavior.

### Custom Configuration

You can override the default by setting the `OLLAMA_MAX_TOKENS` environment variable:

```bash
# In your .env file
OLLAMA_MAX_TOKENS=8192  # Default (same as Gemini)
OLLAMA_MAX_TOKENS=4096  # Lower limit (uses less memory)
OLLAMA_MAX_TOKENS=16384 # Higher limit (for very long documents)
```

### Token to Character Conversion

- **1 token ≈ 4 characters** (average)
- **8,192 tokens ≈ 32,768 characters**
- **4,096 tokens ≈ 16,384 characters**
- **16,384 tokens ≈ 65,536 characters**

## Expected Results

After this fix:
- ✅ Ollama should generate outputs similar in length to Gemini (8,000-10,000+ characters)
- ✅ Documents will be more comprehensive and detailed
- ✅ No code changes needed in agents - the fix is transparent

## Memory Considerations

Higher token limits use more memory:
- **8,192 tokens**: Recommended for most use cases (similar to Gemini)
- **4,096 tokens**: Good balance if memory is constrained
- **16,384+ tokens**: For very long documents, requires more RAM

## Testing

To verify the fix is working:

1. Check that `num_predict` is being set in the API request
2. Verify output lengths are now 8,000-10,000+ characters
3. Compare with previous outputs (should be ~3-4x longer)

## Notes

- The fix is backward compatible - existing code will automatically benefit
- You can still explicitly pass `max_tokens` to override the default
- The environment variable `OLLAMA_MAX_TOKENS` takes precedence over the hardcoded default

