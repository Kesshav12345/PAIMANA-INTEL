# LAYERED ARCHITECTURE

1. **RAW / SOURCE**: Extracted directly from PDF tables and CSVs without modification.
2. **STANDARDIZED / CANONICAL**: Normalized data types, resolved project IDs, resolved geography.
3. **DERIVED / ANALYTICAL**: Calculated features (velocity, escalation %, delays) based on the canonical layer.
4. **ML FEATURE / TARGET**: Structured for point-in-time training (features joined with target outcome labels).
5. **SERVING**: Denormalized views optimized for the dashboard interfaces.