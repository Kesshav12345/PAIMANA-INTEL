# TARGET LEAKAGE

- **Risk**: Including Status = Completed or using final project cost to predict cost overrun.
- **Mitigation**: Do not use Status derived from future months, and ensure targets are created from the *final* known project state (i.e. completion date) while features are only drawn from intermediate observations (t-n).