# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.1.1 (07.07.2023)

### Fixed

- Avoid errors when communication directory is removed while wandb-osh is
  running.

## 1.1.0 (04.07.2023)

### Added

- Added support for pytorch lightning

### Changed

- Removed python 3.7 support

## 1.0.4 (18.01.2023)

### Fixed

- Explicitly add path to `wandb sync` calls (depending on the system, calling
  `wandb sync` inside the run dir resulted in "no runs to be synced" errors)

## 1.0.3 (18.01.2023)

### Fixed

- Fixed path to run directory when syncing with `wandb` and `TriggerWandbSyncHook`
  (without specifying explicit paths). See [#30](https://github.com/klieret/wandb-offline-sync-hook/issues/30)
  for more information

## 1.0.2 (01.01.2023)

### Changed

- Collect all command files, before starting to sync to ensure a minimal waiting
  timing between firing the hook and starting the sync (working around some
  race conditions)
