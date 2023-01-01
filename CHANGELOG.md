# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.2 (01.01.2023)

### Changed

- Collect all command files, before starting to sync to ensure a minimal waiting
  timing between firing the hook and starting the sync (working around some
  race conditions)
