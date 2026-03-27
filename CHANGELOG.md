## [0.7.3](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.2...v0.7.3) (2026-03-27)


### Bug Fixes

* **Game Screen:** add quit keyboard shortcut ([8005dbf](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8005dbf7ec34a1395cad717f872b57f8c4660e27))
* **game screen:** animation on lines cleared ([4d4dd10](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4d4dd10ad538e15da0c1ede2795c4b3ee47dc2bd))
* **Game Screen:** refresh labels when shown ([be214a8](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/be214a8fa9dc2f4f93ff6578b9afda4d438b7289))


### Performance Improvements

* move try again handler from app.py to game_screen.py ([0f6dab1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0f6dab14bfbb369d629f87d78ed904fe7c11fe39))

## [0.7.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.1...v0.7.2) (2026-03-26)


### Bug Fixes

* **game_screen:** add the quit button to end the current game ([79b3f80](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/79b3f80d7601745859b53398953ea7ffba2293a6))
* **game_screen:** add the try again button to start a new game ([8b1b4d4](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8b1b4d4e548f7037c78fb3c83ae0a206ccb76095))
* **menu_screen:** add quit button to exit the application ([7b4797b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/7b4797bafbd620386b22de1a7264f11651f9aade))

## [0.7.1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.7.0...v0.7.1) (2026-03-26)


### Bug Fixes

* when lines cleared, show them being cleared with a timeout among them ([c10e586](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/c10e586014e841b005fc78c486279577a8a2d4e0))

# [0.7.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.6.0...v0.7.0) (2026-03-26)


### Features

* **factory:** add BagTetrominoFactory with 7-bag algorithm ([bf5c878](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/bf5c87873379b8b7446bbbd63970a80e30fdfffa))
* **factory:** add ITetrominoFactory interface ([1005718](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/1005718732271ba9e098cc5e72796b7d3035aaad))
* **factory:** wire ITetrominoFactory into Tetris, replace monkeypatching in tests ([972b9db](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/972b9db718f207fc28693a91d29179f76912e475))


### Performance Improvements

* **test:** increase sleep ([00d67b0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/00d67b011b0b898cee3c2b9954669b4527176199))

# [0.6.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.5.0...v0.6.0) (2026-03-26)


### Features

* **i18n:** add python-i18n locale YAML files (en, it) ([4387836](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4387836aa9ae2843682019b66630654dfb426a4e))
* **i18n:** configure python-i18n in TetrisApp, remove I18n instance ([941749c](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/941749cfc1862a24b51ea047393cc1762f1625e5))
* **i18n:** migrate GameScreen to python-i18n direct API ([0718fe0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0718fe050e20e77340d310a31ba5da37096d7cf7))
* **i18n:** migrate MenuScreen to python-i18n direct API ([87f9047](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/87f90474b3fd1ff2781051ffea858dd9e8f35b50))
* **i18n:** remove custom I18n class and i18n tests ([4ae3334](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4ae3334b36cd8801e287fb0f0115f9fc69eb6a0c))

# [0.5.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.4.0...v0.5.0) (2026-03-26)


### Bug Fixes

* errors from static analysis ([a90a5c9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a90a5c9b207b84d8377f5993241799b58a530bb9))


### Features

* **view:** add BlockRenderer with image-to-integer mapping ([ed647ab](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/ed647abf6daaa65d9659f900856389e7872c6792))
* **view:** add IView interface and i18n module ([23993c0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/23993c04acb0fdb8376c19d3c47021eea6ce0a5e))
* **view:** add TetrisApp entry point and screen navigation ([7ed2fc6](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/7ed2fc6399eb2ef57778486432e34455f875dfa7))
* **view:** implement GameScreen layout, board rendering, Observer events and keyboard input ([a841775](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a84177583c451baac71bd05376fa7e7a2763a1af))
* **view:** implement MenuScreen with language selector ([310e65b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/310e65b8a986fd2501ec1976a9735ed861ea7acf))
* wire main() entry point to TetrisApp ([295742d](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/295742d4aaf7239f4e35ec0b20cdf489d3663761))

# [0.4.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.3.2...v0.4.0) (2026-03-11)


### Features

* **model:** implement Board class ([4cce391](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4cce39134dd03c799e89cac221b2f22a16e93886))
* **model:** implement Tetris class ([6e1f41f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/6e1f41fb05cda00d295a4397e2d89166b94447b4))


### Performance Improvements

* check if piece movement is valid in move method ([384b241](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/384b2418831219a15c1400e2316b3e57896932dc))
* improve code optimization ([a21fb06](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/a21fb061fc975038bd349427b29fff63bf819fe0))
* **test:** increase test coverage ([2b69f61](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/2b69f61d97f35892e47d2655db38a8900f343f85))

## [0.3.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.3.1...v0.3.2) (2026-03-11)


### Bug Fixes

* **devops:** add configuration to Dependabot ([8a6e773](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/8a6e773a7be74a3b9c998e7a9a1437b825489029))

## [0.3.1](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.3.0...v0.3.1) (2026-03-10)


### Bug Fixes

* **model:** update all dependencies for security issues ([cd13327](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/cd133272bb8e5c96ec074046753d11d2a18c7d9f))

# [0.3.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.2.0...v0.3.0) (2026-03-10)


### Bug Fixes

* change ShapeType number coding for future ui recognition ([7421f52](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/7421f52fb53349e27229a59a19a1f15619fc2483))
* define event type constants ([69fe789](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/69fe789530fa9c4f3ff7c4c5e3749b799ed5b8f3))
* define event type constants ([e8b7d11](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/e8b7d11498033253504589b0d26a8f2863dcae05))
* shapetype definition ([04a8547](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/04a8547e07c581d46bb80021eea7161ab9189920))


### Features

* define model interfaces ([0b1e46f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/0b1e46f643802d5ae1691debbedf9db7cb1f14de))

# [0.2.0](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.1.3...v0.2.0) (2026-03-08)


### Features

* **model:** define Tetromino class, shapes and tests ([720ae37](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/720ae378a813614482af4aaa93e39a1e136ebaf2))

## [0.1.3](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.1.2...v0.1.3) (2026-02-02)


### Bug Fixes

* **deploy:** update new_release variable to publish to PyPI ([4e826a5](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/4e826a55c2080d16ab1ae6ebce6119c571b8e1b8))

## [0.1.2](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/compare/v0.1.1...v0.1.2) (2026-02-02)


### Bug Fixes

* guess that everything's ready, ci/cd included ([776e1cc](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/776e1cc12373bb57f231ce40a3ed0776e73f7147))

# 0.1.1 (2026-02-02)


### Bug Fixes

* could not find observer ([17e46c9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/17e46c988970105b7588b9ec21002b2bbf8c030e))
* define first modules of model and gui ([c93b6a5](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/c93b6a598c5173acbb9e1f8eca85dd3dc018779f))
* move scripts in tasks ([806975f](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/806975f96c2f338af17ba0efc620358fec49903c))
* typify classes and methods ([fda4d99](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/fda4d9989697dc67a63a1743ac2cc6e65b7f727d))
* update build and release ([fef5cd9](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/fef5cd976732f409ad622ef4772da597c16e792b))
* update pre-commit operations ([cae804b](https://github.com/unibo-dtm-se-2425-OrecchietTetris/OrecchietTetris-artifact/commit/cae804bbfb523cc90d454f22b8aa571b5979a037))
