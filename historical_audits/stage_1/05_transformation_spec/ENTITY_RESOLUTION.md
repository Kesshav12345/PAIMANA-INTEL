# ENTITY RESOLUTION

- **Projects without IDs**: Older historical tables might lack standard Project IDs. A combination of [Project_Name, Sector, Original_Cost] should be used to heuristically link records over time. Use fuzzy string matching for Name changes.
- **Renamed Agencies**: Map legacy agency names to their modern counterparts via a lookup table.