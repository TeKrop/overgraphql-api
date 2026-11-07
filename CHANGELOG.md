# CHANGELOG

<!-- version list -->

## v1.5.1 (2026-11-07)

### Bug Fixes

- Nullable hero portrait and expose map uses
  ([#35](https://github.com/TeKrop/overgraphql-api/pull/35),
  [`68f0f7c`](https://github.com/TeKrop/overgraphql-api/commit/68f0f7c721f4bb4dc681a37b9402bb1fcece3d78))

### Build System

- Upgrade to Python 3.15 and bump dependencies
  ([#32](https://github.com/TeKrop/overgraphql-api/pull/32),
  [`1c8cfb0`](https://github.com/TeKrop/overgraphql-api/commit/1c8cfb02eeffcd5538c7cca4d5235798b71c546d))

- **deps**: Bump astral-sh/setup-uv from 10.0.1 to 10.1.0
  ([#28](https://github.com/TeKrop/overgraphql-api/pull/28),
  [`02a97f2`](https://github.com/TeKrop/overgraphql-api/commit/02a97f2e22fce9ca2fc000ab6e1652fa5b2c84ae))

- **deps**: Bump python-semantic-release/python-semantic-release from 10.6.1 to 10.6.2
  ([#25](https://github.com/TeKrop/overgraphql-api/pull/25),
  [`0cbdf13`](https://github.com/TeKrop/overgraphql-api/commit/0cbdf133eef7a0d870bc4cb91447c69989a06ff3))

### Documentation

- Trim derivable content from CLAUDE.md
  ([`a031128`](https://github.com/TeKrop/overgraphql-api/commit/a0311285643ef0d64e337317d0e5b99a09b16cf2))

### Refactoring

- Enforce DDD layering with import-linter ([#27](https://github.com/TeKrop/overgraphql-api/pull/27),
  [`c874d97`](https://github.com/TeKrop/overgraphql-api/commit/c874d970463707946dd150cad6ff2083106d1f74))


## v1.5.0 (2026-09-02)

### Build System

- **deps**: Bump astral-sh/setup-uv from 9.0.0 to 10.0.1
  ([#24](https://github.com/TeKrop/overgraphql-api/pull/24),
  [`481814e`](https://github.com/TeKrop/overgraphql-api/commit/481814ec0dcb5008fdf3dccc54a739a22e8b1c49))

### Features

- Added ban rate in heroes stats ([#26](https://github.com/TeKrop/overgraphql-api/pull/26),
  [`3287c69`](https://github.com/TeKrop/overgraphql-api/commit/3287c69422e4be4416245cdc5063d7c4b3609461))


## v1.4.0 (2026-08-13)

### Features

- Add emerald competitive division ([#23](https://github.com/TeKrop/overgraphql-api/pull/23),
  [`9941e12`](https://github.com/TeKrop/overgraphql-api/commit/9941e1251c02c4639dde1957f7ecd5eecbca35de))


## v1.3.0 (2026-08-01)

### Features

- Add Hero.stats (pickrate/winrate) from /heroes/stats
  ([#22](https://github.com/TeKrop/overgraphql-api/pull/22),
  [`3f31a9a`](https://github.com/TeKrop/overgraphql-api/commit/3f31a9a26c3ab8c52f25cc74922eb9a755d4e060))


## v1.2.1 (2026-08-01)

### Bug Fixes

- Enforce type annotations (ANN) and hide uv.lock bump from changelog
  ([#21](https://github.com/TeKrop/overgraphql-api/pull/21),
  [`07bed53`](https://github.com/TeKrop/overgraphql-api/commit/07bed53e089ef3c800ec287d0fa30d959d951038))


## v1.2.0 (2026-08-01)

### Build System

- **deps**: Bump astral-sh/setup-uv from 8.3.0 to 9.0.0
  ([#19](https://github.com/TeKrop/overgraphql-api/pull/19),
  [`eba7681`](https://github.com/TeKrop/overgraphql-api/commit/eba7681ff39680d5b47208327ad4a3dc86be2a12))

- **deps**: Bump python-semantic-release/python-semantic-release
  ([#18](https://github.com/TeKrop/overgraphql-api/pull/18),
  [`3386b08`](https://github.com/TeKrop/overgraphql-api/commit/3386b08f366c36074e91b4f28036eb42b291156b))

- **deps**: Bump schneegans/dynamic-badges-action from 1.8.0 to 1.9.0
  ([#17](https://github.com/TeKrop/overgraphql-api/pull/17),
  [`15c8322`](https://github.com/TeKrop/overgraphql-api/commit/15c8322b2226f11b5fb96b680b6bcb34184ac915))

- **deps**: Bump the uv-deps group with 2 updates
  ([#16](https://github.com/TeKrop/overgraphql-api/pull/16),
  [`f14f7b2`](https://github.com/TeKrop/overgraphql-api/commit/f14f7b26d028b13c166fbfb5ce86d6d241c849fd))

### Chores

- Add Dependabot configuration for package updates
  ([`3286c07`](https://github.com/TeKrop/overgraphql-api/commit/3286c07efd323977bb2864a04a9fb5d4d96e8c93))

- Add Docker and GitHub Actions to Dependabot config
  ([`88363bf`](https://github.com/TeKrop/overgraphql-api/commit/88363bf6a73d3a8bb5781e91433c5577403e7c63))

- Update uv.lock for v1.1.0
  ([`c1f5d00`](https://github.com/TeKrop/overgraphql-api/commit/c1f5d002b6961b74190e62ce630898c00defe284))

### Documentation

- Add CLAUDE.md for Claude Code guidance
  ([`e529fc4`](https://github.com/TeKrop/overgraphql-api/commit/e529fc460231a930aa09a99e1e0575c1e5d7ae6a))

### Features

- Add searchPlayers query ([#20](https://github.com/TeKrop/overgraphql-api/pull/20),
  [`dffe7ff`](https://github.com/TeKrop/overgraphql-api/commit/dffe7ffc1d8f65c55b5c689e2fd7fd7323c9fe23))


## v1.1.0 (2026-07-07)

### Chores

- Update uv.lock for v1.0.0
  ([`d002a7e`](https://github.com/TeKrop/overgraphql-api/commit/d002a7e30c2ceff41e7e6a8d6f9ddfa6dd652d1c))

### Features

- Add deploy job to release workflow ([#15](https://github.com/TeKrop/overgraphql-api/pull/15),
  [`4c9df58`](https://github.com/TeKrop/overgraphql-api/commit/4c9df580422421ab862be350ba313146b65e2bb3))


## v1.0.0 (2026-07-07)

- Initial Release
