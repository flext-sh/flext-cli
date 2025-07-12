# Pydantic Standardization for flext-cli

## Summary of Changes

This document tracks the standardization of Pydantic usage in flext-cli to use flext-core base models.

### Changes Made

1. **Updated `src/flext_cli/client.py`**:

   - Replaced direct `BaseModel` import from pydantic with `APIBaseModel` from flext-core
   - All model classes now inherit from `APIBaseModel` instead of `BaseModel`
   - Kept `PipelineConfig` as a local model since the CLI uses Singer/Meltano specific fields (tap, target, transform) that differ from the generic flext-core PipelineConfig
   - Pipeline model remains local but now extends APIBaseModel

2. **Verified `src/flext_cli/core/base.py`**:
   - Already correctly imports `BaseSettings` from `flext_core.config.base`
   - No changes needed

### Model Hierarchy

```
flext_core.APIBaseModel
├── PipelineConfig (local - Singer/Meltano specific)
├── Pipeline (local - API response model)
└── PipelineList (local - paginated response)
```

### Benefits

- Consistent base model behavior across all FLEXT projects
- Centralized configuration for JSON serialization, validation, etc.
- Maintains compatibility with existing API while using standardized base classes

### Notes

- The local PipelineConfig model is necessary because flext-cli deals with Singer/Meltano pipelines which have different configuration structure than the generic pipeline configuration in flext-core
- All Pydantic method calls (model_validate, model_dump) continue to work as APIBaseModel extends pydantic's BaseModel
